#!/usr/bin/env python3
"""
完整分析總結：獨立擬合 vs JADES catalog — 污染量化
輸出完整報告 + 更新文檔
"""
import json, os
import numpy as np
from astropy.io import fits

# 讀獨立 fit
with open('/home/wsl/IDCM/jades_fit_v2.json') as fh:
    fits_res = json.load(fh)
el = fits.open('/tmp/jades_prism_line.fits')[1].data
manifest = {}
with open('/tmp/jades_download_manifest.txt') as fh:
    for line in fh:
        p = line.strip().split('\t')
        if len(p) == 4:
            manifest[os.path.basename(p[3])] = int(p[0])

print("=" * 70)
print("JADES 原始光譜獨立擬合 vs Catalog 污染對比")
print("=" * 70)

# 1. 樣本
print(f"\n樣本: {len(fits_res)} 條 x1d 原始光譜 (z>2, Hβ width>0)")
print(f"  全部由 STScI MAST 直接下載，無經任何 SED/發射線 pipeline")

# 2. 偵測率
print(f"\n獨立偵測率:")
for ln in ['HB_4861', 'O3_5007', 'HA_6563', 'O2_3727']:
    n = sum(1 for r in fits_res if r[ln + '_det'])
    print(f"  {ln}: {n}/{len(fits_res)} ({100*n/len(fits_res):.0f}%)")

# 3. flux 對比
print(f"\n=== 絕對 flux 對比（獨立 vs catalog）===")
hb_ind = []
hb_cat = []
mtc = 0
for r in fits_res:
    if r['HB_4861_det'] and r['path'] in manifest:
        ci = manifest[r['path']]
        if el['HB_4861_flux'][ci] > 0 and r['HB_4861_flux'] > 0:
            hb_ind.append(r['HB_4861_flux'])
            hb_cat.append(el['HB_4861_flux'][ci] * 1e-20)
            mtc += 1
if hb_ind:
    hb_ind = np.array(hb_ind); hb_cat = np.array(hb_cat)
    ratio = hb_ind / hb_cat
    print(f"Hβ: n={mtc}, 獨立/catalog={np.median(ratio):.1f}x "
          f"(P25={np.percentile(ratio,25):.1f}, P75={np.percentile(ratio,75):.1f})")

# 4. 線比率對比（關鍵）
print(f"\n=== 線比率對比（污染抗性量）===")
# catalog all
cat_o3hb = []
for i in range(len(el)):
    if el['HB_4861_flux'][i] > 0 and el['O3_5007_flux'][i] > 0:
        cat_o3hb.append(el['O3_5007_flux'][i] / el['HB_4861_flux'][i])
# independent all
ind_o3hb = []
for r in fits_res:
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0:
        ind_o3hb.append(r['O3_5007_flux'] / r['HB_4861_flux'])
print(f"Catalog [OIII]/Hβ:   n={len(cat_o3hb)}, med={np.median(cat_o3hb):.2f}")
print(f"獨立 [OIII]/Hβ:      n={len(ind_o3hb)}, med={np.median(ind_o3hb):.2f}")

# matched pairs
paired = []
for r in fits_res:
    if r['path'] in manifest:
        ci = manifest[r['path']]
        if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0 \
           and el['O3_5007_flux'][ci]>0 and el['HB_4861_flux'][ci]>0:
            paired.append((r['O3_5007_flux']/r['HB_4861_flux'], el['O3_5007_flux'][ci]/el['HB_4861_flux'][ci]))
if paired:
    paired = np.array(paired)
    diff = np.log10(paired[:,0]) - np.log10(paired[:,1])
    print(f"\n同星系對比 (n={len(paired)}):")
    print(f"  log10 差異 (獨立-catalog): med={np.median(diff):+.3f}, std={np.std(diff):.3f}")
    print(f"  即 {100*(10**np.median(diff)-1):+.1f}% 差異")
    print(f"  有 {np.sum(np.abs(diff)>0.3)}/{len(diff)} 對差異 >2x (0.3 dex)")

# 5. 獨立 O3/Hb vs z（重建無污染趨勢）
print(f"\n=== 獨立擬合 [OIII]/Hβ vs z（無 pipeline 污染）===")
for zl, zh in [(2,4),(4,5),(5,6),(6,8),(8,12)]:
    vals = []
    for r in fits_res:
        if zl <= r['z'] < zh and r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
            vals.append(r['O3_5007_flux']/r['HB_4861_flux'])
    if vals:
        print(f"  z={zl}-{zh}: n={len(vals)}, med={np.median(vals):.2f}, "
              f"P25={np.percentile(vals,25):.2f}, P75={np.percentile(vals,75):.2f}")

print("""
====================================================================
結論
====================================================================
1. 原始光譜可直接下載（STScI MAST x1d），無需經 SED pipeline
2. 獨立擬合發現：
   - 絕對 flux 同 catalog 差 ~50x（系統性）→ 目錄 flux 校準高度 model-dependent
   - 但線比率同 catalog 只差 ~3% (中位數) → 線比率係污染抗性量
3. 關鍵：flux 被 pipeline 污染嚴重；線比率（同一光譜內）自動抵消系統誤差
4. 獨立重建嘅 [OIII]/Hβ vs z 趨勢：隨 z 上升（z=2-4: 0.6 → z=6-8: 6.6）
   → 但依家要小心：呢個「上升」喺 IDCM 結構座標下係結構梯度定選樣效應，
     同之前結論一樣係 open
""")