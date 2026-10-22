#!/usr/bin/env python3
"""
SDSS 控制變數測試：固定質量 + 固定金屬量下，平均 EW(Hβ) vs z
數據：
  - gal_info: z (DR7 MPA-JHU)
  - gal_line: EW(Hβ) 計算（DR7 MPA-JHU）
  - newmasses_dr4: 恆星質量 rml50 (Kauffmann+03)
  - gal_fiboh: 金屬量 12+log(O/H) (Tremonti+04)
"""
import numpy as np
from astropy.io import fits

# ========== Load DR4 stellar masses ==========
print("Loading DR4 stellar masses (newmasses)...")
mass_map = {}  # (plate, mjd, fiber) -> log M*
with open('/tmp/newmasses_dr4.gz', 'rb') as f:
    import gzip
    with gzip.open('/tmp/newmasses_dr4.gz', 'rt') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 9:
                plate = int(parts[0])
                mjd = int(parts[1])
                fiber = int(parts[2])
                rml50 = float(parts[8])  # column 9 = dust-corrected mass median
                mass_map[(plate, mjd, fiber)] = rml50
print(f"  Loaded {len(mass_map)} galaxies with stellar mass")

# ========== Load SDSS data ==========
print("Loading SDSS DR7 MPA-JHU...")
info = fits.open('/tmp/gal_info_dr7_v5_2.fit.gz')
i_data = info[1].data
line = fits.open('/tmp/gal_line_dr7_v5_2.fit.gz')
l_data = line[1].data
oh = fits.open('/tmp/gal_fiboh.fits.gz')
oh_data = oh[1].data

n = len(i_data)
print(f"  Total galaxies: {n}")

# ========== Build arrays ==========
plate = i_data['PLATEID']
mjd = i_data['MJD']
fiber = i_data['FIBERID']
z = i_data['Z']
oh_med = oh_data['MEDIAN']

# EW(Hβ) from flux / continuum
hb_cont = l_data['H_BETA_CONT']
hb_flux = l_data['H_BETA_FLUX']
ha_cont = l_data['H_ALPHA_CONT']
ha_flux = l_data['H_ALPHA_FLUX']
o3 = l_data['OIII_5007_FLUX']
n2 = l_data['NII_6584_FLUX']

# ========== Select low-z, compute EW, BPT ==========
print("Selecting star-forming galaxies...")
sub = (z > 0.001) & (z < 0.1)
idx = np.where(sub)[0]
print(f"  z<0.1: {len(idx)}")

# Compute EW
hb_ew = np.zeros(len(idx))
ha_ew = np.zeros(len(idx))
for k, i in enumerate(idx):
    if hb_cont[i] > 3 and hb_flux[i] > 0:
        hb_ew[k] = hb_flux[i] / hb_cont[i] * (1 + z[i])
    if ha_cont[i] > 3 and ha_flux[i] > 0:
        ha_ew[k] = ha_flux[i] / ha_cont[i] * (1 + z[i])

# BPT star-forming
good = (hb_cont[idx] > 3) & (hb_flux[idx] > 0) & (ha_cont[idx] > 3) & (ha_flux[idx] > 0) & (o3[idx] > 0) & (n2[idx] > 0)
log_o3hb = np.log10(o3[idx][good] / hb_flux[idx][good])
log_n2ha = np.log10(n2[idx][good] / ha_flux[idx][good])
x = np.clip(log_n2ha, -5, -0.001)
y_lim = 0.61 / (x - 0.05) + 1.3
y_lim = np.clip(y_lim, -5, 5)
sf = (log_o3hb < y_lim)

# Get mass for each galaxy
mass = np.full(len(idx), np.nan)
ohv = np.full(len(idx), np.nan)
for k, i in enumerate(idx):
    key = (int(plate[i]), int(mjd[i]), int(fiber[i]))
    if key in mass_map:
        mass[k] = mass_map[key]
    if oh_med[i] > -50:
        ohv[k] = oh_med[i]

# Combine
sf_idx_global = np.where(good)[0][sf]
sf_mass = mass[sf_idx_global]
sf_oh = ohv[sf_idx_global]
sf_hb = hb_ew[sf_idx_global]
sf_z = z[idx][good][sf]

# Clean: valid EW, mass, metallicity
valid = (sf_hb > 0) & (sf_hb < 1000) & np.isfinite(sf_mass) & np.isfinite(sf_oh) & (sf_mass > 8) & (sf_mass < 12) & (sf_oh > 7.5) & (sf_oh < 9.5)
sf_mass = sf_mass[valid]
sf_oh = sf_oh[valid]
sf_hb = sf_hb[valid]
sf_z = sf_z[valid]

print(f"  Star-forming with mass+OH: {len(sf_mass)}")

# ========== Binned analysis ==========
# Mass bins
mass_bins = [(9.0, 9.5), (9.5, 10.0), (10.0, 10.5), (10.5, 11.0)]
# Metallicity bins
oh_bins = [(8.0, 8.4), (8.4, 8.8), (8.8, 9.2)]

print("\n" + "=" * 70)
print("控制變數測試：固定質量 + 固定金屬量，平均 EW(Hβ) vs z")
print("=" * 70)

print(f"\n{'質量 bin':>12s} {'金屬量 bin':>12s} {'z bin':>10s} {'n':>5s} {'EW(Hβ) mean':>12s} {'EW(Hβ) med':>12s}")
print("-" * 70)

results = []
for mb_lo, mb_hi in mass_bins:
    for oh_lo, oh_hi in oh_bins:
        sel = (sf_mass >= mb_lo) & (sf_mass < mb_hi) & (sf_oh >= oh_lo) & (sf_oh < oh_hi)
        if np.sum(sel) < 30:
            continue
        # Split by z
        for z_lo, z_hi in [(0.001, 0.05), (0.05, 0.1)]:
            zsel = sel & (sf_z >= z_lo) & (sf_z < z_hi)
            nz = np.sum(zsel)
            if nz >= 30:
                mean_ew = np.mean(sf_hb[zsel])
                med_ew = np.median(sf_hb[zsel])
                print(f"{mb_lo:.1f}-{mb_hi:.1f}   {oh_lo:.1f}-{oh_hi:.1f}   {z_lo:.3f}-{z_hi:.2f}  {nz:5d}  {mean_ew:10.1f} A  {med_ew:10.1f} A")
                results.append((mb_lo, mb_hi, oh_lo, oh_hi, z_lo, z_hi, nz, mean_ew, med_ew))

# ========== Summary ==========
print("\n" + "=" * 70)
print("結果解讀")
print("=" * 70)
print("""
如果固定質量 + 固定金屬量後：
  - 低 z (0.001-0.05) 同高 z (0.05-0.1) 嘅平均 EW(Hβ) 相同
    → EW 唔隨 z 變化（喺 SDSS 低 z 範圍內）
  - 呢個係 SDSS 內部嘅 baseline，冇預期嘅 z 趨勢（因為 z<0.1 年齡差別 <1 Gyr）
  
真正嘅測試係同 MOSDEF (z=1.5-3.4) 比較：
  - MOSDEF 固定質量 + 固定金屬量下，EW 仍然隨 z 上升 ~2-4x
  - 呢個殘餘趨勢 = ΛCDM 嘅「年齡效應」證據
  - IDCM 話呢個殘餘趨勢可能係 selection effect
""")

# Save results
import json
def conv(o):
    if isinstance(o, (np.int64, np.int32, np.float32, np.float64)):
        return o.item()
    raise TypeError
with open('/home/wsl/IDCM/sdss_controlled_results.json', 'w') as f:
    json.dump({'results': [{'mass_lo': r[0], 'mass_hi': r[1], 'oh_lo': r[2], 'oh_hi': r[3],
                            'z_lo': r[4], 'z_hi': r[5], 'n': r[6], 'ew_mean': r[7], 'ew_med': r[8]} for r in results]}, f, indent=2, default=conv)
print("\nSaved to /home/wsl/IDCM/sdss_controlled_results.json")