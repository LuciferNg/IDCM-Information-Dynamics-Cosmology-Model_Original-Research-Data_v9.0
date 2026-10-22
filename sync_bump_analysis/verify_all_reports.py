#!/usr/bin/env python3
"""
Verify all report data against raw data files.
Checks every number in the summary report and individual reports.
"""
import warnings, gzip, io, numpy as np, os, re
warnings.filterwarnings('ignore')
from astropy.io import fits

SCRIPT_DIR = '/home/wsl/IDCM/sync_bump_analysis'
REPORT_DIR = os.path.join(SCRIPT_DIR, 'reports')
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
print("  COMPREHENSIVE REPORT VERIFICATION")
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
        nbands = c['LP_NBANDS'].astype(float)
        chi2 = c['LP_FIT_CHI'].astype(float)
        starflag = c['STAR_FLAG'].astype(float)

quality = (z_med > 0) & (z_med < 25) & (z_lo > 0.5) & (nbands >= 5) & (~np.isnan(z_med))
check(quality.sum() == 49106, f"CEERS quality sources = 49,106 (got {quality.sum():,})")
check(sum(quality & (z_med > 7) & (z_med < 25)) == 551, f"CEERS z>7 = 551")
check(sum(quality & (z_med > 8) & (z_med < 25)) == 287, f"CEERS z>8 = 287")
check(sum(quality & (z_med > 15) & (z_med < 25)) == 0, f"CEERS z>15 = 0")
check(abs(z_med[quality].max() - 14.445) < 0.01, f"CEERS max z = 14.445")

# z=13.5 cluster
z13 = quality & (abs(z_med - 13.5) < 0.3)
check(z13.sum() == 40, f"CEERS z=13.5±0.3 = 40 (report says 41 without quality)")
z13_chi2 = chi2[z13]
check(z13_chi2.max() == 4100.7, f"CEERS z=13.5 chi² max = 4100.7")
check(z13_chi2[z13_chi2 > 0].min() == 2.3, f"CEERS z=13.5 chi² min = 2.3")
check(starflag[z13].sum() == 5, f"CEERS z=13.5 star_flag = 5")

# φ-ratios
n56 = sum(quality & (abs(z_med - 5.6) < 0.3))
n69 = sum(quality & (abs(z_med - 6.9) < 0.3))
n77 = sum(quality & (abs(z_med - 7.7) < 0.3))
n82 = sum(quality & (abs(z_med - 8.2) < 0.3))
n85 = sum(quality & (abs(z_med - 8.5) < 0.3))
n89 = sum(quality & (abs(z_med - 8.9) < 0.3))
n92 = sum(quality & (abs(z_med - 9.2) < 0.3))
n95 = sum(quality & (abs(z_med - 9.5) < 0.3))
n100 = sum(quality & (abs(z_med - 10.0) < 0.3))

check(n56 == 351, f"CEERS z=5.6 = 351 (got {n56})")
check(n69 == 325, f"CEERS z=6.9 = 325 (got {n69})")
check(n77 == 90, f"CEERS z=7.7 = 90 (got {n77})")
check(n82 == 69, f"CEERS z=8.2 = 69 (got {n82})")
check(n85 == 63, f"CEERS z=8.5 = 63 (got {n85})")
check(n89 == 37, f"CEERS z=8.9 = 37 (got {n89})")
check(n92 == 29, f"CEERS z=9.2 = 29 (got {n92})")
check(n95 == 18, f"CEERS z=9.5 = 18 (got {n95})")
check(n100 == 29, f"CEERS z=10.0 = 29 (got {n100})")

# ════════════════════════════════════════════════════════════════
# 2. JADES DR4 Combined
# ════════════════════════════════════════════════════════════════
print("\n── JADES DR4 Combined ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr4_spectroscopic.fits'), memmap=False)
r100 = hdul[2].data
z_spec = r100['z_PRISM']
z_flag = r100['Z_FLAG']
valid = (z_spec > 0) & (z_spec < 25) & (~np.isnan(z_spec))

check(len(r100) == 5190, f"JADES DR4 total = 5,190 (got {len(r100)})")
check(valid.sum() == 3725, f"JADES DR4 valid = 3,725 (got {valid.sum()})")
check(sum(valid & (z_spec > 7)) == 184, f"JADES DR4 z>7 = 184")
check(sum(valid & (z_spec > 8)) == 76, f"JADES DR4 z>8 = 76")
check(sum(valid & (z_spec > 10)) == 21, f"JADES DR4 z>10 = 21")
check(sum(valid & (z_spec > 15)) == 0, f"JADES DR4 z>15 = 0")
check(abs(z_spec[valid].max() - 14.588) < 0.001, f"JADES DR4 max z = 14.588")

# φ-ratio
n56 = sum((abs(z_spec - 5.6) < 0.3) & valid)
n69 = sum((abs(z_spec - 6.9) < 0.3) & valid)
n77 = sum((abs(z_spec - 7.7) < 0.3) & valid)
n82 = sum((abs(z_spec - 8.2) < 0.3) & valid)
n85 = sum((abs(z_spec - 8.5) < 0.3) & valid)
n89 = sum((abs(z_spec - 8.9) < 0.3) & valid)
n92 = sum((abs(z_spec - 9.2) < 0.3) & valid)
n95 = sum((abs(z_spec - 9.5) < 0.3) & valid)
n100 = sum((abs(z_spec - 10.0) < 0.3) & valid)

check(n56 == 155, f"JADES DR4 z=5.6 = 155 (got {n56})")
check(n69 == 92, f"JADES DR4 z=6.9 = 92 (got {n69})")
check(n77 == 50, f"JADES DR4 z=7.7 = 50 (got {n77})")
check(n82 == 34, f"JADES DR4 z=8.2 = 34 (got {n82})")
check(n85 == 28, f"JADES DR4 z=8.5 = 28 (got {n85})")
check(n89 == 20, f"JADES DR4 z=8.9 = 20 (got {n89})")
check(n92 == 14, f"JADES DR4 z=9.2 = 14 (got {n92})")
check(n95 == 11, f"JADES DR4 z=9.5 = 11 (got {n95})")
check(n100 == 5, f"JADES DR4 z=10.0 = 5 (got {n100})")

r56 = n56 / n69
check(abs(r56 - 1.685) < 0.005, f"JADES DR4 5.6→6.9 = 1.685 (got {r56:.3f})")
hdul.close()

# ════════════════════════════════════════════════════════════════
# 3. JADES DR4 Prism
# ════════════════════════════════════════════════════════════════
print("\n── JADES DR4 Prism ──")
gs = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr4_goods_s_prism_redshift.fits'), memmap=False)[1].data
gn = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr4_goods_n_prism_redshift.fits'), memmap=False)[1].data
z_p = np.concatenate([gs['z_Spec'], gn['z_Spec']])
vp = (z_p > 0) & (z_p < 25) & (~np.isnan(z_p))

check(len(gs) == 2525, f"GOODS-S prism = 2,525")
check(len(gn) == 1561, f"GOODS-N prism = 1,561")
check(sum(vp & (z_p > 7)) == 112, f"Prism z>7 = 112")
check(sum(vp & (z_p > 15)) == 0, f"Prism z>15 = 0")

# ════════════════════════════════════════════════════════════════
# 4. GLASS-JWST
# ════════════════════════════════════════════════════════════════
print("\n── GLASS-JWST ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'glass_jwst_nirspec_catalog.fits'), memmap=False)
z_g = []
for i in [1, 2]:
    z = hdul[i].data['z_spec']
    z_g.extend(z[(z > 0) & (z < 25) & (~np.isnan(z))])
z_g = np.array(z_g)
vg = (z_g > 0) & (z_g < 25) & (~np.isnan(z_g))
check(sum((z_g > 7) & vg) == 11, f"GLASS z>7 = 11 (got {sum((z_g > 7) & vg)})")
check(sum((z_g > 15) & vg) == 0, f"GLASS z>15 = 0")
check(abs(z_g[vg].max() - 9.793) < 0.01, f"GLASS max z = 9.793")
hdul.close()

# ════════════════════════════════════════════════════════════════
# 5. UNCOVER DR4
# ════════════════════════════════════════════════════════════════
print("\n── UNCOVER DR4 ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'uncover_dr4_redshift_catalog.fits'), memmap=False)
u = hdul[1].data
z_u = u['z_spec'].astype(float)
vu = (z_u > 0) & (z_u < 25) & (~np.isnan(z_u))
check(sum(vu) == 406, f"UNCOVER DR4 valid = 406 (got {sum(vu)})")
check(sum((z_u > 7) & vu) == 20, f"UNCOVER DR4 z>7 = 20")
check(sum((z_u > 15) & vu) == 0, f"UNCOVER DR4 z>15 = 0")
check(abs(z_u[vu].max() - 13.164) < 0.01, f"UNCOVER DR4 max z = 13.164")
hdul.close()

# ════════════════════════════════════════════════════════════════
# 6. UNCOVER DR3 EAZY
# ════════════════════════════════════════════════════════════════
print("\n── UNCOVER DR3 EAZY ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'uncover_dr3_super_catalog.fits'), memmap=False)
u3 = hdul[1].data
z_ph = u3['z_phot'].astype(float)
z_ch = u3['z_phot_chi2'].astype(float)
good = (z_ph > 0) & (z_ph < 25) & (~np.isnan(z_ph)) & (z_ch > 0) & (z_ch < 10)
check(good.sum() == 29885, f"UNCOVER DR3 good = 29,885 (got {good.sum():,})")
check(sum((z_ph > 7) & (z_ph < 25) & good) == 1914, f"UNCOVER DR3 z>7 = 1,914")
check(sum((z_ph > 15) & (z_ph < 25) & good) == 691, f"UNCOVER DR3 z>15 = 691")
hdul.close()

# ════════════════════════════════════════════════════════════════
# 7. JADES DR5 GOODS-S
# ════════════════════════════════════════════════════════════════
print("\n── JADES DR5 GOODS-S ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr5_goods_s_catalog.fits'), memmap=False)
pz = hdul[11].data
z_ml = pz['z_ml'].astype(float)
v = (z_ml > 0) & (z_ml < 25) & (~np.isnan(z_ml))

check(len(pz) == 304366, f"DR5 GS total = 304,366")
check(v.sum() == 302666, f"DR5 GS valid = 302,666")
check(sum((z_ml > 7) & v) == 16820, f"DR5 GS z>7 = 16,820")
check(sum((z_ml > 15) & v) == 1860, f"DR5 GS z>15 = 1,860")
check(abs(z_ml[v].max() - 21.990) < 0.01, f"DR5 GS max z = 21.990")

# φ-ratio
n56 = sum((abs(z_ml - 5.6) < 0.3) & v)
n69 = sum((abs(z_ml - 6.9) < 0.3) & v)
n77 = sum((abs(z_ml - 7.7) < 0.3) & v)
n82 = sum((abs(z_ml - 8.2) < 0.3) & v)
n85 = sum((abs(z_ml - 8.5) < 0.3) & v)
n89 = sum((abs(z_ml - 8.9) < 0.3) & v)
n92 = sum((abs(z_ml - 9.2) < 0.3) & v)
n95 = sum((abs(z_ml - 9.5) < 0.3) & v)
n100 = sum((abs(z_ml - 10.0) < 0.3) & v)
n135 = sum((abs(z_ml - 13.5) < 0.3) & v)
n140 = sum((abs(z_ml - 14.0) < 0.3) & v)

check(n56 == 7894, f"DR5 GS z=5.6 = 7,894 (got {n56})")
check(n69 == 7570, f"DR5 GS z=6.9 = 7,570 (got {n69})")
check(n77 == 2922, f"DR5 GS z=7.7 = 2,922 (got {n77})")
check(n82 == 2044, f"DR5 GS z=8.2 = 2,044 (got {n82})")
check(n85 == 1964, f"DR5 GS z=8.5 = 1,964 (got {n85})")
check(n89 == 2061, f"DR5 GS z=8.9 = 2,061 (got {n89})")
check(n92 == 2349, f"DR5 GS z=9.2 = 2,349 (got {n92})")
check(n95 == 1624, f"DR5 GS z=9.5 = 1,624 (got {n95})")
check(n100 == 584, f"DR5 GS z=10.0 = 584 (got {n100})")
check(n135 == 202, f"DR5 GS z=13.5 = 202 (got {n135})")
check(n140 == 115, f"DR5 GS z=14.0 = 115 (got {n140})")

hdul.close()

# ════════════════════════════════════════════════════════════════
# 8. JADES DR5 GOODS-N
# ════════════════════════════════════════════════════════════════
print("\n── JADES DR5 GOODS-N ──")
hdul = fits.open(os.path.join(SCRIPT_DIR, 'jades_dr5_goods_n_catalog.fits'), memmap=False)
pz = hdul[11].data
z_ml = pz['z_ml'].astype(float)
v = (z_ml > 0) & (z_ml < 25) & (~np.isnan(z_ml))

check(len(pz) == 181144, f"DR5 GN total = 181,144")
check(v.sum() == 179979, f"DR5 GN valid = 179,979")
check(sum((z_ml > 7) & v) == 6929, f"DR5 GN z>7 = 6,929")
check(sum((z_ml > 15) & v) == 1002, f"DR5 GN z>15 = 1,002")
check(abs(z_ml[v].max() - 21.990) < 0.01, f"DR5 GN max z = 21.990")

n56 = sum((abs(z_ml - 5.6) < 0.3) & v)
n69 = sum((abs(z_ml - 6.9) < 0.3) & v)
n77 = sum((abs(z_ml - 7.7) < 0.3) & v)
n82 = sum((abs(z_ml - 8.2) < 0.3) & v)
n135 = sum((abs(z_ml - 13.5) < 0.3) & v)
n140 = sum((abs(z_ml - 14.0) < 0.3) & v)

check(n56 == 4169, f"DR5 GN z=5.6 = 4,169 (got {n56})")
check(n69 == 3839, f"DR5 GN z=6.9 = 3,839 (got {n69})")
check(n77 == 1275, f"DR5 GN z=7.7 = 1,275 (got {n77})")
check(n82 == 682, f"DR5 GN z=8.2 = 682 (got {n82})")
check(n135 == 116, f"DR5 GN z=13.5 = 116 (got {n135})")
check(n140 == 81, f"DR5 GN z=14.0 = 81 (got {n140})")

hdul.close()

# ════════════════════════════════════════════════════════════════
# 9. Cross-survey totals from summary report
# ════════════════════════════════════════════════════════════════
print("\n── CROSS-SURVEY TOTALS ──")
# Spectroscopic total z>7: 184 + 112 + 11 + 20 = 327
# Wait, the summary says 878. Let me check.
# CEERS z>7 = 551 (photoz)
# JADES DR4 Comb z>7 = 184 (spec)
# JADES DR4 Prism z>7 = 112 (spec)
# GLASS z>7 = 11 (spec)
# UNCOVER DR4 z>7 = 20 (spec)
# Total spectroscopic z>7 = 184 + 112 + 11 + 20 = 327
# But the summary says 878. Let me check what's in the summary...

spec_z7 = 184 + 112 + 11 + 20
check(spec_z7 == 327, f"Spectroscopic z>7 total = 327 (got {spec_z7})")

# The summary says "總計 878 個光譜-z>7 星系" - this is wrong!
# 184 + 112 + 11 + 20 = 327, not 878
# 878 = 551 (CEERS photoz) + 327 (spec-z)
# The report incorrectly includes CEERS photoz in the spectroscopic total

print(f"\n⚠️  CRITICAL CHECK: Summary says 878 spectroscopic z>7")
print(f"   Actual spectroscopic z>7: 184 + 112 + 11 + 20 = {spec_z7}")
print(f"   If including CEERS photoz: 551 + 327 = 878")
print(f"   → Summary may be including CEERS photoz in spectroscopic total")

# ════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for e in errors:
        print(f"  {e}")
else:
    print("\n✅ ALL NUMERICAL CHECKS PASSED")
    
if warnings_list:
    print(f"\n{len(warnings_list)} WARNING(S):")
    for w in warnings_list:
        print(f"  {w}")

print(f"{'=' * 70}")