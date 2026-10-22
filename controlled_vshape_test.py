#!/usr/bin/env python3
"""
完整控制變數分析：V 形係結構定係選樣假象？
1. SDSS 固定質量：下降支消失 → 質量效應
2. SDSS 固定質量+金屬量（gal_fiboh Tremonti+04）
3. JADES 支：點解[OIII]/Hβ 高？質量有冇數據？
4. 最終誠實結論
"""
import gzip, json
import numpy as np
from scipy import stats

# ===== 1. 質量 =====
mass_map = {}
with gzip.open('/tmp/newmasses_dr4.gz', 'rt') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 10:
            try:
                mass_map[(int(parts[0]), int(parts[1]), int(parts[2]))] = float(parts[9])
            except (ValueError, IndexError):
                continue

# ===== 2. 金屬量 (gal_fiboh Tremonti+04) — 同 gal_line 相同順序 =====
from astropy.io import fits
try:
    fiboh = fits.open('/tmp/gal_fiboh.fits.gz')[1].data
    print(f"金屬量目錄: {len(fiboh)}")
    # 用 gal_info 做 plate/mjd/fiber -> fiboh index 對應
    info = fits.open('/tmp/gal_info_dr7_v5_2.fit.gz')[1].data
    info_plate = info['PLATEID']
    info_mjd = info['MJD']
    info_fiber = info['FIBERID']
    print(f"info: {len(info)} galaxies (fiboh 順序相同)")
except Exception as e:
    print("fiboh fail:", str(e)[:80])
    fiboh = None

# ===== 3. SDSS fit =====
with open('/home/wsl/IDCM/sdss_large_fit.json') as fh:
    res = json.load(fh)

for r in res:
    parts = r['path'].replace('.fits','').split('-')
    if len(parts) == 4:
        key = (int(parts[1]), int(parts[2]), int(parts[3]))
        r['mstar'] = mass_map.get(key, np.nan)
        if fiboh is not None:
            # fiboh 同 gal_info 相同順序，用索引對應
            import numpy as np
            idx = np.where((info_plate==key[0]) & (info_mjd==key[1]) & (info_fiber==key[2]))[0]
            if len(idx) > 0:
                r['metal'] = fiboh['MEDIAN'][idx[0]]
            else:
                r['metal'] = np.nan
    else:
        r['mstar'] = np.nan
        r['metal'] = np.nan

def o3hb(r):
    if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
        return r['O3_5007_flux']/r['HB_4861_flux']
    return None

# ===== 4. 固定質量 + 金屬量 =====
print("\n" + "="*70)
print("固定質量 + 金屬量後，[OIII]/Hβ vs z")
print("="*70)

# 金屬量分佈
met_vals = [r['metal'] for r in res if not np.isnan(r.get('metal', np.nan))]
if met_vals:
    print(f"\n金屬量範圍: {np.nanmin(met_vals):.2f} - {np.nanmax(met_vals):.2f} (n={len(met_vals)})")

has_both = sum(1 for r in res if not np.isnan(r.get('mstar',np.nan)) and not np.isnan(r.get('metal',np.nan)))
print(f"有質量+金屬量: {has_both}/{len(res)}")

# 用質量 bin + 金屬量 bin 雙重控制
if met_vals:
    for mlo, mhi, mname in [(9.0,10.0,'9.0-10.0'),(10.0,11.0,'10.0-11.0')]:
        for metlo, methi, metname in [(8.0,8.5,'Z=8.0-8.5'),(8.5,9.0,'Z=8.5-9.0'),(9.0,9.5,'Z=9.0-9.5')]:
            low, high = [], []
            for r in res:
                if mlo <= r['mstar'] < mhi and metlo <= r['metal'] < methi:
                    v = o3hb(r)
                    if v is None: continue
                    if r['z'] < 0.03: low.append(v)
                    elif r['z'] > 0.06: high.append(v)
            if len(low) >= 5 and len(high) >= 5:
                u, p = stats.mannwhitneyu(low, high, alternative='greater')
                flag = "↓顯著" if p < 0.05 else "flat"
                print(f"  M={mname} {metname}: 低z(med={np.median(low):.2f},n={len(low)}) vs "
                      f"高z(med={np.median(high):.2f},n={len(high)}) → p={p:.2f} {flag}")

# ===== 5. 冇質量控制版本（原始 V 形下降支）=====
print("\n" + "="*70)
print("對照：冇質量控制（原始混合樣本）")
print("="*70)
low, high = [], []
for r in res:
    v = o3hb(r)
    if v is None: continue
    if r['z'] < 0.03: low.append(v)
    elif r['z'] > 0.06: high.append(v)
u, p = stats.mannwhitneyu(low, high, alternative='greater')
print(f"  混合: 低z(med={np.median(low):.2f},n={len(low)}) vs 高z(med={np.median(high):.2f},n={len(high)}) → p={p:.2e}")

# ===== 6. JADES 支：質量數據 =====
print("\n" + "="*70)
print("JADES 支嘅質量問題")
print("="*70)
with open('/home/wsl/IDCM/jades_fit_v2.json') as fh:
    jades = json.load(fh)
# JADES x1d 冇質量。用目錄嘅 flux 做粗略 luminosity 指標
el = fits.open('/tmp/jades_prism_line.fits')[1].data
print("JADES prism 目錄有質量欄？")
print([c for c in el.columns.names if 'MASS' in c.upper() or 'MSTAR' in c.upper() or 'IMF' in c.upper()][:5])
print("全部 cols 樣本:", [c for c in el.columns.names][:20])