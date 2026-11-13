import lsst.fgcmcal.fgcmOutputProducts
assert type(config) is lsst.fgcmcal.fgcmOutputProducts.FgcmOutputProductsConfig, f"config is of type {type(config).__module__}.{type(config).__name__} instead of lsst.fgcmcal.fgcmOutputProducts.FgcmOutputProductsConfig"

import lsst.meas.algorithms.reserveSourcesTask
import lsst.meas.algorithms.sourceSelector
import lsst.meas.astrom.directMatch
import lsst.pipe.base.config
import lsst.pipe.tasks.colorterms
import lsst.pipe.tasks.photoCal
# Flag to enable/disable saving of log output for a task, enabled by default.
config.saveLogOutput=True

# Mapping from 'physicalFilter' to band.
config.physicalFilterMap={'u_24': 'u', 'g_6': 'g', 'r_57': 'r', 'i_39': 'i', 'z_20': 'z', 'y_10': 'y'}

# Transfer 'absolute' calibration from reference catalog? This afterburner step is unnecessary if reference stars were used in the full fit in FgcmFitCycleTask.
config.doReferenceCalibration=False

# Output atmospheres in transmission_atmosphere_fgcm format
config.doAtmosphereOutput=True

# Output zeropoints in fgcm_photoCalib format
config.doZeropointOutput=True

# Compose Jacobian of WCS with fgcm calibration for output photoCalib?
config.doComposeWcsJacobian=True

# Apply the mean chromatic correction to the zeropoints?
config.doApplyMeanChromaticCorrection=True

# Output tract-sharded standard stars?
config.doTractStars=True

# Matching radius, arcsec
config.photoCal.match.matchRadius=0.25

# Apply flux limit?
config.photoCal.match.sourceSelection.doFluxLimit=False

# Apply flag limitation?
config.photoCal.match.sourceSelection.doFlags=True

# Apply unresolved limitation?
config.photoCal.match.sourceSelection.doUnresolved=False

# Apply signal-to-noise limit?
config.photoCal.match.sourceSelection.doSignalToNoise=True

# Apply isolated limitation?
config.photoCal.match.sourceSelection.doIsolated=False

# Apply finite sky coordinate check?
config.photoCal.match.sourceSelection.doRequireFiniteRaDec=False

# Apply source is primary check?
config.photoCal.match.sourceSelection.doRequirePrimary=False

# Include sky sources, unioned with all other criteria?
config.photoCal.match.sourceSelection.doSkySources=False

# Apply limit on centroid errors?
config.photoCal.match.sourceSelection.doCentroidErrorLimit=False

# Select objects with value greater than this
config.photoCal.match.sourceSelection.fluxLimit.minimum=None

# Select objects with value less than this
config.photoCal.match.sourceSelection.fluxLimit.maximum=None

# Name of the source flux field to use.
config.photoCal.match.sourceSelection.fluxLimit.fluxField='slot_CalibFlux_instFlux'

# List of source flag fields that must be set for a source to be used.
config.photoCal.match.sourceSelection.flags.good=[]

# List of source flag fields that must NOT be set for a source to be used.
config.photoCal.match.sourceSelection.flags.bad=['flag_badStar']

# Select objects with value greater than this
config.photoCal.match.sourceSelection.unresolved.minimum=None

# Select objects with value less than this
config.photoCal.match.sourceSelection.unresolved.maximum=0.1

# Name of column for star/galaxy separation
config.photoCal.match.sourceSelection.unresolved.name='base_ClassificationSizeExtendedness_value'

# Select objects with value greater than this
config.photoCal.match.sourceSelection.signalToNoise.minimum=10.0

# Select objects with value less than this
config.photoCal.match.sourceSelection.signalToNoise.maximum=None

# Name of the source flux field to use.
config.photoCal.match.sourceSelection.signalToNoise.fluxField='instFlux'

# Name of the source flux error field to use.
config.photoCal.match.sourceSelection.signalToNoise.errField='instFluxErr'

# Name of column for parent
config.photoCal.match.sourceSelection.isolated.parentName='parent'

# Name of column for nChild
config.photoCal.match.sourceSelection.isolated.nChildName='deblend_nChild'

# Name of column for RA coordinate
config.photoCal.match.sourceSelection.requireFiniteRaDec.raColName='coord_ra'

# Name of column for Dec coordinate
config.photoCal.match.sourceSelection.requireFiniteRaDec.decColName='coord_dec'

# Name of primary flag column
config.photoCal.match.sourceSelection.requirePrimary.primaryColName='detect_isPrimary'

# List of source flag fields that must be set for a source to be used.
config.photoCal.match.sourceSelection.skyFlag.good=['sky_source']

# List of source flag fields that must NOT be set for a source to be used.
config.photoCal.match.sourceSelection.skyFlag.bad=[]

# Select objects with value greater than this
config.photoCal.match.sourceSelection.centroidErrorLimit.minimum=None

# Select objects with value less than this
config.photoCal.match.sourceSelection.centroidErrorLimit.maximum=3.0

# Name of the source centroid field to use.
config.photoCal.match.sourceSelection.centroidErrorLimit.centroidField='slot_Centroid'

# Apply magnitude limit?
config.photoCal.match.referenceSelection.doMagLimit=False

# Apply flag limitation?
config.photoCal.match.referenceSelection.doFlags=False

# Apply unresolved limitation?
config.photoCal.match.referenceSelection.doUnresolved=False

# Apply signal-to-noise limit?
config.photoCal.match.referenceSelection.doSignalToNoise=True

# Apply magnitude error limit?
config.photoCal.match.referenceSelection.doMagError=False

# Apply finite sky coordinate check?
config.photoCal.match.referenceSelection.doRequireFiniteRaDec=True

# Apply image masked region culling?
config.photoCal.match.referenceSelection.doCullFromMaskedRegion=False

# Select objects with value greater than this
config.photoCal.match.referenceSelection.magLimit.minimum=None

# Select objects with value less than this
config.photoCal.match.referenceSelection.magLimit.maximum=None

# Name of the source flux field to use.
config.photoCal.match.referenceSelection.magLimit.fluxField='flux'

# List of source flag fields that must be set for a source to be used.
config.photoCal.match.referenceSelection.flags.good=[]

# List of source flag fields that must NOT be set for a source to be used.
config.photoCal.match.referenceSelection.flags.bad=[]

# Select objects with value greater than this
config.photoCal.match.referenceSelection.unresolved.minimum=None

# Select objects with value less than this
config.photoCal.match.referenceSelection.unresolved.maximum=0.1

# Name of column for star/galaxy separation
config.photoCal.match.referenceSelection.unresolved.name='base_ClassificationSizeExtendedness_value'

# Name of column for RA coordinate
config.photoCal.match.referenceSelection.requireFiniteRaDec.raColName='coord_ra'

# Name of column for Dec coordinate
config.photoCal.match.referenceSelection.requireFiniteRaDec.decColName='coord_dec'

# Select objects with value greater than this
config.photoCal.match.referenceSelection.signalToNoise.minimum=10.0

# Select objects with value less than this
config.photoCal.match.referenceSelection.signalToNoise.maximum=None

# Name of the source flux field to use.
config.photoCal.match.referenceSelection.signalToNoise.fluxField='flux'

# Name of the source flux error field to use.
config.photoCal.match.referenceSelection.signalToNoise.errField='flux_err'

# Select objects with value greater than this
config.photoCal.match.referenceSelection.magError.minimum=None

# Select objects with value less than this
config.photoCal.match.referenceSelection.magError.maximum=None

# Name of the source flux error field to use.
config.photoCal.match.referenceSelection.magError.magErrField='mag_err'

config.photoCal.match.referenceSelection.colorLimits={}
# List of mask planes for which sources should be removed if a bit is set.
config.photoCal.match.referenceSelection.cullFromMaskedRegion.badMaskNames=['NO_DATA', 'NOT_DEBLENDED']

# Name of column for image x coordinate.
config.photoCal.match.referenceSelection.cullFromMaskedRegion.xColName='centroid_x'

# Name of column for image y coordinate.
config.photoCal.match.referenceSelection.cullFromMaskedRegion.yColName='centroid_y'

# Fraction of candidates to reserve from fitting; none if <= 0
config.photoCal.reserve.fraction=0.0

# This number will be added to the exposure ID to set the random seed for reserving candidates
config.photoCal.reserve.seed=1

# Name of the source instFlux field to use.
# The associated flag field ('<name>_flags') will be implicitly included in badFlags.
config.photoCal.fluxField='instFlux'

# Apply photometric color terms to reference stars?
# `True`: attempt to apply color terms; fail if color term data is not available for the specified reference catalog and filter.
# `False`: do not apply color terms.
config.photoCal.applyColorTerms=False

# maximum sigma to use when clipping
config.photoCal.sigmaMax=0.25

# clip at nSigma
config.photoCal.nSigma=3.0

# use median instead of mean to compute zeropoint
config.photoCal.useMedian=True

# number of iterations
config.photoCal.nIter=20

config.photoCal.colorterms.data={}
# Name of photometric reference catalog; used to select a color term dict in colorterms.
# See also applyColorTerms.
config.photoCal.photoCatName=None

# Additional magnitude uncertainty to be added in quadrature with measurement errors.
config.photoCal.magErrFloor=0.003

# Healpix nside to pixelize catalog to compare to reference catalog
config.referencePixelizationNside=64

# Minimum number of stars per healpix pixel to select for comparisonto the specified reference catalog
config.referencePixelizationMinStars=200

# Minimum number of stars matched to reference catalog to be used in statistics
config.referenceMinMatch=50

# Number of healpix pixels to sample to do comparison. Doing too many will take a long time and not yield any more precise results because the final number is the median offset (per band) from the set of pixels.
config.referencePixelizationNPixels=100

# name for connection camera
config.connections.camera='camera'

# name for connection skymap
config.connections.skymap='skyMap'

# name for connection fgcmLookUpTable
config.connections.fgcmLookUpTable='fgcmLookUpTable'

# name for connection fgcmVisitCatalog
config.connections.fgcmVisitCatalog='fgcmVisitCatalog'

# name for connection fgcmStandardStars
config.connections.fgcmStandardStars='fgcm_Cycle{cycleNumber}_StandardStars'

# name for connection fgcmZeropoints
config.connections.fgcmZeropoints='fgcm_Cycle{cycleNumber}_Zeropoints'

# name for connection fgcmAtmosphereParameters
config.connections.fgcmAtmosphereParameters='fgcm_Cycle{cycleNumber}_AtmosphereParameters'

# name for connection refCat
config.connections.refCat='cal_ref_cat'

# name for connection fgcmPhotoCalib
config.connections.fgcmPhotoCalib='fgcmPhotoCalibCatalog'

# name for connection fgcmTransmissionAtmosphere
config.connections.fgcmTransmissionAtmosphere='transmission_atmosphere_fgcm'

# name for connection fgcmOffsets
config.connections.fgcmOffsets='fgcmReferenceCalibrationOffsets'

# name for connection fgcmTractStars
config.connections.fgcmTractStars='fgcm_standard_star'

# Template parameter used to format corresponding field template parameter
config.connections.cycleNumber='5'
