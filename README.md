# MyRubinLsstRunsatCC
A collection of config files, script to run LSST-pipelines in the context of CCIN2P3 Farm

- creation date : 2025-10-25

## Request an account at CCIN2P3

- if member of LSST: see https://doc.cc.in2p3.fr/en/Daily-usage/users.html#request-an-account
  

## LSST Environnement at CCIN2P3

```bash
# Execute profile for the 'lsst' group
if [[ -r "/pbs/throng/lsst/etc/profile" ]]; then
    source "/pbs/throng/lsst/etc/profile"
fi
```


## Request an IndigoIAM account

To access to a butler with Rubin data, one need an accout
- see the documentation here : https://doc.lsst.eu/tutorial/indigoiam.html

## Do we need PostGres credential

- Access to butler at CC: https://doc.lsst.eu/tutorial/community-butlers.html
 Need to ask for a secret password.



## Get a valid token

Need three commands

```bash
lsstfr register 
lsstfr login
lsstfr token
```

## DM environment

Validated release at CCIN2P3 : release: w_2026_40

```bash
source /cvmfs/sw.lsst.eu/almalinux-x86_64/lsst_distrib/w_2026_40/loadLSST.sh
setup lsst_distrib
butler query-dataset-types --verbose main
```

## BPS environnment

- documentation : https://doc.lsst.eu/tutorial/bps.html

```bash
source /pbs/throng/lsst/software/bps-parsl/prod/setup.sh
export BPS_RUNDIR=/sps/lsst/users/${USER}/bps
```