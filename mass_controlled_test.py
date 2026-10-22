#!/usr/bin/env python3
"""
控制變數測試：SDSS 下降支係咪質量效應？
固定質量 bin 之後，[OIII]/Hβ vs z 仲跌唔跌？
用 newmasses_dr4（ASCII: plate mjd fiber MagR ... rml50 ...）
rml50 = 第十欄 (index 9) 係 rml50 (Kauffmann+03 mass)
"""
import gzip, json
import numpy as np
from scipy import stats

# 1. 讀質量表
mass_map = {}
with gzip.open('/tmp/newmasses_dr4.gz', 'rt') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 10:
            try:
                plate = int(parts[0]); mjd = int(parts[1]); fiber = int(parts[2])
                rml50 = float(parts[9])  # index 9 = 第10欄
                mass_map[(plate, mjd, fiber)] = rml50
            except (ValueError, IndexError):
                continue
print(f"質量表: {len(mass_map)} entries")

# 2. 讀 SDSS fit
with open('/home/wsl/IDCM/sdss_large_fit.json') as fh:
    res = json.load(fh)
print(f"SDSS fit: {len(res)}")

# 3. 加質量
for r in res:
    fname = r['path']  # spec-{plate}-{mjd}-{fiber}.fits
    parts = fname.replace('.fits','').split('-')
    if len(parts) == 4:
        plate, mjd, fiber = int(parts[1]), int(parts[2]), int(parts[3])
        r['mstar'] = mass_map.get((plate, mjd, fiber), np.nan)
    else:
        r['mstar'] = np.nan

has_mass = sum(1 for r in res if not np.isnan(r.get('mstar', np.nan)))
print(f"有質量: {has_mass}/{len(res)}")

# 4. 固定質量，睇 [OIII]/Hβ vs z
print("\n" + "="*70)
print("固定質量 bin 內嘅 [OIII]/Hβ vs z 趨勢")
print("="*70)

def o3hb(r):
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
        return r['O3_5007_flux']/r['HB_4861_flux']
    return None

for mlo, mhi, mname in [(9.0,9.5,'9.0-9.5'),(9.5,10.0,'9.5-10.0'),(10.0,10.5,'10.0-10.5'),(10.5,11.0,'10.5-11.0')]:
    print(f"\n質量 logM={mname}:")
    for zl, zh, zname in [(0.001,0.03,'z=0.001-0.03'),(0.03,0.06,'z=0.03-0.06'),(0.06,0.10,'z=0.06-0.10')]:
        vals = []
        for r in res:
            if mlo <= r['mstar'] < mhi and zl <= r['z'] < zh:
                v = o3hb(r)
                if v is not None:
                    vals.append(v)
        if len(vals) >= 10:
            print(f"  {zname}: n={len(vals):4d}, med={np.median(vals):.2f}")

# 5. 統計：每個質量 bin，低z vs 高z
print("\n" + "="*70)
print("統計：固定質量後，下降仲顯唔顯著？")
print("="*70)
for mlo, mhi, mname in [(9.0,9.5,'9.0-9.5'),(9.5,10.0,'9.5-10.0'),(10.0,10.5,'10.0-10.5'),(10.5,11.0,'10.5-11.0')]:
    low, high = [], []
    for r in res:
        if mlo <= r['mstar'] < mhi:
            v = o3hb(r)
            if v is None: continue
            if r['z'] < 0.03: low.append(v)
            elif r['z'] > 0.06: high.append(v)
    if len(low) >= 10 and len(high) >= 10:
        u, p = stats.mannwhitneyu(low, high, alternative='greater')
        print(f"  logM={mname}: 低z(med={np.median(low):.2f}, n={len(low)}) vs "
              f"高z(med={np.median(high):.2f}, n={len(high)}) → p={p:.2e}")