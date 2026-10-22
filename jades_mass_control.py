#!/usr/bin/env python3
"""JADES 質量控制：用 F277W 光度做質量 proxy，睇 [OIII]/Hβ vs z 仲升唔升"""
import json, os
import numpy as np
from astropy.io import fits
from scipy import stats

# 讀 photometry
kron = fits.open('/home/wsl/IDCM/data/catalogs/jades_photo.fits')['KRON'].data
# 讀 emission line catalog
el = fits.open('/tmp/jades_prism_line.fits')[1].data
# 讀獨立 fit
with open('/home/wsl/IDCM/jades_fit_v2.json') as fh:
    jades = json.load(fh)

# 建立對應
pid = kron['ID']
nid = el['NIRSpec_ID']
id_map = {}
for i in range(len(nid)):
    m = np.where(pid == nid[i])[0]
    if len(m) > 0:
        id_map[i] = m[0]

print(f"Matched: {len(id_map)} emission lines -> photometry")

# 用 F277W_KRON flux 做質量 proxy（rest-frame optical 喺高 z）
flux_col = 'F277W_KRON'
if flux_col not in kron.columns.names:
    print(f"{flux_col} not found, trying alternatives")
    for c in kron.columns.names:
        if 'F277W' in c:
            flux_col = c
            break
print(f"Using {flux_col} as mass proxy")

# 加質量 proxy 到 fit 結果
for r in jades:
    # 搵對應 emission line catalog index
    pass  # 用檔名對應

# 更直接：用 emission catalog 嘅 photometry index
# 按質量分 bin，睇 [OIII]/Hβ 趨勢
k277 = kron[flux_col]
k277[k277 <= 0] = np.nan
mass_proxy = np.log10(k277)  # log flux

# 對於有 match 嘅 emission line
for zl, zh in [(2,4),(4,5),(5,6),(6,8)]:
    # 揀 z bin 內有 match 嘅
    idx = [i for i in id_map if zl <= el['z_Spec'][i] < zh]
    if len(idx) < 5:
        continue
    # 低質量 vs 高質量
    mp = np.array([mass_proxy[id_map[i]] for i in idx])
    med_mp = np.median(mp)
    low_m = [i for i in idx if mass_proxy[id_map[i]] < med_mp]
    high_m = [i for i in idx if mass_proxy[id_map[i]] >= med_mp]
    print(f"  z={zl}-{zh}: n={len(idx)}, med_flux={np.nanmedian(mp):.2f}")

# 完整分析：match 到我嘅獨立 fit
# 用 manifest 對應檔名到 emission catalog index
manifest = {}
with open('/tmp/jades_download_manifest.txt') as fh:
    for line in fh:
        p = line.strip().split('\t')
        if len(p) == 4:
            manifest[os.path.basename(p[3])] = int(p[0])

import os
for r in jades:
    fname = r['path']
    if fname in manifest:
        ci = manifest[fname]
        if ci in id_map:
            pi = id_map[ci]
            r['mass_proxy'] = mass_proxy[pi]
        else:
            r['mass_proxy'] = np.nan
    else:
        r['mass_proxy'] = np.nan

# 按質量控制後睇 [OIII]/Hβ vs z
print("\n" + "="*70)
print("固定質量 proxy 後，[OIII]/Hβ vs z")
print("="*70)

def o3hb(r):
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
        return r['O3_5007_flux']/r['HB_4861_flux']
    return None

# 按質量三分位 divide
mp_vals = np.array([r['mass_proxy'] for r in jades if not np.isnan(r.get('mass_proxy', np.nan))])
if len(mp_vals) > 10:
    q1, q2 = np.percentile(mp_vals, [33, 67])
    print(f"質量 proxy 三分位: {np.nanmin(mp_vals):.2f} / {q1:.2f} / {q2:.2f} / {np.nanmax(mp_vals):.2f}")
    
    for mlo, mhi, mname in [(-np.inf, q1, 'low'), (q1, q2, 'mid'), (q2, np.inf, 'high')]:
        print(f"\n質量 {mname}:")
        for zl, zh in [(2,4),(4,5),(5,6),(6,8)]:
            vals = [o3hb(r) for r in jades if mlo <= r.get('mass_proxy', np.nan) < mhi 
                    and zl <= r['z'] < zh]
            vals = [v for v in vals if v is not None]
            if len(vals) >= 5:
                print(f"  z={zl}-{zh}: n={len(vals)}, med={np.median(vals):.2f}")