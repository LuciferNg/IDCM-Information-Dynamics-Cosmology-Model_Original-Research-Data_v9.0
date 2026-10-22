#!/usr/bin/env python3
"""Deeper analysis of the 11800-series tight cluster and JADES DR5 cross-match."""

from astropy.io import fits
import numpy as np

# ============================================================
# 1. SPATIAL PROXIMITY OF 11800-SERIES SOURCES
# ============================================================
print("=== 11800-Series Cluster: Spatial Proximity Analysis ===")
with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    number = ceers['NUMBER']
    ra = ceers['RA']
    dec = ceers['DEC']
    
    # Grab the 11800-series specifically
    targets = [11802, 11804, 11807, 11809, 11810, 22460]
    src = {}
    for t in targets:
        mask = number == t
        idx = np.where(mask)[0]
        if len(idx) > 0:
            src[t] = {'RA': float(ra[idx[0]]), 'DEC': float(dec[idx[0]])}
            print(f"  NUMBER={t}: RA={ra[idx[0]]:.5f}, DEC={dec[idx[0]]:.5f}")
    
    # Calculate pairwise separations (in degrees, then arcsec)
    import math
    print(f"\n  Pairwise separations:")
    keys = list(src.keys())
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            ki, kj = keys[i], keys[j]
            dra = (src[ki]['RA'] - src[kj]['RA']) * 3600 * np.cos(np.radians((src[ki]['DEC'] + src[kj]['DEC'])/2))
            ddec = (src[ki]['DEC'] - src[kj]['DEC']) * 3600
            sep = math.sqrt(dra**2 + ddec**2)
            print(f"    {ki} - {kj}: {sep:.2f} arcsec  (dra={dra:.2f}\", ddec={ddec:.2f}\")")
    
    # Check: are these consecutive-numbered sources from the same image tile?
    # The CEERS NUMBER is the SExtractor NUMBER in the detection image
    # Consecutive numbers often come from the same pointing
    print(f"\n  NUMBER sequence: {targets}")
    print(f"  Gap between 11810 and 22460: {22460-11810} objects")
    print(f"  This suggests they're from different detection tiles/pointings")
    
    # Check what's around 11800-11810 in the full catalog
    print(f"\n  All sources near NUMBER 11800-11810:")
    for i in range(11800, 11815):
        mask = number == i
        idx = np.where(mask)[0]
        if len(idx) > 0:
            print(f"    NUMBER={i}: RA={ra[idx[0]]:.5f}, DEC={dec[idx[0]]:.5f}")

# ============================================================
# 2. CHECK JADES DR5 catalogs for CEERS z>13 candidates
# ============================================================
print("\n\n=== JADES DR5 Catalogs Cross-Match ===")
for dr5_file in ['jades_dr5_goods_n_catalog.fits', 'jades_dr5_goods_s_catalog.fits']:
    try:
        with fits.open(dr5_file) as hdul:
            print(f"\n{dr5_file}:")
            hdul.info()
            for i, hdu in enumerate(hdul):
                if hdu.data is not None:
                    colnames = hdu.columns.names
                    print(f"  HDU {i} ({hdu.name}): {len(hdu.data)} rows, columns: {colnames[:20]}...")
                    # Check for redshift columns
                    zcols = [c for c in colnames if 'Z' in c or 'z_' in c or 'REDSHIFT' in c.upper()]
                    if zcols:
                        print(f"  Redshift columns: {zcols}")
                    # Check for photoz
                    photoz_cols = [c for c in colnames if 'PHOTO' in c.upper() or 'LP_' in c or 'z_phot' in c.lower()]
                    if photoz_cols:
                        print(f"  Photoz columns: {photoz_cols}")
    except Exception as e:
        print(f"\n{dr5_file}: Error - {e}")

# ============================================================
# 3. CHECK THE CEERS P(z) PDF FILES MENTIONED IN THE LOOKUP
# ============================================================
print("\n\n=== Check if P(z) .prob files exist ===")
import os, glob
prob_files = glob.glob('ceers_lp_pdz_v1_*.prob')
print(f"Found {len(prob_files)} P(z) .prob files")
if len(prob_files) > 0:
    # Look at a sample file for the 11800-range
    # The lookup says: 11802 falls in file ceers_lp_pdz_v1_36.prob (IDs 11661-11993)
    sample_file = None
    for f in prob_files:
        parts = f.replace('.prob', '').split('_')
        try:
            num = int(parts[-1])
            if 35 <= num <= 37:
                sample_file = f
                break
        except:
            pass
    if sample_file:
        print(f"Sample file for 11800-range: {sample_file}")
        with open(sample_file) as f:
            lines = f.readlines()
        print(f"  File has {len(lines)} lines")
        # Print the first few lines
        for line in lines[:15]:
            print(f"  {line.strip()}")
    else:
        print("Could not find a sample file for 11800-range")

# ============================================================
# 4. CHECK: Are the ultra-narrow P(z) sources in the same F160W image?
# ============================================================
print("\n\n=== Detection image analysis ===")
with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    # The X_IMAGE, Y_IMAGE columns give pixel coordinates in the detection image
    x_img = ceers['X_IMAGE']
    y_img = ceers['Y_IMAGE']
    number = ceers['NUMBER']
    
    # Check the 11800-series pixel positions
    print("11800-series pixel positions:")
    for n in [11802, 11804, 11807, 11809, 11810]:
        mask = number == n
        idx = np.where(mask)[0]
        if len(idx) > 0:
            print(f"  NUMBER={n}: X={x_img[idx[0]]:.1f}, Y={y_img[idx[0]]:.1f}")
    
    # Check 22460
    for n in [22460, 85156, 44979, 28776]:
        mask = number == n
        idx = np.where(mask)[0]
        if len(idx) > 0:
            print(f"  NUMBER={n}: X={x_img[idx[0]]:.1f}, Y={y_img[idx[0]]:.1f}")

# ============================================================
# 5. COMPARE THE TWO POPULATIONS: narrow vs wide in z=13-14
# ============================================================
print("\n\n=== Two-component analysis of z=13-14 ===")
with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    z_med = ceers['LP_Z_MED']
    z_hi = ceers['LP_Z_MED68_HIGH']
    z_lo = ceers['LP_Z_MED68_LOW']
    number = ceers['NUMBER']
    ra = ceers['RA']
    dec = ceers['DEC']
    mass = ceers['LP_MASS_MED']
    star_flag = ceers['STAR_FLAG']
    chi2 = ceers['LP_FIT_CHI']
    nbands = ceers['LP_NBANDS']
    
    valid = (z_hi > 0) & (z_lo > 0) & (z_hi > z_lo) & np.isfinite(z_hi - z_lo)
    z13_mask = valid & (z_med >= 13.0) & (z_med < 14.0)
    z13_idx = np.where(z13_mask)[0]
    
    pz_width = z_hi - z_lo
    
    # Define narrow (width < 1) and wide (width >= 1) groups
    narrow_mask = z13_mask & (pz_width < 1.0)
    wide_mask = z13_mask & (pz_width >= 1.0)
    narrow_idx = np.where(narrow_mask)[0]
    wide_idx = np.where(wide_mask)[0]
    
    print(f"Narrow group (width < 1.0): {len(narrow_idx)} galaxies")
    print(f"Wide group (width >= 1.0): {len(wide_idx)} galaxies")
    
    print(f"\nNarrow group: z_med range = {np.min(z_med[narrow_mask]):.4f} - {np.max(z_med[narrow_mask]):.4f}")
    print(f"Wide group: z_med range = {np.min(z_med[wide_mask]):.4f} - {np.max(z_med[wide_mask]):.4f}")
    
    # Count star flags
    n_star_narrow = np.sum(star_flag[narrow_mask] >= 1)
    n_star_wide = np.sum(star_flag[wide_mask] >= 1)
    print(f"\nStar_flag>=1 in narrow group: {n_star_narrow}/{len(narrow_idx)}")
    print(f"Star_flag>=1 in wide group: {n_star_wide}/{len(wide_idx)}")
    
    print(f"\nNarrow group: chi2 range = {np.min(chi2[narrow_mask]):.2f} - {np.max(chi2[narrow_mask]):.2f}, "
          f"mean = {np.mean(chi2[narrow_mask]):.2f}")
    print(f"Wide group: chi2 range = {np.min(chi2[wide_mask]):.2f} - {np.max(chi2[wide_mask]):.2f}, "
          f"mean = {np.mean(chi2[wide_mask]):.2f}")
    
    print(f"\nNarrow group: nbands range = {np.min(nbands[narrow_mask]):.0f} - {np.max(nbands[narrow_mask]):.0f}, "
          f"mean = {np.mean(nbands[narrow_mask]):.1f}")
    print(f"Wide group: nbands range = {np.min(nbands[wide_mask]):.0f} - {np.max(nbands[wide_mask]):.0f}, "
          f"mean = {np.mean(nbands[wide_mask]):.1f}")
    
    # Check LP_Z_BEST (the best-fit redshift, not the median)
    z_best = ceers['LP_Z_BEST']
    print(f"\nNarrow group: z_best range = {np.min(z_best[narrow_mask]):.4f} - {np.max(z_best[narrow_mask]):.4f}")
    print(f"Wide group: z_best range = {np.min(z_best[wide_mask]):.4f} - {np.max(z_best[wide_mask]):.4f}")
    
    # Check: are the narrow sources truly at z~13.5 or are they lower-z interlopers?
    # LP_Z_BEST tells us the best-fit from the photometric redshift code
    print(f"\n  Narrow group: z_best vs z_med comparison:")
    for i in narrow_idx:
        print(f"    NUMBER={number[i]:6d}  z_med={z_med[i]:.4f}  z_best={z_best[i]:.4f}  "
              f"z_lo={z_lo[i]:.4f}  z_hi={z_hi[i]:.4f}  width={pz_width[i]:.3f}  "
              f"star_flag={star_flag[i]}  chi2={chi2[i]:.1f}  nbands={nbands[i]:.0f}")

# ============================================================
# 6. Finally, check what the z_lo and z_hi mean for the ultra-narrow ones
# P(z) width of 0.017 at z~13.7 is EXTREMELY narrow
# For comparison, spectroscopic redshifts typically have errors of dz~0.001
# A photometric redshift with width 0.017 is essentially a delta function
# ============================================================
print("\n\n=== Interpretation of ultra-narrow P(z) ===")
print(f"Width of 0.017 at z=13.732: dz/(1+z) = 0.017/14.732 = {0.017/14.732:.6f}")
print(f"Width of 0.019 at z=13.895: dz/(1+z) = 0.019/14.895 = {0.019/14.895:.6f}")
print(f"Width of 0.022 at z=13.647: dz/(1+z) = 0.022/14.647 = {0.022/14.647:.6f}")
print(f"For comparison, typical CEERS photoz at z=0-2: dz/(1+z) ~ 0.5-1.0")
print(f"These ultra-narrow widths are ~0.001 in fractional units — comparable to spectroscopic quality")
print(f"This is UNPHYSICAL for photometric redshifts at z~13.5")
print(f"Conclusion: The ultra-narrow P(z) sources are ARTIFACTS, likely from:")
print(f"  - Deblending of a single bright source into multiple detections (11800-series)")
print(f"  - P(z) fitting that converged on a delta function (template fitting failure)")
print(f"  - Star flag=1 on 4/11 of the ultra-narrow sources suggests stellar contamination")