# notebooks : checking the bps runs of the COSMOS DRP

- created : 2026-11-11

These notebooks check that the bps runs submitted from the parent folder
(`../README.md`, runs `stage1`, `stage2`, `stage2_v2`) produced what they should : which datasets exist in the
collections, what they contain, and what the `analysis_tools` plots look like.

They are about **verifying the runs**. The study of FGCM itself (replaying the step 2a tasks, new look-up table,
injecting the AuxTel atmosphere) is in `/Users/dagoret/Desktop/MyRubinLsstRunsatCC/notebooks/07_FGCM`.

All of them need a kernel with the LSST stack (same release as the jobs, `w_2026_43`) and a Butler pointing to `main`.

Collections used (prefix `u/${USER}/LSSTCam/runcosmos01_20261103_tract9813patchsel_RunCosmos9patches/`) :
`stage1`, `stage2` (first stage 2 attempt and step2a rerun), `stage2_v2` (stage 2 with `fgcmFitCycle:minStarPerExp=100`).

## Files

| file | what it does |
|---|---|
| `nb2026-11-05_CheckCollections_DRPstage1-single-visit.ipynb` | Lists the datasets of the `stage1` collection and looks at their content. |
| `nb2026-11-05_CheckCollections_DRPstage2-recalibrate.ipynb` | Same for the inputs and outputs of the stage 2 (`stage2-recalibrate`), including the `fgcm_*` datasets. |
| `nb2026-11-05_CheckCollections_DRPstage2-recalibrate_v2.ipynb` | Second version of the previous notebook, for the `stage2_v2` run. |
| `nb2026-11-06_ComparePostISRvsPreliminaryImage_DRPstage1-step1a.ipynb` | Compares the post-ISR image with the preliminary image of step 1a. |
| `nb2026-11-06_ShowPlots_DRPstage1-single-visit.ipynb` | Displays the `lsst.analysis.tools` plots (`*Plot` datasets) of the stage 1. |
| `nb2026-11-06_ShowPlots_DRPstage2-recalibrate.ipynb` | Same for the stage 2. |
| `showplots_utils.py` | Helper functions imported by the two `ShowPlots` notebooks. |
| `DEBUG_stage2_DiagnoseFgcmVisitCatalog.ipynb` | Diagnosis of the failure of `fgcmBuildFromIsolatedStar` : identifies the bad visit `2026040400105` and the 10 visits without PSF (see `../README.md`, History 2026-11-07). |

`.ipynb_checkpoints/` is created by Jupyter : it should not be committed.

## Related

- `../check_fgcm_visit_catalog.py`, `../check_fgcm_fit_cycle.py` : scripts (not notebooks) that reproduce the stage 2 failures in the job environment ;
- the quantum graph diagrams and `pipeline_drp_pipe_LSSTCam_DRP.yaml` (tasks of each stage / step) are in
  `/Users/dagoret/Desktop/MyRubinLsstRunsatCC/notebooks/fig_diagrams`.
