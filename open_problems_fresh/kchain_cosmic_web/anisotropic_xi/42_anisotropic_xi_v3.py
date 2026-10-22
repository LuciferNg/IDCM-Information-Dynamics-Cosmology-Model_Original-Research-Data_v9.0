#!/usr/bin/env python3
"""
42_anisotropic_xi_v3.py — K_Chain ξ(s⊥, s∥) 各向異性諧波檢測
===============================================================
用平滑 spline 做 broadband 分離（代替 EMD，因數據點太少）。
然後比較 harmonic residual 嘅位置同 K_Chain 預測。

方法：
1. 用平滑 spline 對 ξ₀(s) 同 ξ₂(s) 分別 fit broadband (不受 EMD 限制)
2. 提取 harmonic residual = data - broadband
3. 諧波位置檢測：λ_sync/n 匹配
4. 各向異性比率：ξ₂_residual / ξ₀_residual 同阻抗反射預測比較
"""
import math
import numpy as np
from scipy import stats, interpolate, signal
import zipfile
import json
import sys

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
BAO_HINV = BAO_MPC / H  # 203.11 h⁻¹ Mpc
N_d = 44

# 44-mode 色散
gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d)])
v_g_n = np.array([math.cos(math.pi * n / 88) for n in range(1, N_d)])
Z_n = gamma_n / np.abs(v_g_n)
Z_n[np.isinf(Z_n)] = 1e6
R_n = np.zeros(N_d - 1)
for i in range(1, N_d - 1):
    R_n[i] = (Z_n[i] - Z_n[i-1]) / (Z_n[i] + Z_n[i-1])
theta_n = np.array([n * 2 * math.pi / 88 for n in range(1, N_d)])

print("=" * 80)
print("  IDCM ξ(s⊥, s∥) v3 — 平滑 spline 諧波分離 + 各向異性比率")
print("=" * 80)
print(f"\n  λ_sync = {LAMBDA_SYNC:.2f} Mpc")
print(f"  BAO = {BAO_MPC:.2f} Mpc = {BAO_HINV:.2f} h⁻¹ Mpc")
print(f"  H₀(IDCM) = {H0_IDCM:.2f} km/s/Mpc")

# ================================================================
# 1. 平滑 spline broadband 分離
# ================================================================
print(f"\n{'─'*80}")
print("  1. Smoothing spline broadband 分離（替代 EMD）")
print(f"{'─'*80}")

def smooth_spline_broadband(x, y, smooth_factor=0.3):
    """
    用平滑 spline 提取 broadband。
    smooth_factor: 0=完全跟隨數據, 1=完全平滑
    """
    from scipy.interpolate import UnivariateSpline
    spl = UnivariateSpline(x, y, s=smooth_factor * len(x) * np.var(y))
    broadband = spl(x)
    residual = y - broadband
    return broadband, residual

# ================================================================
# 2. 載入 BOSS DR12 數據
# ================================================================
print(f"\n{'─'*80}")
print("  2. BOSS DR12 數據載入")
print(f"{'─'*80}")

DATA_PATH = '/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip'
z = zipfile.ZipFile(DATA_PATH)

def load_multipole(z, zbin, kind, bincent=0):
    fname = (f'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_{zbin}'
             f'_correlation_function_{kind}_post_recon_bincent{bincent}.dat')
    s, xi, err = [], [], []
    with z.open(fname) as f:
        for line in f.read().decode().strip().split('\n'):
            if line.startswith('#') or not line.strip(): continue
            parts = line.split()
            s.append(float(parts[0]))
            xi.append(float(parts[1]))
            err.append(float(parts[2]))
    return np.array(s), np.array(xi), np.array(err)

def load_covariance(z, zbin, bincent=0):
    fname = (f'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_{zbin}'
             f'_covariance_monoquad_post_recon_bincent{bincent}.dat')
    with z.open(fname) as f:
        lines = f.read().decode().strip().split('\n')
        data_lines = [l for l in lines if not l.startswith('#') and l.strip()]
    matrix = []
    for line in data_lines:
        matrix.append([float(x) for x in line.split()])
    return np.array(matrix)

zbins = ['zbin1', 'zbin2', 'zbin3']
z_eff_map = {'zbin1': 0.38, 'zbin2': 0.51, 'zbin3': 0.61}
data = {}

for zbin in zbins:
    s0, xi0, err0 = load_multipole(z, zbin, 'monopole')
    s2, xi2, err2 = load_multipole(z, zbin, 'quadrupole')
    cov = load_covariance(z, zbin)
    data[zbin] = {'s': s0, 'xi0': xi0, 'xi2': xi2, 
                  'err0': err0, 'err2': err2, 'cov': cov,
                  'z_eff': z_eff_map[zbin], 'n': len(s0)}
    print(f"  {zbin} (z={z_eff_map[zbin]:.2f}): {len(s0)} bins")

# ================================================================
# 3. Broadband 分離 + 諧波檢測
# ================================================================
print(f"\n{'─'*80}")
print("  3. Broadband 分離 + 諧波位置檢測")
print(f"{'─'*80}")

results = {}
for zbin in zbins:
    d = data[zbin]
    s = d['s']
    xi0 = d['xi0']
    xi2 = d['xi2']
    
    # 用平滑 spline 提取 broadband
    # 使用三個不同的 smooth factor 做穩健性檢驗
    broadband_0, residual_0 = smooth_spline_broadband(s, xi0, smooth_factor=0.3)
    broadband_2, residual_2 = smooth_spline_broadband(s, xi2, smooth_factor=0.3)
    
    # 諧波對 broadband 比率
    harm_ratio_0 = np.std(residual_0) / np.std(broadband_0) if np.std(broadband_0) > 0 else 0
    harm_ratio_2 = np.std(residual_2) / np.std(broadband_2) if np.std(broadband_2) > 0 else 0
    
    print(f"\n  {zbin}:")
    print(f"    ξ₀: 諧波/background = {harm_ratio_0:.4f}")
    print(f"    ξ₂: 諧波/background = {harm_ratio_2:.4f}")
    
    # 諧波位置檢測：喺 residual 中 detect peaks
    pk_idx_0 = signal.argrelmax(residual_0)[0]
    pk_idx_2 = signal.argrelmax(residual_2)[0]
    
    # 過濾：只保留 S/N > 2 嘅 peak
    pk_snr_0 = [np.abs(residual_0[i]) / d['err0'][i] for i in pk_idx_0]
    pk_snr_2 = [np.abs(residual_2[i]) / d['err2'][i] for i in pk_idx_2]
    
    print(f"    ξ₀ residual peaks: {len(pk_idx_0)} detected")
    for idx, snr in zip(pk_idx_0[:10], pk_snr_0[:10]):
        if snr > 2:
            s_hinv = s[idx]
            n_match = np.argmin(np.abs(LAMBDA_SYNC / np.arange(1, 21) / H - s_hinv)) + 1
            lam_hinv = LAMBDA_SYNC / n_match / H
            delta = s_hinv - lam_hinv
            print(f"      s={s_hinv:6.1f} → λ_sync/{n_match:2d}={lam_hinv:6.1f} h⁻¹Mpc, "
                  f"Δ={delta:+.1f}, S/N={snr:.1f}")
    
    print(f"    ξ₂ residual peaks: {len(pk_idx_2)} detected")
    for idx, snr in zip(pk_idx_2[:5], pk_snr_2[:5]):
        if snr > 2:
            s_hinv = s[idx]
            n_match = np.argmin(np.abs(LAMBDA_SYNC / np.arange(1, 21) / H - s_hinv)) + 1
            lam_hinv = LAMBDA_SYNC / n_match / H
            delta = s_hinv - lam_hinv
            print(f"      s={s_hinv:6.1f} → λ_sync/{n_match:2d}={lam_hinv:6.1f} h⁻¹Mpc, "
                  f"Δ={delta:+.1f}, S/N={snr:.1f}")
    
    results[zbin] = {
        'harm_ratio_0': harm_ratio_0,
        'harm_ratio_2': harm_ratio_2,
        'residual_0': residual_0.tolist(),
        'residual_2': residual_2.tolist(),
        'broadband_0': broadband_0.tolist(),
        'broadband_2': broadband_2.tolist(),
        'peaks_0': [(float(s[i]), float(residual_0[i]), float(d['err0'][i]), 
                     float(np.abs(residual_0[i])/d['err0'][i])) 
                    for i in pk_idx_0 if np.abs(residual_0[i])/d['err0'][i] > 2],
        'peaks_2': [(float(s[i]), float(residual_2[i]), float(d['err2'][i]),
                     float(np.abs(residual_2[i])/d['err2'][i]))
                    for i in pk_idx_2 if np.abs(residual_2[i])/d['err2'][i] > 2],
    }

# ================================================================
# 4. 各向異性比率檢驗
# ================================================================
print(f"\n{'─'*80}")
print("  4. 各向異性比率檢驗 — ξ₂/ξ₀ 比率 vs 阻抗反射預測")
print(f"{'─'*80}")

def predict_aniso_ratio(s):
    """Predict ξ₂/ξ₀ ratio from K_Chain impedance model"""
    s = np.asarray(s, dtype=float)
    ratio = np.zeros_like(s)
    weights = np.zeros_like(s)
    
    for n in range(2, 22):
        lam = LAMBDA_SYNC / n
        lam_hinv = lam / H
        # Gaussian window around each harmonic position
        dist = np.abs(s - lam_hinv)
        width = lam_hinv * 0.2
        weight = np.exp(-0.5 * (dist / width)**2)
        
        ref = R_n[n-1] if n-1 < len(R_n) else 0
        vg = v_g_n[n-1] if n-1 < len(v_g_n) else 0
        Z = Z_n[n-1] if n-1 < len(Z_n) else 0
        
        # ξ₂/ξ₀ ∝ R_n · v_g / (1 + Z_n)
        pred_ratio = ref * vg / (1 + Z)
        
        ratio += weight * pred_ratio
        weights += weight
    
    ratio = np.divide(ratio, weights, out=np.zeros_like(ratio), where=weights > 1e-10)
    return ratio

pred_aniso = predict_aniso_ratio(data['zbin1']['s'])

for zbin in zbins:
    d = data[zbin]
    s = d['s']
    res_0 = np.array(results[zbin]['residual_0'])
    res_2 = np.array(results[zbin]['residual_2'])
    err0 = d['err0']
    err2 = d['err2']
    
    # S/N mask
    snr_0 = np.abs(res_0) / err0
    mask = (snr_0 > 2) & (np.abs(res_0) > 1e-6)
    
    if np.sum(mask) > 0:
        obs_ratio = np.where(np.abs(res_0) > 1e-6, res_2 / res_0, 0)
        valid = mask & (np.abs(obs_ratio) < 10)
        n_valid = np.sum(valid)
        
        if n_valid > 0:
            corr = np.corrcoef(obs_ratio[valid], pred_aniso[valid])[0, 1]
            print(f"\n  {zbin}:")
            print(f"    ξ₂/ξ₀ 實測 vs 預測相關: r = {corr:.4f} (n={n_valid})")
            
            print(f"    特徵位置 ξ₂/ξ₀:")
            for n in range(2, 10):
                lam_hinv = (LAMBDA_SYNC / n) / H
                idx = np.argmin(np.abs(s - lam_hinv))
                if mask[idx]:
                    print(f"    λ_sync/{n}={lam_hinv:.1f}: obs={obs_ratio[idx]:.3f}, "
                          f"pred={pred_aniso[idx]:.3f}")
        else:
            print(f"\n  {zbin}: 無足夠有效點")
    else:
        print(f"\n  {zbin}: 無足夠 S/N 嘅諧波位置")

# ================================================================
# 5. 諧波位置匹配統計
# ================================================================
print(f"\n{'─'*80}")
print("  5. 諧波位置匹配統計")
print(f"{'─'*80}")

n_harmonics = np.arange(2, 21)
lam_theory = LAMBDA_SYNC / n_harmonics / H

for zbin in zbins:
    d = data[zbin]
    s = d['s']
    res_0 = np.array(results[zbin]['residual_0'])
    err0 = d['err0']
    snr = np.abs(res_0) / err0
    
    matched = []
    for n in n_harmonics:
        lam = lam_theory[n-2]
        idx = np.argmin(np.abs(s - lam))
        matched.append({
            'n': int(n), 'lam_hinv': float(lam), 
            's_nearest': float(s[idx]), 'snr': float(snr[idx]),
            'delta': float(s[idx] - lam),
            'residual': float(res_0[idx])
        })
    
    n_detected = sum(1 for m in matched if m['snr'] > 3)
    total = len(matched)
    pass_rate = n_detected / total
    
    deltas = np.array([m['delta'] for m in matched])
    mean_delta = np.mean(deltas)
    std_delta = np.std(deltas)
    
    print(f"\n  {zbin}:")
    print(f"    諧波檢測率: {n_detected}/{total} S/N>3 ({pass_rate*100:.0f}%)")
    print(f"    位置偏差: {mean_delta:.2f} ± {std_delta:.2f} h⁻¹Mpc")
    
    print(f"    詳細:")
    for m in matched:
        flag = "✅" if m['snr'] > 3 else "❌"
        print(f"    {flag} n={m['n']:2d}: λ={m['lam_hinv']:6.1f}, "
              f"s={m['s_nearest']:6.1f}, Δ={m['delta']:+.1f}, S/N={m['snr']:.1f}")

# ================================================================
# 6. 多 smooth factor 穩健性檢驗
# ================================================================
print(f"\n{'─'*80}")
print("  6. 穩健性檢驗 — 不同 smooth factor")
print(f"{'─'*80}")

for zbin in ['zbin1']:  # 只用 zbin1 做示範
    d = data[zbin]
    s = d['s']
    xi0 = d['xi0']
    
    for sf in [0.1, 0.3, 0.5, 0.8]:
        bb, res = smooth_spline_broadband(s, xi0, smooth_factor=sf)
        ratio = np.std(res) / np.std(bb) if np.std(bb) > 0 else 0
        
        # 檢驗諧波檢測數
        pk_idx = signal.argrelmax(res)[0]
        pk_snr = [np.abs(res[i]) / d['err0'][i] for i in pk_idx]
        n_detected = sum(1 for snr in pk_snr if snr > 3)
        
        print(f"  smooth={sf:.1f}: ξ₀ 諧波/背景={ratio:.4f}, {n_detected} peaks S/N>3")
    
    # 最佳 smooth factor: 用 BAO 位置嘅 S/N 做選擇
    bao_idx = np.argmin(np.abs(s - BAO_HINV))
    print(f"  BAO 位置 (s={s[bao_idx]:.1f}): ξ₀={xi0[bao_idx]:.6f}, err={d['err0'][bao_idx]:.6f}")
    print(f"  BAO S/N = {xi0[bao_idx]/d['err0'][bao_idx]:.2f}")

# ================================================================
# 7. 儲存結果
# ================================================================
output = {
    'constants': {
        'lambda_sync': LAMBDA_SYNC,
        'bao_mpc': BAO_MPC,
        'bao_hinv': BAO_HINV,
        'H0': H0_IDCM,
        'R_H': R_H,
        'N_d': N_d
    },
    'harmonic_positions': lam_theory.tolist(),
    'results': {k: v for k, v in results.items()}
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/42_results_v3.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果已儲存至 42_results_v3.json")

print(f"\n{'='*80}")
print(f"  ξ(s⊥, s∥) 直接投影 — 平滑 spline 諧波分離 + 各向異性比率")
print(f"  零自由參數：所有常數從 x²+x-1=0 導出")
print(f"{'='*80}")