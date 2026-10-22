#!/usr/bin/env python3
"""
JADES 獨立驗證: metallicity-z 趨勢
===================================
用獨立 fit 嘅發射線 flux，計算金屬量，做質量控制，
睇 metallicity-z trend 係咪質量假象。

方法:
- O3N2 = log10(([OIII]5007/Hβ) / ([NII]6584/Hα)) → 12+log(O/H) = 8.73 - 0.32×O3N2
- N2 = log10([NII]6584/Hα) → 12+log(O/H) = 9.12 + 0.58×N2 (N2>-2.5)
- R23 = log10(([OII]3727+[OIII]4959+5007)/Hβ) → cross-check

質量 proxy: F277W_KRON flux (rest-frame optical at z~2-8)
"""

import json, math, numpy as np
from collections import OrderedDict

# ================================================================
# 1. 載入數據
# ================================================================
with open('/home/wsl/IDCM/jades_fit_v2.json') as f:
    jades = json.load(f)
print(f"Total JADES spectra: {len(jades)}")

# 載入 photometry catalog
from astropy.io import fits
photo = fits.open('/home/wsl/IDCM/data/catalogs/jades_photo.fits')
kron = photo['KRON'].data  # 94,000 galaxies
el_cat = fits.open('/tmp/jades_prism_line.fits')[1].data  # 2,525 emission line entries

# ================================================================
# 2. 建立 ID 對應: fit result → photometry
# ================================================================
# fit result 用檔名 path, 例如 "hlsp_jades_jwst_nirspec_goods-s-...x1d.fits"
# photometry 用 ID (NIRSpec_ID)
# emission line catalog 有 NIRSpec_ID 同 z_Spec

# 從 emission line catalog 建立 NIRSpec_ID → index 對應
el_nid = el_cat['NIRSpec_ID']  # NIRSpec IDs
print(f"Emission catalog: {len(el_nid)} entries")

# 從 fit result 嘅 path 提取 NIRSpec ID
# path 格式: hlsp_jades_jwst_nirspec_<field>-<tier>-<id>_clear-prism_v1.0_x1d.fits
# 但 ID 可能唔係直接 NIRSpec_ID

# 更簡單: 用 emission catalog 嘅 z_Spec match fit result 嘅 z
# 同埋用 RA/Dec match

# 先睇 emission catalog 有冇 RA/Dec
print(f"\nEmission catalog columns:")
for c in el_cat.columns.names:
    print(f"  {c}")

# 睇下 photometry KRON 有冇 RA/Dec
print(f"\nPhotometry KRON ID sample: {kron['ID'][:5]}")
print(f"Emission catalog NIRSpec_ID sample: {el_nid[:5]}")

# ================================================================
# 3. Match fit results to photometry via emission catalog
# ================================================================
# 策略: fit result z → match emission catalog z (within Δz<0.01)
# → get NIRSpec_ID → match photometry ID

# Emission catalog z
el_z = el_cat['z_Spec']
el_ra = el_cat['RA_TARG']
el_dec = el_cat['Dec_TARG']

# Build match: for each fit result, find closest emission catalog entry
print(f"\nMatching {len(jades)} fit results to emission catalog...")
matches = 0
for r in jades:
    rz = r['z']
    # Find closest z match in emission catalog
    dz = np.abs(el_z - rz)
    min_idx = np.argmin(dz)
    min_dz = dz[min_idx]
    if min_dz < 0.01:
        r['NIRSpec_ID'] = int(el_nid[min_idx])
        r['el_idx'] = int(min_idx)
        matches += 1

print(f"Matched to emission catalog: {matches}/{len(jades)}")

# Now match to photometry via NIRSpec_ID
photo_id = kron['ID']
n_matched = 0
for r in jades:
    if 'NIRSpec_ID' not in r:
        continue
    # Find in photometry
    idx = np.where(photo_id == r['NIRSpec_ID'])[0]
    if len(idx) > 0:
        r['photo_idx'] = int(idx[0])
        n_matched += 1

print(f"Matched to photometry: {n_matched}/{matches}")

# ================================================================
# 4. 計算金屬量
# ================================================================
print(f"\n{'='*70}")
print(f"金屬量計算")
print(f"{'='*70}")

def calc_metallicity(r):
    """Calculate metallicity using O3N2 and N2 methods"""
    results = {}
    
    # O3N2 method (Pettini & Pagel 2004)
    # O3N2 = log10(([OIII]5007/Hβ) / ([NII]6584/Hα))
    # 12+log(O/H) = 8.73 - 0.32 × O3N2 (for -1 < O3N2 < 1.9)
    if (r['O3_5007_det'] == 'True' and r['HB_4861_det'] == 'True' and
        r['HA_6563_det'] == 'True' and r['N2_6584_det'] == 'True' and
        r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0 and
        r['HA_6563_flux'] > 0 and r['N2_6584_flux'] > 0):
        
        o3hb = r['O3_5007_flux'] / r['HB_4861_flux']
        n2ha = r['N2_6584_flux'] / r['HA_6563_flux']
        if o3hb > 0 and n2ha > 0:
            o3n2 = math.log10(o3hb / n2ha)
            if -1 < o3n2 < 1.9:
                results['O3N2'] = o3n2
                results['Z_O3N2'] = 8.73 - 0.32 * o3n2
                results['Z_O3N2_err'] = 0.25  # calibration error
    
    # N2 method (Denicolo+2002, Pettini & Pagel 2004)
    # N2 = log10([NII]6584/Hα)
    # 12+log(O/H) = 9.12 + 0.58 × N2 (for N2 > -2.5)
    if (r['HA_6563_det'] == 'True' and r['N2_6584_det'] == 'True' and
        r['HA_6563_flux'] > 0 and r['N2_6584_flux'] > 0):
        n2 = math.log10(r['N2_6584_flux'] / r['HA_6563_flux'])
        if n2 > -2.5:
            results['N2'] = n2
            results['Z_N2'] = 9.12 + 0.58 * n2  # Denicolo+2002
            # Also PP04: Z = 8.90 + 0.57 × N2
            results['Z_N2_PP04'] = 8.90 + 0.57 * n2
    
    # R23 method (for cross-check)
    # R23 = log10(([OII]3727 + [OIII]4959+5007) / Hβ)
    if (r['O2_3727_det'] == 'True' and r['O3_5007_det'] == 'True' and
        r['HB_4861_det'] == 'True' and r['O3_4959_det'] == 'True' and
        r['O3_5007_flux'] > 0 and r['HB_4861_flux'] > 0 and
        r['O2_3727_flux'] > 0):
        o3 = r['O3_4959_flux'] + r['O3_5007_flux']
        r23 = (r['O2_3727_flux'] + o3) / 2 / r['HB_4861_flux']  # /2 for O3+Hβ normalization
        results['R23'] = math.log10(r23) if r23 > 0 else None
    
    return results

# Compute metallicities
for r in jades:
    r['met'] = calc_metallicity(r)

# Count valid metallicity measurements
n_o3n2 = sum(1 for r in jades if 'Z_O3N2' in r['met'])
n_n2 = sum(1 for r in jades if 'Z_N2' in r['met'])
n_r23 = sum(1 for r in jades if 'R23' in r['met'] and r['met']['R23'] is not None)
print(f"\nO3N2 valid: {n_o3n2}")
print(f"N2 valid: {n_n2}")
print(f"R23 valid: {n_r23}")

# ================================================================
# 5. 金屬量 vs z (無質量控制)
# ================================================================
print(f"\n{'='*70}")
print(f"5. 金屬量 vs z (無質量控制)")
print(f"{'='*70}")

# O3N2 method
z_bins = [(2, 3), (3, 4), (4, 5), (5, 6), (6, 8)]
print(f"\nO3N2 method (12+log(O/H) = 8.73 - 0.32×O3N2):")
print(f"{'z range':<12} {'n':<6} {'median Z':<12} {'P25-P75':<16} {'median O3N2':<12} {'O3/Hb(N2)':<12}")
print(f"{'-'*70}")
for zl, zh in z_bins:
    vals = [r['met']['Z_O3N2'] for r in jades if 'Z_O3N2' in r['met'] and zl <= r['z'] < zh]
    o3n2_vals = [r['met']['O3N2'] for r in jades if 'O3N2' in r['met'] and zl <= r['z'] < zh]
    if len(vals) >= 3:
        med = np.median(vals)
        p25, p75 = np.percentile(vals, [25, 75])
        med_o3n2 = np.median(o3n2_vals)
        print(f"z={zl}-{zh:<4}  {len(vals):<6} {med:<12.4f} {p25:.4f}-{p75:.4f}  {med_o3n2:<12.4f}")

# N2 method (Denicolo+2002)
print(f"\nN2 method (12+log(O/H) = 9.12 + 0.58×N2):")
print(f"{'z range':<12} {'n':<6} {'median Z':<12} {'P25-P75':<16} {'median N2':<12}")
print(f"{'-'*60}")
for zl, zh in z_bins:
    vals = [r['met']['Z_N2'] for r in jades if 'Z_N2' in r['met'] and zl <= r['z'] < zh]
    n2_vals = [r['met']['N2'] for r in jades if 'N2' in r['met'] and zl <= r['z'] < zh]
    if len(vals) >= 3:
        med = np.median(vals)
        p25, p75 = np.percentile(vals, [25, 75])
        med_n2 = np.median(n2_vals)
        print(f"z={zl}-{zh:<4}  {len(vals):<6} {med:<12.4f} {p25:.4f}-{p75:.4f}  {med_n2:<12.4f}")

# N2 method (PP04)
print(f"\nN2 method (PP04: 12+log(O/H) = 8.90 + 0.57×N2):")
print(f"{'z range':<12} {'n':<6} {'median Z':<12} {'P25-P75':<16}")
print(f"{'-'*40}")
for zl, zh in z_bins:
    vals = [r['met']['Z_N2_PP04'] for r in jades if 'Z_N2_PP04' in r['met'] and zl <= r['z'] < zh]
    if len(vals) >= 3:
        med = np.median(vals)
        p25, p75 = np.percentile(vals, [25, 75])
        print(f"z={zl}-{zh:<4}  {len(vals):<6} {med:<12.4f} {p25:.4f}-{p75:.4f}")

# ================================================================
# 6. 質量控制
# ================================================================
print(f"\n{'='*70}")
print(f"6. 質量控制")
print(f"{'='*70}")

# 用 F277W_KRON flux 做質量 proxy (rest-frame optical at z~2-8)
# 對於 z>5, rest-frame optical 移到 F444W, 但我哋用 F277W 做統一 proxy

# 加 mass proxy 到 fit results
mass_col = 'F277W_KRON'
mass_cols = [c for c in kron.columns.names if 'F277W' in c and 'KRON' in c and 'e' not in c.lower()]
print(f"Available F277W_KRON columns: {mass_cols}")

# Use the first one that's not an error column
mass_col = 'F277W_KRON'
for c in mass_cols:
    if 'ei' not in c and '_e' not in c.lower() and c != 'F277W_KRON_ei':
        mass_col = c
        break

print(f"Using mass proxy column: {mass_col}")

for r in jades:
    if 'photo_idx' in r:
        pi = r['photo_idx']
        f277 = kron[mass_col][pi]
        if f277 > 0 and not np.isnan(f277):
            r['mass_proxy'] = np.log10(f277)
            r['mass_raw'] = f277
        else:
            r['mass_proxy'] = np.nan
    else:
        r['mass_proxy'] = np.nan

# Stats
mp_vals = np.array([r['mass_proxy'] for r in jades if not np.isnan(r.get('mass_proxy', np.nan))])
print(f"\nMass proxy stats:")
print(f"  N with mass: {len(mp_vals)}")
print(f"  Range: {np.nanmin(mp_vals):.2f} - {np.nanmax(mp_vals):.2f}")
print(f"  Median: {np.median(mp_vals):.2f}")

# One more approach: also look at IR color as mass proxy
# F277W - F444W color (redder = older/more massive)
# 但需要 F444W 都有 flux

# ================================================================
# 7. 質量控制後 metallicity-z
# ================================================================
print(f"\n{'='*70}")
print(f"7. 質量控制後 metallicity-z (O3N2 method)")
print(f"{'='*70}")

# 按質量三分位分組
mp_all = [r['mass_proxy'] for r in jades if 'Z_O3N2' in r['met'] and not np.isnan(r.get('mass_proxy', np.nan))]
if len(mp_all) >= 10:
    q1, q2 = np.percentile(mp_all, [33, 67])
    print(f"Mass terciles: {np.nanmin(mp_all):.2f} / {q1:.2f} / {q2:.2f} / {np.nanmax(mp_all):.2f}")
    
    for mlo, mhi, mname in [(-np.inf, q1, 'low mass'), (q1, q2, 'mid mass'), (q2, np.inf, 'high mass')]:
        print(f"\n  {mname}:")
        print(f"  {'z range':<12} {'n':<6} {'Z_med':<10} {'P25-P75':<16}")
        print(f"  {'-'*44}")
        for zl, zh in z_bins:
            vals = [r['met']['Z_O3N2'] for r in jades 
                    if 'Z_O3N2' in r['met'] 
                    and zl <= r['z'] < zh
                    and not np.isnan(r.get('mass_proxy', np.nan))
                    and mlo <= r['mass_proxy'] < mhi]
            if len(vals) >= 3:
                med = np.median(vals)
                p25, p75 = np.percentile(vals, [25, 75])
                print(f"  z={zl}-{zh:<4}  {len(vals):<6} {med:<10.4f} {p25:.4f}-{p75:.4f}")

# Same for N2 method
print(f"\n{'='*70}")
print(f"質量控制後 metallicity-z (N2 method, PP04)")
print(f"{'='*70}")

mp_all_n2 = [r['mass_proxy'] for r in jades if 'Z_N2_PP04' in r['met'] and not np.isnan(r.get('mass_proxy', np.nan))]
if len(mp_all_n2) >= 10:
    q1_n2, q2_n2 = np.percentile(mp_all_n2, [33, 67])
    print(f"Mass terciles: {np.nanmin(mp_all_n2):.2f} / {q1_n2:.2f} / {q2_n2:.2f} / {np.nanmax(mp_all_n2):.2f}")
    
    for mlo, mhi, mname in [(-np.inf, q1_n2, 'low mass'), (q1_n2, q2_n2, 'mid mass'), (q2_n2, np.inf, 'high mass')]:
        print(f"\n  {mname}:")
        for zl, zh in z_bins:
            vals = [r['met']['Z_N2_PP04'] for r in jades 
                    if 'Z_N2_PP04' in r['met'] 
                    and zl <= r['z'] < zh
                    and not np.isnan(r.get('mass_proxy', np.nan))
                    and mlo <= r['mass_proxy'] < mhi]
            if len(vals) >= 3:
                med = np.median(vals)
                p25, p75 = np.percentile(vals, [25, 75])
                print(f"  z={zl}-{zh:<4}  {len(vals):<6} {med:<10.4f} {p25:.4f}-{p75:.4f}")

# ================================================================
# 8. 獨立 fit vs 目錄 O3N2 對比 (skip - catalog has blended Hα+[NII]+[SII])
# ================================================================
print(f"\n{'='*70}")
print(f"8. 注意: JADES DR3 目錄嘅 [NII]6584 係 Blnd_HA_N2_S2 (blended)")
print(f"   獨立 fit 用高斯分離 Hα+[NII]，但 catalog 冇 clean [NII]")
print(f"   所以 catalog 對比唔適用")
print(f"{'='*70}")

print(f"{'='*70}")

# ================================================================
# 9. IDCM 結構座標分析
# ================================================================
print(f"\n{'='*70}")
print(f"9. IDCM 結構座標 ℓ = log₄(1+z)")
print(f"{'='*70}")

# 喺 IDCM 框架入面，z 唔係 lookback time，係結構座標
# ℓ = log₄(1+z) = K_Tree level
# 更高 z = 更細 K_Tree level = 更細結構尺度

B = 4  # K_Tree branching factor
for r in jades:
    if 'Z_O3N2' in r['met']:
        r['ell'] = math.log(1 + r['z'], B)  # ℓ = log₄(1+z)

# Group by ℓ
print(f"\nMetallicity by ℓ (K_Tree level):")
print(f"{'ℓ range':<12} {'z range':<14} {'n':<6} {'Z_med':<10}")
print(f"{'-'*42}")
for ell in [0.5, 1.0, 1.5, 2.0, 2.5]:
    zl = B**ell - 1
    zh = B**(ell+0.5) - 1
    vals = [r['met']['Z_O3N2'] for r in jades if 'Z_O3N2' in r['met'] and zl <= r['z'] < zh]
    if len(vals) >= 3:
        print(f"ℓ={ell:.1f}-{ell+0.5:.1f}  z={zl:.1f}-{zh:.1f}  {len(vals):<6} {np.median(vals):<10.4f}")

# ================================================================
# 10. 統計測試
# ================================================================
print(f"\n{'='*70}")
print(f"10. 統計測試")
print(f"{'='*70}")

from scipy import stats

# Spearman correlation: Z vs z
z_o3n2 = [(r['z'], r['met']['Z_O3N2']) for r in jades if 'Z_O3N2' in r['met']]
if len(z_o3n2) >= 10:
    zs = np.array([x[0] for x in z_o3n2])
    zs_vals = np.array([x[1] for x in z_o3n2])
    rho, p = stats.spearmanr(zs, zs_vals)
    print(f"\nSpearman Z vs z (O3N2): ρ={rho:.4f}, p={p:.2e}")
    
    # After mass control
    # Partial correlation: Z vs z controlling for mass
    mp_o3n2 = [r['mass_proxy'] for r in jades if 'Z_O3N2' in r['met'] and not np.isnan(r.get('mass_proxy', np.nan))]
    z_o3n2_m = [r['z'] for r in jades if 'Z_O3N2' in r['met'] and not np.isnan(r.get('mass_proxy', np.nan))]
    z_vals_m = [r['met']['Z_O3N2'] for r in jades if 'Z_O3N2' in r['met'] and not np.isnan(r.get('mass_proxy', np.nan))]
    if len(mp_o3n2) >= 10:
        # Partial correlation
        from scipy.stats import pearsonr
        r_zm, _ = pearsonr(np.array(z_o3n2_m), np.array(mp_o3n2))
        r_zv, _ = pearsonr(np.array(z_o3n2_m), np.array(z_vals_m))
        r_mv, _ = pearsonr(np.array(mp_o3n2), np.array(z_vals_m))
        
        # Partial correlation: r_{zv.m} = (r_{zv} - r_{zm}·r_{mv}) / √((1-r_{zm}²)(1-r_{mv}²))
        r_partial = (r_zv - r_zm * r_mv) / math.sqrt((1 - r_zm**2) * (1 - r_mv**2))
        print(f"\nPartial correlation Z vs z | mass: r={r_partial:.4f}")
        print(f"  r(Z,z)={r_zv:.4f}, r(Z,mass)={r_mv:.4f}, r(z,mass)={r_zm:.4f}")

# N2 method
z_n2 = [(r['z'], r['met']['Z_N2']) for r in jades if 'Z_N2' in r['met']]
if len(z_n2) >= 10:
    zs_n2 = np.array([x[0] for x in z_n2])
    vals_n2 = np.array([x[1] for x in z_n2])
    rho_n2, p_n2 = stats.spearmanr(zs_n2, vals_n2)
    print(f"\nSpearman Z vs z (N2): ρ={rho_n2:.4f}, p={p_n2:.2e}")

# ================================================================
# 11. 總結
# ================================================================
print(f"\n{'='*70}")
print(f"11. 總結")
print(f"{'='*70}")

print(f"""
JADES 獨立驗證: metallicity-z 趨勢
===================================
樣本: {len(jades)} 條 JADES NIRSpec 原始光譜獨立擬合
      O3N2 金屬量: {n_o3n2} 個星系
      N2 金屬量: {n_n2} 個星系
      R23 可用: {n_r23} 個星系
      z 範圍: 2.00 - 9.43

O3N2 metallicity-z 趨勢:
  (運行結果見上)

質量控制後:
  (運行結果見上)

IDCM 結構座標 ℓ = log₄(1+z):
  (運行結果見上)

Spearman 相關:
  (運行結果見上)
""")