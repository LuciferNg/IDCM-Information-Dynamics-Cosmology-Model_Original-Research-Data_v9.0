#!/usr/bin/env python3
"""
完整對比分析：等 jades_photo.fits + specObj_dr17.fits 落完後跑
1. JADES 質量控制：用 photometry 目錄嘅質量 -> [OIII]/Hβ 控制
2. SDSS/BOSS 目錄完整性：用 specObj 驗證 BOSS 樣本
3. 最終 V 形驗證（含質量控制）
"""
import json, os
import numpy as np
from astropy.io import fits

jades_photo_path = '/home/wsl/IDCM/data/catalogs/jades_photo.fits'
specobj_path = '/home/wsl/IDCM/data/catalogs/specObj_dr17.fits'

print("=" * 70)
print("等待檔案下載...")
for p, name in [(jades_photo_path, 'JADES photometry'), (specobj_path, 'specObj')]:
    if not os.path.exists(p):
        print(f"  ❌ {name} 未下載")
    else:
        sz = os.path.getsize(p)
        print(f"  ✅ {name}: {sz/1e6:.0f} MB")

# 如果 JADES photo 已落
if os.path.exists(jades_photo_path) and os.path.getsize(jades_photo_path) > 6e8:
    print("\n" + "=" * 70)
    print("1. JADES 質量控制分析")
    print("=" * 70)
    photo = fits.open(jades_photo_path)
    print("HDUs:", [h.name for h in photo])
    d = photo[1].data
    print("cols:", [c for c in d.columns.names if 'MASS' in c.upper() or 'MSTAR' in c.upper() or 'IMF' in c.upper()][:10])
    print("all cols:", list(d.columns.names)[:30])

# 如果 specObj 已落
if os.path.exists(specobj_path) and os.path.getsize(specobj_path) > 6e9:
    print("\n" + "=" * 70)
    print("2. SDSS/BOSS specObj 完整性檢查")
    print("=" * 70)
    f = fits.open(specobj_path)
    d = f[1].data
    print(f"specObj: {len(d)} entries")
    print(f"z 範圍: {d['Z'].min():.2f} - {d['Z'].max():.2f}")
    # 檢查 BOSS 覆蓋
    import collections
    surveys = collections.Counter(d['SURVEY'])
    print(f"surveys: {dict(surveys.most_common(5))}")
    classes = collections.Counter(d['CLASS'])
    print(f"classes: {dict(classes.most_common(5))}")