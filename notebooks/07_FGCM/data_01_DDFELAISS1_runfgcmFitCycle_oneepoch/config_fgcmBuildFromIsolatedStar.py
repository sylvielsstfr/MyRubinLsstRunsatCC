import lsst.fgcmcal.fgcmBuildFromIsolatedStars
assert type(config) is lsst.fgcmcal.fgcmBuildFromIsolatedStars.FgcmBuildFromIsolatedStarsConfig, f"config is of type {type(config).__module__}.{type(config).__name__} instead of lsst.fgcmcal.fgcmBuildFromIsolatedStars.FgcmBuildFromIsolatedStarsConfig"

import lsst.fgcmcal.fgcmLoadReferenceCatalog
import lsst.meas.algorithms.flaggedSourceSelector
import lsst.meas.algorithms.objectSizeStarSelector
import lsst.meas.algorithms.sourceSelector
import lsst.pipe.base.config
import lsst.pipe.tasks.colorterms
import lsst.pipe.tasks.reserveIsolatedStars
# Flag to enable/disable saving of log output for a task, enabled by default.
config.saveLogOutput=True

# Faull name of the source instFlux field to use, including 'instFlux'. The associated flag will be implicitly included in badFlags
config.instFluxField='normCompTophatFlux_instFlux'

# Minimum observations per band
config.minPerBand=2

# Match radius (arcseconds)
config.matchRadius=1.0

# Isolation radius (arcseconds)
config.isolationRadius=2.0

# Density cut healpix nside
config.densityCutNside=128

# Density cut number of stars per pixel
config.densityCutMaxPerPixel=1000

# Random seed for high density down-sampling.
config.randomSeed=123456

# Healpix Nside for matching
config.matchNside=4096

# Healpix coarse Nside for partitioning matches
config.coarseNside=64

# Mapping from 'physicalFilter' to band.
config.physicalFilterMap={'u_24': 'u', 'g_6': 'g', 'r_57': 'r', 'i_39': 'i', 'z_20': 'z', 'y_10': 'y'}

# Bands required for each star
config.requiredBands=[]

# Bands for 'primary' star matches. A star must be observed in one of these bands to be considered as a calibration star.
config.primaryBands=['i', 'r', 'g', 'z', 'y', 'u']

# Apply the jacobian of the WCS to the star observations prior to fit?
config.doApplyWcsJacobian=True

# Model flux errors with background term?
config.doModelErrorsWithBackground=True

# Name of field with psf candidate flag for propagation
config.psfCandidateName='calib_psf_candidate'

# Subtract the local background before performing calibration? This is only supported for circular aperture calibration fluxes.
config.doSubtractLocalBackground=False

# Full name of the local background instFlux field to use.
config.localBackgroundFluxField='localBackground_instFlux'

# Apply flux limit?
config.sourceSelector['science'].doFluxLimit=False

# Apply flag limitation?
config.sourceSelector['science'].doFlags=False

# Apply unresolved limitation?
config.sourceSelector['science'].doUnresolved=False

# Apply signal-to-noise limit?
config.sourceSelector['science'].doSignalToNoise=True

# Apply isolated limitation?
config.sourceSelector['science'].doIsolated=False

# Apply finite sky coordinate check?
config.sourceSelector['science'].doRequireFiniteRaDec=False

# Apply source is primary check?
config.sourceSelector['science'].doRequirePrimary=False

# Include sky sources, unioned with all other criteria?
config.sourceSelector['science'].doSkySources=False

# Apply limit on centroid errors?
config.sourceSelector['science'].doCentroidErrorLimit=False

# Select objects with value greater than this
config.sourceSelector['science'].fluxLimit.minimum=None

# Select objects with value less than this
config.sourceSelector['science'].fluxLimit.maximum=None

# Name of the source flux field to use.
config.sourceSelector['science'].fluxLimit.fluxField='slot_CalibFlux_instFlux'

# List of source flag fields that must be set for a source to be used.
config.sourceSelector['science'].flags.good=[]

# List of source flag fields that must NOT be set for a source to be used.
config.sourceSelector['science'].flags.bad=[]

# Select objects with value greater than this
config.sourceSelector['science'].unresolved.minimum=None

# Select objects with value less than this
config.sourceSelector['science'].unresolved.maximum=0.5

# Name of column for star/galaxy separation
config.sourceSelector['science'].unresolved.name='base_ClassificationSizeExtendedness_value'

# Select objects with value greater than this
config.sourceSelector['science'].signalToNoise.minimum=9.0

# Select objects with value less than this
config.sourceSelector['science'].signalToNoise.maximum=1000.0

# Name of the source flux field to use.
config.sourceSelector['science'].signalToNoise.fluxField='normCompTophatFlux_instFlux'

# Name of the source flux error field to use.
config.sourceSelector['science'].signalToNoise.errField='normCompTophatFlux_instFluxErr'

# Name of column for parent
config.sourceSelector['science'].isolated.parentName='parent'

# Name of column for nChild
config.sourceSelector['science'].isolated.nChildName='deblend_nChild'

# Name of column for RA coordinate
config.sourceSelector['science'].requireFiniteRaDec.raColName='coord_ra'

# Name of column for Dec coordinate
config.sourceSelector['science'].requireFiniteRaDec.decColName='coord_dec'

# Name of primary flag column
config.sourceSelector['science'].requirePrimary.primaryColName='detect_isPrimary'

# List of source flag fields that must be set for a source to be used.
config.sourceSelector['science'].skyFlag.good=['sky_source']

# List of source flag fields that must NOT be set for a source to be used.
config.sourceSelector['science'].skyFlag.bad=[]

# Select objects with value greater than this
config.sourceSelector['science'].centroidErrorLimit.minimum=None

# Select objects with value less than this
config.sourceSelector['science'].centroidErrorLimit.maximum=3.0

# Name of the source centroid field to use.
config.sourceSelector['science'].centroidErrorLimit.centroidField='slot_Centroid'

# Apply magnitude limit?
config.sourceSelector['references'].doMagLimit=False

# Apply flag limitation?
config.sourceSelector['references'].doFlags=False

# Apply unresolved limitation?
config.sourceSelector['references'].doUnresolved=False

# Apply signal-to-noise limit?
config.sourceSelector['references'].doSignalToNoise=False

# Apply magnitude error limit?
config.sourceSelector['references'].doMagError=False

# Apply finite sky coordinate check?
config.sourceSelector['references'].doRequireFiniteRaDec=True

# Apply image masked region culling?
config.sourceSelector['references'].doCullFromMaskedRegion=False

# Select objects with value greater than this
config.sourceSelector['references'].magLimit.minimum=None

# Select objects with value less than this
config.sourceSelector['references'].magLimit.maximum=None

# Name of the source flux field to use.
config.sourceSelector['references'].magLimit.fluxField='flux'

# List of source flag fields that must be set for a source to be used.
config.sourceSelector['references'].flags.good=[]

# List of source flag fields that must NOT be set for a source to be used.
config.sourceSelector['references'].flags.bad=[]

# Select objects with value greater than this
config.sourceSelector['references'].unresolved.minimum=None

# Select objects with value less than this
config.sourceSelector['references'].unresolved.maximum=0.1

# Name of column for star/galaxy separation
config.sourceSelector['references'].unresolved.name='base_ClassificationSizeExtendedness_value'

# Name of column for RA coordinate
config.sourceSelector['references'].requireFiniteRaDec.raColName='coord_ra'

# Name of column for Dec coordinate
config.sourceSelector['references'].requireFiniteRaDec.decColName='coord_dec'

# Select objects with value greater than this
config.sourceSelector['references'].signalToNoise.minimum=None

# Select objects with value less than this
config.sourceSelector['references'].signalToNoise.maximum=None

# Name of the source flux field to use.
config.sourceSelector['references'].signalToNoise.fluxField='flux'

# Name of the source flux error field to use.
config.sourceSelector['references'].signalToNoise.errField='flux_err'

# Select objects with value greater than this
config.sourceSelector['references'].magError.minimum=None

# Select objects with value less than this
config.sourceSelector['references'].magError.maximum=None

# Name of the source flux error field to use.
config.sourceSelector['references'].magError.magErrField='mag_err'

config.sourceSelector['references'].colorLimits={}
# List of mask planes for which sources should be removed if a bit is set.
config.sourceSelector['references'].cullFromMaskedRegion.badMaskNames=['NO_DATA', 'NOT_DEBLENDED']

# Name of column for image x coordinate.
config.sourceSelector['references'].cullFromMaskedRegion.xColName='centroid_x'

# Name of column for image y coordinate.
config.sourceSelector['references'].cullFromMaskedRegion.yColName='centroid_y'

# Apply flux limit to Psf Candidate selection?
config.sourceSelector['objectSize'].doFluxLimit=False

# Minimum flux value for good Psf Candidates.
config.sourceSelector['objectSize'].fluxMin=12500.0

# Maximum flux value for good Psf Candidates (ignored if == 0).
config.sourceSelector['objectSize'].fluxMax=0.0

# Apply signal-to-noise (i.e. flux/fluxErr) limit to Psf Candidate selection?
config.sourceSelector['objectSize'].doSignalToNoiseLimit=True

# Minimum signal-to-noise for good Psf Candidates (value should take into consideration the detection thresholds set for the catalog of interest).
config.sourceSelector['objectSize'].signalToNoiseMin=50.0

# Maximum signal-to-noise for good Psf Candidates (ignored if == 0).
config.sourceSelector['objectSize'].signalToNoiseMax=0.0

# Minimum width to include in histogram.
config.sourceSelector['objectSize'].widthMin=0.9

# Maximum width to include in histogram.
config.sourceSelector['objectSize'].widthMax=10.0

# Name of field in Source to use for flux measurement.
config.sourceSelector['objectSize'].sourceFluxField='base_PsfFlux_instFlux'

# Standard deviation of width allowed to be interpreted as good stars.
config.sourceSelector['objectSize'].widthStdAllowed=0.15

# Keep objects within this many sigma of cluster 0's median.
config.sourceSelector['objectSize'].nSigmaClip=2.0

# List of flags which cause a source to be rejected as bad.
config.sourceSelector['objectSize'].badFlags=['base_PixelFlags_flag_edge', 'base_PixelFlags_flag_nodata', 'base_PixelFlags_flag_interpolatedCenter', 'base_PixelFlags_flag_saturatedCenter', 'base_PixelFlags_flag_crCenter', 'base_PixelFlags_flag_bad', 'base_PixelFlags_flag_interpolated', 'slot_Centroid_flag']

# Name of a flag field that is True for Sources that should be used.
config.sourceSelector['flagged'].field='calib_psf_used'

config.sourceSelector.name='science'
# Full name of instFlux field that contains inner aperture flux for aperture correction proxy
config.apertureInnerInstFluxField='apFlux_12_0_instFlux'

# Full name of instFlux field that contains outer aperture flux for aperture correction proxy
config.apertureOuterInstFluxField='apFlux_17_0_instFlux'

# Match reference catalog as additional constraint on calibration
config.doReferenceMatches=True

# Mapping from physicalFilter label to reference filter name.
config.fgcmLoadReferenceCatalog.filterMap={'none': 'monster_ComCam_r', 'white': 'monster_ComCam_r', 'u_24': 'monster_ComCam_u', 'g_6': 'monster_ComCam_g', 'r_57': 'monster_ComCam_r', 'i_39': 'monster_ComCam_i', 'z_20': 'monster_ComCam_z', 'y_10': 'monster_ComCam_y', 'u': 'monster_ComCam_u', 'g': 'monster_ComCam_g', 'r': 'monster_ComCam_r', 'i': 'monster_ComCam_i', 'z': 'monster_ComCam_z', 'y': 'monster_ComCam_y'}

# Apply photometric color terms to reference stars?Requires that colorterms be set to a ColorTermLibrary
config.fgcmLoadReferenceCatalog.applyColorTerms=False

config.fgcmLoadReferenceCatalog.colorterms.data={}
# Apply magnitude limit?
config.fgcmLoadReferenceCatalog.referenceSelector.doMagLimit=False

# Apply flag limitation?
config.fgcmLoadReferenceCatalog.referenceSelector.doFlags=False

# Apply unresolved limitation?
config.fgcmLoadReferenceCatalog.referenceSelector.doUnresolved=False

# Apply signal-to-noise limit?
config.fgcmLoadReferenceCatalog.referenceSelector.doSignalToNoise=True

# Apply magnitude error limit?
config.fgcmLoadReferenceCatalog.referenceSelector.doMagError=False

# Apply finite sky coordinate check?
config.fgcmLoadReferenceCatalog.referenceSelector.doRequireFiniteRaDec=True

# Apply image masked region culling?
config.fgcmLoadReferenceCatalog.referenceSelector.doCullFromMaskedRegion=False

# Select objects with value greater than this
config.fgcmLoadReferenceCatalog.referenceSelector.magLimit.minimum=None

# Select objects with value less than this
config.fgcmLoadReferenceCatalog.referenceSelector.magLimit.maximum=None

# Name of the source flux field to use.
config.fgcmLoadReferenceCatalog.referenceSelector.magLimit.fluxField='flux'

# List of source flag fields that must be set for a source to be used.
config.fgcmLoadReferenceCatalog.referenceSelector.flags.good=[]

# List of source flag fields that must NOT be set for a source to be used.
config.fgcmLoadReferenceCatalog.referenceSelector.flags.bad=[]

# Select objects with value greater than this
config.fgcmLoadReferenceCatalog.referenceSelector.unresolved.minimum=None

# Select objects with value less than this
config.fgcmLoadReferenceCatalog.referenceSelector.unresolved.maximum=0.1

# Name of column for star/galaxy separation
config.fgcmLoadReferenceCatalog.referenceSelector.unresolved.name='base_ClassificationSizeExtendedness_value'

# Name of column for RA coordinate
config.fgcmLoadReferenceCatalog.referenceSelector.requireFiniteRaDec.raColName='coord_ra'

# Name of column for Dec coordinate
config.fgcmLoadReferenceCatalog.referenceSelector.requireFiniteRaDec.decColName='coord_dec'

# Select objects with value greater than this
config.fgcmLoadReferenceCatalog.referenceSelector.signalToNoise.minimum=50.0

# Select objects with value less than this
config.fgcmLoadReferenceCatalog.referenceSelector.signalToNoise.maximum=None

# Name of the source flux field to use.
config.fgcmLoadReferenceCatalog.referenceSelector.signalToNoise.fluxField='monster_ComCam_i_flux'

# Name of the source flux error field to use.
config.fgcmLoadReferenceCatalog.referenceSelector.signalToNoise.errField='monster_ComCam_i_fluxErr'

# Select objects with value greater than this
config.fgcmLoadReferenceCatalog.referenceSelector.magError.minimum=None

# Select objects with value less than this
config.fgcmLoadReferenceCatalog.referenceSelector.magError.maximum=None

# Name of the source flux error field to use.
config.fgcmLoadReferenceCatalog.referenceSelector.magError.magErrField='mag_err'

config.fgcmLoadReferenceCatalog.referenceSelector.colorLimits={}
# List of mask planes for which sources should be removed if a bit is set.
config.fgcmLoadReferenceCatalog.referenceSelector.cullFromMaskedRegion.badMaskNames=['NO_DATA', 'NOT_DEBLENDED']

# Name of column for image x coordinate.
config.fgcmLoadReferenceCatalog.referenceSelector.cullFromMaskedRegion.xColName='centroid_x'

# Name of column for image y coordinate.
config.fgcmLoadReferenceCatalog.referenceSelector.cullFromMaskedRegion.yColName='centroid_y'

# Number of visits read between checkpoints
config.nVisitsPerCheckpoint=500

# Reference detector for checking PSF and background.
config.referenceCCD=40

# Name to use for random seed selection hash.
config.reserve_selection.reserve_name='fgcmcal'

# Fraction of stars to reserve.  None if == 0.
config.reserve_selection.reserve_fraction=0.1

# name for connection camera
config.connections.camera='camera'

# name for connection fgcm_lookup_table
config.connections.fgcm_lookup_table='fgcmLookUpTable'

# name for connection ref_cat
config.connections.ref_cat='the_monster_20250219'

# name for connection isolated_star_cats
config.connections.isolated_star_cats='isolated_star_association'

# name for connection isolated_star_sources
config.connections.isolated_star_sources='isolated_star'

# name for connection visit_summaries
config.connections.visit_summaries='preliminary_visit_summary'

# name for connection fgcm_visit_catalog
config.connections.fgcm_visit_catalog='fgcmVisitCatalog'

# name for connection fgcm_star_observations
config.connections.fgcm_star_observations='fgcm_star_observations'

# name for connection fgcm_star_ids
config.connections.fgcm_star_ids='fgcm_star_ids'

# name for connection fgcm_reference_stars
config.connections.fgcm_reference_stars='fgcm_reference_stars'
