# 07_FGCM : understanding FGCM and injecting the AuxTel atmosphere

- created : 2026-11-11
- status : **written but not yet executed** (to be committed, pushed and tested at CC-IN2P3)

## Goal

FGCM (`lsst.fgcmcal`, step 2a of the DRP `stage2-recalibrate`) fits the atmosphere (PWV, O3, aerosols) *and* the
instrument at the same time. The final goal is to **inject the atmospheric parameters measured by AuxTel**
(libRadtran, through the emulator [getObsAtmo](https://github.com/LSSTDESC/getObsAtmo)) so that FGCM only fits the
many instrumental effects.

This needs three things, and this folder is where they are studied one after the other :

1. understand what the three tasks of step 2a read and write, and be able to replay them by hand ;
2. replace the MODTRAN4-based `fgcmLookUpTable` by one computed with libRadtran ;
3. control what `fgcmFitCycle` is allowed to fit (freeze the atmosphere to the AuxTel values).

The tasks are `fgcmBuildFromIsolatedStar` -> `fgcmFitCycle` -> `fgcmOutputProducts`
(pipeline subset `DRP.yaml#step2a-recalibrate-global`). All three read `fgcmLookUpTable`, so changing it
invalidates the three of them : they are always replayed together.

The *checks of the bps runs* (did the submitted jobs behave ?) are **not** here : they are in
`../../scripts/myRunDRPCosmos/2026-11-03-DRPstages1and2inTractandSelectedPatches/` (see its `README.md`).

## Files

| file | what it does |
|---|---|
| `01_runfgcmFitCyle.ipynb` | Replays step 2a from the stage1 collection of the COSMOS run. Reads the pipeline connections and configs, inventories the inputs (stage1 + `LSSTCam/defaults`), shows the `fgcmLookUpTable`, builds (and optionally runs) `pipetask qgraph` / `pipetask run`, then displays the outputs : star observations per visit and the `fgcmFitCycle` cuts, fit parameters, zero points, and the comparison with the bps run `stage2_v2`. |
| `make_fgcm_lut_obsatmo.sh` | Builds the fgcm atmosphere table from getObsAtmo, then runs `FgcmMakeLutTask` (`fgcmMakeLUT.yaml`) to produce a new `fgcmLookUpTable` in the collection `u/${USER}/LSSTCam/fgcm_lut_<TAG>`. |
| `../../src/make_fgcm_atm_table_from_obsatmo.py` | Called by the shell script. Evaluates getObsAtmo on the fgcm grids and writes the FITS atmosphere table (same layout as `fgcm_atm_lsst2.fits`). With `--check --reference <table>` it reads the table back with fgcm, compares with the emulator and with the shipped MODTRAN table, and makes a comparison figure. |

Directories created when running (not to be committed) :

- `data_01_runfgcmFitCycle/`, `figs_01_runfgcmFitCycle/` : CSV, task configs, qgraph, logs and figures of the notebook ;
- `data_fgcm_atm_<TAG>/` : the FITS atmosphere table, its comparison figure and the log of the LUT run.

## How to use

1. **Replay without change.** Open `01_runfgcmFitCyle.ipynb` (kernel with the same release as the bps jobs, `w_2026_43`).
   With the defaults (`EXECUTE = False`, `INSPECT = 'reference'`) nothing is run : it only inspects the existing
   `stage2_v2` collection. Then set `EXECUTE = True` to replay the three tasks into
   `u/${USER}/LSSTCam/<run>/fgcm_nb01`, set `INSPECT = 'new'` and check that the zero points reproduce `stage2_v2`
   (section 9 of the notebook). `RUN_DIR` points to the bps run folder to read `tractIds.txt`, `patchIds.txt`,
   `ccdIds.txt` and `visits_to_exclude.txt`.
2. **New look-up table.** `./make_fgcm_lut_obsatmo.sh obsatmo01`. Requires the lsst stack, astropy and getObsAtmo
   (`pip install --user git+https://github.com/LSSTDESC/getObsAtmo.git`). The script needs `FGCMCAL_DIR` ;
   `FGCM_DIR` is optional (used for the comparison with `fgcm_atm_lsst2`).
3. **Replay with the new table.** In the notebook set `LUT_COLLECTION = f'u/{username}/LSSTCam/fgcm_lut_obsatmo01'`
   (it is chained before `LSSTCam/defaults`) and rerun. The output collection gets the suffix `_newlut`.
   The difference of zero points with the first replay is the effect of MODTRAN -> libRadtran alone.
4. **Freeze the atmosphere** (not written yet, see below).

## What was learned from the fgcm / fgcmcal code

(read on the main branch of `lsst/fgcm` and `lsst/fgcmcal` : to be confirmed on the tag used at CC)

- The atmosphere table is a FITS file : a `PARS` table (grids `PMB`, `LNPWV`, `O3`, `LNTAU`, `ALPHA`, `SECZENITH`,
  standard values, `ATMLAMBDA` in Angstrom, `ATMSTDTRANS`) and four images `PWVATM`, `O3ATM`, `O2ATM`, `RAYATM`.
  Each axis has one extra node. Aerosols are not in the table : fgcm applies
  `exp(-tau * secZ * (lambda / 7750 A)^-alpha)` itself.
- `FgcmMakeLutTask` reads this table through `atmosphereTableName` (a full path is accepted). The LSSTCam config of
  `obs_lsst` uses `fgcm_atm_lsst2`. It produces `fgcmLookUpTable`, `fgcm_standard_atmosphere`,
  `fgcm_standard_passband` and `standard_passband`.
- The atmosphere is fitted **per night** : `parO3`, `parAlpha`, `parLnTauIntercept/Slope`,
  `parLnPwvIntercept/Slope/Quadratic`. `freezeStdAtmosphere=True` sets their bounds equal to their *current value*,
  so editing a `FitParameters` catalog before a cycle and freezing should keep the injected values (to be tested).
- `fgcmcal` does not pass the fgcm `pwvFile` option (external PWV), and `externalTau` is not implemented in fgcm.
  A per-visit PWV cannot be injected with this mechanism : the parameters are nightly.

## Known limits and choices to confirm

- The getObsAtmo table stops at airmass 2.5 (emulator limit 2.6 including the extra grid node), the shipped table goes to ~2.9.
- Pressure : default grid 720-750 hPa and standard pressure = reference pressure of the emulator for LSST (731.5 hPa).
  The shipped `lsst2` table uses 770-790 hPa and 778 hPa as standard : check what is wanted for Rubin
  (`--pmb-range`, `--pmb-steps`, `--pmb-std`).
- Spectral resolution : ~1 nm for the emulator against 0.5 nm for the table of fgcm : narrow lines (O2 A-band, H2O
  near 940 nm) are smoothed. Agreement with the MODTRAN table is ~1 % in median and 2-3 % rms, concentrated in these bands.
- The time of `FgcmMakeLutTask` with per-detector transmissions is unknown.
- `pipetask qgraph` with the data query of the bps scripts (with `patch` and `detector`) failed at CC-IN2P3 with
  `temp_file_limit exceeded` (postgres). The three tasks only have dimensions `{instrument}`, so the notebook uses
  `QUERY_MODE = 'minimal'` by default (instrument, skymap, tract, `visit NOT IN (...)`). `QUERY_MODE = 'bps'` restores
  the original query, and `QGRAPH_EXTRA_OPTIONS = ['--dataset-query-constraint', 'preliminary_visit_summary']` is the next
  thing to try if the query is still too heavy. The kernel (`w_2026_45`) is also not the release of the bps jobs
  (`w_2026_43`).
- Tested so far : the table builder and its read-back by fgcm (outside the lsst stack). Not tested : the notebook,
  the shell script and the LUT run on Butler.

## Next steps

- Notebook `02_` : single-cycle run (`doMultipleCycles=False`, `cycleNumber>0`) with an edited `FitParameters`
  catalog containing the AuxTel values and `freezeStdAtmosphere=True`.
- Compare AuxTel and fgcm atmospheric parameters night by night.
