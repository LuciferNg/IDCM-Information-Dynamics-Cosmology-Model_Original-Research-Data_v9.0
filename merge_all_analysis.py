#!/usr/bin/env python3
"""
最終合併分析：SDSS + BOSS + JADES — 完整 [OIII]/Hβ vs z（結構座標 ℓ）
用 BOSS 填 z=0.3-1.5 gap，睇 V 形係咪真
"""
import json
import numpy as np
from scipy import stats

def load(path):
    with open(path) as fh:
        return json.load(fh)

def o3hb_vals(res, zl, zh):
    vals = []
    for r in res:
        if zl <= r['z'] < zh and r['O3_5007_det'] and r['HB_4861_det'] \
           and r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0:
            vals.append(r['O3_5007_flux']/r['HB_4861_flux'])
    return np.array(vals)

def l_of_z(z):
    return np.log(1+z)/np.log(4)

# 讀所有樣本
sdss = load('/home/wsl/IDCM/sdss_large_fit.json')
gap = load('/home/wsl/IDCM/jades_gap_fit.json')
jades = load('/home/wsl/IDCM/jades_fit_v2.json')

# BOSS 可能未完成 — 檢查
import os
boss_path = '/home/wsl/IDCM/boss_fit.json'
boss = load(boss_path) if os.path.exists(boss_path) else []
print(f"SDSS: {len(sdss)}, JADES-gap: {len(gap)}, JADES: {len(jades)}, BOSS: {len(boss)}")

print("\n" + "="*80)
print("[OIII]/Hβ vs z — 完整樣本（含 BOSS gap）")
print("="*80)
print(f"{'z bin':>14s} {'ℓ(中點)':>8s} {'n':>5s} {'med':>6s} {'P25':>6s} {'P75':>6s} {'樣本':>8s}")

all_bins = [(0.001,0.02),(0.02,0.03),(0.03,0.04),(0.04,0.05),(0.05,0.06),
            (0.06,0.07),(0.07,0.08),(0.08,0.10),
            (0.3,0.4),(0.4,0.5),(0.5,0.6),(0.6,0.7),(0.7,0.8),(0.8,0.9),(0.9,1.0),
            (1.0,1.2),(1.2,1.5),
            (2,3),(3,4),(4,5),(5,6),(6,8)]

for zl, zh in all_bins:
    vals = []
    src = ''
    if zh <= 0.15:
        vals = o3hb_vals(sdss, zl, zh); src = 'SDSS'
    elif 0.3 <= zl and zh <= 1.5:
        vals = o3hb_vals(boss, zl, zh); src = 'BOSS'
        if len(vals) < 5:
            vals = o3hb_vals(gap, zl, zh); src += '/gap'
    elif zh > 2:
        vals = o3hb_vals(jades, zl, zh); src = 'JADES'
    if len(vals) >= 5:
        zm = (zl+zh)/2
        print(f"z={zl}-{zh}   {l_of_z(zm):8.3f} {len(vals):5d} {np.median(vals):6.2f} "
              f"{np.percentile(vals,25):6.2f} {np.percentile(vals,75):6.2f} {src:>8s}")

# 統計：BOSS 區間有冇趨勢？
if len(boss) > 50:
    print("\n" + "="*80)
    print("BOSS 區間 (z=0.3-1.5) 內部趨勢")
    print("="*80)
    b_all = []
    for r in boss:
        if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
            b_all.append((l_of_z(r['z']), r['O3_5007_flux']/r['HB_4861_flux']))
    if len(b_all) > 50:
        b_all = np.array(b_all)
        rho, p = stats.spearmanr(b_all[:,0], b_all[:,1])
        print(f"BOSS (ℓ=0.38-0.83): n={len(b_all)}, rho={rho:.3f}, p={p:.2e} → {'上升' if rho>0 else '下降' if rho<0 else 'flat'}")
        # 分段
        for zl, zh in [(0.3,0.5),(0.5,0.7),(0.7,0.9),(0.9,1.1),(1.1,1.5)]:
            vals = o3hb_vals(boss, zl, zh)
            if len(vals) >= 10:
                print(f"  z={zl}-{zh}: n={len(vals)}, med={np.median(vals):.2f}")