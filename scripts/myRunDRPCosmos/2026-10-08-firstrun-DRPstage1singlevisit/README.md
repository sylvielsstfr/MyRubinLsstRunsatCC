# README.md 
- created 2026-10-06 in context of Bifrost workshop context
- updated : 2026-10-08
- 
- want to run the DRP in COSMOS field from a number of selected visits
- select the visits only into COSMOS and the the early stage of DP2
- Working directory /pbs/home/d/dagoret/rubin_user/lsst_dev/myRunDRPCosmos
  

- I try to merge the example of Cyrille Doux on blending running at CCIN2P3 copied here /pbs/home/d/dagoret/rubin_user/lsst_dev/cdoux_example
- with the example of Pierre François Leget running at USDF /pbs/home/d/dagoret/rubin_user/lsst_dev/pfleget_example


# Deprecated : run the command   sh bps_dp2cosmos.sh inside /pbs/home/d/dagoret/rubin_user/lsst_dev/myRunDRPCosmos

- refer to the cc doc on BPS here : https://doc.lsst.eu/tutorial/bps.html

## 1) init BPS
source /pbs/throng/lsst/software/bps-parsl/prod/setup.sh

## 2) run bps 
bps_submit.sh --interactive bps_dp2cosmos_parsl.yaml



