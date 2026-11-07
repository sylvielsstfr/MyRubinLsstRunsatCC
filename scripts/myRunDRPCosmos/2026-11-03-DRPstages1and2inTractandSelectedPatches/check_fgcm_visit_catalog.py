"""Replay fgcmcal's fgcmMakeVisitCatalog on every stage-1 preliminary_visit_summary,
in the software environment of the bps job.

The stage-2 quantum fgcmBuildFromIsolatedStar failed in this function with
    ValueError: can only convert an array of size 1 to a Python scalar
(fgcmBuildStarsBase.py, _fillVisitCatalog, rec['psfSigma'] = psfSigma.item()),
but the same computation does not fail in the w_2026_45 kernel. This script runs the real
code in the very environment used by the job (same release, same container) to see
whether it fails there, and for which visit.

Usage at CC-IN2P3 (same wrapper and release as runQuantumCommand in the bps yaml):

    ${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_visit_catalog.py
    ${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_visit_catalog.py --stride 20
"""
import argparse
import logging
import os
import platform
import traceback

import numpy as np
import lsst.fgcmcal
from lsst.daf.butler import Butler
from lsst.fgcmcal.fgcmBuildFromIsolatedStars import (FgcmBuildFromIsolatedStarsConfig,
                                                      FgcmBuildFromIsolatedStarsTask)

parser = argparse.ArgumentParser()
parser.add_argument('--repo', default='main')
parser.add_argument('--run-tag', default='runcosmos01_20261103_tract9813patchsel_RunCosmos9patches')
parser.add_argument('--stride', type=int, default=1, help='use one visit out of STRIDE')
args = parser.parse_args()

user = os.getenv('USER')
stage1 = f'u/{user}/LSSTCam/{args.run_tag}/stage1'
defaults = 'LSSTCam/defaults'
instrument = 'LSSTCam'

# 1. the environment
print('python        :', platform.python_version())
print('numpy         :', np.__version__)
print('fgcmcal from  :', lsst.fgcmcal.__file__)
print('LSST_LIBRARY_PATH / EUPS_PATH:', os.getenv('EUPS_PATH'))

# 2. the numpy behaviour the task relies on (median of an empty selection, then .item())
empty = np.median(np.array([], dtype=np.float32))
print('median of empty float32:', type(empty), empty, 'size', np.size(empty))
try:
    print('   .item() ->', empty.item())
except Exception as exc:
    print('   .item() FAILS:', type(exc).__name__, exc)

# 3. the real fgcmcal code on the real visit summaries
logging.getLogger('lsst').setLevel(logging.WARNING)
butler = Butler(args.repo, collections=[stage1, defaults])
refs = sorted(butler.registry.queryDatasets('preliminary_visit_summary', collections=[stage1], findFirst=True),
              key=lambda r: r.dataId['visit'])
print(len(refs), 'preliminary_visit_summary datasets in', stage1)
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
    print('the task would use useScienceDetectors =', len(camera) != lut_nccd)

task = FgcmBuildFromIsolatedStarsTask(config=FgcmBuildFromIsolatedStarsConfig())
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
            failures.append((use_science, visit, f'{type(exc).__name__}: {str(exc)[:150]}'))
            if first_traceback is None:
                first_traceback = traceback.format_exc()
    print(f'useScienceDetectors={use_science}: {n_fail} failing visits out of {len(refs)}')

with open('fgcm_visit_catalog_failures.csv', 'w') as fh:
    fh.write('use_science,visit,error' + chr(10))
    for use_science, visit, err in failures:
        fh.write(f'{use_science},{visit},"{err}"' + chr(10))
print('failures written to fgcm_visit_catalog_failures.csv')
if first_traceback:
    print('first traceback:')
    print(first_traceback)
