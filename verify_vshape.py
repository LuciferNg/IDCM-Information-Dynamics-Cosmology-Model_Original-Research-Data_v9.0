#!/usr/bin/env python3
"""
完整 V 形驗證：所有樣本合併（同一套獨立擬合方法）
SDSS 小樣本 (1000) + SDSS 大樣本 (5000) + JADES gap (688) + JADES 高z (463)
用 [OIII]/Hβ 同 Hα/[OIII] 兩個污染抗性比率
"""
import json
import numpy as np

def load(path):
    with open(path) as fh:
        return json.load(fh)

sdss1 = load('/home/wsl/IDCM/sdss_fit_results.json')
sdss2 = load('/home/wsl/IDCM/sdss_large_fit.json')
gap = load('/home/wsl/IDCM/jades_gap_fit.json')
jades = load('/home/wsl/IDCM/jades_fit_v2.json')

print(f"SDSS 小樣本: {len(sdss1)}")
print(f"SDSS 大樣本: {len(sdss2)}")
print(f"JADES gap: {len(gap)}")
print(f"JADES 高z: {len(jades)}")

def o3hb_vals(res, zl, zh):
    vals = []
    for r in res:
        if zl <= r['z'] < zh and r['O3_5007_det'] and r['HB_4861_det'] \
           and r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0:
            vals.append(r['O3_5007_flux']/r['HB_4861_flux'])
    return vals

def hao3_vals(res, zl, zh):
    vals = []
    for r in res:
        if zl <= r['z'] < zh and r['HA_6563_det'] and r['O3_5007_det'] \
           and r['HA_6563_flux'] > 0 and r['O3_5007_flux'] > 0:
            vals.append(r['HA_6563_flux']/r['O3_5007_flux'])
    return vals

def l_of_z(z):
    return np.log(1+z)/np.log(4)

print("\n" + "="*78)
print("[OIII]/Hβ vs z 完整趨勢（獨立擬合，無目錄污染）")
print("="*78)
print(f"{'z bin':>14s} {'ℓ(中點)':>8s} {'n':>5s} {'med':>6s} {'P25':>6s} {'P75':>6s} {'樣本':>8s}")

# SDSS bins (細 bin 睇 V 形)
for zl, zh in [(0.001,0.02),(0.02,0.03),(0.03,0.04),(0.04,0.05),(0.05,0.06),
               (0.06,0.07),(0.07,0.08),(0.08,0.09),(0.09,0.10)]:
    vals = o3hb_vals(sdss1, zl, zh) + o3hb_vals(sdss2, zl, zh)
    if len(vals) >= 5:
        zm = (zl+zh)/2
        print(f"z={zl:.3f}-{zh:.3f} {l_of_z(zm):8.3f} {len(vals):5d} {np.median(vals):6.2f} "
              f"{np.percentile(vals,25):6.2f} {np.percentile(vals,75):6.2f} {'SDSS':>8s}")

# JADES gap bins
for zl, zh in [(0.5,1.0),(1.0,1.5),(1.5,2.0),(2.0,2.5),(2.5,3.0)]:
    vals = o3hb_vals(gap, zl, zh)
    if len(vals) >= 3:
        zm = (zl+zh)/2
        print(f"z={zl}-{zh}   {l_of_z(zm):8.3f} {len(vals):5d} {np.median(vals):6.2f} "
              f"{np.percentile(vals,25):6.2f} {np.percentile(vals,75):6.2f} {'JADES-gap':>8s}")

# JADES high bins
for zl, zh in [(2,4),(4,5),(5,6),(6,8),(8,12)]:
    vals = o3hb_vals(jades, zl, zh)
    if len(vals) >= 3:
        zm = (zl+zh)/2
        print(f"z={zl}-{zh}   {l_of_z(zm):8.3f} {len(vals):5d} {np.median(vals):6.2f} "
              f"{np.percentile(vals,25):6.2f} {np.percentile(vals,75):6.2f} {'JADES':>8s}")

# Hα/[OIII] 做第二個無污染比率（gap 樣本 Hβ 少）
print("\n" + "="*78)
print("Hα/[OIII] vs z（第二個無污染比率，gap 樣本 Hβ 偵測少用呢個）")
print("="*78)
print(f"{'z bin':>14s} {'ℓ(中點)':>8s} {'n':>5s} {'med':>6s} {'P25':>6s} {'P75':>6s} {'樣本':>8s}")
all_res = [('SDSS', sdss1+sdss2), ('JADES-gap', gap), ('JADES', jades)]
for zl, zh in [(0.001,0.02),(0.02,0.05),(0.05,0.10),(0.5,1.0),(1.0,1.5),(1.5,2.0),
               (2.0,2.5),(2.5,3.0),(3,4),(4,5),(5,6),(6,8)]:
    for name, res in all_res:
        vals = hao3_vals(res, zl, zh)
        if len(vals) >= 5:
            zm = (zl+zh)/2
            print(f"z={zl}-{zh}   {l_of_z(zm):8.3f} {len(vals):5d} {np.median(vals):6.2f} "
                  f"{np.percentile(vals,25):6.2f} {np.percentile(vals,75):6.2f} {name:>8s}")
            break