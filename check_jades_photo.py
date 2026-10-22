#!/usr/bin/env python3
"""
JADES 質量控制分析：用 photometry catalog 嘅質量做 [OIII]/Hβ 控制
確認 JADES 上升支係咪質量效應
"""
import json, os
import numpy as np
from astropy.io import fits

# 1. 讀 JADES photometry catalog
photo_path = '/home/wsl/IDCM/data/catalogs/jades_photo.fits'
if not os.path.exists(photo_path):
    print("jades_photo.fits 未找到")
    exit(1)

photo = fits.open(photo_path)
print(f"HDUs: {[h.name for h in photo]}")

# 試唔同 extension
for hdu in photo:
    if hdu.data is not None and hasattr(hdu, 'columns') and hdu.columns is not None:
        d = hdu.data
        cols = list(d.columns.names)
        print(f"\nHDU {hdu.name}: {len(d)} rows, cols: {cols[:10]}")
        # 搵質量欄
        mass_cols = [c for c in cols if 'MASS' in c.upper() or 'MSTAR' in c.upper() or 'IMF' in c.upper() or 'STELLAR' in c.upper()]
        print(f"  mass cols: {mass_cols}")
        if mass_cols:
            for mc in mass_cols[:3]:
                print(f"  {mc}: {d[mc][:5]}")
        # 搵 redshift 欄
        z_cols = [c for c in cols if 'Z' in c.upper() and 'PHOTO' in c.upper()]
        print(f"  z cols: {z_cols}")
        # 睇 sample NIRSpec_ID
        id_cols = [c for c in cols if 'ID' in c.upper() or 'NIRSpec' in c.upper()]
        print(f"  ID cols: {id_cols}")