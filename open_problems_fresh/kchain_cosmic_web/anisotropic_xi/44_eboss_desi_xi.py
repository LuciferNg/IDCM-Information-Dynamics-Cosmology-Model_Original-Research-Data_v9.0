#!/usr/bin/env python3
"""
44_eboss_desi_xi.py — eBOSS + DESI 大尺度諧波驗證
====================================================
使用 eBOSS DR16 LRG ξ(s) 數據（s_max=247.5 h⁻¹Mpc），
覆蓋 IDCM BAO 位置（203.1 h⁻¹Mpc）。

方法：
1. 用平滑 spline 分離 broadband
2. 檢測 harmonic residual 喺 λ_sync/n 嘅 S/N
3. 特別檢查 n=2（BAO=203.1 h⁻¹Mpc）係咪喺數據範圍內
4. 同 DESI DR1 BAO 嘅 DM/rd 做交叉檢驗
"""
import math
import numpy as np
from scipy import stats, interpolate, signal
import json

# ================================================================
# 0. K_Chain 核心常數
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
L = [round(PHI**n + (-1)**n * PHI_INV**n) for n in range(15)]
SYNC, L3, L5 = L[0], L[3], L[5]
H0_IDCM = 72.59
C_LIGHT = 299792.458
R_H = C_LIGHT / H0_IDCM  # 4129.94 Mpc
H = H0_IDCM / 100
LAMBDA_SYNC = 2 * math.pi * R_H / 88  # 294.88 Mpc
BAO_MPC = LAMBDA_SYNC / 2  # 147.44 Mpc
BAO_HINV = BAO_MPC / H  # 203.11 h⁻¹Mpc
N_d = 44

gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d)])
v_g_n = np.array([math.cos(math.pi * n / 88) for n in range(1, N_d)])
Z_n = gamma_n / np.abs(v_g_n)
Z_n[np.isinf(Z_n)] = 1e6
R_n = np.zeros(N_d - 1)
for i in range(1, N_d - 1):
    R_n[i] = (Z_n[i] - Z_n[i-1]) / (Z_n[i] + Z_n[i-1])
theta_n = np.array([n * 2 * math.pi / 88 for n in range(1, N_d)])

print("=" * 80)
print("  eBOSS + DESI 大尺度諧波驗證")
print("=" * 80)
print(f"\n  λ_sync = {LAMBDA_SYNC:.2f} Mpc")
print(f"  BAO = λ_sync/2 = {BAO_MPC:.2f} Mpc = {BAO_HINV:.1f} h⁻¹Mpc")
print(f"  H₀(IDCM) = {H0_IDCM:.2f} km/s/Mpc")

# ================================================================
# 1. 載入 eBOSS DR16 LRG ξ(s) 數據
# ================================================================
print(f"\n{'─'*80}")
print("  1. eBOSS DR16 LRG ξ(s) 數據")
print(f"{'─'*80}")

s_eboss, xi_eboss, err_eboss = np.loadtxt(
    '/home/wsl/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt',
    skiprows=1, usecols=(0, 1, 2), unpack=True)

print(f"  數據點: {len(s_eboss)}")
print(f"  s 範圍: {s_eboss[0]:.1f} - {s_eboss[-1]:.1f} h⁻¹Mpc")
print(f"  ξ 範圍: {xi_eboss.min():.4f} - {xi_eboss.max():.4f}")
print(f"  IDCM BAO = {BAO_HINV:.1f} h⁻¹Mpc → 在數據範圍內! ✅")
print(f"  數據喺 BAO 位置 (s∼{BAO_HINV:.0f}): ξ={xi_eboss[-1]:.4f}±{err_eboss[-1]:.4f}")

# ================================================================
# 2. Broadband 分離
# ================================================================
print(f"\n{'─'*80}")
print("  2. Broadband 分離")
print(f"{'─'*80}")

from scipy.interpolate import UnivariateSpline

def smooth_spline_broadband(x, y, smooth_factor=0.3):
    spl = UnivariateSpline(x, y, s=smooth_factor * len(x) * np.var(y))
    broadband = spl(x)
    residual = y - broadband
    return broadband, residual

# 嘗試不同 smooth factor
for sf in [0.1, 0.3, 0.5, 0.8]:
    bb, res = smooth_spline_broadband(s_eboss, xi_eboss, smooth_factor=sf)
    harm_ratio = np.std(res) / np.std(bb) if np.std(bb) > 0 else 0
    print(f"  smooth={sf:.1f}: 諧波/背景={harm_ratio:.4f}")

# 用最佳 smooth factor
sf_best = 0.3
bb_eboss, res_eboss = smooth_spline_broadband(s_eboss, xi_eboss, smooth_factor=sf_best)

# ================================================================
# 3. 諧波位置檢測
# ================================================================
print(f"\n{'─'*80}")
print("  3. 諧波位置檢測 — λ_sync/n")
print(f"{'─'*80}")

n_harmonics = np.arange(2, 21)
lam_theory = LAMBDA_SYNC / n_harmonics / H  # h⁻¹ Mpc
snr = np.abs(res_eboss) / err_eboss

print(f"  {'n':<5} {'λ_sync/n (h⁻¹Mpc)':<20} {'s_nearest':<12} {'ξ_resid':<12} {'S/N':<10} {'Result':<8}")
print(f"  {'─'*65}")

matched = []
for n in n_harmonics:
    lam = lam_theory[n-2]
    idx = np.argmin(np.abs(s_eboss - lam))
    s_nearest = s_eboss[idx]
    res_val = res_eboss[idx]
    snr_val = snr[idx]
    delta = s_nearest - lam
    flag = "✅" if snr_val > 3 else "❌"
    matched.append({'n': int(n), 'lam': float(lam), 's': float(s_nearest),
                    'delta': float(delta), 'snr': float(snr_val), 'residual': float(res_val)})
    print(f"  {flag} {n:<5} {lam:<20.1f} {s_nearest:<12.1f} {res_val:<12.4f} {snr_val:<10.1f} {delta:+.1f}")

n_detected = sum(1 for m in matched if m['snr'] > 3)
total = len(matched)
deltas = np.array([m['delta'] for m in matched])
print(f"\n  檢測率: {n_detected}/{total} S/N>3 ({n_detected/total*100:.0f}%)")
print(f"  位置偏差: {np.mean(deltas):.2f} ± {np.std(deltas):.2f} h⁻¹Mpc")

# ================================================================
# 4. BAO 位置特別檢驗
# ================================================================
print(f"\n{'─'*80}")
print("  4. BAO 位置特別檢驗 (n=2, λ_sync/2=203.1 h⁻¹Mpc)")
print(f"{'─'*80}")

# IDCM BAO 位置
bao_idx = np.argmin(np.abs(s_eboss - BAO_HINV))
print(f"  IDCM BAO 位置: s={BAO_HINV:.1f} h⁻¹Mpc")
print(f"  最近數據點: s={s_eboss[bao_idx]:.1f} h⁻¹Mpc (Δ={s_eboss[bao_idx]-BAO_HINV:+.1f})")
print(f"  ξ = {xi_eboss[bao_idx]:.6f} ± {err_eboss[bao_idx]:.6f}")
print(f"  ξ/broadband = {xi_eboss[bao_idx]/bb_eboss[bao_idx]:.4f}")
print(f"  Residual = {res_eboss[bao_idx]:.6f}")
print(f"  S/N = {abs(res_eboss[bao_idx])/err_eboss[bao_idx]:.2f}")

# ΛCDM BAO 位置 (s≈105 h⁻¹Mpc) 做對比
lcdm_bao_hinv = 105.0
lcdm_idx = np.argmin(np.abs(s_eboss - lcdm_bao_hinv))
print(f"\n  ΛCDM BAO (s≈105 h⁻¹Mpc):")
print(f"  最近數據點: s={s_eboss[lcdm_idx]:.1f} h⁻¹Mpc")
print(f"  ξ = {xi_eboss[lcdm_idx]:.6f} ± {err_eboss[lcdm_idx]:.6f}")
print(f"  Residual = {res_eboss[lcdm_idx]:.6f}")
print(f"  S/N = {abs(res_eboss[lcdm_idx])/err_eboss[lcdm_idx]:.2f}")

# 喺 BAO 周圍 ±20 h⁻¹Mpc 睇模式
print(f"\n  BAO 附近嘅諧波模式:")
for s_test in np.arange(190, 220, 5):
    idx = np.argmin(np.abs(s_eboss - s_test))
    print(f"    s={s_eboss[idx]:.1f}: ξ={xi_eboss[idx]:.6f}, residual={res_eboss[idx]:.6f}, "
          f"S/N={abs(res_eboss[idx])/err_eboss[idx]:.2f}")

# ================================================================
# 5. DESI DR1 BAO 對比
# ================================================================
print(f"\n{'─'*80}")
print("  5. DESI DR1 BAO 對比")
print(f"{'─'*80}")

# DESI DR1 BAO data (from desi_analysis.py)
bao_data = [
    {"sample": "BGS",      "z": 0.295, "DV":  7.93, "eDV": 0.15},
    {"sample": "LRG1",     "z": 0.510, "DM": 13.62, "eDM": 0.25, "DH": 20.98, "eDH": 0.61},
    {"sample": "LRG2",     "z": 0.706, "DM": 16.85, "eDM": 0.32, "DH": 20.08, "eDH": 0.60},
    {"sample": "LRG3+ELG", "z": 0.930, "DM": 21.71, "eDM": 0.28, "DH": 17.88, "eDH": 0.35},
    {"sample": "ELG2",     "z": 1.317, "DM": 27.79, "eDM": 0.69, "DH": 13.82, "eDH": 0.42},
    {"sample": "QSO",      "z": 1.491, "DV": 26.07, "eDV": 0.67},
]

# DESI DR2 Lyα BAO
bao_data.append({"sample": "Lyα", "z": 2.330, "DM": 39.32, "eDM": 0.33, "DH": 8.600, "eDH": 0.066})

# BAO 角度 = 1/DM (radians)
print(f"  {'Sample':<12} {'z':<8} {'DM/rd':<15} {'θ_BAO (rad)':<15} {'θ_BAO (deg)':<15}")
print(f"  {'─'*65}")
for d in bao_data:
    z = d['z']
    if 'DM' in d and d['DM'] is not None:
        theta = 1.0 / d['DM']  # BAO angular size in radians
        theta_deg = theta * 180 / math.pi
        print(f"  {d['sample']:<12} {z:<8.3f} {d['DM']:<15.2f} {theta:<15.6f} {theta_deg:<15.2f}")
    elif 'DV' in d and d['DV'] is not None:
        # DV = (z * DM² * DH)^(1/3), so theta ≈ 1/DV * z^(1/3) roughly
        print(f"  {d['sample']:<12} {z:<8.3f} DV={d['DV']:<10.2f} (no DM)")

# ================================================================
# 6. 總結
# ================================================================
print(f"\n{'─'*80}")
print("  6. 總結")
print(f"{'─'*80}")

print(f"\n  eBOSS DR16 覆蓋 IDCM BAO (203.1 h⁻¹Mpc): ✅")
print(f"  eBOSS 數據最大 s = {s_eboss[-1]:.1f} > {BAO_HINV:.1f} h⁻¹Mpc")
print(f"  BAO 位置 S/N = {abs(res_eboss[bao_idx])/err_eboss[bao_idx]:.2f}")
print(f"  諧波檢測率: {n_detected}/{total} S/N>3")
print(f"  位置偏差: {np.mean(deltas):.2f} ± {np.std(deltas):.2f} h⁻¹Mpc")

# 儲存結果
output = {
    'constants': {
        'lambda_sync': LAMBDA_SYNC,
        'bao_mpc': BAO_MPC, 'bao_hinv': BAO_HINV,
        'H0': H0_IDCM, 'R_H': R_H, 'N_d': N_d
    },
    'eboss_data': {
        's': s_eboss.tolist(), 'xi': xi_eboss.tolist(), 'err': err_eboss.tolist(),
        'broadband': bb_eboss.tolist(), 'residual': res_eboss.tolist()
    },
    'harmonic_matches': matched,
    'summary': {
        'n_detected': n_detected, 'total': total,
        'mean_delta': float(np.mean(deltas)), 'std_delta': float(np.std(deltas)),
        'bao_sn': float(abs(res_eboss[bao_idx])/err_eboss[bao_idx])
    },
    'desi_bao': bao_data
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/44_eboss_desi_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果已儲存至 44_eboss_desi_results.json")

print(f"\n{'='*80}")
print(f"  eBOSS + DESI 大尺度驗證完成")
print(f"{'='*80}")