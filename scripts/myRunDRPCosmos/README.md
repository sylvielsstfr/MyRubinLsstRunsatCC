# README.md

- author : Sylvie Dagoret-Campagne
- creation date : 2026-11-17

## Goal
Runs bps rubin-lsst pipelines on stage1 and stage2 in the DDF COSMOS.
A series of runs is performed by increasing the size of the region starting by a single patch


## Various run series

### 2026-10-08-firstrun-DRPstage1singlevisit:
- Try a single visit.

### 2026-10-14-MultiVisits-DRPstage1singlevisit-try2:
- try a single visit

### 2026-10-11-MultiVisits-DRPstage1singlevisit:
- try multiple visits (specified explicitely)

### 2026-11-03-DRPstages1and2inTractandSelectedPatches:
- First successful run by selected one tract and 9 patches
- able to run stage1,step1c, step1d and stage2


### 2026-11-16-DRPstages1and2inOneTract:
- try to run over a whole tract:
- run stage1
- run step1 ? need more memory
- step2d failed tu to large memory
- no Plot seen
