#!/usr/bin/env python3
"""
JADES z>5 分析：線比率 [OIII]/Hβ、[OIII]/[OII] — 唔需要連續譜/質量
比較 JADES 高 z 同 SDSS 低 z 嘅電離狀態
"""
import numpy as np
from astropy.io import fits

p = fits.open('/tmp/jades_prism_line.fits')[1].data

z = p['z_Spec']
hb = p['HB_4861_flux']
hb_err = p['HB_4861_err']
o3 = p['O3_5007_flux']
o3_err = p['O3_5007_err']
o2 = p['O2_3727_flux']
o2_err = p['O2_3727_err']
ha = p['HA_6563_flux']
ha_err = p['HA_6563_err']

print("=== JADES 高 z 電離狀態（原始數據）===")
print(f"總樣本: {len(p)}")

# Good detections
good = (z > 0) & (hb > 0) & (hb_err > 0) & (o3 > 0) & (o3_err > 0)
print(f"Hβ+[OIII] 偵測: {np.sum(good)}")

# O3/Hβ ratio by z bin (excitation indicator, metallicity proxy)
print("\n[OIII]/Hβ 比率（越高 = 越低金屬量/越高電離）:")
print(f"{'z bin':>10s} {'n':>5s} {'O3/Hb med':>10s} {'O3/Hb P25-P75':>15s}")
for z_lo, z_hi in [(0,2),(2,4),(4,5),(5,6),(6,8),(8,12)]:
    sel = good & (z>=z_lo) & (z<z_hi)
    if np.sum(sel) > 5:
        r = o3[sel]/hb[sel]
        print(f"z={z_lo}-{z_hi}  {np.sum(sel):5d} {np.median(r):10.2f} {np.percentile(r,25):7.2f}-{np.percentile(r,75):.2f}")

# [OIII]/[OII] ratio (O32) - ionization parameter
good2 = good & (o2 > 0) & (o2_err > 0)
print(f"\n[OIII]/[OII] (O32) 比率（更高 = 更高電離參數）:")
print(f"{'z bin':>10s} {'n':>5s} {'O32 med':>8s}")
for z_lo, z_hi in [(0,2),(2,4),(4,5),(5,6),(6,8),(8,12)]:
    sel = good2 & (z>=z_lo) & (z<z_hi)
    if np.sum(sel) > 5:
        r = o3[sel]/o2[sel]
        print(f"z={z_lo}-{z_hi}  {np.sum(sel):5d} {np.median(r):8.2f}")

# Hα detection
good3 = good & (ha > 0) & (ha_err > 0)
print(f"\nHα 偵測: {np.sum(good3)}")

# Hβ flux vs z (raw)
print(f"\nHβ 流量分布（x1e-20 erg/s/cm2）:")
for z_lo, z_hi in [(0,2),(2,4),(4,5),(5,6),(6,8),(8,12)]:
    sel = good & (z>=z_lo) & (z<z_hi)
    if np.sum(sel) > 5:
        print(f"z={z_lo}-{z_hi}: n={np.sum(sel):4d}, med={np.median(hb[sel]):.2f}, 25th={np.percentile(hb[sel],25):.2f}, 75th={np.percentile(hb[sel],75):.2f}")

# Balmer decrement (Hα/Hβ) - dust indicator
print(f"\nBalmer decrement Hα/Hβ (2.86 = 無塵):")
for z_lo, z_hi in [(0,2),(2,4),(4,5),(5,6),(6,8)]:
    sel = good3 & (z>=z_lo) & (z<z_hi)
    if np.sum(sel) > 5:
        r = ha[sel]/hb[sel]
        r = r[np.isfinite(r) & (r>0) & (r<10)]
        print(f"z={z_lo}-{z_hi}: n={len(r):4d}, med={np.median(r):.2f}")