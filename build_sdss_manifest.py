#!/usr/bin/env python3
"""
建立 SDSS 原始光譜大樣本下載清單：
從 SDSS DR7 MPA-JHU 揀低 z (0.001-0.1) 星形成星系，對應到 DR18 spec 檔案
（MPA-JHU plate/mjd/fiber 同 SDSS DR18 specObj 一致）
"""
import numpy as np
from astropy.io import fits

# 1. 讀 MPA-JHU（有 z + BPT 分類基礎）
info = fits.open('/tmp/gal_info_dr7_v5_2.fit.gz')[1].data
line = fits.open('/tmp/gal_line_dr7_v5_2.fit.gz')[1].data

z = info['Z']
plate = info['PLATEID']
mjd = info['MJD']
fiber = info['FIBERID']

# 2. 揀低 z 樣本
sub = (z > 0.001) & (z < 0.1)
idx = np.where(sub)[0]
print(f"z<0.1: {len(idx)}")

# 3. 星形成選擇（BPT）— 用同之前一樣嘅邏輯
def select_sf(idx):
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
    y_lim = 0.61 / (x - 0.05) + 1.3
    y_lim = np.clip(y_lim, -5, 5)
    sf = (log_o3hb < y_lim)
    return good, sf

good, sf = select_sf(idx)
sf_idx = idx[good][sf]
print(f"Star-forming: {len(sf_idx)}")

# 4. 抽樣：每個 z bin 攞 200 個（總共 ~1000，大樣本）
rng = np.random.RandomState(42)
bins = [(0.001, 0.02), (0.02, 0.04), (0.04, 0.06), (0.06, 0.08), (0.08, 0.10)]
selected = []
for zl, zh in bins:
    inbin = (z[sf_idx] >= zl) & (z[sf_idx] < zh)
    cand = sf_idx[inbin]
    n_take = min(200, len(cand))
    pick = rng.choice(cand, n_take, replace=False) if n_take < len(cand) else cand
    selected.extend(pick.tolist())
    print(f"z={zl}-{zh}: {len(cand)} avail, take {len(pick)}")

selected = np.array(selected)
print(f"\nTotal selected: {len(selected)}")

# 5. 寫下載清單: plate/mjd/fiber/url
with open('/tmp/sdss_download_manifest.txt', 'w') as fh:
    for i in selected:
        p = int(plate[i])
        m = int(mjd[i])
        fb = int(fiber[i])
        url = f"https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/{p:04d}/spec-{p:04d}-{m}-{fb:04d}.fits"
        fh.write(f"{i}\t{p}\t{m}\t{fb}\t{z[i]:.5f}\t{url}\n")

print("Manifest: /tmp/sdss_download_manifest.txt")
# 顯示前5
with open('/tmp/sdss_download_manifest.txt') as fh:
    for _ in range(5):
        print(" ", fh.readline().strip())