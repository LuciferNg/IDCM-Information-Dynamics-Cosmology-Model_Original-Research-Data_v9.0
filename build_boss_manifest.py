#!/usr/bin/env python3
"""
建立 BOSS 光譜下載 manifest：從 boss_galaxies.txt 抽樣
每個 z bin 攞一批（總共 ~3000），下載 spec 光譜填 gap
BOSS 光譜路徑: data.sdss.org/sas/dr18/spectro/sdss/redux/103/spectra/{plate}/spec-{plate}-{mjd}-{fiber}.fits
（BOSS run2d 係 103，唔係 26）
"""
import numpy as np

# 讀 BOSS galaxy 清單
rows = []
with open('/tmp/boss_galaxies.txt') as fh:
    for line in fh:
        line = line.strip()
        if line and not line.startswith('plate') and not line.startswith('#'):
            parts = line.split(',')
            if len(parts) >= 4:
                rows.append((int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3])))

print(f"BOSS galaxies: {len(rows)}")

# 抽樣：每 z bin 攞 ~400
rng = np.random.RandomState(7)
bins = [(0.3,0.4),(0.4,0.5),(0.5,0.6),(0.6,0.7),(0.7,0.8),(0.8,0.9),
        (0.9,1.0),(1.0,1.2),(1.2,1.5),(1.5,2.0)]
selected = []
for zl, zh in bins:
    inbin = [r for r in rows if zl <= r[3] < zh]
    n_take = min(400, len(inbin))
    pick = rng.choice(len(inbin), n_take, replace=False) if n_take < len(inbin) else np.arange(len(inbin))
    for i in pick:
        selected.append(inbin[i])
    print(f"z={zl}-{zh}: {len(inbin)} avail, take {len(pick)}")

print(f"\nTotal selected: {len(selected)}")

# 寫 manifest: plate mjd fiber z url
with open('/tmp/boss_download_manifest.txt', 'w') as fh:
    for plate, mjd, fiber, z in selected:
        # BOSS 用 redux/103
        url = f"https://data.sdss.org/sas/dr18/spectro/sdss/redux/103/spectra/{plate}/spec-{plate}-{mjd}-{fiber:04d}.fits"
        fh.write(f"{plate}\t{mjd}\t{fiber}\t{z:.4f}\t{url}\n")

print("Manifest: /tmp/boss_download_manifest.txt")
with open('/tmp/boss_download_manifest.txt') as fh:
    for _ in range(3):
        print(" ", fh.readline().strip())