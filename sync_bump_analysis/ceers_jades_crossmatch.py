#!/usr/bin/env python3
"""Cross-match CEERS z=13-14 galaxies with JADES DR4 spectroscopic catalog."""

from astropy.io import fits
import numpy as np

# ============================================================
# LOAD CEERS z=13-14 galaxies
# ============================================================
with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    z_med = ceers['LP_Z_MED']
    z_hi = ceers['LP_Z_MED68_HIGH']
    z_lo = ceers['LP_Z_MED68_LOW']
    number = ceers['NUMBER']
    ra = ceers['RA']
    dec = ceers['DEC']
    
    valid = (z_hi > 0) & (z_lo > 0) & (z_hi > z_lo) & np.isfinite(z_hi - z_lo)
    z13_mask = valid & (z_med >= 13.0) & (z_med < 14.0)
    z13_idx = np.where(z13_mask)[0]
    
    ceers_z13_numbers = set(int(number[i]) for i in z13_idx)
    print(f"CEERS z=13-14 galaxies: {len(ceers_z13_numbers)}")
    print(f"CEERS NUMBER range: {min(ceers_z13_numbers)} - {max(ceers_z13_numbers)}")

# ============================================================
# LOAD JADES DR4 - R100_5pix HDU (has z_PRISM)
# ============================================================
print("\n=== JADES DR4 Spectroscopic Cross-Match ===")
with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    # R100_5pix HDU (index 2)
    r100 = hdul[2].data
    z_prism = r100['z_PRISM']
    z_flag = r100['Z_FLAG']
    unique_id = r100['Unique_ID']
    nircam_id = r100['NIRCam_DR5_ID']
    
    print(f"JADES DR4 R100_5pix entries: {len(r100)}")
    
    # Check for NaN/invalid z_PRISM
    valid_z = np.isfinite(z_prism) & (z_prism > 0)
    print(f"Valid z_PRISM measurements: {np.sum(valid_z)}")
    print(f"z_PRISM range: {np.min(z_prism[valid_z]):.4f} to {np.max(z_prism[valid_z]):.4f}")
    
    # Check for high-z galaxies in JADES
    high_z_mask = valid_z & (z_prism > 10)
    high_z_idx = np.where(high_z_mask)[0]
    print(f"\nJADES galaxies with z_PRISM > 10: {len(high_z_idx)}")
    sorted_high = sorted(high_z_idx, key=lambda i: z_prism[i], reverse=True)
    for i in sorted_high[:20]:
        print(f"  Unique_ID={unique_id[i]}  z_PRISM={z_prism[i]:.4f}  Z_FLAG={z_flag[i]}  "
              f"NIRCam_DR5_ID={nircam_id[i]}")
    
    # Check if any JADES NIRCam_DR5_ID matches CEERS numbers
    print(f"\n=== Cross-matching by NIRCam_DR5_ID ===")
    match_count = 0
    for i in range(len(r100)):
        nid = str(nircam_id[i]).strip()
        if nid and nid != '' and nid != '0' and nid != 'None' and nid.isdigit():
            nid_int = int(nid)
            if nid_int in ceers_z13_numbers:
                match_count += 1
                print(f"  MATCH: CEERS NUMBER={nid_int}  JADES z_PRISM={z_prism[i]:.4f}  "
                      f"Z_FLAG={z_flag[i]}  Unique_ID={unique_id[i]}")
    
    print(f"\nTotal CEERS z=13-14 galaxies matched in JADES DR4: {match_count}")
    
    # Also check Obs_info HDU for z_Spec and z_PRISM
    info = hdul[1].data
    z_spec = info['z_Spec']
    z_prism_info = info['z_PRISM']
    z_phot = info['z_phot']
    
    print(f"\n=== JADES DR4 Obs_info high-z === ")
    hi_z_info = np.isfinite(z_prism_info) & (z_prism_info > 10)
    hi_idx = np.where(hi_z_info)[0]
    sorted_hi = sorted(hi_idx, key=lambda i: z_prism_info[i], reverse=True)
    for i in sorted_hi[:20]:
        print(f"  z_PRISM={z_prism_info[i]:.4f}  z_Spec={z_spec[i]:.4f}  z_phot={z_phot[i]:.4f}  "
              f"NIRCam_DR5_ID={info['NIRCam_DR5_ID'][i]}")
    
    # Also check R1000 high-z
    r1000 = hdul[4].data
    z_r1000 = r1000['z_R1000']
    print(f"\n=== JADES DR4 R1000_5pix high-z ===")
    hi_r1000 = np.isfinite(z_r1000) & (z_r1000 > 10)
    hi_r1000_idx = np.where(hi_r1000)[0]
    sorted_r1000 = sorted(hi_r1000_idx, key=lambda i: z_r1000[i], reverse=True)
    print(f"Galaxies with z_R1000 > 10: {len(hi_r1000_idx)}")
    for i in sorted_r1000[:20]:
        print(f"  z_R1000={z_r1000[i]:.4f}  NIRCam_DR5_ID={r1000['NIRCam_DR5_ID'][i]}  Unique_ID={r1000['Unique_ID'][i]}")

# ============================================================
# ANALYZE THE TIGHT CLUSTER (NUMBER ~11800-11810, 22460, 85156)
# ============================================================
print("\n\n=== Tight Cluster Analysis (width < 0.1) ===")
with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    z_med = ceers['LP_Z_MED']
    z_hi = ceers['LP_Z_MED68_HIGH']
    z_lo = ceers['LP_Z_MED68_LOW']
    number = ceers['NUMBER']
    ra = ceers['RA']
    dec = ceers['DEC']
    mass = ceers['LP_MASS_MED']
    mass_lo = ceers['LP_MASS_MED68_LOW']
    mass_hi = ceers['LP_MASS_MED68_HIGH']
    star_flag = ceers['STAR_FLAG']
    
    valid = (z_hi > 0) & (z_lo > 0) & (z_hi > z_lo) & np.isfinite(z_hi - z_lo)
    z13_mask = valid & (z_med >= 13.0) & (z_med < 14.0)
    z13_idx = np.where(z13_mask)[0]
    
    pz_width = z_hi - z_lo
    
    # Find the ultra-narrow ones (width < 0.1)
    tight_mask = z13_mask & (pz_width < 0.1)
    tight_idx = np.where(tight_mask)[0]
    print(f"Ultra-narrow P(z) galaxies (width < 0.1): {len(tight_idx)}")
    
    tight_sorted = sorted(tight_idx, key=lambda i: number[i])
    for i in tight_sorted:
        print(f"  NUMBER={number[i]:6d}  z_med={z_med[i]:.4f}  width={pz_width[i]:.3f}  "
              f"RA={ra[i]:.5f}  DEC={dec[i]:.5f}  "
              f"mass={mass[i]:.2e}  star_flag={star_flag[i]}")
    
    # Check if they're spatially clustered
    if len(tight_idx) > 0:
        ra_tight = np.array([ra[i] for i in tight_idx])
        dec_tight = np.array([dec[i] for i in tight_idx])
        print(f"\nTight cluster RA range: {np.min(ra_tight):.5f} to {np.max(ra_tight):.5f} "
              f"(span: {np.max(ra_tight)-np.min(ra_tight):.5f} deg)")
        print(f"Tight cluster DEC range: {np.min(dec_tight):.5f} to {np.max(dec_tight):.5f} "
              f"(span: {np.max(dec_tight)-np.min(dec_tight):.5f} deg)")
        
        # Print their positions for comparison
        print(f"\nTight cluster positions:")
        for i in tight_idx:
            print(f"  NUMBER={number[i]:6d}  RA={ra[i]:.5f}  DEC={dec[i]:.5f}  "
                  f"z_med={z_med[i]:.4f}  width={pz_width[i]:.3f}  mass={mass[i]:.2e}")
    
    # Also check: what about the z_lo and z_hi bounds for these narrow sources?
    print(f"\n\n=== Narrow P(z) sources: detailed bounds ===")
    narrow_mask = z13_mask & (pz_width < 0.5)
    narrow_idx = np.where(narrow_mask)[0]
    narrow_sorted = sorted(narrow_idx, key=lambda i: pz_width[i])
    print(f"Narrow P(z) sources (width < 0.5): {len(narrow_idx)}")
    for i in narrow_sorted:
        print(f"  NUMBER={number[i]:6d}  z_med={z_med[i]:.4f}  z_lo={z_lo[i]:.4f}  "
              f"z_hi={z_hi[i]:.4f}  width={pz_width[i]:.3f}  "
              f"RA={ra[i]:.5f}  DEC={dec[i]:.5f}  star_flag={star_flag[i]}")

# ============================================================
# CHECK: does the CEERS catalog have the same IDs as the lookup file?
# ============================================================
print("\n\n=== Check ID lookup file ===")
try:
    with open('ceers_lp_pdz_IDlookup.dat') as f:
        lines = f.readlines()
    print(f"ID lookup file: {len(lines)} lines")
    # Check if any known numbers are there
    for line in lines[:5]:
        print(f"  {line.strip()}")
    print(f"  ...")
    for line in lines[-5:]:
        print(f"  {line.strip()}")
except Exception as e:
    print(f"Could not read: {e}")