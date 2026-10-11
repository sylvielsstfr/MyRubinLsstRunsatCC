# !/bin/sh

# activate DM w_2026_40 (2026-10-08)
release="w_2026_40"

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
