#!/usr/bin/env python3
"""
完整對比：獨立擬合 vs JADES catalog
驗證目錄嘅擬合值有冇問題，同埋量化「無污染」線比率 vs「目錄」線比率嘅差異
"""
import json, os
import numpy as np
from astropy.io import fits

# 1. 讀獨立 fit 結果
with open('/home/wsl/IDCM/jades_fit_v2.json') as fh:
    fits_res = json.load(fh)

# 2. 讀 catalog（有目錄擬合嘅 flux）
el = fits.open('/tmp/jades_prism_line.fits')[1].data
z_cat = el['z_Spec']
hb_cat = el['HB_4861_flux']
o3_cat = el['O3_5007_flux']
ha_cat = el['HA_6563_flux']
o2_cat = el['O2_3727_flux']
nspec = el['NIRSpec_ID']
tier = el['TIER']

# 3. Match by filename -> catalog
# manifest: filename -> (idx, z, hb)
manifest = {}
with open('/tmp/jades_download_manifest.txt') as fh:
    for line in fh:
        p = line.strip().split('\t')
        if len(p) == 4:
            manifest[os.path.basename(p[3])] = int(p[0])  # catalog index

print(f"Independent fits: {len(fits_res)}")
print(f"Catalog entries: {len(el)}")

# 4. 對比 Hβ flux
matched = 0
hb_ind, hb_catv = [], []
o3_ind, o3_catv = [], []
for r in fits_res:
    fname = r['path']
    if fname in manifest:
        ci = manifest[fname]
        if r['HB_4861_det'] and hb_cat[ci] > 0:
            hb_ind.append(r['HB_4861_flux'])
            hb_catv.append(hb_cat[ci])
        if r['O3_5007_det'] and o3_cat[ci] > 0:
            o3_ind.append(r['O3_5007_flux'])
            o3_catv.append(o3_cat[ci])

print(f"\n=== Hβ flux 對比（獨立 vs catalog）===")
print(f"Matched: {len(hb_ind)}")
if hb_ind:
    hb_ind = np.array(hb_ind)
    hb_catv = np.array(hb_catv) * 1e-20  # catalog x1e-20 -> erg/s/cm2
    ratio = hb_ind / hb_catv
    print(f"獨立/catalog 比率: med={np.median(ratio):.2f}, mean={np.mean(ratio):.2f}")
    print(f"  P25={np.percentile(ratio,25):.2f}, P75={np.percentile(ratio,75):.2f}")
    print(f"  中位數差異: {100*(np.median(ratio)-1):+.1f}%")

print(f"\n=== [OIII] flux 對比 ===")
print(f"Matched: {len(o3_ind)}")
if o3_ind:
    o3_ind = np.array(o3_ind)
    o3_catv = np.array(o3_catv) * 1e-20
    ratio = o3_ind / o3_catv
    print(f"獨立/catalog 比率: med={np.median(ratio):.2f}, mean={np.mean(ratio):.2f}")
    print(f"  中位數差異: {100*(np.median(ratio)-1):+.1f}%")

# 5. 線比率對比（關鍵！）
print(f"\n=== 線比率對比：目錄 vs 獨立擬合 ===")

# catalog O3/Hb
cat_ratios = []
for i in range(len(el)):
    if hb_cat[i] > 0 and o3_cat[i] > 0:
        cat_ratios.append(o3_cat[i] / hb_cat[i])

# independent O3/Hb（同一批星系）
ind_ratios = []
for r in fits_res:
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0:
        ind_ratios.append(r['O3_5007_flux'] / r['HB_4861_flux'])

if cat_ratios:
    print(f"Catalog [OIII]/Hβ: n={len(cat_ratios)}, med={np.median(cat_ratios):.2f}, "
          f"P25={np.percentile(cat_ratios,25):.2f}, P75={np.percentile(cat_ratios,75):.2f}")
if ind_ratios:
    print(f"獨立 [OIII]/Hβ:   n={len(ind_ratios)}, med={np.median(ind_ratios):.2f}, "
          f"P25={np.percentile(ind_ratios,25):.2f}, P75={np.percentile(ind_ratios,75):.2f}")

# 6. 逐對比（同一星系）
print(f"\n=== 逐星系對比（同一批樣本）===")
pair_ratios = []
pair_cat = []
for r in fits_res:
    fname = r['path']
    if fname in manifest:
        ci = manifest[fname]
        if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0 \
           and o3_cat[ci] > 0 and hb_cat[ci] > 0:
            pair_ratios.append(r['O3_5007_flux'] / r['HB_4861_flux'])
            pair_cat.append(o3_cat[ci] / hb_cat[ci])

if pair_ratios:
    pair_ratios = np.array(pair_ratios)
    pair_cat = np.array(pair_cat)
    diff = np.log10(pair_ratios) - np.log10(pair_cat)
    print(f"Matched pairs: {len(pair_ratios)}")
    print(f"log10 差異 (獨立-catalog): med={np.median(diff):+.3f}, std={np.std(diff):.3f}")
    print(f"  即平均差異: {100*(10**np.median(diff)-1):+.1f}% ({10**np.median(diff):.2f}x)")
    print(f"  有 {np.sum(np.abs(diff)>0.3)}/{len(diff)} 對差異 >2x (0.3 dex)")