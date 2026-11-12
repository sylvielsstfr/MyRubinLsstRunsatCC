"""Why does fgcmFitCycle stop with "FATAL: All observations in %s band have been cut!"?

fgcm (fgcmExposureSelector.selectGoodExposures, then checkFlaggedExposuresPerBand) flags every
exposure/visit that fails one of these cuts:

    BAD_FWHM               psfFwhm > config.expFwhmCutDict[band]
    NO_STARS               no good star observation in the visit
    TOO_FEW_STARS          fewer than config.minStarPerExp good star observations (default 600)
    EXP_GRAY_TOO_NEGATIVE / EXP_GRAY_TOO_POSITIVE   exposure gray outside the per-band cuts
    VAR_GRAY_TOO_LARGE     gray variance above config.expVarGrayPhotometricCutDict[band]

and raises as soon as, in one band, all the visits but at most one are flagged. The message does
not say which band ("%s" is never filled in).

With a small footprint (one tract, a few patches) a visit contains far fewer stars than a
typical survey visit, so TOO_FEW_STARS is the first suspect. This script reads the inputs of
fgcmFitCycle that were written by fgcmBuildFromIsolatedStar in the stage-2 collection:

    fgcmVisitCatalog                         one row per visit (band, psfFwhm, ...)
    fgcm_star_observations / fgcm_star_ids   star observations and star ids (parquet format)

and applies the first three cuts per visit, which only need these inputs. A visit with fewer
*observations* than minStarPerExp certainly has fewer *good stars* than minStarPerExp, so the
flagged counts below are lower bounds: if they already reach "all visits but one" in a band, that
band certainly makes fgcmFitCycle fail. The gray cuts need the fit itself and are not replayed.

The task configuration (cuts per band, minStarPerExp, ...) is read from the pipeline, exactly as
in the bps job.

Usage at CC-IN2P3 (same wrapper and release as runQuantumCommand in the bps yaml):

    ${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_fit_cycle.py
    ${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_fit_cycle.py \
        --stage2-run u/dagoret/LSSTCam/<run_tag>/stage2/<timestamp>

Note: the outputs of the quanta executed by bps (here fgcmVisitCatalog and the star catalogs) are
registered in the butler repository by the final bps job (transfer-from-graph). If the script
cannot find them, that job has not run (or not for this run): run it first, or give the run
collection with --stage2-run.
"""
import argparse
import logging
import os
import platform
import sys

import numpy as np
import pandas as pd
import lsst.fgcmcal
from lsst.daf.butler import Butler
from lsst.pipe.base import Pipeline

parser = argparse.ArgumentParser()
parser.add_argument('--repo', default='main')
parser.add_argument('--run-tag', default='runelaiss1_20261111_tract2877patchsel_mediumpatcharray')
parser.add_argument('--task-label', default='fgcmFitCycle')
parser.add_argument('--stage2-run', default=None,
                    help='run collection holding the stage-2 outputs; default: all runs under .../stage2/, newest first')
parser.add_argument('--min-star-per-exp', type=int, default=None,
                    help='override config.minStarPerExp (to test another threshold)')
parser.add_argument('--out-prefix', default='fgcm_fit_cycle')
args = parser.parse_args()

pd.set_option('display.width', 220)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 200)

user = os.getenv('USER')
stage1 = f'u/{user}/LSSTCam/{args.run_tag}/stage1/20261111T170346Z'
stage2 = f'u/{user}/LSSTCam/{args.run_tag}/stage2_v2'
defaults = 'LSSTCam/defaults'
instrument = 'LSSTCam'

# 1. the environment
print('python        :', platform.python_version())
print('numpy         :', np.__version__)
print('fgcmcal from  :', lsst.fgcmcal.__file__)

# 2. the task configuration, as in the pipeline
drp_pipe_dir = os.getenv('DRP_PIPE_DIR')
if not drp_pipe_dir:
    sys.exit('DRP_PIPE_DIR is not set in this environment')
pipeline_uri = f'{drp_pipe_dir}/pipelines/LSSTCam/DRP.yaml#stage2-recalibrate'
graph = Pipeline.from_uri(pipeline_uri).to_graph()
node = graph.tasks[args.task_label]
config = node.config
print('pipeline      :', pipeline_uri)
print('task class    :', node.task_class_name)
for name in ('cycleNumber', 'isFinalCycle', 'multipleCyclesFinalCycleNumber', 'useParquetCatalogFormat',
             'minStarPerExp', 'minExpPerNight', 'expGrayInitialCut'):
    print(f'   {name:34s}', getattr(config, name, 'n/a'))
for name in ('bands', 'fitBands', 'expFwhmCutDict', 'expGrayPhotometricCutDict', 'expGrayHighCutDict',
             'expVarGrayPhotometricCutDict'):
    value = getattr(config, name, 'n/a')
    print(f'   {name:34s}', dict(value) if hasattr(value, 'items') else value)
min_star = args.min_star_per_exp if args.min_star_per_exp is not None else int(config.minStarPerExp)
# extraQgraphOptions: "-c fgcmFitCycle:minStarPerExp=100"
min_star = 100
fwhm_cut = dict(getattr(config, 'expFwhmCutDict', {}) or {})
print('minStarPerExp used here:', min_star)

# 3. the data written by fgcmBuildFromIsolatedStar
logging.getLogger('lsst').setLevel(logging.WARNING)
butler = Butler(args.repo)
registry = butler.registry
if args.stage2_run:
    stage2_runs = [args.stage2_run]
else:
    stage2_runs = sorted(registry.queryCollections(f'{stage2}/*'), reverse=True)
collections = stage2_runs + [stage1, defaults]
print('stage-2 runs searched (newest first):')
for run in stage2_runs:
    print('   ', run)


def find_one(dataset_type):
    try:
        refs = list(registry.queryDatasets(dataset_type, collections=collections, findFirst=True))
    except Exception as exc:
        print(f'   {dataset_type}: query failed ({type(exc).__name__}: {str(exc)[:120]})')
        return None
    return refs[0] if refs else None


visit_ref = find_one('fgcmVisitCatalog')
if visit_ref is None:
    sys.exit('fgcmVisitCatalog not found in the registry: has the final bps job (transfer-from-graph) run for '
             'this stage-2 run? Pass --stage2-run if the run is not under ' + stage2)
print('fgcmVisitCatalog found in', visit_ref.run)

use_parquet = bool(getattr(config, 'useParquetCatalogFormat', True))
if not use_parquet:
    sys.exit('this script reads the parquet star catalogs (fgcm_star_observations); config.useParquetCatalogFormat is False')
obs_ref = find_one('fgcm_star_observations')
ids_ref = find_one('fgcm_star_ids')
if obs_ref is None:
    sys.exit('fgcm_star_observations not found in the registry')
print('fgcm_star_observations found in', obs_ref.run)

# 3a. visit catalog -> one row per visit
catalog = butler.get(visit_ref)
scalar_fields = ['visit', 'physicalFilter', 'mjd', 'exptime', 'psfSigma', 'psfFwhm', 'deltaAper',
                 'skyBackground', 'used']
fields = [name for name in scalar_fields if name in catalog.schema]
visits = pd.DataFrame([{name: rec[name] for name in fields} for rec in catalog])
band_of = {rec.name: rec.band for rec in registry.queryDimensionRecords('physical_filter', instrument=instrument)}
visits['band'] = visits['physicalFilter'].map(band_of)
print()
print(len(visits), 'visits in fgcmVisitCatalog;', int(visits['used'].sum()), "marked 'used'")

# 3b. star observations -> number of observations per visit
obs = butler.get(obs_ref)
print('fgcm_star_observations:', len(obs), 'observations; columns:', list(obs.colnames))
if ids_ref is not None:
    print('fgcm_star_ids:', len(butler.get(ids_ref)), 'stars')
n_obs = pd.Series(np.asarray(obs['visit'])).value_counts()
visits['n_obs'] = visits['visit'].map(n_obs).fillna(0).astype(int)

# 4. the cuts of selectGoodExposures that only need these inputs
visits['fwhm_cut'] = visits['band'].map(fwhm_cut)
visits['BAD_FWHM'] = (visits['psfFwhm'] > visits['fwhm_cut']).fillna(False)
visits['NO_STARS'] = visits['n_obs'] == 0
visits['TOO_FEW_STARS'] = (visits['n_obs'] > 0) & (visits['n_obs'] < min_star)
visits['flagged'] = visits['BAD_FWHM'] | visits['NO_STARS'] | visits['TOO_FEW_STARS']

summary = visits.groupby('band').agg(
    n_visits=('visit', 'size'),
    n_bad_fwhm=('BAD_FWHM', 'sum'),
    n_no_stars=('NO_STARS', 'sum'),
    n_too_few_stars=('TOO_FEW_STARS', 'sum'),
    n_flagged=('flagged', 'sum'),
    median_obs=('n_obs', 'median'),
    max_obs=('n_obs', 'max'),
    median_fwhm=('psfFwhm', 'median'),
)
summary['n_not_flagged'] = summary['n_visits'] - summary['n_flagged']
summary['FATAL_FOR_SURE'] = summary['n_flagged'] >= summary['n_visits'] - 1
print()
print(f'Per band, with minStarPerExp = {min_star} (flag counts are lower bounds, see the docstring):')
print(summary.to_string())

fatal = list(summary.index[summary['FATAL_FOR_SURE']])
print()
if fatal:
    print('Bands that make checkFlaggedExposuresPerBand raise for sure:', fatal)
else:
    print('No band is certainly fatal with these three cuts: the failure then comes from the gray cuts')
    print('(EXP_GRAY_TOO_NEGATIVE / EXP_GRAY_TOO_POSITIVE / VAR_GRAY_TOO_LARGE); look at the full fgcmFitCycle log,')
    print('which prints "band: N of M exposures" for each flag and each band.')

# 5. what other value of minStarPerExp would keep enough visits?
thresholds = [1, 10, 25, 50, 100, 200, 300, 600]
scan = pd.DataFrame({thr: visits[~visits['BAD_FWHM'] & (visits['n_obs'] >= thr)].groupby('band').size()
                     for thr in thresholds}).fillna(0).astype(int)
scan.insert(0, 'n_visits', visits.groupby('band').size())
print()
print('Visits kept (observations >= threshold and not BAD_FWHM) per band, for several minStarPerExp:')
print(scan.to_string())

print()
print('Number of star observations per visit, percentiles per band:')
quantiles = visits.groupby('band')['n_obs'].quantile([0.0, 0.1, 0.5, 0.9, 1.0]).unstack()
print(quantiles.to_string())

visits.drop(columns=['physicalFilter']).to_csv(f'{args.out_prefix}_visits.csv', index=False)
summary.to_csv(f'{args.out_prefix}_band_summary.csv')
scan.to_csv(f'{args.out_prefix}_threshold_scan.csv')
print()
print(f'written: {args.out_prefix}_visits.csv, {args.out_prefix}_band_summary.csv, {args.out_prefix}_threshold_scan.csv')
