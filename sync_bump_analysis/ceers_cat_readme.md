README for CEERS NIRCam + HST hot and cold catalogue
- Version 1.0 date 9/30/2025
- Released 13 October 2025
- Created by Isa Cox (igc5972@rit.edu)
- Alternate contact: Jeyhan Kartaltepe (jsksps@rit.edu)


This readme file contains information about the photometric catalogue released alongside CEERS NIRCam imaging v1.0. The construction process is described in detail in Cox et al. (submitted, https://arxiv.org/abs/2510.08743), a summary of which is given at the end of this readme.

------------------------------------------------------
CATALOGUE (AND ASSOCIATED FILES) DESCRIPTION
------------------------------------------------------
The file "ceers_cat_v1.0.fits.gz" is the photometric catalog, containing fluxes in units of nJy, all of which have been corrected for foreground galactic extinction. Aperture corrections are described in this readme. 

The file "ceers_segmap_v1.0.fits.gz" is the combined hot+cold segmentation map associated with the catalog (FITS image file).

Photometric redshifts (from LePHARE) and physical properties from multiple codes are also included (LP = LePHARE, DB = Dense Basis, CI = CIGALE).

The point spread functions (PSFs) used for image convolution (see description below) are available in "ceers_psfs_v1.0.tar.gz".

A description of the columns are:

NUMBER: Identification number from Source Extractor
X_IMAGE: The x-coordinate in pixel units of the source's centroid (measured in the detection image)
Y_IMAGE: The y-coordinate in pixel units of the source's centroid (measured in the detection image)
RA: The J2000 right ascension of the source's centroid (measured in the detection image)
DEC: The J2000 declination of the source's centroid (measured in the detection image)
CXX_IMAGE: CXX object ellipse parameter from SE (in units of inverse square pixels)
CXY_IMAGE: CXY object ellipse parameter from SE (in units of inverse square pixels)
CYY_IMAGE: CYY object ellipse parameter from SE (in units of inverse square pixels)
THETA_IMAGE: Position angle of the Kron aperture
ELLIPTICITY: Defined as 1-B_IMAGE / 1-A_IMAGE
KRON_RADIUS: Kron radius for the fiducial small Kron aperture
A_IMAGE: Used to define. The semi-major axis of the Kron aperture as A_IMAGE * KRON_RADIUS
B_IMAGE: Used to define. The semi-minor axis of the Kron aperture as A_IMAGE * KRON_RADIUS
ISO_AREA: Area (in units of pixels) of the segmentation map of object
STAR_FLAG: Flag based on star-mask
BAD_REGION_FLAG: Flag to denote source lies in region where spurious detections are likely
APCORR_AUTO: Aperture correction factor for auto fluxes (described below)
APCORR_RESIDUAL [13]: The residual aperture correction for auto fluxes and 12 circular apertures
F###_FLUX: Flux measured in Kron aperture with aperture correction applied
F###_FLUXERR_SE: Flux error from SE for flux measured in Kron aperture with aperture and residual aperture correction applied
F###_FLUXERR_EMP: Empirical flux error for flux measured in Kron aperture with aperture and residual aperture correction applied
F###_FLUX_APER [12]: Flux measured in 12 circular apertures with residual aperture correction applied
F###_FLUXERR_APER_SE [12]: Flux error from SE for flux measured in 12 circular aperture with residual aperture correction applied
F###_FLUXERR_APER_EMP [12]: Empirical flux error for flux measured in 12 circular aperture with aperture and residual aperture correction applied
F###_CLASS_STAR: The SE reported value of likelihood source is a stellar object
LP_Z_MED: Median photometric redshift (LePHARE PDF)
LP_Z_MED_LOW: 16th percentile from LePHARE PDF for photometric redshift
LP_Z_MED_HIGH: 84th percentile from LePHARE PDF for photometric redshift
LP_Z_BEST: chi2 minimized photometric redshift
LP_Z_CHI: chi2 value of best-fit LePHARE template for photometric redshift
LP_NBANDS: number of bands used by LePHARE
LP_MASS_MED: median stellar mass from LePHARE
LP_MASS_MED_LOW: 16th percentile from LePHARE PDF for stellar mass
LP_MASS_MED_HIGH: 84th percentile from LePHARE PDF for stellar mass
LP_MASS_BEST: chi2 minimized stellar mass from LePHARE
LP_SFR_MED: median star formation rate from LePHARE
LP_SFR_MED_LOW: 16th percentile from LePHARE for star formation rate 
LP_SFR_MED_HIGH: 84th percentile from LePHARE for star formation rate 
LP_SFR_BEST: chi2 minimized star formation rate from LePHARE
LP_E_BV: E(B-V) value from best-fit template
DB_MASS: 50th percentile Bayesian stellar mass from Dense Basis
DB_MASS_LOW: 16th percentile Bayesian stellar mass from Dense Basis
DB_MASS_HIGH: 84th percentile Bayesian stellar mass from Dense Basis
DB_SFR: 50th percentile Bayesian star formation rate from Dense Basis
DB_SFR_LOW: 16th percentile Bayesian star formation rate from Dense Basis
DB_SFR_HIGH: 84th percentile Bayesian star formation rate from Dense Basis
DB_AV: 50th percentile Bayesian extinction from Dense Basis
DB_AV_LOW: 16th percentile Bayesian extinction from Dense Basis
DB_AV_HIGH: 84th percentile Bayesian extinction from Dense Basis
CI_MASS: Bayesian stellar mass from CIGALE
CI_MASS_ERR: Bayesian stellar mass error from CIGALE
CI_SFR: Bayesian star formation rate from CIGALE
CI_SFR_ERR: Bayesian star formation rate error from CIGALE
CI_EBV: Bayesian extinction from CIGALE
CI_EBV: Bayesian extinction error from CIGALE


------------------------------------------------------
PDZ DATA PRODUCT
------------------------------------------------------
We also include the probability distribution functions for the photometric redshifts, "ceers_lp_pdz_v1.prob" as output by LePHARE. For each object ID (ID matches to "NUMBER" in catalog), there are 1,500 columns which indicate the probability of each photometric redshift from z = 0 to 15 in steps of 0.01. For example, "P4.08" gives the probability that the photometric redshift is z=4.08. 

We offer this data product as both a single .prob file ("ceers_lp_pdz_v1.prob",  ~2.54GB) or separated (smaller) files that each contain a chunk of IDs in order ("ceers_lp_pdz_v1_*.prob"). We also provide a lookup table to identify which of the smaller files your favorite source is in ("ceers_lp_pdz_IDlookup.dat").

These do not convert neatly to an Astropy Table, advice for reading in these .pdz in Python: 

```
#access the three header lines
with open("combined.prob") as f:
    header_lines = [next(f).strip() for _ in range(3)]
    
#get the third header line which is the columns, and skip the "#"
cols = header_lines[-1].lstrip("#").split()

#get the columns (after the ID one) into floats to show the redshfit steps
z_steps = [float(c[1:]) for c in cols[1:]]


#load the actual data, skipping 3 header lines
data = np.loadtxt("combined.prob", skiprows=3)

#practice plotting an example PDF for ID = 8

target_id = 8

ids = (data[:, 0]).astype(int)
probs = data[:, 1:] 

row = np.where(ids == target_id)[0][0]
pdz = probs[row, :]

fig, ax = plt.subplots(1)
ax.set_xlim(0,15)
ax.set_ylim(0,5)
ax.plot(z_steps, pdz, color = 'r', lw = 4)
plt.show()

```



------------------------------------------------------
INCLUDED PHOTOMETRY
------------------------------------------------------
We include photometry from the 7 CEERS NIRCam filters (F115W, F150W, F200W, F277W, F356W, F410M, F444W)
and 7 HST (ACS/WFC3) filters (F435W, F606W, F814W, F105W, F125W, F140W, F160W)


------------------------------------------------------
FILTERING OUT LESS-CERTAIN DETECTIONS
------------------------------------------------------
The BAD_REGION_FLAG flags locations in the mosaic where our detection image did not have full coverage of all filters. This means that the detections are less-certain in that area. If you are not targeting a specific source in that region, we recommend filtering out those sources (and also filtering out sources in STAR_FLAG). To apply both of these cuts, you would keep only sources where: (STAR_FLAG == 0) & (BAD_REGION_FLAG == 0). 

We also caution users of sources that have F###_FLUXERR_SE=0 and/or F###_FLUXERR_EMP=NAN for specific filters as those sources may be out of the pointings for those filters. We left those sources in for completeness, but we encourage users to vet any sources like that they wish to use.


------------------------------------------------------
A NOTE ON ERRORS
------------------------------------------------------
We report both errors direct from SE (F###_FLUXERR_SE) and our own calculated empirical errors (F###_FLUXERR_EMP), which will include both uncorrelated and correlated noise. For most use cases, the empirical errors are more appropriate, but to be complete, we also include the SE errors. See the last section, "Science Process Summary" for more details on the empirical error calculation.



------------------------------------------------------
A NOTE ON APERTURE CORRECTIONS
------------------------------------------------------
We perform an aperture correction on the auto (kron radius) fluxes, since we measured our photometry in small kron radii. For both the AUTO and APER (circular) apertures, we apply a "residual" aperture correction, described in the last section, "Science Process Summary." Both of these corrections can be "undone" by dividing by the APCORR_AUTO and/or APCORR_RESIDUAL columns.


------------------------------------------------------
CIRCULAR APERTURES
------------------------------------------------------
The twelve circular apertures in _APER (in units of arcseconds are): 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.4, 2.0


------------------------------------------------------
SCIENCE PROCESS SUMMARY
------------------------------------------------------
Summary of process (full process described in Cox et al., 2025).

#PSF-Matching and Correction
We match all NIRCam bands and the two HST/ACS bands to the resolution scale of the F444W PSF. For the four HST/WFC3 bands not PSF-matched to F444W, we calculate multiplicative correction factors by convolving the F444W PSFs with each of those PSFs, and measuring the flux ratio in the native F444W to the convolved image. This correction factor allows us to account for any missing flux in the images convolved with the larger PSF.


#SE Photometry
Photometry was performed using Source Extractor (v2.28.0) in dual image mode, with measurements being made on each PSF-convolved science image and the detection image is a chi-mean combination of F150W+F200W+F277W+F356W. We construct both hot and cold catalogs with two different sets of parameters. The hot mode was fine-tuned to detect faint, high redshift sources, whereas the cold mode was specialized to avoid over-deblending bright, extended sources. We combine the two modes using the same logic as Galapagos (Häußler et al., 2022), where all cold sources are kept and hot sources that overlap with any cold sources are discarded. For the cold mode, we use a relative DETECT_THRESH=9, a DETECT_MINAREA=25, a DEBELND_NTHRESH=64, and DEBLEND_MINCONT=0.0001. We also used a 5x5 pixel tophat convolution kernel with a width of 4 pixels. For the hot mode, we use a relative DETECT_THRESH=6, a DETECT_MINAREA=5, a DEBELND_NTHRESH=64, and DEBLEND_MINCONT=0.00001. We also used a 5x5 pixel gaussian convolution kernel with a width of 3 pixels. For the gain, we used an effective gain calculated as GAINxEXPTIME.


#Empirical Errors
Following the previous work of Papovich et al., 2016, and Finkelstein et al., 2022, 2023, we opt to calculate our own empirical errors to include in the catalog along with the flux errors reported by Source Extractor. To do this, we measured flux in circular apertures in the images' backgrounds, and constructed a four-parameter function fit to the distribution of the NMAD of these fluxes vs. their size. 


#Aperture Corrections
We measured our fiducial fluxes in small Kron apertures, so we apply a correction to ensure all the light is accounted for. This correction is a multiplicative factor that is the ratio of the fluxes measured in the larger default MAG_AUTO Kron aperture to our smaller apertures. We compute this correction for the two PSF-matched-to images and adopt them for all images PSF-matched to each one.


#Residual Aperture Corrections
An additional correction we make is to account for flux missed on larger scales. We did source injection simulations, injecting galaxies with small sersic profiles constructed with GALFIT into the PSF-match-to images as well as the images that go into the construction of the detection image. We then create a new detection image with the injected sources and measure photometry in F444W and F160W. We find that the input fluxes are brighter than the measured fluxes. We fit a step-wise function to constrain this offset, with a correction factor of 2.5% at the bright end and capping at 24% for magnitudes > 28.


#Foreground Galactic Extinction
Basic wavelength-dependent extinction corrections were applied by following Calzetti 1989.
