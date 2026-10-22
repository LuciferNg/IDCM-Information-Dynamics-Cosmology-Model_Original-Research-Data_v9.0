#!/usr/bin/env python3
"""
Cross-match CEERS DR1 z>7 galaxies with JADES DR4 spectroscopic catalog.
Find matched sources and compare photometric vs spectroscopic redshifts.
"""

import numpy as np
from astropy.io import fits
from astropy.coordinates import SkyCoord, Angle
from astropy import units as u
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. Load CEERS DR1 catalog
# ============================================================
print("=" * 70)
print("CEERS DR1 CROSS-MATCH WITH JADES DR4 SPECTROSCOPIC CATALOG")
print("=" * 70)

with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    n_ceers_total = len(ceers)
    print(f"\nCEERS DR1 total sources: {n_ceers_total}")

# Quality cuts: z_med > 7, z_lo > 0.5, nbands >= 5
mask_z7 = (ceers['LP_Z_MED'] > 7.0)
mask_lo = (ceers['LP_Z_MED68_LOW'] > 0.5)
mask_nb = (ceers['LP_NBANDS'] >= 5)

mask_all = mask_z7 & mask_lo & mask_nb

print(f"  z_med > 7:            {np.sum(mask_z7)}")
print(f"  z_lo > 0.5:           {np.sum(mask_lo)}")
print(f"  nbands >= 5:          {np.sum(mask_nb)}")
print(f"  All cuts combined:    {np.sum(mask_all)}")

ceers_sel = ceers[mask_all]
ceers_coords = SkyCoord(ra=ceers_sel['RA'], dec=ceers_sel['DEC'], unit=u.deg)
print(f"  RA range: {ceers_sel['RA'].min():.4f} to {ceers_sel['RA'].max():.4f}")
print(f"  Dec range: {ceers_sel['DEC'].min():.4f} to {ceers_sel['DEC'].max():.4f}")

# ============================================================
# 2. Load JADES DR4 — join Obs_info (positions) with R100_5pix (z_PRISM)
# ============================================================
with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    obs_info = hdul[1].data      # HDU 1: Obs_info — positions, field
    r100_5pix = hdul[2].data     # HDU 2: R100_5pix — z_PRISM, Z_FLAG

# Build lookup from Obs_info
obs_by_id = {}
for row in obs_info:
    obs_by_id[row['Unique_ID']] = row

# Build lookup from R100_5pix
r100_by_id = {}
for row in r100_5pix:
    r100_by_id[row['Unique_ID']] = row

# Join on Unique_ID
jades_records = []
for uid in set(obs_by_id.keys()) & set(r100_by_id.keys()):
    o = obs_by_id[uid]
    r = r100_by_id[uid]
    z_prism = r['z_PRISM']
    z_flag = r['Z_FLAG']
    z_spec = o['z_Spec']
    field = o['Field']
    
    # Skip NaN z_PRISM
    if np.isnan(z_prism):
        continue
    
    jades_records.append({
        'Unique_ID': uid.decode() if isinstance(uid, bytes) else uid,
        'RA_TARG': o['RA_TARG'],
        'Dec_TARG': o['Dec_TARG'],
        'Field': field.decode() if isinstance(field, bytes) else field,
        'NIRCam_DR5_ID': o['NIRCam_DR5_ID'],
        'z_PRISM': z_prism,
        'Z_FLAG': z_flag.decode().strip() if isinstance(z_flag, bytes) else str(z_flag).strip(),
        'z_Spec': z_spec if not np.isnan(z_spec) else None,
    })

print(f"\nJADES DR4 total sources (with z_PRISM): {len(jades_records)}")

# Filter to z_PRISM > 7
jades_z7 = [r for r in jades_records if r['z_PRISM'] > 7.0]
print(f"  z_PRISM > 7: {len(jades_z7)}")

# Count by field
fields = {}
for r in jades_z7:
    f = r['Field']
    fields[f] = fields.get(f, 0) + 1
for f, cnt in sorted(fields.items()):
    print(f"    {f}: {cnt}")

# CEERS is in GOODS-S, so we care about GS sources
jades_gs = [r for r in jades_z7 if r['Field'] in ('GS', 'GN')]
print(f"\nJADES z>7 sources in GOODS-S fields: {sum(1 for r in jades_z7 if r['Field'] == 'GS')}")

# ============================================================
# 3. Cross-match: CEERS (z7 candidates) vs JADES DR4 (z_PRISM > 7, GS only)
# ============================================================
jades_gs_z7 = [r for r in jades_z7 if r['Field'] == 'GS']
print(f"\nJADES z>7 sources in GOODS-S: {len(jades_gs_z7)}")

if len(jades_gs_z7) > 0:
    jades_coords = SkyCoord(
        ra=[r['RA_TARG'] for r in jades_gs_z7],
        dec=[r['Dec_TARG'] for r in jades_gs_z7],
        unit=u.deg
    )
    
    # 1-arcsecond match radius
    match_radius = Angle(1.0, unit=u.arcsec)
    
    idx_ceers, idx_jades, d2d, d3d = ceers_coords.search_around_sky(
        jades_coords, 
        seplimit=match_radius
    )
    
    # d2d is in arcseconds (astropy Quantity)
    sep_arcsec = d2d.to(u.arcsec).value
    
    # Group: multiple JADES sources can match one CEERS source
    # We need to find unique CEERS matches
    matched_ceers_indices = set(idx_ceers)
    
    print(f"\n=== CROSS-MATCH RESULTS ===")
    print(f"Match radius: 1 arcsecond")
    print(f"Number of unique CEERS z>7 sources matched: {len(matched_ceers_indices)}")
    print(f"Number of JADES z>7 matches: {len(idx_ceers)}")
    
    # Build match table
    matches = []
    for i, (ci, ji) in enumerate(zip(idx_ceers, idx_jades)):
        ceers_src = ceers_sel[ci]
        jades_src = jades_gs_z7[ji]
        sep = sep_arcsec[i]
        
        matches.append({
            'ceers_number': int(ceers_src['NUMBER']),
            'ceers_ra': ceers_src['RA'],
            'ceers_dec': ceers_src['DEC'],
            'z_phot': ceers_src['LP_Z_MED'],
            'z_phot_lo': ceers_src['LP_Z_MED68_LOW'],
            'z_phot_hi': ceers_src['LP_Z_MED68_HIGH'],
            'z_phot_best': ceers_src['LP_Z_BEST'],
            'mass_med': ceers_src['LP_MASS_MED'],
            'sfr_med': ceers_src['LP_SFR_MED'],
            'nbands': ceers_src['LP_NBANDS'],
            'jades_uid': jades_src['Unique_ID'],
            'jades_ra': jades_src['RA_TARG'],
            'jades_dec': jades_src['Dec_TARG'],
            'z_spec': jades_src['z_PRISM'],
            'z_flag': jades_src['Z_FLAG'],
            'sep_arcsec': sep,
            'field': jades_src['Field'],
        })
    
    # Sort by separation
    matches.sort(key=lambda m: m['sep_arcsec'])
    
    # Print match table
    print(f"\n{'N':<4} {'CEERS#':<8} {'z_phot':<8} {'z_phot_lo':<10} {'z_phot_hi':<10} {'z_spec':<8} {'Δz':<8} {'Δz/(1+z_s)':<12} {'sep(″)':<8} {'NB':<4} {'Z_FLAG':<10}")
    print("-" * 100)
    
    for i, m in enumerate(matches):
        dz = m['z_phot'] - m['z_spec']
        dz_norm = dz / (1 + m['z_spec']) if m['z_spec'] != 0 else 0
        print(f"{i+1:<4} {m['ceers_number']:<8} {m['z_phot']:<8.3f} {m['z_phot_lo']:<10.3f} {m['z_phot_hi']:<10.3f} {m['z_spec']:<8.3f} {dz:<8.3f} {dz_norm:<12.4f} {m['sep_arcsec']:<8.3f} {m['nbands']:<4.0f} {m['z_flag']:<10}")
    
    # Stats
    if len(matches) > 0:
        z_phots = np.array([m['z_phot'] for m in matches])
        z_specs = np.array([m['z_spec'] for m in matches])
        dzs = z_phots - z_specs
        dz_norms = dzs / (1 + z_specs)
        seps = np.array([m['sep_arcsec'] for m in matches])
        
        print(f"\n=== STATISTICS ===")
        print(f"Total matches: {len(matches)}")
        print(f"z>8 matches (z_spec > 8): {np.sum(z_specs > 8)}")
        print(f"z>8 matches (z_phot > 8): {np.sum(z_phots > 8)}")
        print(f"z_phot range: {z_phots.min():.3f} - {z_phots.max():.3f}")
        print(f"z_spec range: {z_specs.min():.3f} - {z_specs.max():.3f}")
        print(f"Δz median: {np.median(dzs):.4f}")
        print(f"Δz MAD: {np.median(np.abs(dzs - np.median(dzs))):.4f}")
        print(f"|Δz|/(1+z_spec) median: {np.median(np.abs(dz_norms)):.4f}")
        print(f"Separation median: {np.median(seps):.3f} arcsec")
        print(f"Separation max: {seps.max():.3f} arcsec")
        
        # Aliasing analysis: look for systematic offsets
        print(f"\n=== ALIASING ANALYSIS ===")
        print(f"Mean Δz: {np.mean(dzs):.4f} ± {np.std(dzs):.4f}")
        print(f"Mean Δz/(1+z_spec): {np.mean(dz_norms):.4f} ± {np.std(dz_norms):.4f}")
        
        # Check for z_phot ~ z_spec * N systematic patterns
        ratios = z_phots / z_specs
        print(f"z_phot/z_spec mean: {np.mean(ratios):.4f} ± {np.std(ratios):.4f}")
        
        # Look for sources where z_phot is significantly off from z_spec
        outliers = [m for m in matches if abs(m['z_phot'] - m['z_spec']) / (1 + m['z_spec']) > 0.15]
        print(f"\nOutliers (|Δz|/(1+z_spec) > 0.15): {len(outliers)}")
        if outliers:
            for m in outliers:
                dz = m['z_phot'] - m['z_spec']
                dz_n = dz / (1 + m['z_spec'])
                print(f"  CEERS#{m['ceers_number']}: z_phot={m['z_phot']:.3f} z_spec={m['z_spec']:.3f} Δz={dz:.3f} Δz/(1+z)={dz_n:.4f} sep={m['sep_arcsec']:.3f}″")
        
        # Check for harmonic aliasing structure
        # z_phot being a multiple/harmonic of z_spec could indicate Lyman-break aliasing
        print(f"\n--- Harmonic Aliasing Check ---")
        for m in matches:
            ratio = m['z_phot'] / m['z_spec']
            # Check if ratio is close to integer (1, 2, 3...) or 1/N
            for n in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]:
                if abs(ratio - n) < 0.15:
                    dz = m['z_phot'] - m['z_spec']
                    dz_n = dz / (1 + m['z_spec'])
                    print(f"  CEERS#{m['ceers_number']}: z_phot={m['z_phot']:.3f} z_spec={m['z_spec']:.3f} ratio={ratio:.3f}≈{n} Δz/(1+z)={dz_n:.4f}")
                    break
    
    # Save results to CSV
    import csv
    csv_path = 'ceers_jades_crossmatch_results.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'ceers_number', 'ceers_ra', 'ceers_dec', 
            'z_phot', 'z_phot_lo', 'z_phot_hi', 'z_phot_best',
            'mass_med', 'sfr_med', 'nbands',
            'jades_uid', 'jades_ra', 'jades_dec',
            'z_spec', 'z_flag', 'sep_arcsec', 'field'
        ])
        writer.writeheader()
        for m in matches:
            writer.writerow(m)
    print(f"\nResults saved to: {csv_path}")
    
else:
    print("No JADES DR4 z>7 sources in GOODS-S to cross-match with CEERS.")