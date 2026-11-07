"""Replay fgcmcal's fgcmMakeVisitCatalog on the stage-1 preliminary_visit_summary datasets,
in the software environment of the bps job.

The stage-2 quantum fgcmBuildFromIsolatedStar failed in this function with
    ValueError: can only convert an array of size 1 to a Python scalar
(fgcmBuildStarsBase.py, _fillVisitCatalog, rec['psfSigma'] = psfSigma.item()).
Already established: the numpy behaviour of the job environment is the same as in the
notebook kernel (median of an empty float32 selection is a float32 NaN, .item() works), and
no visit summary of the latest stage-1 run makes the hand-written replay fail.

This script runs the REAL task code, configured exactly as in the pipeline (the config
comes from ${DRP_PIPE_DIR}/pipelines/LSSTCam/DRP.yaml#stage2-recalibrate), and with
--all-runs also on the datasets of every stage-1 run, not only the first one found in the chain.

Usage at CC-IN2P3 (same wrapper and release as runQuantumCommand in the bps yaml):

    ${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_visit_catalog.py --stride 20
    ${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_visit_catalog.py --all-runs
"""
import argparse
import logging
import os
import platform
import sys
import traceback
from collections import Counter

import numpy as np
import lsst.fgcmcal
from lsst.daf.butler import Butler
from lsst.pipe.base import Pipeline

parser = argparse.ArgumentParser()
parser.add_argument('--repo', default='main')
parser.add_argument('--run-tag', default='runcosmos01_20261103_tract9813patchsel_RunCosmos9patches')
parser.add_argument('--task-label', default='fgcmBuildFromIsolatedStar')
parser.add_argument('--stride', type=int, default=1, help='use one dataset out of STRIDE')
parser.add_argument('--all-runs', action='store_true',
                    help='replay the datasets of every stage-1 run, not only the first found in the chain')
args = parser.parse_args()

user = os.getenv('USER')
stage1 = f'u/{user}/LSSTCam/{args.run_tag}/stage1'
defaults = 'LSSTCam/defaults'
instrument = 'LSSTCam'

# 1. the environment
print('python        :', platform.python_version())
print('numpy         :', np.__version__)
print('fgcmcal from  :', lsst.fgcmcal.__file__)

# 2. the task, configured as in the pipeline
drp_pipe_dir = os.getenv('DRP_PIPE_DIR')
if not drp_pipe_dir:
    sys.exit('DRP_PIPE_DIR is not set in this environment')
pipeline_uri = f'{drp_pipe_dir}/pipelines/LSSTCam/DRP.yaml#stage2-recalibrate'
graph = Pipeline.from_uri(pipeline_uri).to_graph()
node = graph.tasks[args.task_label]
task = node.task_class(config=node.config)
print('pipeline      :', pipeline_uri)
print('task class    :', node.task_class_name)
print('referenceCCD  :', task.config.referenceCCD, '| primaryBands:', list(task.config.primaryBands))

# 3. the data
logging.getLogger('lsst').setLevel(logging.WARNING)
butler = Butler(args.repo, collections=[stage1, defaults])
refs = sorted(butler.registry.queryDatasets('preliminary_visit_summary', collections=[stage1],
                                            findFirst=not args.all_runs),
              key=lambda r: (int(r.dataId['visit']), r.run))
print(len(refs), 'preliminary_visit_summary datasets', '(all runs)' if args.all_runs else '(first found in the chain)')
for run, n in Counter(ref.run for ref in refs).items():
    print(f'   {n:6d} in {run}')
per_visit = Counter(int(ref.dataId['visit']) for ref in refs)
print('visits with more than one dataset:', sum(1 for n in per_visit.values() if n > 1), 'of', len(per_visit))
refs = refs[::args.stride]

try:
    camera = butler.get('camera', instrument=instrument, exposure=int(refs[0].dataId['visit']))
except Exception:
    from lsst.obs.lsst import LsstCam
    camera = LsstCam().getCamera()

lut_nccd = None
try:
    lut = butler.get('fgcmLookUpTable', instrument=instrument)
    lut_nccd = int(lut[0]['nCcd'])
except Exception as exc:
    print('fgcmLookUpTable not read:', type(exc).__name__, str(exc)[:150])
print('detectors in the camera:', len(camera), '| nCcd in the look-up table:', lut_nccd)
if lut_nccd is not None:
    print('the task uses useScienceDetectors =', len(camera) != lut_nccd)

# 4. the real code, one summary at a time
failures = []
first_traceback = None
for use_science in (False, True):
    n_fail = 0
    for ref in refs:
        visit = int(ref.dataId['visit'])
        try:
            task.fgcmMakeVisitCatalog(camera, {visit: [butler.getDeferred(ref), None]},
                                      useScienceDetectors=use_science)
        except Exception as exc:
            n_fail += 1
            failures.append((use_science, visit, ref.run, f'{type(exc).__name__}: {str(exc)[:150]}'))
            if first_traceback is None:
                first_traceback = traceback.format_exc()
    print(f'useScienceDetectors={use_science}: {n_fail} failing datasets out of {len(refs)}')

with open('fgcm_visit_catalog_failures.csv', 'w') as fh:
    fh.write('use_science,visit,run,error' + chr(10))
    for use_science, visit, run, err in failures:
        fh.write(f'{use_science},{visit},{run},"{err}"' + chr(10))
print('failures written to fgcm_visit_catalog_failures.csv')
if first_traceback:
    print('first traceback:')
    print(first_traceback)
