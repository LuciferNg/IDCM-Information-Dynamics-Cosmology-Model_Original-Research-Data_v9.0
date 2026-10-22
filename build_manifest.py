#!/usr/bin/env python3
"""建立 NIRSpec_ID → x1d URL 對應表，揀出有 Hβ 偵測嘅高 z 星系"""
import re
import numpy as np
from astropy.io import fits

# 1. 讀 emission line catalog（有 z + Hβ 偵測）
el = fits.open('/tmp/jades_prism_line.fits')[1].data
z = el['z_Spec']
hb = el['HB_4861_flux']
hb_err = el['HB_4861_err']
nspec_id = el['NIRSpec_ID']
tier = el['TIER']

# 有 Hβ 偵測 (S/N>3) 且 z>2
good = (z > 2) & (hb > 0) & (hb_err > 0) & ((hb/hb_err) > 3)
print(f"Emission catalog: {len(el)} total")
print(f"z>2 + Hβ S/N>3: {np.sum(good)}")

# 2. 讀 x1d URL 列表
with open('/tmp/jades_x1d_list.txt') as fh:
    x1d_urls = [l.strip() for l in fh if l.strip()]

# 3. 建立對應：URL 含 NIRSpec ID（例如 -00030599_）
url_by_id = {}  # (tier_str, ID) -> url
for u in x1d_urls:
    m = re.search(r'goods-s-(\w+)-(\d+)_([a-z0-9-]+)_v\d+\.\d+_x1d\.fits', u)
    if m:
        field, sid, grating = m.groups()
        key = ('goods-s-' + field, int(sid))  # URL field 冇 'goods-s-' 前綴
        url_by_id.setdefault(key, []).append(u)

print(f"x1d URLs with IDs: {len(url_by_id)} unique")

# 4. Match: emission catalog 嘅 NIRSpec_ID + TIER → field
# TIER values: 'goods-s-mediumhst', 'goods-s-mediumjwst' 等
tier_map = {
    'goods-s-mediumhst': 'goods-s-mediumhst',
    'goods-s-mediumjwst': 'goods-s-mediumjwst',
    'goods-s-mediumjwst1180': 'goods-s-mediumjwst1180',
    'goods-s-ultradeep': 'goods-s-ultradeep',
}

matched = 0
matched_ids = []
for i in np.where(good)[0]:
    key = (str(tier[i]), int(nspec_id[i]))
    if key in url_by_id:
        matched += 1
        matched_ids.append(i)
    else:
        # 試 field 唔 match 嘅情況
        for fld in tier_map.values():
            if (fld, int(nspec_id[i])) in url_by_id:
                matched += 1
                matched_ids.append(i)
                break

print(f"Matched to x1d: {matched} / {np.sum(good)}")

# 5. 寫下載清單（揀 clear-prism 為主，因為佢覆蓋最廣）
download_list = []
matched_set = set(matched_ids)
for i in sorted(matched_set):
    key = (str(tier[i]), int(nspec_id[i]))
    urls = url_by_id.get(key, [])
    # 優先 clear-prism
    prism = [u for u in urls if 'clear-prism' in u]
    if prism:
        download_list.append((i, prism[0]))
    elif urls:
        download_list.append((i, urls[0]))

print(f"Download list (prism preferred): {len(download_list)}")

# 6. 存清單
with open('/tmp/jades_download_manifest.txt', 'w') as fh:
    for i, url in download_list:
        fh.write(f"{i}\t{z[i]:.4f}\t{hb[i]:.2f}\t{url}\n")

# 統計
z_list = [z[i] for i, _ in download_list]
print(f"\n下載清單 z 分佈:")
for zl, zh in [(2,4),(4,5),(5,6),(6,8),(8,12)]:
    n = sum(1 for zz in z_list if zl<=zz<zh)
    print(f"  z={zl}-{zh}: {n}")

print(f"\nManifest saved: /tmp/jades_download_manifest.txt")
print(f"前 5 個:")
for i, url in download_list[:5]:
    print(f"  z={z[i]:.2f} Hβ={hb[i]:.1f} {url.split('/')[-1]}")