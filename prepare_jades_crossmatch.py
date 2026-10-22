#!/usr/bin/env python3
"""
JADES 交叉比對：光度目錄（質量+連續譜）↔ 發射線目錄（EW）
做「SDSS z<0.1 vs JADES z>5」同質量 bin 嘅 EW(Hβ) 比較

光度目錄：hlsp_jades_jwst_nircam_goods-s-deep_photometry_v2.0_catalog.fits
  - CIRC extension: 圓孔測光 (F090W..F480M 24 bands) → 連續譜
  - PHOTOZ extension: EAZY photo-z
發射線目錄：hlsp_jades_jwst_nirspec_goods-s_prism-line-fluxes_v1.1_catalog.fits
  - z_Spec, HB_4861_flux, O3_5007_flux
  
方法：
  1. 用 NIRCam_ID 交叉比對（發射線目錄有 NIRCam_ID，光度目錄有 ID）
  2. Hβ rest 4861 Å → observed λ = 4861(1+z) → 搵最近 filter 嘅連續譜
  3. EW(Hβ) = F_line / F_cont
  4. 質量：光度目錄冇直接質量 → 用 F444W 光度做 sSFR/質量 proxy 或註明限制
"""
import numpy as np
from astropy.io import fits

print("=" * 70)
print("JADES z>5 分析：光度目錄 ↔ 發射線目錄")
print("=" * 70)

# ========== Load catalogs ==========
print("\nLoading emission-line catalog...")
el = fits.open('/tmp/jades_prism_line.fits')[1].data
print(f"  {len(el)} sources")

print("Loading photometry catalog...")
photo = fits.open('/tmp/jades_photo.fits')
print(f"  HDUs: {[h.name for h in photo]}")

# Find the photometry HDU (CIRC or similar)
for h in photo:
    if h.name in ['CIRC', 'FLUX', 'PHOTOMETRY', '']:
        print(f"  HDU {h.name}: cols={list(h.columns.names)[:20]}... nrows={len(h.data)}")
        break

# Build ID map from photometry
print("\nBuilding NIRCam ID map...")
photo_main = None
for h in photo:
    if h.data is not None and 'ID' in h.columns.names:
        photo_main = h
        break
if photo_main is not None:
    ids = photo_main.data['ID']
    print(f"  Photometry IDs: {len(ids)}")
    # Check for flux columns
    cols = photo_main.columns.names
    flux_cols = [c for c in cols if 'FLUX' in c.upper() or 'MAG' in c.upper()]
    print(f"  Flux/mag columns ({len(flux_cols)}): {flux_cols[:15]}")