# -*- coding: utf-8 -*-
#
#    --extra-qgraph-options "--config-file isr:isrLSST.py" \
export CCDIDS=$(paste -sd, ccdIds.txt)
export PATCHIDS=$(paste -sd, patchIds_mediumarray.txt)
export TRACTIDS=$(paste -sd, tractIds.txt)
export NOVISITS=$(paste -sd, visits_to_exclude.txt)

echo "Prepare to run RUBIN-LSST STAGE2 pipeline on some tract and patches belonging to DDF ELAIS S1"

echo "Init EXPOSURES EXCLUDED"
echo $NOVISITS

echo "Init list of CCDS"
echo $CCDIDS

echo "Init list of Tracts"
echo $TRACTIDS

echo "Init list of PATCHES"
echo $PATCHIDS



echo "init rubin-lsst setup"
#source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/w_2026_40/loadLSST.sh
#setup lsst_distrib

#define the release
release="w_2026_43"
export LSST_RELEASE=${release}
echo "LSST_RELEASE : ${LSST_RELEASE}"

exit 0

#launch LSST libs

ARCH=$(uname -m)
case "$ARCH" in
    x86_64)
        source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/${release}/loadLSST.sh
        ;;

    aarch64)
        source /cvmfs/sw.lsst.eu/almalinux-aarch64/lsst_distrib/${release}/loadLSST.sh
        ;;

    *)
        echo "Architecture non supportée : $ARCH"
        exit 1
        ;;
esac
setup lsst_distrib

echo "init BPS"
source /pbs/throng/lsst/software/bps-parsl/prod/setup.sh

echo "run BPS"
#bps_submit.sh --interactive bps_dp2cosmos_parsl_2026-11-05_stage2.yaml

# No interactive mode for a long run
bps_submit.sh bps_dp2elaiss1_parsl_2026-11-11_stage2.yaml
