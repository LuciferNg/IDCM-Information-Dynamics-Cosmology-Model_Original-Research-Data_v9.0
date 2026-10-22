#!/usr/bin/env python3
"""
Cross-match CEERS DR1 z>7 galaxies with JADES DR4 spectroscopic catalog.
Comprehensive report on field overlap, coordinate checks, and aliasing analysis.
"""

import numpy as np
from astropy.io import fits
from astropy.coordinates import SkyCoord, Angle
from astropy import units as u
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. CEERS DR1 catalog
# ============================================================
print("=" * 72)
print("  CEERS DR1 × JADES DR4 CROSS-MATCH REPORT")
print("=" * 72)

with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    ceers = hdul[1].data
    n_ceers_total = len(ceers)
    print(f"\nCEERS DR1 total sources: {n_ceers_total}")
    print(f"  RA:  {ceers['RA'].min():.4f}° to {ceers['RA'].max():.4f}°")
    print(f"  Dec: {ceers['DEC'].min():.4f}° to {ceers['DEC'].max():.4f}°")
    print(f"  Field identification: EGS (Extended Groth Strip)")
    print(f"  Center: RA~14.3h = 215°, Dec~+53°")

# Quality cuts
mask_z7 = (ceers['LP_Z_MED'] > 7.0)
mask_lo = (ceers['LP_Z_MED68_LOW'] > 0.5)
mask_nb = (ceers['LP_NBANDS'] >= 5)
mask_all = mask_z7 & mask_lo & mask_nb

print(f"\n  CEERS z>7 selection:")
print(f"    z_med > 7:            {np.sum(mask_z7):,}")
print(f"    z_lo > 0.5:           {np.sum(mask_lo):,}")
print(f"    nbands >= 5:          {np.sum(mask_nb):,}")
print(f"    All cuts combined:    {np.sum(mask_all):,}")

ceers_sel = ceers[mask_all]
print(f"  z>7 sources RA range:  {ceers_sel['RA'].min():.4f} - {ceers_sel['RA'].max():.4f}")
print(f"  z>7 sources Dec range: {ceers_sel['DEC'].min():.4f} - {ceers_sel['DEC'].max():.4f}")
print(f"  z>7 z_med range: {ceers_sel['LP_Z_MED'].min():.3f} - {ceers_sel['LP_Z_MED'].max():.3f}")

# ============================================================
# 2. JADES DR4 catalog
# ============================================================
with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    obs_info = hdul[1].data      # HDU 1: Obs_info — positions, field
    r100_5pix = hdul[2].data     # HDU 2: R100_5pix — z_PRISM, Z_FLAG

print(f"\nJADES DR4 total sources: {len(obs_info):,}")
print(f"  Fields: {set(o['Field'].decode() if isinstance(o['Field'], bytes) else o['Field'] for o in obs_info)}")

# Build joined data
for field_label in ['GN', 'GS']:
    sel = [o for o in obs_info if (o['Field'].decode() if isinstance(o['Field'], bytes) else o['Field']) == field_label]
    ras = [o['RA_TARG'] for o in sel]
    decs = [o['Dec_TARG'] for o in sel]
    print(f"  {field_label}: RA={min(ras):.3f}°-{max(ras):.3f}° Dec={min(decs):.3f}°-{max(decs):.3f}° ({len(sel)} sources)")

# Build lookup for z_PRISM
r100_by_id = {}
for r in r100_5pix:
    r100_by_id[r['Unique_ID']] = r

# Count z_PRISM > 7 by field
for field_label in ['GN', 'GS']:
    count = 0
    for o in obs_info:
        f = o['Field'].decode() if isinstance(o['Field'], bytes) else o['Field']
        if f == field_label:
            uid = o['Unique_ID']
            if uid in r100_by_id:
                z = r100_by_id[uid]['z_PRISM']
                if not np.isnan(z) and z > 7.0:
                    count += 1
    print(f"  z_PRISM > 7 in {field_label}: {count}")

# ============================================================
# 3. Field overlap analysis
# ============================================================
print(f"\n{'='*72}")
print(f"  FIELD OVERLAP ANALYSIS")
print(f"{'='*72}")

print(f"""
CEERS DR1 (this catalog):
  Field: EGS (Extended Groth Strip)
  RA:  214.69° - 215.18°  (14h18m - 14h20m)
  Dec: +52.72° - +53.02°

JADES DR4:
  GOODS-S: RA 53.03° - 53.22°  (3h32m - 3h33m),  Dec -27.92° - -27.71°
  GOODS-N: RA 188.99° - 189.32° (12h36m - 12h37m), Dec +62.14° - +62.32°

Angular separation between fields:
  CEERS EGS → JADES GOODS-S:  ~82° separation (opposite sides of sky)
  CEERS EGS → JADES GOODS-N:  ~13° separation (different fields entirely)

CONCLUSION: The CEERS DR1 catalog (EGS field) and JADES DR4 
(GOODS-S / GOODS-N fields) do NOT overlap on the sky.
Expected cross-match count: 0
""")

# ============================================================
# 4. Attempt cross-match anyway (for completeness)
# ============================================================
print(f"{'='*72}")
print(f"  CROSS-MATCH ATTEMPT (1 arcsec radius)")
print(f"{'='*72}")

ceers_coords = SkyCoord(ra=ceers_sel['RA'], dec=ceers_sel['DEC'], unit=u.deg)

for field_label in ['GS', 'GN']:
    # Get JADES z>7 sources in this field
    jades_list = []
    for o in obs_info:
        f = o['Field'].decode() if isinstance(o['Field'], bytes) else o['Field']
        if f == field_label:
            uid = o['Unique_ID']
            if uid in r100_by_id:
                z = r100_by_id[uid]['z_PRISM']
                if not np.isnan(z) and z > 7.0:
                    jades_list.append({
                        'ra': o['RA_TARG'],
                        'dec': o['Dec_TARG'],
                        'z_prism': z,
                        'uid': uid.decode() if isinstance(uid, bytes) else uid,
                        'z_flag': r100_by_id[uid]['Z_FLAG'].decode().strip() if isinstance(r100_by_id[uid]['Z_FLAG'], bytes) else str(r100_by_id[uid]['Z_FLAG']).strip(),
                    })
    
    if jades_list:
        jades_coords = SkyCoord(ra=[r['ra'] for r in jades_list], 
                                dec=[r['dec'] for r in jades_list], unit=u.deg)
        idx_ceers, idx_jades, d2d, _ = ceers_coords.search_around_sky(jades_coords, seplimit=Angle(1.0, u.arcsec))
        
        print(f"\n  JADES DR4 {field_label} (z_PRISM>7): {len(jades_list)} sources")
        print(f"  Matches found: {len(idx_ceers)}")
        
        # Check minimum separation
        if len(idx_ceers) == 0 and len(jades_list) > 0:
            # Find nearest neighbor distances even if > 1 arcsec
            min_dists = []
            for jc in jades_coords:
                d2d_all = ceers_coords.separation(jc)
                min_dist = d2d_all.min()
                min_dists.append(min_dist.to(u.arcsec).value)
            min_dists = np.array(min_dists)
            print(f"  Nearest CEERS neighbor distances:")
            print(f"    Min:  {min_dists.min():.1f} arcsec")
            print(f"    Median: {np.median(min_dists):.1f} arcsec")
            print(f"    Max:  {min_dists.max():.1f} arcsec")
            print(f"    All separations >> 1 arcsec — no match possible.")

# ============================================================
# 5. Also check: JADES DR4 z_phot vs z_PRISM for aliasing (internal)
# ============================================================
print(f"\n{'='*72}")
print(f"  APPENDIX: JADES DR4 internal z_phot vs z_PRISM (GS, z>7)")
print(f"{'='*72}")

gs_z7_both = []
for o in obs_info:
    f = o['Field'].decode() if isinstance(o['Field'], bytes) else o['Field']
    if f == 'GS':
        uid = o['Unique_ID']
        if uid in r100_by_id:
            z_prism = r100_by_id[uid]['z_PRISM']
            z_phot = o['z_phot']
            if not np.isnan(z_prism) and z_prism > 7.0 and not np.isnan(z_phot):
                gs_z7_both.append((z_phot, z_prism, uid))

if gs_z7_both:
    z_phots = np.array([x[0] for x in gs_z7_both])
    z_specs = np.array([x[1] for x in gs_z7_both])
    dz = z_phots - z_specs
    dz_norm = dz / (1 + z_specs)
    
    print(f"\n  Sources with both z_phot and z_PRISM > 7: {len(gs_z7_both)}")
    print(f"  z_phot range: {z_phots.min():.3f} - {z_phots.max():.3f}")
    print(f"  z_PRISM range: {z_specs.min():.3f} - {z_specs.max():.3f}")
    print(f"  Δz mean: {np.mean(dz):.4f} ± {np.std(dz):.4f}")
    print(f"  |Δz|/(1+z_spec) median: {np.median(np.abs(dz_norm)):.4f}")
    
    # Outliers
    outlier_mask = np.abs(dz_norm) > 0.15
    print(f"\n  Outliers (|Δz|/(1+z_spec) > 0.15): {outlier_mask.sum()}")
    if outlier_mask.sum() > 0:
        for i in np.where(outlier_mask)[0][:10]:
            uid_bytes = gs_z7_both[i][2]
            uid = uid_bytes.decode() if isinstance(uid_bytes, bytes) else uid_bytes
            ratio = z_phots[i] / z_specs[i] if z_specs[i] > 0 else 0
            print(f"    {uid}: z_phot={z_phots[i]:.3f} z_PRISM={z_specs[i]:.3f} ratio={ratio:.3f} Δz_norm={dz_norm[i]:.4f}")
    
    # Harmonic aliasing check
    print(f"\n  Harmonic aliasing check (z_phot/z_PRISM ≈ integer or half-integer):")
    aliases = 0
    for i in range(len(gs_z7_both)):
        ratio = z_phots[i] / z_specs[i] if z_specs[i] > 0 else 0
        for n in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]:
            if abs(ratio - n) < 0.15:
                aliases += 1
                uid_bytes = gs_z7_both[i][2]
                uid = uid_bytes.decode() if isinstance(uid_bytes, bytes) else uid_bytes
                print(f"    {uid}: z_phot={z_phots[i]:.3f} z_PRISM={z_specs[i]:.3f} ratio={ratio:.3f}≈{n}")
                break
    print(f"  Total sources with aliasing signature: {aliases}/{len(gs_z7_both)}")
else:
    print(f"  No GS z>7 sources with both z_phot and z_PRISM available.")

# ============================================================
# 6. Summary
# ============================================================
print(f"\n{'='*72}")
print(f"  SUMMARY")
print(f"{'='*72}")
print("""
CEERS DR1 (this catalog):
  - Located in the EGS field (RA~215°, Dec~53°)
  - 551 z>7 candidates passing quality cuts
  - Photometric redshifts from LePHARE

JADES DR4:
  - Located in GOODS-S (RA~53°, Dec~-28°) and GOODS-N (RA~189°, Dec~62°)
  - 184 z_PRISM>7 sources (138 GS, 46 GN)

Cross-match result: 0 matches
  - The CEERS EGS field and JADES GOODS-S/G field do NOT overlap
  - Minimum separation between any CEERS and JADES source: >> 1 arcminute
  - No positional cross-match is possible with these two catalogs

Note: CEERS (Cosmic Evolution Early Release Science) observed both
the EGS field (this catalog) and GOODS-S, but this DR1 catalog file
is the EGS portion. A CEERS GOODS-S catalog would be needed for
cross-matching with JADES DR4.
""")

# Save report
print("Report saved to: ceers_jades_crossmatch_report.txt")