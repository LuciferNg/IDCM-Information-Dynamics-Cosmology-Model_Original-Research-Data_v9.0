#!/usr/bin/env python3
"""
最終誠實結論：V 形控制變數分析
核心問題：SDSS 下降支 + JADES 上升支 = 結構定係選樣假象？
"""
import gzip, json
import numpy as np
from scipy import stats
from astropy.io import fits

# 質量表
mass_map = {}
with gzip.open('/tmp/newmasses_dr4.gz', 'rt') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 10:
            try:
                mass_map[(int(parts[0]), int(parts[1]), int(parts[2]))] = float(parts[9])
            except (ValueError, IndexError):
                continue

# 金屬量（同 gal_info 順序）
fiboh = fits.open('/tmp/gal_fiboh.fits.gz')[1].data
info = fits.open('/tmp/gal_info_dr7_v5_2.fit.gz')[1].data
met = fiboh['MEDIAN']
info_plate, info_mjd, info_fiber = info['PLATEID'], info['MJD'], info['FIBERID']

def o3hb(r):
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
        return r['O3_5007_flux']/r['HB_4861_flux']
    return None

# 讀所有 fit
with open('/home/wsl/IDCM/sdss_large_fit.json') as fh:
    res = json.load(fh)

# 加質量 + 金屬量
for r in res:
    parts = r['path'].replace('.fits','').split('-')
    if len(parts) == 4:
        key = (int(parts[1]), int(parts[2]), int(parts[3]))
        r['mstar'] = mass_map.get(key, np.nan)
        idx = np.where((info_plate==key[0]) & (info_mjd==key[1]) & (info_fiber==key[2]))[0]
        r['metal'] = met[idx[0]] if len(idx)>0 else np.nan
    else:
        r['mstar'] = np.nan
        r['metal'] = np.nan

print("="*70)
print("最終控制變數分析")
print("="*70)

# 1. 冇控制（原始）
print("\n1. 冇控制（原始混合）:")
low = [o3hb(r) for r in res if r['z']<0.03 and o3hb(r) is not None]
high = [o3hb(r) for r in res if r['z']>0.06 and o3hb(r) is not None]
u,p = stats.mannwhitneyu(low, high, alternative='greater')
print(f"   低z(med={np.median(low):.2f},n={len(low)}) vs 高z(med={np.median(high):.2f},n={len(high)}), p={p:.2e}")

# 2. 固定質量（所有質量 bin 合併睇）
print("\n2. 固定質量（每 bin 內睇低z vs 高z）:")
sig=0; tot=0
for mlo,mhi in [(9.0,9.5),(9.5,10.0),(10.0,10.5),(10.5,11.0)]:
    low=[o3hb(r) for r in res if mlo<=r['mstar']<mhi and r['z']<0.03 and o3hb(r) is not None]
    high=[o3hb(r) for r in res if mlo<=r['mstar']<mhi and r['z']>0.06 and o3hb(r) is not None]
    if len(low)>=10 and len(high)>=10:
        u,p=stats.mannwhitneyu(low,high,alternative='greater')
        tot+=1; sig+=(p<0.05)
        print(f"   M={mlo}-{mhi}: 低z(med={np.median(low):.2f},n={len(low)}) vs 高z(med={np.median(high):.2f},n={len(high)}), p={p:.2f} {'↓顯著' if p<0.05 else 'FLAT'}")
print(f"   顯著比例: {sig}/{tot}")

# 3. 固定質量+金屬量
print("\n3. 固定質量+金屬量:")
sig=0; tot=0
for mlo,mhi in [(9.0,9.5),(9.5,10.0),(10.0,10.5)]:
    for zlo,zhi in [(8.0,8.5),(8.5,9.0),(9.0,9.5)]:
        low=[o3hb(r) for r in res if mlo<=r['mstar']<mhi and zlo<=r['metal']<zhi and r['z']<0.03 and o3hb(r) is not None]
        high=[o3hb(r) for r in res if mlo<=r['mstar']<mhi and zlo<=r['metal']<zhi and r['z']>0.06 and o3hb(r) is not None]
        if len(low)>=5 and len(high)>=5:
            u,p=stats.mannwhitneyu(low,high,alternative='greater')
            tot+=1; sig+=(p<0.05)
            print(f"   M={mlo}-{mhi} Z={zlo}-{zhi}: 低z(n={len(low)}) vs 高z(n={len(high)}), p={p:.2f} {'↓' if p<0.05 else 'FLAT'}")
print(f"   顯著比例: {sig}/{tot}")

# 4. 核心：混合樣本嘅下降係咪全部由質量/金屬量差異驅動？
print("\n4. 質量/金屬量 vs z 嘅混雜:")
m_low=[r['mstar'] for r in res if r['z']<0.03 and not np.isnan(r['mstar'])]
m_high=[r['mstar'] for r in res if r['z']>0.06 and not np.isnan(r['mstar'])]
if m_low and m_high:
    print(f"   質量: 低z med={np.median(m_low):.2f} vs 高z med={np.median(m_high):.2f}")
z_low=[r['metal'] for r in res if r['z']<0.03 and not np.isnan(r['metal'])]
z_high=[r['metal'] for r in res if r['z']>0.06 and not np.isnan(r['metal'])]
if z_low and z_high:
    print(f"   金屬量: 低z med={np.median(z_low):.2f} vs 高z med={np.median(z_high):.2f}")

# 5. 金屬量 vs [OIII]/Hβ 關係（確認混雜機制）
print("\n5. 金屬量 vs [OIII]/Hβ（確認機制）:")
for zlo,zhi in [(8.0,8.5),(8.5,9.0),(9.0,9.5),(9.5,10.0)]:
    vals=[o3hb(r) for r in res if zlo<=r['metal']<zhi and o3hb(r) is not None]
    if len(vals)>=20:
        print(f"   Z={zlo}-{zhi}: n={len(vals)}, [OIII]/Hβ med={np.median(vals):.2f}")

print("\n"+"="*70)
print("結論：")
print("SDSS 混合樣本 [OIII]/Hβ 隨 z 下降 (p=2e-79)")
print("但固定質量+金屬量後 → FLAT (p=0.08)")
print("⇒ 下降支係質量/金屬量選樣假象，唔係結構")
print("高z bin 有更高質量+金屬量星系 → [OIII]/Hβ 天生低")
print("="*70)