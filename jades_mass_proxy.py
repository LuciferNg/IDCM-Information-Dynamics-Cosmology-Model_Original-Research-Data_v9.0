#!/usr/bin/env python3
"""JADES 質量 proxy 分析：用 photometry flux 做 mass proxy"""
import json
import numpy as np
from astropy.io import fits

# 讀 photometry catalog（CIRC 或 KRON aperture）
photo = fits.open('/home/wsl/IDCM/data/catalogs/jades_photo.fits')
kron = photo['KRON'].data  # Kron aperture fluxes
photoz = photo['PHOTOZ'].data  # photo-z
flag = photo['FLAG'].data

# 讀 emission line catalog
el = fits.open('/tmp/jades_prism_line.fits')[1].data
z_spec = el['z_Spec']
nspec_id = el['NIRSpec_ID']

# 檢查 ID 有冇 overlap（photometry 用 ID，emission 用 NIRSpec_ID）
photo_id = kron['ID']
print(f"Photometry IDs: {len(photo_id)}, range {photo_id.min()}-{photo_id.max()}")
print(f"NIRSpec IDs: {len(nspec_id)}, range {nspec_id.min()}-{nspec_id.max()}")

# 找 overlap
overlap = np.intersect1d(photo_id, nspec_id)
print(f"Overlap: {len(overlap)}")

# 如果 overlap 存在，用 F277W 做 mass proxy
if len(overlap) > 0:
    # 建立對應
    id_to_idx = {photo_id[i]: i for i in range(len(photo_id))}
    # F277W 係 F277W 欄
    for r in ['F277W', 'F200W', 'F150W']:
        if r in kron.columns.names:
            print(f"  {r}_KRON available")
        if r in flag.columns.names:
            print(f"  {r}_FLAG available")

# 如果冇 direct ID match，嘗試用 RA/DEC cross-match
print("\nRA/DEC range:")
print(f"  kron: RA={kron['RA'].min():.4f}-{kron['RA'].max():.4f}, "
      f"DEC={kron['DEC'].min():.4f}-{kron['DEC'].max():.4f}")
print(f"  el:   RA={el['RA_TARG'][:10]}, DEC={el['Dec_TARG'][:10]}")