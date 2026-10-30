#
#    --extra-qgraph-options "--config-file isr:isrLSST.py" \
#export VISITIDS=$(paste -sd, exposure_lists/exposures_2025_05.txt)
export CCDIDS=$(paste -sd, ccdIds.txt)

#echo "Init Visits and CCDS"
#echo $VISITIDS
echo "Init CCDS"
echo $CCDIDS

echo "init rubin-lsst setup"
#source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/w_2026_40/loadLSST.sh
#setup lsst_distrib

#define the release
release="w_2026_43"
export LSST_RELEASE=${release}

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
#bps_submit.sh --interactive bps_dp2cosmos_parsl_2026-10-27_stage1.yaml

# No interactive mode for a long run
bps_submit.sh bps_dp2cosmos_parsl_2026-10-28_stage1.yaml
