#!/bin/sh


# added 2026-10-06 add the groupe config
# Execute profile for the 'lsst' group
if [[ -r "/pbs/throng/lsst/etc/profile" ]]; then
    source "/pbs/throng/lsst/etc/profile"
fi
# added 2026-10-08
source /pbs/throng/lsst/software/bps-parsl/prod/setup.sh

# added 2026-10-06
export BPS_RUNDIR=/sps/lsst/users/${USER}/bps
