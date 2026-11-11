#!/bin/bash
# Build an fgcm atmosphere table from the getObsAtmo (libRadtran) emulator, then build the
# fgcmLookUpTable of LSSTCam from it with FgcmMakeLutTask.
#
# Outputs of the pipetask run (all with dimensions {instrument}) :
#   fgcmLookUpTable, fgcm_standard_atmosphere, fgcm_standard_passband, standard_passband
# in the chained collection u/${USER}/LSSTCam/fgcm_lut_${TAG}. To use it, put this collection BEFORE
# LSSTCam/defaults in the input collections of the three step2a tasks (LUT_COLLECTION in 01_runfgcmFitCyle.ipynb).
#
# Prerequisites : the lsst stack set up (same release as the stage 2 run), astropy, and getObsAtmo, e.g.
#   pip install --user git+https://github.com/LSSTDESC/getObsAtmo.git
#
# Usage : ./make_fgcm_lut_obsatmo.sh [TAG]        (default TAG = obsatmo01)

set -euo pipefail

TAG=${1:-obsatmo01}
HERE=$(cd "$(dirname "$0")" && pwd)                     # notebooks/07_FGCM
SRC=$(cd "${HERE}/../../src" && pwd)                    # MyRubinLsstRunsatCC/src
OUTDIR=${HERE}/data_fgcm_atm_${TAG}
TABLE=${OUTDIR}/fgcm_atm_lsst_${TAG}.fits               # absolute path : read by FgcmMakeLutTask
REFERENCE_TABLE=${FGCM_DIR:-}/fgcm/data/tables/fgcm_atm_lsst2.fits   # optional, for the comparison figure
LUT_COLLECTION=u/${USER}/LSSTCam/fgcm_lut_${TAG}
PIPELINE=${FGCMCAL_DIR}/pipelines/LSSTCam/fgcmMakeLUT.yaml

mkdir -p "${OUTDIR}"

echo "=== 1. atmosphere table from getObsAtmo : ${TABLE}"
CHECK_OPTS=""
if [ -f "${REFERENCE_TABLE}" ]; then
    CHECK_OPTS="--check --reference ${REFERENCE_TABLE} --figure ${OUTDIR}/vs_reference_${TAG}.png"
fi
python "${SRC}/make_fgcm_atm_table_from_obsatmo.py" -o "${TABLE}" --clobber ${CHECK_OPTS}

echo "=== 2. fgcmLookUpTable with FgcmMakeLutTask -> ${LUT_COLLECTION}"
if [ ! -f "${PIPELINE}" ]; then
    echo "pipeline ${PIPELINE} not found : check FGCMCAL_DIR" >&2
    exit 1
fi

# The LSSTCam config of obs_lsst gives physicalFilters (u_24 ... y_10) and doFilterDetectorTransmission=True;
# only the atmosphere table is replaced (default : "fgcm_atm_lsst2").
pipetask run -b main \
    -i LSSTCam/defaults \
    -o "${LUT_COLLECTION}" \
    -p "${PIPELINE}" \
    -c fgcmMakeLut:atmosphereTableName="${TABLE}" \
    -d "instrument='LSSTCam'" \
    --register-dataset-types \
    2>&1 | tee "${OUTDIR}/pipetask_makeLut_${TAG}.log"

echo "=== done. Check with :"
echo "  butler query-datasets main fgcmLookUpTable --collections ${LUT_COLLECTION}"
