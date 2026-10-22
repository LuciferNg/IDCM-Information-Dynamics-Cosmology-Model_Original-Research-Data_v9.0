#!/usr/bin/env python3
"""診斷 BOSS 偵測率低 — 檢查 z 分佈 + 波長覆蓋"""
import json
import numpy as np

with open('/home/wsl/IDCM/boss_fit.json') as fh:
    res = json.load(fh)

print(f"BOSS fit: {len(res)} spectra")
z = np.array([r['z'] for r in res])
print(f"z 範圍: {z.min():.2f} - {z.max():.2f}")
print(f"z 分佈: <0.5: {np.sum(z<0.5)}, 0.5-0.7: {np.sum((z>=0.5)&(z<0.7))}, "
      f"0.7-1.0: {np.sum((z>=0.7)&(z<1.0))}, >1.0: {np.sum(z>=1.0)}")

# 偵測率 by z bin
print("\n偵測率 by z:")
for zl, zh in [(0.3,0.5),(0.5,0.7),(0.7,1.0),(1.0,1.5),(1.5,2.0)]:
    n = sum(1 for r in res if zl<=r['z']<zh)
    hb = sum(1 for r in res if zl<=r['z']<zh and r['HB_4861_det'])
    o3 = sum(1 for r in res if zl<=r['z']<zh and r['O3_5007_det'])
    ha = sum(1 for r in res if zl<=r['z']<zh and r['HA_6563_det'])
    print(f"  z={zl}-{zh}: n={n}, Hβ={hb} ({100*hb/max(n,1):.0f}%), O3={o3} ({100*o3/max(n,1):.0f}%), Hα={ha} ({100*ha/max(n,1):.0f}%)")

# Hα 波長檢查: z=0.7 時 Hα = 6563*(1.7) = 11157Å > 10400Å (BOSS 上限)
print(f"\nBOSS 光譜範圍: 3600-10400 Å")
for zq in [0.3, 0.5, 0.7, 1.0]:
    ha_obs = 6563*(1+zq)
    hb_obs = 4861*(1+zq)
    o3_obs = 5007*(1+zq)
    print(f"  z={zq}: Hα={ha_obs:.0f}Å, Hβ={hb_obs:.0f}Å, O3={o3_obs:.0f}Å")