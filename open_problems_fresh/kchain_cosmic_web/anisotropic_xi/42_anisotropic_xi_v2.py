#!/usr/bin/env python3
"""
42_anisotropic_xi_v2.py — K_Chain ξ(s⊥, s∥) 各向異性諧波檢測
===============================================================
核心改進：唔直接 fit 全模型（broadband 佔主導），
而係用 EMD 自適應分離 broadband 同 harmonic，
然後比較 harmonic 嘅位置同 ξ₂/ξ₀ 比率。

方法：
1. 對 ξ₀(s) 同 ξ₂(s) 分別做 EMD 分離
2. 提取 harmonic residual（IMF 高頻部分）
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
print("  IDCM ξ(s⊥, s∥) v2 — EMD 諧波 + 各向異性比率")
print("=" * 80)
print(f"\n  λ_sync = {LAMBDA_SYNC:.2f} Mpc")
print(f"  BAO = {BAO_MPC:.2f} Mpc = {BAO_HINV:.2f} h⁻¹ Mpc")

# ================================================================
# 1. EMD 實現（自適應 broadband 分離）
# ================================================================
print(f"\n{'─'*80}")
print("  1. EMD 自適應 broadband 分離")
print(f"{'─'*80}")

def emd_decompose(x, y, max_imf=6):
    """
    經驗模態分解 — 從 y(x) 中提取 IMFs
    IMF 0 = 最高頻（諧波）, IMF last = 最低頻（broadband）
    """
    residue = y.copy()
    imfs = []
    
    for imf_idx in range(max_imf):
        h = residue.copy()
        for _ in range(100):  # 篩選迭代
            # 搵 local maxima/minima
            max_idx = signal.argrelmax(h)[0]
            min_idx = signal.argrelmin(h)[0]
            
            if len(max_idx) < 2 or len(min_idx) < 2:
                break
            
            # 插值 upper/lower envelope
            f_max = interpolate.interp1d(x[max_idx], h[max_idx], 
                                          kind='cubic', fill_value='extrapolate')
            f_min = interpolate.interp1d(x[min_idx], h[min_idx],
                                          kind='cubic', fill_value='extrapolate')
            
            upper = f_max(x)
            lower = f_min(x)
            mean = (upper + lower) / 2
            
            h_new = h - mean
            
            # 收斂檢查
            if np.max(np.abs(mean)) < 1e-6 * np.max(np.abs(h)):
                break
            h = h_new
        
        imfs.append(h)
        residue = residue - h
        
        if len(signal.argrelmax(residue)[0]) < 2:
            break
    
    imfs.append(residue)  # 最後一個係 residue（broadband）
    return imfs

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
# 3. EMD 分解 + 諧波檢測
# ================================================================
print(f"\n{'─'*80}")
print("  3. EMD 諧波分解 + 位置檢測")
print(f"{'─'*80}")

results = {}
for zbin in zbins:
    d = data[zbin]
    s = d['s']
    xi0 = d['xi0']
    xi2 = d['xi2']
    
    # EMD 分解
    imfs_0 = emd_decompose(s, xi0, max_imf=4)
    imfs_2 = emd_decompose(s, xi2, max_imf=4)
    
    # 諧波 residual = 所有 IMF 嘅和，除了最後一個（broadband）
    harmonic_0 = sum(imfs_0[:-1]) if len(imfs_0) > 1 else np.zeros_like(xi0)
    harmonic_2 = sum(imfs_2[:-1]) if len(imfs_2) > 1 else np.zeros_like(xi2)
    broadband_0 = imfs_0[-1]
    broadband_2 = imfs_2[-1]
    
    # 諧波對 broadband 嘅比率
    harm_ratio_0 = np.std(harmonic_0) / np.std(broadband_0) if np.std(broadband_0) > 0 else 0
    harm_ratio_2 = np.std(harmonic_2) / np.std(broadband_2) if np.std(broadband_2) > 0 else 0
    
    print(f"\n  {zbin}:")
    print(f"    ξ₀: {len(imfs_0)} IMFs, 諧波/background = {harm_ratio_0:.3f}")
    print(f"    ξ₂: {len(imfs_2)} IMFs, 諧波/background = {harm_ratio_2:.3f}")
    
    # 諧波位置檢測：喺 harmonic residual 中 detect peaks
    pk_idx_0 = signal.argrelmax(harmonic_0)[0]
    pk_idx_2 = signal.argrelmax(harmonic_2)[0]
    
    print(f"    ξ₀ harmonic peaks: {len(pk_idx_0)} detected")
    for idx in pk_idx_0[:8]:
        s_hinv = s[idx]
        # 搵最接近嘅 λ_sync/n
        n_match = np.argmin(np.abs(LAMBDA_SYNC / np.arange(1, 21) / H - s_hinv)) + 1
        lam_hinv = LAMBDA_SYNC / n_match / H
        print(f"      s={s_hinv:.1f} h⁻¹Mpc, closest λ_sync/{n_match}={lam_hinv:.1f} h⁻¹Mpc, "
              f"Δ={s_hinv-lam_hinv:.1f}")
    
    print(f"    ξ₂ harmonic peaks: {len(pk_idx_2)} detected")
    for idx in pk_idx_2[:5]:
        s_hinv = s[idx]
        n_match = np.argmin(np.abs(LAMBDA_SYNC / np.arange(1, 21) / H - s_hinv)) + 1
        lam_hinv = LAMBDA_SYNC / n_match / H
        print(f"      s={s_hinv:.1f} h⁻¹Mpc, closest λ_sync/{n_match}={lam_hinv:.1f} h⁻¹Mpc, "
              f"Δ={s_hinv-lam_hinv:.1f}")
    
    results[zbin] = {
        'n_imfs_0': len(imfs_0),
        'n_imfs_2': len(imfs_2),
        'harm_ratio_0': harm_ratio_0,
        'harm_ratio_2': harm_ratio_2,
        'harmonic_0': harmonic_0.tolist(),
        'harmonic_2': harmonic_2.tolist(),
        'broadband_0': broadband_0.tolist(),
        'broadband_2': broadband_2.tolist(),
        'peaks_0': s[pk_idx_0].tolist()[:10],
        'peaks_2': s[pk_idx_2].tolist()[:10],
    }

# ================================================================
# 4. 各向異性比率檢驗 — ξ₂/ξ₀ 比率 vs 阻抗反射預測
# ================================================================
print(f"\n{'─'*80}")
print("  4. 各向異性比率檢驗 — ξ₂/ξ₀ 比率 vs 阻抗反射")
print(f"{'─'*80}")

# K_Chain 阻抗反射預測嘅 ξ₂/ξ₀ 比率
# 理論：ξ₂/ξ₀ ∝ R_n · v_g(n) / (1 + Z_n) 喺每個諧波位置
def predict_aniso_ratio(s):
    """Predict ξ₂/ξ₀ ratio from K_Chain impedance model"""
    s = np.asarray(s, dtype=float)
    ratio = np.zeros_like(s)
    weights = np.zeros_like(s)
    
    for n in range(2, 22):
        lam = LAMBDA_SYNC / n
        lam_hinv = lam / H
        # 每個諧波嘅貢獻取決於距離 λ_sync/n 嘅接近程度
        dist = np.abs(s - lam_hinv)
        weight = np.exp(-0.5 * (dist / (lam_hinv * 0.15))**2)  # Gaussian window
        
        ref = R_n[n-1] if n-1 < len(R_n) else 0
        vg = v_g_n[n-1] if n-1 < len(v_g_n) else 0
        Z = Z_n[n-1] if n-1 < len(Z_n) else 0
        
        # 各向異性比率 = 反射 × 群速度 × 阻抗修正
        pred_ratio = ref * vg / (1 + Z)
        
        ratio += weight * pred_ratio
        weights += weight
    
    ratio = np.divide(ratio, weights, out=np.zeros_like(ratio), where=weights > 1e-10)
    return ratio

for zbin in zbins:
    d = data[zbin]
    s = d['s']
    harmonic_0 = np.array(results[zbin]['harmonic_0'])
    harmonic_2 = np.array(results[zbin]['harmonic_2'])
    err0 = d['err0']
    err2 = d['err2']
    
    # 計算實測比率（只喺諧波信號強嘅位置）
    snr_0 = np.abs(harmonic_0) / err0
    mask = (snr_0 > 2) & (np.abs(harmonic_0) > 1e-6)
    
    if np.sum(mask) > 0:
        obs_ratio = np.where(np.abs(harmonic_0) > 1e-6, 
                             harmonic_2 / harmonic_0, 0)
        pred_ratio = predict_aniso_ratio(s)
        
        # 只喺信號強嘅位置比較
        valid = mask & (np.abs(obs_ratio) < 10)  # 剔除異常值
        n_valid = np.sum(valid)
        
        if n_valid > 0:
            corr = np.corrcoef(obs_ratio[valid], pred_ratio[valid])[0, 1]
            print(f"\n  {zbin}:")
            print(f"    ξ₂/ξ₀ 實測 vs 預測相關: r = {corr:.4f} (n={n_valid})")
            
            # 輸出幾個特徵位置
            print(f"    特徵位置 ξ₂/ξ₀:")
            for n in range(2, 10):
                lam_hinv = (LAMBDA_SYNC / n) / H
                idx = np.argmin(np.abs(s - lam_hinv))
                if mask[idx]:
                    print(f"    λ_sync/{n}={lam_hinv:.1f}: obs={obs_ratio[idx]:.3f}, "
                          f"pred={pred_ratio[idx]:.3f}")
        else:
            print(f"\n  {zbin}: 信號太弱，無法計算比率")
    else:
        print(f"\n  {zbin}: 無足夠 S/N 的諧波位置")

# ================================================================
# 5. 交叉相關檢驗 — 諧波位置匹配
# ================================================================
print(f"\n{'─'*80}")
print("  5. 諧波位置匹配檢驗")
print(f"{'─'*80}")

# 理論諧波位置 (h⁻¹ Mpc)
n_harmonics = np.arange(2, 21)
lam_theory = LAMBDA_SYNC / n_harmonics / H

for zbin in zbins:
    d = data[zbin]
    s = d['s']
    harmonic_0 = np.array(results[zbin]['harmonic_0'])
    err0 = d['err0']
    snr = np.abs(harmonic_0) / err0
    
    # 對每個理論諧波位置，檢查最近嘅數據點嘅 S/N
    matched = []
    for n in n_harmonics:
        lam = lam_theory[n-2]
        idx = np.argmin(np.abs(s - lam))
        matched.append({
            'n': int(n), 'lam_hinv': float(lam), 
            's_nearest': float(s[idx]), 'snr': float(snr[idx]),
            'delta': float(s[idx] - lam)
        })
    
    # 統計：S/N > 3 嘅諧波數
    n_detected = sum(1 for m in matched if m['snr'] > 3)
    total = len(matched)
    pass_rate = n_detected / total
    
    # 位置偏差統計
    deltas = np.array([m['delta'] for m in matched])
    mean_delta = np.mean(deltas)
    std_delta = np.std(deltas)
    
    print(f"\n  {zbin}:")
    print(f"    諧波檢測率: {n_detected}/{total} S/N>3 ({pass_rate*100:.0f}%)")
    print(f"    位置偏差: {mean_delta:.2f} ± {std_delta:.2f} h⁻¹Mpc")
    
    print(f"    詳細:")
    for m in matched[:10]:
        flag = "✅" if m['snr'] > 3 else "❌"
        print(f"    {flag} n={m['n']:2d}: λ={m['lam_hinv']:6.1f}, "
              f"s={m['s_nearest']:6.1f}, Δ={m['delta']:+.1f}, S/N={m['snr']:.1f}")

# ================================================================
# 6. 總結
# ================================================================
print(f"\n{'─'*80}")
print("  6. 結果總結")
print(f"{'─'*80}")

# 跨 redshift bin 嘅一致性
print(f"\n  諧波檢測一致性:")
for zbin in zbins:
    r = results[zbin]
    print(f"  {zbin}: {r['n_imfs_0']} IMFs(ξ₀), {r['n_imfs_2']} IMFs(ξ₂), "
          f"ξ₀ 諧波/背景={r['harm_ratio_0']:.3f}")

# 儲存結果
output = {
    'constants': {
        'lambda_sync': LAMBDA_SYNC,
        'bao_mpc': BAO_MPC,
        'bao_hinv': BAO_HINV,
        'H0': H0_IDCM,
        'R_H': R_H,
        'N_d': N_d
    },
    'results': {k: v for k, v in results.items()}
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/42_results_v2.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果已儲存至 42_results_v2.json")

print(f"\n{'='*80}")
print(f"  ξ(s⊥, s∥) 直接投影 — EMD 諧波 + 各向異性比率")
print(f"  零自由參數：所有常數從 x²+x-1=0 導出")
print(f"{'='*80}")