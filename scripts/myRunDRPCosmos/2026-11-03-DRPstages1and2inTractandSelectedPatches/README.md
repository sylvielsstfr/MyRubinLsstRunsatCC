# README.md
- created 2026-11-03 : prepare LSST-France
- updated : 2026-11-03
-
- want to run the DRP in COSMOS field from a number of selected visits
- select the visits only into COSMOS and the the early stage of DP2
- Working directory /pbs/home/d/dagoret/rubin_user/MyRubinLsstRunsatCC/scripts/myRunDRPCosmos/2026-11-03-DRPstages1and2inTractandSelectedPatches
- Note the daraQuery is improved
       dataQuery: "instrument='LSSTCam' AND skymap='lsst_cells_v2' AND tract IN (${TRACTIDS})  AND patch IN (${PATCHIDS}) AND detector IN (${CCDIDS}) AND exposure.observation_type='science'"


- refer to the cc doc on BPS here : https://doc.lsst.eu/tutorial/bps.html

## 1) init BPS
source /pbs/throng/lsst/software/bps-parsl/prod/setup.sh

## 2) run bps
bps_dp2cosmos_2026-11-03_stage1.sh
