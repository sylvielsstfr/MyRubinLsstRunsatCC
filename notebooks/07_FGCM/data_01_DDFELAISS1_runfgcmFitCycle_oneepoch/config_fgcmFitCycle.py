import lsst.fgcmcal.fgcmFitCycle
assert type(config) is lsst.fgcmcal.fgcmFitCycle.FgcmFitCycleConfig, f"config is of type {type(config).__module__}.{type(config).__name__} instead of lsst.fgcmcal.fgcmFitCycle.FgcmFitCycleConfig"

import lsst.fgcmcal.sedterms
import lsst.pipe.base.config
# Flag to enable/disable saving of log output for a task, enabled by default.
config.saveLogOutput=True

# Run multiple fit cycles in one task
config.doMultipleCycles=True

# Use parquet catalog format?
config.useParquetCatalogFormat=True

# Final cycle number in multiple cycle mode.  The initial cycle is 0, with limited parameters fit.  The next cycle is 1 with full parameter fit.  The final cycle is a clean-up with no parameters fit.  There will be a total of (multipleCycleFinalCycleNumber + 1) cycles run, and the final cycle number cannot be less than 2.
config.multipleCyclesFinalCycleNumber=5

# Bands to run calibration
config.bands=['u', 'g', 'r', 'i', 'z', 'y']

# Bands to use in atmospheric fit. The bands not listed here will have the atmosphere constrained from the 'fitBands' on the same night. Must be a subset of `config.bands`
config.fitBands=['u', 'g', 'r', 'i', 'z', 'y']

# Bands that are required for a star to be considered a calibration star. Must be a subset of `config.bands`
config.requiredBands=[]

# Mapping from 'physicalFilter' to band.
config.physicalFilterMap={'u_24': 'u', 'g_6': 'g', 'r_57': 'r', 'i_39': 'i', 'z_20': 'z', 'y_10': 'y'}

# Use reference catalog as additional constraint on calibration
config.doReferenceCalibration=True

# Reference star signal-to-noise minimum to use in calibration.  Set to <=0 for no cut.
config.refStarSnMin=50.0

# Number of sigma compared to average mag for reference star to be considered an outlier. Computed per-band, and if it is an outlier in any band it is rejected from fits.
config.refStarOutlierNSig=4.0

# Apply color cuts defined in ``starColorCuts`` to reference stars? These cuts are in addition to any cuts defined in ``refStarColorCuts``
config.applyRefStarColorCuts=True

# Maximum fraction of reference stars to use in the fit. Remainder will be used only for validation.
config.refStarMaxFracUse=0.5

# Use per-exposure (visit) offsets between calibrated stars and reference stars for final zeropoints? This may help uniformity for disjoint surveys.
config.useExposureReferenceOffset=False

# Number of stars to run in each chunk. Larger values tend to be faster for large datasets, at the expense of some memory overhead.
config.nStarPerRun=200000

# Number of stars to run in each chunk (including gray correction). Increasing this value may increase the peak memory use significantly.
config.nStarPerGrayRun=50000

# Number of observations to run in each chunk. Larger values tend to be faster for large datasets, at the expense of some memory overhead.
config.nObsPerRun=500000

# Number of observations to run in each chunk (including gray correction). Increasing this value may increase the peak memory use significantly.
config.nObsPerGrayRun=100000

# Number of exposures to run in each chunk
config.nExpPerRun=100

# Fraction of stars to reserve for testing
config.reserveFraction=0.1

# Freeze atmosphere parameters to standard (for testing)
config.freezeStdAtmosphere=True

# Precompute superstar flat for initial cycle
config.precomputeSuperStarInitialCycle=True

# Per-band specification on whether to compute superstar flat on sub-ccd scale. Must have one entry per band.
config.superStarSubCcdDict={'u': True, 'g': True, 'r': True, 'i': True, 'z': True, 'y': True}

# Order of the 2D chebyshev polynomials for sub-ccd superstar fit. Global default is first-order polynomials, and should be overridden on a camera-by-camera basis depending on the ISR.
config.superStarSubCcdChebyshevOrder=2

# Should the sub-ccd superstar chebyshev matrix be triangular to suppress high-order cross terms?
config.superStarSubCcdTriangular=False

# Number of sigma to clip outliers when selecting for superstar flats
config.superStarSigmaClip=5.0

# If plotting is enabled, should per-detector residuals be plotted? This may produce a lot of output, and should be used only for debugging purposes.
config.superStarPlotCcdResiduals=False

# When computing the super-star flat, force the focal-plane mean to zero (per band)? This should only be used when computing stand-alone illumination corrections.
config.superStarForceZeroMean=False

# Number of sigma to clip outliers per focal-plane.
config.focalPlaneSigmaClip=4.0

# Per-band specification on whether to compute achromatic per-ccd residual ('ccd gray') on a sub-ccd scale. This will only be used as a fallback if ``ccdGrayFocalPlaneDict[band]`` is set to True.
config.ccdGraySubCcdDict={'u': True, 'g': True, 'r': True, 'i': True, 'z': True, 'y': True}

# Order of the 2D chebyshev polynomials for sub-ccd gray fit.
config.ccdGraySubCcdChebyshevOrder=1

# Should the sub-ccd gray chebyshev matrix be triangular to suppress high-order cross terms?
config.ccdGraySubCcdTriangular=True

# Per-band specification on whether to compute focal-plane residual ('ccd gray') corrections. The focal-plane residuals will be used instead of per-CCD residuals except when there are insufficient good CCDs (see ``ccdGrayFocalPlaneFitMinCcd``). Therefore, this is not recommended for large focal planes with non-photometric exposures.
config.ccdGrayFocalPlaneDict={'u': False, 'g': False, 'r': False, 'i': False, 'z': False, 'y': False}

# Minimum number of 'good' CCDs required to perform focal-plane gray corrections.  If there are fewer good CCDs then the gray correction is computed per-ccd.
config.ccdGrayFocalPlaneFitMinCcd=3

# Order of the 2D chebyshev polynomials for focal plane fit.
config.ccdGrayFocalPlaneChebyshevOrder=2

# Maximum number of stars to use for focal plane fit. Required to keep matrix memory usage from running away. If there are more stars than this then they will be down-sampled.
config.ccdGrayFocalPlaneMaxStars=10000

# FGCM fit cycle number.  This is automatically incremented after each run and stage of outlier rejection.  See cookbook for details.
config.cycleNumber=0

# Is this the final cycle of the fitting?  Will automatically compute final selection of stars and photometric exposures, and will output zeropoints and standard stars for use in fgcmOutputProducts
config.isFinalCycle=False

# Maximum fit iterations, prior to final cycle.  The number of iterations will always be 0 in the final cycle for cleanup and final selection.
config.maxIterBeforeFinalCycle=100

# Percentile brightest stars on a visit/ccd to use to compute net offset from local background subtraction.
config.deltaMagBkgOffsetPercentile=0.25

# Compute net offset from local background subtraction per-ccd? Otherwise, use computation per visit.
config.deltaMagBkgPerCcd=False

# Boundary (in UTC) from day-to-day
config.utBoundary=0.0

# Mirror wash MJDs
config.washMjds=[0.0]

# Epoch boundaries in MJD
config.epochMjds=[0.0, 100000.0]

# Minimum good observations per band
config.minObsPerBand=2

# Observatory latitude
config.latitude=-30.2333

# Mirror area (square meters) of telescope.  If not set, will try to estimate from camera.telescopeDiameter.
config.mirrorArea=34.524

# Average camera gain. If not set, will use the median of the camera model/detector/amplifier gains.
config.cameraGain=1.0

# Default camera orientation for QA plots.
config.defaultCameraOrientation=0.0

# Maximum gray extinction to be considered bright observation
config.brightObsGrayMax=0.15

# Minimum number of good stars per CCD to be used in calibration fit. CCDs with fewer stars will have their calibration estimated from other CCDs in the same visit, with zeropoint error increased accordingly.
config.minStarPerCcd=5

# Minimum number of good CCDs per exposure/visit to be used in calibration fit. Visits with fewer good CCDs will have CCD zeropoints estimated where possible.
config.minCcdPerExp=10

# Maximum error on CCD gray offset to be considered photometric
config.maxCcdGrayErr=0.05

# Minimum number of good stars per exposure/visit to be used in calibration fit. Visits with fewer good stars will have CCD zeropoints estimated where possible.
config.minStarPerExp=100

# Minimum number of good exposures/visits to consider a partly photometric night
config.minExpPerNight=3

# Maximum exposure/visit gray value for initial selection of possible photometric observations.
config.expGrayInitialCut=-0.25

# Per-band specification on maximum exposure FWHM (arcseconds) that will be considered for the model fit. Exposures with median FWHM larger than this threshold will get zeropoints based on matching to good stars.
config.expFwhmCutDict={'u': 2.0, 'g': 2.0, 'r': 2.0, 'i': 2.0, 'z': 2.0, 'y': 2.0}

# Per-band specification on maximum (negative) achromatic exposure residual ('gray term') for a visit to be considered photometric.  Must have one entry per band. Broad-band filters should be -0.05.
config.expGrayPhotometricCutDict={'u': -0.1, 'g': -0.05, 'r': -0.05, 'i': -0.05, 'z': -0.05, 'y': -0.05}

# Per-band specification on maximum (positive) achromatic exposure residual ('gray term') for a visit to be considered photometric.  Must have one entry per band.  Broad-band filters should be 0.2.
config.expGrayHighCutDict={'u': 0.2, 'g': 0.2, 'r': 0.2, 'i': 0.2, 'z': 0.2, 'y': 0.2}

# Maximum (negative) exposure gray to be able to recover bad ccds via interpolation. Visits with more gray extinction will only get CCD zeropoints if there are sufficient star observations (minStarPerCcd) on that CCD.
config.expGrayRecoverCut=-1.0

# Per-band specification on maximum exposure variance to be considered possibly photometric.  Must have one entry per band.  Broad-band filters should be 0.0005.
config.expVarGrayPhotometricCutDict={'u': 0.15, 'g': 0.05, 'r': 0.05, 'i': 0.05, 'z': 0.05, 'y': 0.05}

# Maximum exposure gray error to be able to recover bad ccds via interpolation. Visits with more gray variance will only get CCD zeropoints if there are sufficient star observations (minStarPerCcd) on that CCD.
config.expGrayErrRecoverCut=0.05

# Use PSF FWHM for aperture corrections?  Otherwise delta_aper statistic is used.
config.aperCorrUsePsfFwhm=True

# Use aperture corrections per-ccd (detector) instead of per-visit?
config.aperCorrPerCcd=False

# Number of aperture bins used in aperture correction fit.  When set to 0no fit will be performed, and the config.aperCorrInputSlopes will be used if available.
config.aperCorrFitNBins=10

# Per-band specification of aperture correction input slope parameters.  These are used on the first fit iteration, and aperture correction parameters will be updated from the data if config.aperCorrFitNBins > 0.  It is recommended to set this when there is insufficient data to fit the parameters (e.g. tract mode).
config.aperCorrInputSlopeDict={'u': 0.0, 'g': 0.0, 'r': 0.0, 'i': 0.0, 'z': 0.0, 'y': 0.0}

config.sedboundaryterms.data={}
config.sedboundaryterms.data['ug']=lsst.fgcmcal.sedterms.Sedboundaryterm()
# name of primary band
config.sedboundaryterms.data['ug'].primary='u'

# name of secondary band
config.sedboundaryterms.data['ug'].secondary='g'

config.sedboundaryterms.data['gr']=lsst.fgcmcal.sedterms.Sedboundaryterm()
# name of primary band
config.sedboundaryterms.data['gr'].primary='g'

# name of secondary band
config.sedboundaryterms.data['gr'].secondary='r'

config.sedboundaryterms.data['ri']=lsst.fgcmcal.sedterms.Sedboundaryterm()
# name of primary band
config.sedboundaryterms.data['ri'].primary='r'

# name of secondary band
config.sedboundaryterms.data['ri'].secondary='i'

config.sedboundaryterms.data['iz']=lsst.fgcmcal.sedterms.Sedboundaryterm()
# name of primary band
config.sedboundaryterms.data['iz'].primary='i'

# name of secondary band
config.sedboundaryterms.data['iz'].secondary='z'

config.sedboundaryterms.data['zy']=lsst.fgcmcal.sedterms.Sedboundaryterm()
# name of primary band
config.sedboundaryterms.data['zy'].primary='z'

# name of secondary band
config.sedboundaryterms.data['zy'].secondary='y'

config.sedterms.data={}
config.sedterms.data['u']=lsst.fgcmcal.sedterms.Sedterm()
# Name of primary Sedboundaryterm
config.sedterms.data['u'].primaryTerm='ug'

# Name of secondary Sedboundaryterm
config.sedterms.data['u'].secondaryTerm='gr'

# Extrapolate to compute SED slope
config.sedterms.data['u'].extrapolated=True

# Adjustment constant for SED slope
config.sedterms.data['u'].constant=0.5

# Primary band name for extrapolation
config.sedterms.data['u'].primaryBand='u'

# Secondary band name for extrapolation
config.sedterms.data['u'].secondaryBand='g'

# Tertiary band name for extrapolation
config.sedterms.data['u'].tertiaryBand='r'

config.sedterms.data['g']=lsst.fgcmcal.sedterms.Sedterm()
# Name of primary Sedboundaryterm
config.sedterms.data['g'].primaryTerm='gr'

# Name of secondary Sedboundaryterm
config.sedterms.data['g'].secondaryTerm='ri'

# Extrapolate to compute SED slope
config.sedterms.data['g'].extrapolated=False

# Adjustment constant for SED slope
config.sedterms.data['g'].constant=1.5

# Primary band name for extrapolation
config.sedterms.data['g'].primaryBand=None

# Secondary band name for extrapolation
config.sedterms.data['g'].secondaryBand=None

# Tertiary band name for extrapolation
config.sedterms.data['g'].tertiaryBand=None

config.sedterms.data['r']=lsst.fgcmcal.sedterms.Sedterm()
# Name of primary Sedboundaryterm
config.sedterms.data['r'].primaryTerm='gr'

# Name of secondary Sedboundaryterm
config.sedterms.data['r'].secondaryTerm='ri'

# Extrapolate to compute SED slope
config.sedterms.data['r'].extrapolated=False

# Adjustment constant for SED slope
config.sedterms.data['r'].constant=0.9

# Primary band name for extrapolation
config.sedterms.data['r'].primaryBand=None

# Secondary band name for extrapolation
config.sedterms.data['r'].secondaryBand=None

# Tertiary band name for extrapolation
config.sedterms.data['r'].tertiaryBand=None

config.sedterms.data['i']=lsst.fgcmcal.sedterms.Sedterm()
# Name of primary Sedboundaryterm
config.sedterms.data['i'].primaryTerm='ri'

# Name of secondary Sedboundaryterm
config.sedterms.data['i'].secondaryTerm='iz'

# Extrapolate to compute SED slope
config.sedterms.data['i'].extrapolated=False

# Adjustment constant for SED slope
config.sedterms.data['i'].constant=1.1

# Primary band name for extrapolation
config.sedterms.data['i'].primaryBand=None

# Secondary band name for extrapolation
config.sedterms.data['i'].secondaryBand=None

# Tertiary band name for extrapolation
config.sedterms.data['i'].tertiaryBand=None

config.sedterms.data['z']=lsst.fgcmcal.sedterms.Sedterm()
# Name of primary Sedboundaryterm
config.sedterms.data['z'].primaryTerm='iz'

# Name of secondary Sedboundaryterm
config.sedterms.data['z'].secondaryTerm='ri'

# Extrapolate to compute SED slope
config.sedterms.data['z'].extrapolated=True

# Adjustment constant for SED slope
config.sedterms.data['z'].constant=1.0

# Primary band name for extrapolation
config.sedterms.data['z'].primaryBand='z'

# Secondary band name for extrapolation
config.sedterms.data['z'].secondaryBand='i'

# Tertiary band name for extrapolation
config.sedterms.data['z'].tertiaryBand='r'

config.sedterms.data['y']=lsst.fgcmcal.sedterms.Sedterm()
# Name of primary Sedboundaryterm
config.sedterms.data['y'].primaryTerm='zy'

# Name of secondary Sedboundaryterm
config.sedterms.data['y'].secondaryTerm='iz'

# Extrapolate to compute SED slope
config.sedterms.data['y'].extrapolated=True

# Adjustment constant for SED slope
config.sedterms.data['y'].constant=1.0

# Primary band name for extrapolation
config.sedterms.data['y'].primaryBand='y'

# Secondary band name for extrapolation
config.sedterms.data['y'].secondaryBand='z'

# Tertiary band name for extrapolation
config.sedterms.data['y'].tertiaryBand='i'

# Maximum mag error for fitting sigma_FGCM
config.sigFgcmMaxErr=0.005

# Per-band specification for maximum (absolute) achromatic residual (gray value) for observations in sigma_fgcm (raw repeatability).  Broad-band filters should be 0.05.
config.sigFgcmMaxEGrayDict={'u': 0.15, 'g': 0.05, 'r': 0.05, 'i': 0.05, 'z': 0.05, 'y': 0.05}

# Maximum error on a star observation to use in ccd gray (achromatic residual) computation
config.ccdGrayMaxStarErr=0.1

# Per-band specification of the approximate overall throughput at the start of calibration observations.  Must have one entry per band.  Typically should be 1.0.
config.approxThroughputDict={'u': 1.0, 'g': 1.0, 'r': 1.0, 'i': 1.0, 'z': 1.0, 'y': 1.0}

# Allowed range for systematic error floor estimation
config.sigmaCalRange=[0.001, 0.003]

# Magnitude percentile range to fit systematic error floor
config.sigmaCalFitPercentile=[0.05, 0.15]

# Magnitude percentile range to plot systematic error floor
config.sigmaCalPlotPercentile=[0.05, 0.95]

# Systematic error floor for all zeropoints
config.sigma0Phot=0.003

# Reference longitude for plotting maps
config.mapLongitudeRef=0.0

# Healpix nside for plotting maps
config.mapNSide=256

# Filename start for plot output files
config.outfileBase='fgcmLSSTCam'

# Encoded star-color cuts (using calibration star colors). This is a list with each entry a string of the format ``band1,band2,low,high`` such that only stars of color low < band1 - band2 < high will be used for calibration.
config.starColorCuts=['g, i, 0.0, 3.5']

# Encoded star color cuts specifically to apply to reference stars. This is a list with each entry a string of the format ``band1,band2,low,high`` such that only stars of color low < band1 - band2 < high will be used as reference stars.
config.refStarColorCuts=['g, i, 0.4, 1.0']

# Band names to use to split stars by color.  Must have 2 entries.
config.colorSplitBands=['g', 'i']

# Should FGCM model the magnitude errors from sky/fwhm? (False means trust inputs)
config.modelMagErrors=True

# Model PWV with a quadratic term for variation through the night?
config.useQuadraticPwv=False

# Use per-exposure ``retrieved`` PWV instead of full night model.
config.useRetrievedPwv=False

# Smoothing block width (in exposures) for ``retrieved`` PWV.
config.retrievedPwvSmoothingBlock=10

# Bands used for computing ``retrieved`` PWV.
config.retrievedPwvBands=['z', 'y']

# Model instrumental parameters per band? Otherwise, instrumental parameters (QE changes with time) are shared among all bands.
config.instrumentParsPerBand=False

# Minimum time change (in days) between observations to use in constraining instrument slope.
config.instrumentSlopeMinDeltaT=20.0

# Fit (intraband) mirror chromatic term?
config.fitMirrorChromaticity=False

# Specification on whether to compute first-order quantum efficiency (QE) adjustments. Key is band, and value will be True or False. Any band not explicitly specified will default to False.
config.fitCcdChromaticityDict={}

# Mirror coating dates in MJD
config.coatingMjds=[]

# Output standard stars prior to final cycle?  Used in debugging.
config.outputStandardsBeforeFinalCycle=False

# Output standard stars prior to final cycle?  Used in debugging.
config.outputZeropointsBeforeFinalCycle=False

# Per-band specification on whether to use star repeatability (instead of exposures) for computing photometric cuts. Recommended for tract mode or bands with few visits.
config.useRepeatabilityForExpGrayCutsDict={'u': False, 'g': False, 'r': False, 'i': False, 'z': False, 'y': False}

# Number of sigma for automatic computation of (low) photometric cut. Cut is based on exposure gray width (per band), unless useRepeatabilityForExpGrayCuts is set, in which case the star repeatability is used (also per band).
config.autoPhotometricCutNSig=3.0

# Number of sigma for automatic computation of (high) outlier cut. Cut is based on exposure gray width (per band), unless useRepeatabilityForExpGrayCuts is set, in which case the star repeatability is used (also per band).
config.autoHighCutNSig=6.0

# Be less verbose with logging.
config.quietMode=False

# Make fgcm QA plots.
config.doPlots=True

# Make fgcm QA plots before the final two fit cycles? This only applies inmulti-cycle mode, and if doPlots is True. These are typically the mostimportant QA plots to inspect.
config.doPlotsBeforeFinalCycles=False

# Random seed for fgcm for consistency in tests.
config.randomSeed=12345

# Minimum number of good observations to use mean delta-aper values in fits.
config.deltaAperFitMinNgoodObs=2

# Number of x bins per ccd when computing delta-aper background offsets. Only used when ``doComputeDeltaAperPerCcd`` is True.
config.deltaAperFitPerCcdNx=8

# Number of y bins per ccd when computing delta-aper background offsets. Only used when ``doComputeDeltaAperPerCcd`` is True.
config.deltaAperFitPerCcdNy=8

# Healpix nside to compute spatial delta-aper background offset maps.
config.deltaAperFitSpatialNside=32

# Inner radius used to compute deltaMagAper (arcseconds). Must be positive and less than ``deltaAperOuterRadiusArcsec`` if any of ``doComputeDeltaAperPerVisit``, ``doComputeDeltaAperPerStar``, ``doComputeDeltaAperMap``, ``doComputeDeltaAperPerCcd`` are set.
config.deltaAperInnerRadiusArcsec=2.4

# Outer radius used to compute deltaMagAper (arcseconds). Must be positive and greater than ``deltaAperInnerRadiusArcsec`` if any of ``doComputeDeltaAperPerVisit``, ``doComputeDeltaAperPerStar``, ``doComputeDeltaAperMap``, ``doComputeDeltaAperPerCcd`` are set.
config.deltaAperOuterRadiusArcsec=3.4

# Do the computation of delta-aper background offsets per visit? Note: this option can be very slow when there are many visits.
config.doComputeDeltaAperPerVisit=False

# Do the computation of delta-aper mean values per star?
config.doComputeDeltaAperPerStar=True

# Do the computation of delta-aper spatial maps? This is only used if ``doComputeDeltaAperPerStar`` is True,
config.doComputeDeltaAperMap=True

# Do the computation of per-ccd delta-aper background offsets?
config.doComputeDeltaAperPerCcd=True

# name for connection camera
config.connections.camera='camera'

# name for connection fgcmLookUpTable
config.connections.fgcmLookUpTable='fgcmLookUpTable'

# name for connection fgcmVisitCatalog
config.connections.fgcmVisitCatalog='fgcmVisitCatalog'

# name for connection fgcmStarObservationsParquet
config.connections.fgcmStarObservationsParquet='fgcm_star_observations'

# name for connection fgcmStarIdsParquet
config.connections.fgcmStarIdsParquet='fgcm_star_ids'

# name for connection fgcmReferenceStarsParquet
config.connections.fgcmReferenceStarsParquet='fgcm_reference_stars'

# name for connection fgcmStarObservations
config.connections.fgcmStarObservations='fgcmStarObservations'

# name for connection fgcmStarIds
config.connections.fgcmStarIds='fgcmStarIds'

# name for connection fgcmStarIndices
config.connections.fgcmStarIndices='fgcmStarIndices'

# name for connection fgcmReferenceStars
config.connections.fgcmReferenceStars='fgcmReferenceStars'

# Template parameter used to format corresponding field template parameter
config.connections.previousCycleNumber='-1'

# Template parameter used to format corresponding field template parameter
config.connections.cycleNumber='0'
