#!/usr/bin/env python3
"""
1. JADES 低 z 天體（z=0.5-3）下載清單 — 填 z=0.1-3 gap
2. SDSS 加大樣本清單（每 bin 1000）
"""
import re
import numpy as np
from astropy.io import fits

# ========== 1. JADES 低 z ==========
el = fits.open('/tmp/jades_prism_line.fits')[1].data
z = el['z_Spec']
nspec = el['NIRSpec_ID']
tier = el['TIER']

# 讀 x1d URL 列表
with open('/tmp/jades_x1d_list.txt') as fh:
    x1d_urls = [l.strip() for l in fh if l.strip()]

url_by_id = {}
for u in x1d_urls:
    m = re.search(r'goods-s-(\w+)-(\d+)_([a-z0-9-]+)_v\d+\.\d+_x1d\.fits', u)
    if m:
        field, sid, grating = m.groups()
        key = ('goods-s-' + field, int(sid))
        url_by_id.setdefault(key, []).append(u)

# z=0.5-3 嘅天體（填 gap），有 Hβ 偵測優先但唔強制
gap_idx = []
for i in range(len(el)):
    if 0.5 <= z[i] < 3.0:
        key = (str(tier[i]), int(nspec[i]))
        if key in url_by_id:
            prism = [u for u in url_by_id[key] if 'clear-prism' in u]
            if prism:
                gap_idx.append((i, prism[0]))

print(f"JADES 低 z (0.5-3) matched to x1d: {len(gap_idx)}")

with open('/tmp/jades_gap_manifest.txt', 'w') as fh:
    for i, url in gap_idx:
        fh.write(f"{i}\t{z[i]:.4f}\t{url}\n")

# 分佈
for zl, zh in [(0.5,1.0),(1.0,1.5),(1.5,2.0),(2.0,2.5),(2.5,3.0)]:
    n = sum(1 for i,_ in gap_idx if zl <= z[i] < zh)
    print(f"  z={zl}-{zh}: {n}")

# ========== 2. SDSS 加大 ==========
info = fits.open('/tmp/gal_info_dr7_v5_2.fit.gz')[1].data
line = fits.open('/tmp/gal_line_dr7_v5_2.fit.gz')[1].data

z_s = info['Z']
plate = info['PLATEID']
mjd = info['MJD']
fiber = info['FIBERID']

sub = (z_s > 0.001) & (z_s < 0.1)
idx = np.where(sub)[0]

# BPT 星形成
hb_cont = line['H_BETA_CONT'][idx]
hb_flux = line['H_BETA_FLUX'][idx]
ha_cont = line['H_ALPHA_CONT'][idx]
ha_flux = line['H_ALPHA_FLUX'][idx]
o3 = line['OIII_5007_FLUX'][idx]
n2 = line['NII_6584_FLUX'][idx]
good = (hb_cont > 3) & (hb_flux > 0) & (ha_cont > 3) & (ha_flux > 0) & (o3 > 0) & (n2 > 0)
log_o3hb = np.log10(o3[good] / hb_flux[good])
log_n2ha = np.log10(n2[good] / ha_flux[good])
x = np.clip(log_n2ha, -5, -0.001)
y_lim = np.clip(0.61 / (x - 0.05) + 1.3, -5, 5)
sf = log_o3hb < y_lim
sf_idx = idx[good][sf]
print(f"\nSDSS star-forming: {len(sf_idx)}")

# 每 bin 1000
rng = np.random.RandomState(42)
bins = [(0.001, 0.02), (0.02, 0.04), (0.04, 0.06), (0.06, 0.08), (0.08, 0.10)]
selected = []
for zl, zh in bins:
    inbin = (z_s[sf_idx] >= zl) & (z_s[sf_idx] < zh)
    cand = sf_idx[inbin]
    n_take = min(1000, len(cand))
    pick = rng.choice(cand, n_take, replace=False) if n_take < len(cand) else cand
    selected.extend(pick.tolist())
    print(f"z={zl}-{zh}: {len(cand)} avail, take {n_take}")

selected = np.array(selected)
print(f"\nTotal SDSS selected: {len(selected)}")

with open('/tmp/sdss_large_manifest.txt', 'w') as fh:
    for i in selected:
        p = int(plate[i]); m = int(mjd[i]); fb = int(fiber[i])
        url = f"https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/{p:04d}/spec-{p:04d}-{m}-{fb:04d}.fits"
        fh.write(f"{i}\t{p}\t{m}\t{fb}\t{z_s[i]:.5f}\t{url}\n")
print("Manifest: /tmp/sdss_large_manifest.txt")