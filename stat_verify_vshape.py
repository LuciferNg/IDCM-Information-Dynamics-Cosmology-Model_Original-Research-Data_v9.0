#!/usr/bin/env python3
"""
統計驗證 V 形：
1. SDSS 內部下降（z=0.01→0.09）係咪統計顯著？
2. JADES 上升（z=3→7）係咪統計顯著？
3. 合併後 V 形（下降→上升）測試
4. 對比：單調趨勢 vs V 形 — 用結構座標 ℓ
"""
import json
import numpy as np
from scipy import stats

def load(path):
    with open(path) as fh:
        return json.load(fh)

sdss2 = load('/home/wsl/IDCM/sdss_large_fit.json')
gap = load('/home/wsl/IDCM/jades_gap_fit.json')
jades = load('/home/wsl/IDCM/jades_fit_v2.json')

def o3hb_vals(res, zl, zh):
    vals = []
    for r in res:
        if zl <= r['z'] < zh and r['O3_5007_det'] and r['HB_4861_det'] \
           and r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0:
            vals.append(r['O3_5007_flux']/r['HB_4861_flux'])
    return np.array(vals)

print("="*70)
print("統計驗證：V 形係咪真實？")
print("="*70)

# 1. SDSS 下降支
low = o3hb_vals(sdss2, 0.001, 0.03)
high = o3hb_vals(sdss2, 0.07, 0.10)
print(f"\n1. SDSS 下降支（z=0.001-0.03 vs z=0.07-0.10）:")
print(f"   低z: n={len(low)}, med={np.median(low):.2f}")
print(f"   高z: n={len(high)}, med={np.median(high):.2f}")
if len(low) > 10 and len(high) > 10:
    u, p = stats.mannwhitneyu(low, high, alternative='greater')
    print(f"   Mann-Whitney U: p={p:.2e} (低z > 高z)")

# 2. JADES 上升支
jlow = o3hb_vals(jades, 2, 4)
jhigh = o3hb_vals(jades, 5, 8)
print(f"\n2. JADES 上升支（z=2-4 vs z=5-8）:")
print(f"   低z: n={len(jlow)}, med={np.median(jlow):.2f}")
print(f"   高z: n={len(jhigh)}, med={np.median(jhigh):.2f}")
if len(jlow) > 5 and len(jhigh) > 5:
    u, p = stats.mannwhitneyu(jhigh, jlow, alternative='greater')
    print(f"   Mann-Whitney U: p={p:.2e} (高z > 低z)")

# 3. V 形：SDSS 高z vs JADES 低z（gap 底部）
s_high = o3hb_vals(sdss2, 0.07, 0.10)
g_low = o3hb_vals(gap, 0.5, 1.5)
print(f"\n3. V 形底部（SDSS z=0.07-0.10 vs JADES z=0.5-1.5 gap）:")
print(f"   SDSS高z: n={len(s_high)}, med={np.median(s_high):.2f}")
print(f"   gap低z: n={len(g_low)}, med={np.median(g_low):.2f}")
if len(s_high) > 5 and len(g_low) > 5:
    u, p = stats.mannwhitneyu(s_high, g_low)
    print(f"   Mann-Whitney U: p={p:.2f}")

# 4. 趨勢檢驗：喺結構座標 ℓ 上
print(f"\n4. 結構座標 ℓ 上嘅趨勢（Spearman 相關）:")
def l_of_z(z): return np.log(1+z)/np.log(4)

# SDSS 下降
sdss_all = []
for r in sdss2:
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
        sdss_all.append((l_of_z(r['z']), r['O3_5007_flux']/r['HB_4861_flux']))
sdss_all = np.array(sdss_all)
if len(sdss_all) > 50:
    rho, p = stats.spearmanr(sdss_all[:,0], sdss_all[:,1])
    print(f"   SDSS (ℓ=0.001-0.065): rho={rho:.3f}, p={p:.2e} → {'下降' if rho<0 else '上升'}")

# JADES 上升
jades_all = []
for r in jades:
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
        jades_all.append((l_of_z(r['z']), r['O3_5007_flux']/r['HB_4861_flux']))
jades_all = np.array(jades_all)
if len(jades_all) > 50:
    rho, p = stats.spearmanr(jades_all[:,0], jades_all[:,1])
    print(f"   JADES (ℓ=1.0-1.73): rho={rho:.3f}, p={p:.2e} → {'下降' if rho<0 else '上升'}")

# 5. 合併後全樣本 — 檢查 U 形（分段）
print(f"\n5. 全樣本分佈（ℓ bins）:")
all_pairs = []
for res in [sdss2, gap, jades]:
    for r in res:
        if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
            all_pairs.append((l_of_z(r['z']), r['O3_5007_flux']/r['HB_4861_flux']))
all_pairs = np.array(all_pairs)
for zl, zh in [(0.0,0.02),(0.02,0.04),(0.04,0.065),(0.4,0.7),(0.9,1.1),(1.2,1.4),(1.4,1.6)]:
    m = (all_pairs[:,0] >= zl) & (all_pairs[:,0] < zh)
    if np.sum(m) >= 5:
        print(f"   ℓ={zl}-{zh}: n={np.sum(m)}, med={np.median(all_pairs[m,1]):.2f}")