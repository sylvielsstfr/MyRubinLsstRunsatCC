# README.md
- created 2026-11-03 : prepare LSST-France
- updated : 2026-11-11
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


## History
  ### 2026-11-07 :
  correct stage2 failure inside fgcmBuildFromIsolatedStarsTask due to
  a single bad visit  (2026040400105) identified in check_fgcm_visit_catalog.py (see also notebooks/DEBUG_stage2_DiagnoseFgcmVisitCatalog.ipynb).
  The notebook DEBUG_stage2_DiagnoseFgcmVisitCatalog.ipynb also identifies 10 bad visits without PSF. Exclude the bad visit  (2026040400105) from the dataQuery.


  - inCollection: u/${USER}/LSSTCam/runcosmos01_20261103_tract9813patchsel_RunCosmos9patches/stage1,LSSTCam/defaults
  - output: u/${USER}/LSSTCam/runcosmos01_20261103_tract9813patchsel_RunCosmos9patches/stage2
  dataQuery: "instrument='LSSTCam' AND skymap='lsst_cells_v2' AND tract IN (${TRACTIDS})  AND patch IN (${PATCHIDS}) AND detector IN (${CCDIDS}) AND exposure NOT IN (2026040400105) AND exposure.observation_type='science'"

  sh bps_dp2cosmos_2026-11-03_stage2.sh
  log : slurm_bps_submit_63005758.log

### 2026-11-08 :
    Found an error in task fgcmFitCycle : the task fgcmFitCycle fails in a visit in band u that has not enough sources : thus must reduce the number of minimal stars per exposure to 100 (default is 200) in the fgcmFitCycle task. This is done by adding the following line in the bps_dp2cosmos_parsl_2026-11-03_stage2.yaml file :

  extraQgraphOptions: "-c fgcmFitCycle:minStarPerExp=100"

 - inCollection: u/${USER}/LSSTCam/runcosmos01_20261103_tract9813patchsel_RunCosmos9patches/stage1,LSSTCam/defaults
  - output: u/${USER}/LSSTCam/runcosmos01_20261103_tract9813patchsel_RunCosmos9patches/stage2_v2
  dataQuery: "instrument='LSSTCam' AND skymap='lsst_cells_v2' AND tract IN (${TRACTIDS})  AND patch IN (${PATCHIDS}) AND detector IN (${CCDIDS}) AND exposure NOT IN (${NOVISITS}) AND exposure.observation_type='science'"

   sh bps_dp2cosmos_2026-11-03_stage2.sh
   slurm_bps_submit_63020986.log




### 2026-11-11 :
  The study of FGCM itself (replaying fgcmBuildFromIsolatedStar / fgcmFitCycle / fgcmOutputProducts by hand, new
  look-up table from libRadtran, freezing the atmosphere) is NOT done in this folder : it is in
  `/Users/dagoret/Desktop/MyRubinLsstRunsatCC/notebooks/07_FGCM` (see its README.md). This folder only keeps what is
  needed to check that the bps runs went well, and the selection files that the 07_FGCM notebook reads
  (tractIds.txt, patchIds.txt, ccdIds.txt, visits_to_exclude.txt).


## Content of this directory

### Selection files (read by the bps shell scripts and by notebooks/07_FGCM)
- `tractIds.txt`, `patchIds.txt`, `ccdIds.txt` : values of `${TRACTIDS}`, `${PATCHIDS}`, `${CCDIDS}` in the dataQuery
- `visits_to_exclude.txt` : visits excluded from stage 2 (`${NOVISITS}`) : the bad visit 2026040400105 and the visits without PSF

### bps submission : one shell script + one yaml per run
All use release `w_2026_43`, `payloadName: dp2cosmos202611`, and the collection prefix
`u/${USER}/LSSTCam/runcosmos01_20261103_tract9813patchsel_RunCosmos9patches/`.

| shell script | yaml | pipeline subset (`DRP.yaml#...`) | input collections | output collection |
|---|---|---|---|---|
| `bps_dp2cosmos_2026-11-03_stage1.sh` | `bps_dp2cosmos_parsl_2026-11-03_stage1.yaml` | `stage1-single-visit` | `LSSTCam/defaults` | `.../stage1` |
| `bps_dp2cosmos_2026-11-03_step1c.sh` | `bps_dp2cosmos_parsl_2026-11-03_stage1stepc.yaml` | `step1c-single-visit-tracts` | `.../stage1`, `LSSTCam/defaults` | `.../stage1` |
| `bps_dp2cosmos_2026-11-03_step1d.sh` | `bps_dp2cosmos_parsl_2026-11-03_stage1stepd.yaml` | `step1d-single-visit-global` | `.../stage1`, `LSSTCam/defaults` | `.../stage1` |
| `bps_dp2cosmos_2026-11-03_step2a.sh` | `bps_dp2cosmos_parsl_2026-11-03_step2a.yaml` | `step2a-recalibrate-global` | `.../stage1`, `LSSTCam/defaults` | `.../stage2` |
| `bps_dp2cosmos_2026-11-03_stage2.sh` | `bps_dp2cosmos_parsl_2026-11-03_stage2.yaml` | `stage2-recalibrate` | `.../stage1`, `LSSTCam/defaults` | `.../stage2_v2` (with `-c fgcmFitCycle:minStarPerExp=100`) |

step1c, step1d and step2a are partial reruns of one step of a stage into an existing collection
(the shell scripts are the launchers of the matching yaml).

- `bps_parsl_logs/` : parsl logs of the submissions

### Checks of the failures of the stage 2 (see History 2026-11-07 and 2026-11-08)
- `check_fgcm_visit_catalog.py` : runs the real fgcmMakeVisitCatalog visit by visit in the job environment (via `quantum_runner.sh --pipelines w_2026_43`) ; output `fgcm_visit_catalog_failures.csv`
- `check_fgcm_fit_cycle.py` : reproduces on the inputs of fgcmFitCycle the cuts that lead to "All observations in %s band have been cut" ; outputs `fgcm_fit_cycle_visits.csv` (one row per visit), `fgcm_fit_cycle_band_summary.csv` (per band), `fgcm_fit_cycle_threshold_scan.csv` (scan of the minimal number of stars per exposure)
- `*_fgcmFitCycle_.stderr` : stderr of a failed fgcmFitCycle quantum, kept as reference
- `notebooks/` : notebooks that check the collections and show the plots of the bps runs (see `notebooks/README.md`)

### Where is what
- checking that the bps runs are right : this folder and `notebooks/`
- general analysis and understanding of FGCM : `/Users/dagoret/Desktop/MyRubinLsstRunsatCC/notebooks/` (in particular `07_FGCM`)


### Notes de discussion avec Claude IA
Je finalise : j’ai relu ton yaml de stage 2 et créé un script qui rejoue le vrai code fgcmcal dans l’environnement du job.

Ton test confirme que les 10 visites sans PSF ne suffisent pas. Dans le kernel w_2026_45, la médiane d’un tableau vide donne un NaN float32 de taille 1, et .item() retourne nan sans erreur. Une visite tout-NaN donne donc seulement un psfSigma NaN silencieux, pas le ValueError.

Une différence d’environnement entre le job et ton notebook. Ton yaml fixe release: w_2026_43 et lance chaque quantum par quantum_runner.sh --pipelines w_2026_43 -- pipetask .... Ton kernel est un w_2026_45 sur cvmfs. Le code de fgcmcal est identique sur ces tags (je l’ai comparé), mais numpy ou afw peuvent différer. Je n’ai pas de preuve que c’est la cause, c’est l’hypothèse à tester.

Le test décisif. J’ai créé check_fgcm_visit_catalog.py dans scripts/myRunDRPCosmos/2026-11-03-DRPstages1and2inTractandSelectedPatches/. Il se lance comme le job, via le même wrapper et la même release :

bash
${BPS_PARSL_CCIN2P3}/quantum_runner.sh --pipelines w_2026_43 -- python check_fgcm_visit_catalog.py --stride 20

Il fait trois choses :

Il affiche les versions de numpy et de fgcmcal, plus le test « médiane d’un tableau vide puis .item() » dans cet environnement.
Il lit la caméra et la look-up table, et indique la valeur de useScienceDetectors que la task choisirait.
Il exécute le vrai fgcmMakeVisitCatalog visite par visite, pour les deux valeurs de useScienceDetectors. Il écrit les visites qui échouent dans fgcm_visit_catalog_failures.csv et affiche la première trace complète.

Le script est vérifié en syntaxe seulement. Les noms FgcmBuildFromIsolatedStarsConfig / FgcmBuildFromIsolatedStarsTask et le dataset fgcmLookUpTable sont supposés ; si l’import ou la lecture échoue, ajuste-les.

Comment lire le résultat

Si .item() échoue dans w_2026_43, c’est confirmé : toute visite sans PSF valide fait planter fgcm dans cette release. Exclure les 10 visites de visits_to_exclude.txt règle alors le problème.
Si le test numpy passe mais que le vrai code échoue sur certaines visites, tu auras la visite et la trace complète.
Si tout passe aussi dans w_2026_43, la cause est ailleurs, dans le contexte du job lui-même (qgraph, handles qbb, visites du graphe). Colle-moi la sortie et on creusera à partir de là.

Tu peux aussi lancer la section 7 du notebook 07 dans ton kernel w_2026_45 : si ça passe partout là-bas, ça renforce l’hypothèse d’un écart d’environnement.
