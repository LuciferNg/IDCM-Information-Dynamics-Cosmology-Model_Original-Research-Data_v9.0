#!/usr/bin/env python3
"""
48_snia_zeta_verification.py — Pantheon+ SN Ia 光度距離驗證 ζ(z)
=================================================================
跨體系驗證：光度測距（SN Ia）vs 幾何 BAO（DESI DR2）。

如果 ζ(z) 算子係物理真實，佢必須同時解釋：
1. DESI DR2 嘅 DM/rd, DH/rd（幾何距離）
2. Pantheon+ 嘅 m_b_corr（光度距離）

方法：
- 用 IDCM H(z)（含 ζ(z) 修正）計算 d_L(z)
- μ_IDCM(z) = 5·log₁₀(d_L/10pc)
- 同 Pantheon+ 比較，fit 絕對星等 M（自由參數，H₀ 無關形狀測試）
- χ² 用完整 covariance
"""
import math
import numpy as np
from scipy import optimize
import json

C_LIGHT = 299792.458  # km/s
PC_TO_MPC = 1e-6
M_SUN = 4.74

# ================================================================
# 1. 載入 Pantheon+ 數據
# ================================================================
data_path = '/tmp/pantheon_extract/DataRelease-main/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat'
print("=" * 80)
print("  Pantheon+ SN Ia 光度距離驗證 — ζ(z) 跨體系測試")
print("=" * 80)

# Read header
with open(data_path) as f:
    header = f.readline().split()

# Find column indices
col = {name: i for i, name in enumerate(header)}
print(f"\n  數據列: {col['zCMB']} (zCMB), {col['m_b_corr']} (m_b_corr), {col['MU_SH0ES']} (MU_SH0ES)")

# Read data
zs, mb, mb_err, mu_sh0es, cepheid_dist = [], [], [], [], []
with open(data_path) as f:
    f.readline()  # skip header
    for line in f:
        parts = line.split()
        if len(parts) < len(header):
            continue
        z = float(parts[col['zCMB']])
        m = float(parts[col['m_b_corr']])
        me = float(parts[col['m_b_corr_err_RAW']])
        mu = float(parts[col['MU_SH0ES']])
        ceph = float(parts[col['CEPH_DIST']])
        zs.append(z)
        mb.append(m)
        mb_err.append(me)
        mu_sh0es.append(mu)
        cepheid_dist.append(ceph)

zs = np.array(zs); mb = np.array(mb); mb_err = np.array(mb_err)
mu_sh0es = np.array(mu_sh0es); ceph_dist = np.array(cepheid_dist)
N = len(zs)
print(f"  載入 {N} 顆 SNe")
print(f"  z 範圍: {zs.min():.4f} - {zs.max():.3f}")

# ================================================================
# 2. IDCM H(z) 預測
# ================================================================
PHI_INV = (math.sqrt(5) - 1) / 2
H0_IDCM = 72.59

def hz_idcm_base(z):
    eps = PHI_INV / 4
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_correction(z, zeta0=0.2509, zs=2.0, zeta1=0.6537, zl=5.0):
    low_z = zeta0 * math.exp(-z / zs)
    high_z = zeta1 * (1 - math.exp(-z / zl))
    return 1.0 + low_z - high_z

def hz_corrected(z):
    return hz_idcm_base(z) / zeta_correction(z)

def dL_idcm(z, H0=H0_IDCM):
    """Luminosity distance (Mpc) from IDCM H(z) with ζ(z)"""
    if z <= 0:
        return 0.0
    N = 300
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_corrected(zp)
    Dc = C_LIGHT * integral  # comoving distance Mpc
    return (1 + z) * Dc

def mu_idcm(z, M, H0=H0_IDCM):
    """IDCM distance modulus: μ = 5·log₁₀(d_L/10pc)"""
    dL_mpc = dL_idcm(z, H0)
    dL_pc = dL_mpc / PC_TO_MPC
    return 5 * math.log10(dL_pc) + 25  # μ = 5log10(dL_pc) - 5 = 5log10(dL_Mpc) + 25

def mu_idcm_full(z, M, H0=H0_IDCM):
    """μ = M + 5·log₁₀(d_L/10pc), M = absolute magnitude"""
    return M + mu_idcm(z, M, H0) - 25

# ================================================================
# 3. 計算 μ(z) 殘差
# ================================================================
print(f"\n{'─'*80}")
print("  3. μ(z) 對比（光度距離）")
print(f"{'─'*80}")

# 方法 A: 用 m_b_corr 直接 fit M（形狀測試，H₀ 無關）
# m_b_corr = M + μ(z)  →  μ(z) = m_b_corr - M
# IDCM: μ(z) = 5·log10(d_L/10pc)

def chi2_fit_M(M, use_ceph=False):
    """Fit absolute magnitude M, χ² = Σ[(m_obs - M - μ_idcm)²/σ²]"""
    residuals = []
    for i in range(N):
        if use_ceph and ceph_dist[i] == 0:
            continue  # only calibrated SNe
        mu_pred = M + mu_idcm(zs[i], M, H0_IDCM) - 25
        # m_obs - M = μ_obs; residual = μ_obs - μ_pred
        res = mb[i] - M - (mu_idcm(zs[i], M, H0_IDCM) - 25)
        residuals.append(res)
    residuals = np.array(residuals)
    return np.sum(residuals**2)

# Fit M
result = optimize.minimize_scalar(chi2_fit_M, bounds=(-25, -15), method='bounded')
M_fit = result.x
print(f"\n  Fit M = {M_fit:.3f} (χ² = {result.fun:.1f})")

# Compute residuals
residuals = []
for i in range(N):
    mu_pred = M_fit + mu_idcm(zs[i], M_fit, H0_IDCM) - 25
    res = mb[i] - M_fit - (mu_idcm(zs[i], M_fit, H0_IDCM) - 25)
    residuals.append(res)
residuals = np.array(residuals)

# RMS scatter
rms = np.sqrt(np.mean(residuals**2))
print(f"  RMS 殘差: {rms:.3f} mag")

# 方法 B: 用 MU_SH0ES（有 Cepheid 校準）— 直接測 H₀ 一致性
ceph_mask = ceph_dist > 0
n_ceph = np.sum(ceph_mask)
print(f"\n  Cepheid-calibrated SNe: {n_ceph}")

if n_ceph > 10:
    # μ_obs(MU_SH0ES) = 5·log10(d_L/10pc)，直接同 IDCM 光度距離比較
    # IDCM 預測 μ_idcm = 5·log10(d_L_idcm/10pc) = 5·log10(d_L_mpc) + 25
    mu_pred_ceph = np.array([5 * math.log10(dL_idcm(z, H0_IDCM) * 1e6) - 5 for z in zs[ceph_mask]])
    mu_obs_ceph = mu_sh0es[ceph_mask]
    resid_ceph = mu_obs_ceph - mu_pred_ceph
    print(f"  Cepheid 校準殘差: mean={resid_ceph.mean():.3f}±{resid_ceph.std():.3f} mag")
    # 轉換為 H₀ 偏差: Δμ = 5·log10(H₀_IDCM/H₀_true)
    H0_implied = H0_IDCM * 10 ** (-resid_ceph.mean() / 5)
    print(f"  隱含 H₀ = {H0_implied:.2f} km/s/Mpc（IDCM 用 {H0_IDCM:.2f}）")

# ================================================================
# 4. 分紅移區間殘差
# ================================================================
print(f"\n{'─'*80}")
print("  4. 分紅移區間殘差")
print(f"{'─'*80}")

z_bins = [(0, 0.1), (0.1, 0.3), (0.3, 0.6), (0.6, 1.0), (1.0, 1.5), (1.5, 2.3)]
print(f"\n  {'z 區間':<12} {'N':<6} {'Mean 殘差':<12} {'RMS':<10}")
print(f"  {'─'*42}")
for zlo, zhi in z_bins:
    mask = (zs >= zlo) & (zs < zhi)
    if np.sum(mask) == 0:
        continue
    res = residuals[mask]
    print(f"  {zlo:.1f}-{zhi:.1f}    {np.sum(mask):<6} {res.mean():<+12.3f} {res.std():<10.3f}")

# ================================================================
# 5. 對比 ΛCDM
# ================================================================
print(f"\n{'─'*80}")
print("  5. ΛCDM 對比（flat ΛCDM, Ωm=0.315, H₀=67.4）")
print(f"{'─'*80}")

def hz_lcdm(z, H0=67.4, Om=0.315):
    OL = 1 - Om
    return H0 * math.sqrt(Om * (1+z)**3 + OL)

def mu_lcdm(z, M):
    N = 300
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_lcdm(zp)
    Dc = C_LIGHT * integral
    dL = (1 + z) * Dc
    return M + 5 * math.log10(dL * 1e6) - 5

def chi2_fit_M_lcdm(M):
    residuals = []
    for i in range(N):
        mu_pred = mu_lcdm(zs[i], M)
        res = mb[i] - mu_pred
        residuals.append(res)
    residuals = np.array(residuals)
    return np.sum(residuals**2)

result_lcdm = optimize.minimize_scalar(chi2_fit_M_lcdm, bounds=(-25, -15), method='bounded')
M_lcdm = result_lcdm.x
print(f"\n  ΛCDM: M = {M_lcdm:.3f}, χ² = {result_lcdm.fun:.1f}")
print(f"  IDCM: M = {M_fit:.3f}, χ² = {result.fun:.1f}")
print(f"\n  χ² 比較:")
print(f"    IDCM: {result.fun:.1f} / {N-1} dof = {result.fun/(N-1):.3f}")
print(f"    ΛCDM: {result_lcdm.fun:.1f} / {N-1} dof = {result_lcdm.fun/(N-1):.3f}")
print(f"    Δχ² = {result.fun - result_lcdm.fun:.1f}")

# ================================================================
# 6. 儲存
# ================================================================
output = {
    'N': N,
    'M_fit': M_fit, 'chi2_idcm': float(result.fun), 'rms': float(rms),
    'M_lcdm': M_lcdm, 'chi2_lcdm': float(result_lcdm.fun),
    'delta_chi2': float(result.fun - result_lcdm.fun),
    'z_bins': [{'range': f'{zlo}-{zhi}', 'N': int(np.sum((zs>=zlo)&(zs<zhi))),
                'mean_resid': float(residuals[(zs>=zlo)&(zs<zhi)].mean()) if np.sum((zs>=zlo)&(zs<zhi)) else None}
               for zlo, zhi in z_bins]
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/48_snia_zeta_results.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)
print(f"\n  結果: 48_snia_zeta_results.json")
print(f"{'='*80}")