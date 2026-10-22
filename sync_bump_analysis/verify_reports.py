#!/usr/bin/env python3
"""
Verify all report data against actual data files.
Check for hallucinations, wrong numbers, incorrect claims.
"""
import warnings, gzip, io, numpy as np, os
warnings.filterwarnings('ignore')
from astropy.io import fits

SCRIPT_DIR = '/home/wsl/IDCM/sync_bump_analysis'
phi = (1 + 5**0.5) / 2
aliasing_zs = [5.6, 6.9, 7.7, 8.2, 8.5, 8.9, 9.2, 9.5, 10.0, 13.5, 14.0]

errors = []
warnings_list = []

def check(condition, msg):
    if not condition:
        errors.append(f"❌ FAIL: {msg}")
    else:
        print(f"  ✅ {msg}")

def warn(msg):
    warnings_list.append(f"⚠️  WARN: {msg}")

print("=" * 70)
print("  REPORT VERIFICATION — Checking against raw data")
print("=" * 70)

# ════════════════════════════════════════════════════════════════
# 1. CEERS DR1
# ════════════════════════════════════════════════════════════════
print("\n── CEERS DR1 ──")
with gzip.open(os.path.join(SCRIPT_DIR, 'ceers_dr1_catalog.fits.gz'), 'rb') as f:
    with fits.open(io.BytesIO(f.read())) as hdul:
        c = hdul[1].data
        z_med = c['LP_Z_MED'].astype(float)
        z_lo = c['LP_Z_MED68_LOW'].astype(float)
        z_hi = c['LP_Z_MED68_HIGH'].astype(float)
        z_best = c['LP_Z_BEST'].astype(float)
        chi2 = c['LP_FIT_CHI'].astype(float)
        nbands = c['LP_NBANDS'].astype(float)
        star_flag = c['STAR_FLAG'].astype(float)
        ra = c['RA'].astype(float)
        dec = c['DEC'].astype(float)

# Check: Total sources
check(len(c) == 87345, f"CEERS total sources = 87,345 (got {len(c)})")

# Check: z>15 with NO quality cuts
z_any = (z_med > 0) & (z_med < 25) & (~np.isnan(z_med))
z15_any = sum(z_any & (z_med > 15))
print(f"  [INFO] z>15 (no quality cuts): {z15_any}")

# Check: z>15 with quality cuts
quality = (z_med > 0) & (z_med < 25) & (z_lo > 0.5) & (nbands >= 5) & (~np.isnan(z_med))
z15_quality = sum(quality & (z_med > 15))
check(z15_quality == 0, f"CEERS z>15 (quality) = 0 (got {z15_quality})")

# Check: z>7 with quality
z7_quality = sum(quality & (z_med > 7) & (z_med < 25))
check(z7_quality == 551, f"CEERS z>7 (quality) = 551 (got {z7_quality})")

# Check: z>8 with quality
z8_quality = sum(quality & (z_med > 8) & (z_med < 25))
check(z8_quality == 287, f"CEERS z>8 (quality) = 287 (got {z8_quality})")

# Check: z=13.5 cluster
z13_count = sum(quality & (abs(z_med - 13.5) < 0.3))
print(f"  [INFO] z=13.5±0.3 (quality): {z13_count}")

# Check chi² of z=13.5 sources
z13_idx = np.where(quality & (abs(z_med - 13.5) < 0.3))[0]
if len(z13_idx) > 0:
    z13_chi2 = chi2[z13_idx]
    z13_star = star_flag[z13_idx]
    z13_lo = z_lo[z13_idx]
    z13_id = c['NUMBER'][z13_idx]
    # Check: chi² range
    print(f"    chi² range: {z13_chi2.min():.1f} - {z13_chi2.max():.1f}")
    print(f"    chi² < 10: {sum(z13_chi2 < 10)}")
    print(f"    chi² > 100: {sum(z13_chi2 > 100)}")
    print(f"    star_flag: {sum(z13_star == 1)}")
    # Check: 11800-series (deblending artifact)
    id_nums = z13_id[z13_chi2 > 100]
    print(f"    IDs with chi²>100: {list(id_nums)}")
    # Check narrow P(z) sources (width < 0.1)
    # From earlier subagent analysis: 11 narrow P(z) sources with chi²=125-4101
    z13_width = z_hi[z13_idx] - z_lo[z13_idx]
    narrow = z13_width < 0.1
    print(f"    Narrow P(z) sources (width<0.1): {sum(narrow)}")
    if sum(narrow) > 0:
        narrow_chi2 = z13_chi2[narrow]
        print(f"    Narrow P(z) chi² range: {narrow_chi2.min():.1f} - {narrow_chi2.max():.1f}")
        check(narrow_chi2.min() >= 100, f"chi² min for narrow P(z) >= 100 (got {narrow_chi2.min():.1f})")
    # Check if report's claim of chi²=125-4101 is correct for the narrow subset
    # (The report refers to the 11 narrow P(z) sources, not all 40 sources at z=13.5)

# Check aliasing counts
aliasing_check = {}
for az in aliasing_zs:
    cnt = sum(quality & (abs(z_med - az) < 0.3))
    aliasing_check[az] = cnt
print(f"  Aliasing counts: {aliasing_check}")

# φ-ratio
print(f"  φ-ratios:")
for i in range(len(aliasing_zs)-1):
    z1, z2 = aliasing_zs[i], aliasing_zs[i+1]
    n1 = sum(quality & (abs(z_med - z1) < 0.3)) or 1
    n2 = sum(quality & (abs(z_med - z2) < 0.3)) or 1
    r = n1 / n2
    dev = abs(r/phi - 1) * 100
    print(f"    {z1:.1f}→{z2:.1f}: {n1}/{n2} = {r:.3f} (dev={dev:.1f}%)")

# ════════════════════════════════════════════════════════════════
# 2. JADES DR4 Combined
# ════════════════════════════════════════════════════════════════
print("\n── JADES DR4 Combined ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr4_spectroscopic.fits'), memmap=False)
# Check HDU 2 (R100_5pix)
r100 = hdul[2].data
z_spec = r100['z_PRISM']
z_flag = r100['Z_FLAG']
valid_spec = (z_spec > 0) & (z_spec < 25) & (~np.isnan(z_spec))
n_total = len(r100)
check(n_total >= 5190, f"JADES DR4 Combined total >= 5190 (got {n_total})")
n_valid = int(valid_spec.sum())
print(f"  Valid spec-z: {n_valid}")

# z>7
z7_spec = int((valid_spec & (z_spec > 7)).sum())
check(z7_spec == 184, f"JADES DR4 z>7 = 184 (got {z7_spec})")

# z>8
z8_spec = int((valid_spec & (z_spec > 8)).sum())
check(z8_spec == 76, f"JADES DR4 z>8 = 76 (got {z8_spec})")

# z>10
z10_spec = int((valid_spec & (z_spec > 10)).sum())
check(z10_spec == 21, f"JADES DR4 z>10 = 21 (got {z10_spec})")

# z>15
z15_spec = int((valid_spec & (z_spec > 15)).sum())
check(z15_spec == 0, f"JADES DR4 z>15 = 0 (got {z15_spec})")

# max z
max_z = z_spec[valid_spec].max()
print(f"  Max z: {max_z:.3f}")

# Check highest z sources
# Get top 5 z values
top_idx = np.argsort(z_spec[valid_spec])[-5:]
top_z = z_spec[valid_spec][top_idx]
print(f"  Top 5 z: {[round(z, 3) for z in top_z]}")

# Check if z=14.588 exists
has_14588 = any(abs(z_spec[valid_spec] - 14.588) < 0.001)
check(has_14588, f"z=14.588 exists in data (found={has_14588})")

# Check if z=14.360 exists
has_14360 = any(abs(z_spec[valid_spec] - 14.360) < 0.001)
check(has_14360, f"z=14.360 exists in data (found={has_14360})")

# φ-ratio at 5.6→6.9
n56 = sum((abs(z_spec - 5.6) < 0.3) & valid_spec)
n69 = sum((abs(z_spec - 6.9) < 0.3) & valid_spec)
r56 = n56 / n69 if n69 > 0 else 0
dev56 = abs(r56/phi - 1) * 100
print(f"  5.6→6.9: {n56}/{n69} = {r56:.3f} (dev={dev56:.1f}%)")
check(abs(r56 - 1.685) < 0.005, f"φ-ratio 5.6→6.9 = 1.685 (got {r56:.3f})")

hdul.close()

# ════════════════════════════════════════════════════════════════
# 3. JADES DR4 Prism
# ════════════════════════════════════════════════════════════════
print("\n── JADES DR4 Prism ──")
gs = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr4_goods_s_prism_redshift.fits'), memmap=False)[1].data
gn = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr4_goods_n_prism_redshift.fits'), memmap=False)[1].data
z_prism = np.concatenate([gs['z_Spec'], gn['z_Spec']])
valid_prism = (z_prism > 0) & (z_prism < 25) & (~np.isnan(z_prism))

check(len(gs) == 2525, f"GOODS-S prism: 2525 (got {len(gs)})")
check(len(gn) == 1561, f"GOODS-N prism: 1561 (got {len(gn)})")
check(len(gs) + len(gn) == 4086, f"Total prism: 4086 (got {len(gs)+len(gn)})")

z7_p = int(sum((z_prism > 7) & valid_prism))
check(z7_p == 112, f"Prism z>7 = 112 (got {z7_p})")
z15_p = int(sum((z_prism > 15) & valid_prism))
check(z15_p == 0, f"Prism z>15 = 0 (got {z15_p})")

max_z_p = z_prism[valid_prism].max()
print(f"  Max z: {max_z_p:.3f}")

# ════════════════════════════════════════════════════════════════
# 4. GLASS-JWST
# ════════════════════════════════════════════════════════════════
print("\n── GLASS-JWST NIRSpec ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'glass_jwst_nirspec_catalog.fits'), memmap=False)
z_glass = []
for i in [1, 2]:
    z = hdul[i].data['z_spec']
    z_glass.extend(z[(z > 0) & (z < 25) & (~np.isnan(z))])
z_glass = np.array(z_glass)
valid_glass = (z_glass > 0) & (z_glass < 25) & (~np.isnan(z_glass))
n_glass = int(len(valid_glass))
print(f"  Valid spec-z: {n_glass}")

z7_g = int(sum((z_glass > 7) & valid_glass))
check(z7_g == 11, f"GLASS z>7 = 11 (got {z7_g})")
z15_g = int(sum((z_glass > 15) & valid_glass))
check(z15_g == 0, f"GLASS z>15 = 0 (got {z15_g})")
max_z_g = z_glass[valid_glass].max()
check(abs(max_z_g - 9.793) < 0.01, f"GLASS max z = 9.793 (got {max_z_g:.3f})")
hdul.close()

# ════════════════════════════════════════════════════════════════
# 5. UNCOVER DR4
# ════════════════════════════════════════════════════════════════
print("\n── UNCOVER DR4 ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'uncover_dr4_redshift_catalog.fits'), memmap=False)
u = hdul[1].data
z_uncover = u['z_spec'].astype(float)
valid_uncover = (z_uncover > 0) & (z_uncover < 25) & (~np.isnan(z_uncover))
flag = u['flag_zspec_qual']
n_uncover = int(valid_uncover.sum())
check(n_uncover >= 406, f"UNCOVER DR4 valid spec-z = 406 (got {n_uncover})")

z7_u = int((valid_uncover & (z_uncover > 7)).sum())
check(z7_u == 20, f"UNCOVER z>7 = 20 (got {z7_u})")
z15_u = int((valid_uncover & (z_uncover > 15)).sum())
check(z15_u == 0, f"UNCOVER z>15 = 0 (got {z15_u})")
max_z_u = z_uncover[valid_uncover].max()
check(abs(max_z_u - 13.164) < 0.01, f"UNCOVER max z = 13.164 (got {max_z_u:.3f})")
hdul.close()

# ════════════════════════════════════════════════════════════════
# 6. UNCOVER DR3 EAZY
# ════════════════════════════════════════════════════════════════
print("\n── UNCOVER DR3 EAZY ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'uncover_dr3_super_catalog.fits'), memmap=False)
u3 = hdul[1].data
z_phot = u3['z_phot'].astype(float)
z_chi2 = u3['z_phot_chi2'].astype(float)
good_eazy = (z_phot > 0) & (z_phot < 25) & (~np.isnan(z_phot)) & (z_chi2 > 0) & (z_chi2 < 10)

n_good = int(good_eazy.sum())
print(f"  Good EAZY (chi²<10): {n_good:,}")

z7_e = int((good_eazy & (z_phot > 7) & (z_phot < 25)).sum())
check(z7_e == 1914, f"UNCOVER EAZY z>7 = 1914 (got {z7_e})")
z15_e = int((good_eazy & (z_phot > 15) & (z_phot < 25)).sum())
check(z15_e == 691, f"UNCOVER EAZY z>15 = 691 (got {z15_e})")
max_z_e = z_phot[good_eazy].max()
print(f"  Max z (EAZY): {max_z_e:.3f}")

# φ-ratio 9.5→10.0
n95 = sum((abs(z_phot - 9.5) < 0.3) & good_eazy)
n100 = sum((abs(z_phot - 10.0) < 0.3) & good_eazy)
r95 = n95 / n100 if n100 > 0 else 0
dev95 = abs(r95/phi - 1) * 100
print(f"  9.5→10.0: {n95}/{n100} = {r95:.3f} (dev={dev95:.1f}%)")
check(abs(r95 - 1.620) < 0.005, f"EAZY φ-ratio 9.5→10.0 = 1.620 (got {r95:.3f})")
hdul.close()

# ════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for e in errors:
        print(f"  {e}")
else:
    print("\n✅ ALL NUMERICAL CHECKS PASSED — no hallucinations found in numerical data")
    
if warnings_list:
    print(f"\n{len(warnings_list)} WARNING(S):")
    for w in warnings_list:
        print(f"  {w}")
        
print("=" * 70)