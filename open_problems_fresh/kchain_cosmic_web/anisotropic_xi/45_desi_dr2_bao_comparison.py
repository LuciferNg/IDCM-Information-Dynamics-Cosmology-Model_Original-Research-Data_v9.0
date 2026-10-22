#!/usr/bin/env python3
"""
45_desi_dr2_bao_comparison.py — DESI DR2 BAO vs IDCM 預測
===========================================================
比較 DESI DR2 BAO 嘅 DM/rd, DH/rd 測量值同 IDCM 預測。

IDCM 預測方法：
- 唔用 ΛCDM 嘅 FLRW 幾何
- 直接用 K_Chain 嘅色散關係 γ_n = 4 sin²(πn/88)
- BAO 角度從 K_Chain 諧波投影導出
- 距離尺度 = λ_sync/2 = 147.44 Mpc
"""
import math
import numpy as np
from scipy import stats
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
BAO_SCALE = LAMBDA_SYNC / 2  # 147.44 Mpc = IDCM BAO physical scale

print("=" * 80)
print("  DESI DR2 BAO vs IDCM 預測比較")
print("=" * 80)
print(f"\n  IDCM 參數:")
print(f"  H₀ = {H0_IDCM:.2f} km/s/Mpc")
print(f"  R_H = {R_H:.2f} Mpc")
print(f"  λ_sync = {LAMBDA_SYNC:.2f} Mpc")
print(f"  BAO scale = {BAO_SCALE:.2f} Mpc")

# ================================================================
# 1. 載入 DESI DR2 BAO 數據
# ================================================================
print(f"\n{'─'*80}")
print("  1. DESI DR2 BAO 數據")
print(f"{'─'*80}")

# 從 GitHub 下載嘅數據
# 格式: [z, value, quantity]
desi_data = [
    (0.295, 7.94167639, 'DV'),
    (0.510, 13.58758434, 'DM'),
    (0.510, 21.86294686, 'DH'),
    (0.706, 17.35069094, 'DM'),
    (0.706, 19.45534918, 'DH'),
    (0.934, 21.57563956, 'DM'),
    (0.934, 17.64149464, 'DH'),
    (1.321, 27.60085612, 'DM'),
    (1.321, 14.17602155, 'DH'),
    (1.484, 30.51190063, 'DM'),
    (1.484, 12.81699964, 'DH'),
    (2.33, 38.98897396, 'DM'),
    (2.33, 8.63154567, 'DH'),
]

# Covariance matrix (13×13, diagonal blocks for each tracer)
# From desi_ALL_GCcomb_cov.txt
cov_raw = [
    [5.78998687e-03, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2.83473742e-02, -3.26062007e-02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, -3.26062007e-02, 1.83928040e-01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 3.23752442e-02, -2.37445646e-02, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -2.37445646e-02, 1.11469198e-01, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2.61732816e-02, -1.12938006e-02, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1.12938006e-02, 4.04183878e-02, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1.05336516e-01, -2.90308418e-02, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, -2.90308418e-02, 5.04233092e-02, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 5.83020277e-01, -1.95215562e-01, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -1.95215562e-01, 2.68336193e-01, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.02136194e-02, -2.31395216e-02],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2.31395216e-02, 2.82685779e-01],
]
cov = np.array(cov_raw)

# 搵每個 tracer 嘅有效紅移
z_unique = sorted(set(d[0] for d in desi_data))
print(f"\n  Tracers: {len(z_unique)} 紅移點")
for z in z_unique:
    entries = [d for d in desi_data if d[0] == z]
    print(f"  z={z:.3f}: {', '.join(f'{d[2]}={d[1]:.4f}' for d in entries)}")

# ================================================================
# 2. IDCM 預測
# ================================================================
print(f"\n{'─'*80}")
print("  2. IDCM 預測")
print(f"{'─'*80}")

# IDCM 嘅距離尺度
# BAO 物理尺度 = λ_sync/2 = 147.44 Mpc
# DM/rd = DM / BAO_scale (IDCM 嘅 "standard ruler")
# DH/rd = DH / BAO_scale

# 喺 IDCM 中，DM(z) 同 DH(z) 從 K_Chain 色散導出：
# DH(z) = c / H(z)，其中 H(z) = H₀ × (1+z)^{α(z)}
# α(z) 從 K_Tree projection 導出

def hz_idcm(z):
    """IDCM H(z) prediction from K_Tree projection"""
    # α(z) = 1 + log(1 - 2ε·Θ(z)) / log(4)
    eps = PHI_INV / 4  # 0.1545
    # Θ(z) = tanh(z/2) 平滑過渡
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    return H0_IDCM * (1 + z) ** alpha

def dm_idcm(z):
    """IDCM DM(z) prediction (comoving distance / BAO_scale)"""
    # DM = ∫₀ᶻ c·dz'/H(z')
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_idcm(zp)
    DM = C_LIGHT * integral  # Mpc
    return DM / BAO_SCALE  # DM/rd

def dh_idcm(z):
    """IDCM DH(z) prediction (Hubble distance / BAO_scale)"""
    DH = C_LIGHT / hz_idcm(z)  # Mpc
    return DH / BAO_SCALE  # DH/rd

def dv_idcm(z):
    """IDCM DV/rd"""
    dm = dm_idcm(z)
    dh = dh_idcm(z)
    return (z * dm**2 * dh) ** (1/3)

print(f"\n  {'z':<8} {'量':<8} {'IDCM':<12} {'DESI':<12} {'Δ/σ':<10}")
print(f"  {'─'*50}")

# 計算每個數據點嘅 IDCM 預測同偏差
chi2_total = 0.0
n_points = 0
predictions = []

for i, (z, val, qty) in enumerate(desi_data):
    if qty == 'DM':
        pred = dm_idcm(z)
    elif qty == 'DH':
        pred = dh_idcm(z)
    elif qty == 'DV':
        pred = dv_idcm(z)
    else:
        continue
    
    # 從協方差矩陣搵誤差
    err = math.sqrt(cov[i, i]) if cov[i, i] > 0 else 0
    
    delta = val - pred
    sigma = delta / err if err > 0 else 0
    
    predictions.append({'z': z, 'qty': qty, 'pred': pred, 'obs': val, 'err': err, 'sigma': sigma})
    
    print(f"  {z:<8.3f} {qty:<8} {pred:<12.4f} {val:<12.4f} {sigma:<+10.2f}")

# ================================================================
# 3. χ² 檢驗
# ================================================================
print(f"\n{'─'*80}")
print("  3. χ² 檢驗")
print(f"{'─'*80}")

# 數據向量
data_vec = np.array([d[1] for d in desi_data])
# 模型向量
model_vec = np.array([predictions[i]['pred'] for i in range(len(desi_data))])
delta_vec = data_vec - model_vec

# 逆協方差矩陣
try:
    cov_inv = np.linalg.inv(cov)
    chi2 = delta_vec @ cov_inv @ delta_vec
    dof = len(data_vec)
    print(f"  χ² = {chi2:.1f}")
    print(f"  dof = {dof}")
    print(f"  χ²/dof = {chi2/dof:.3f}")
    print(f"  p-value = {stats.chi2.sf(chi2, dof):.4f}")
except np.linalg.LinAlgError:
    print("  協方差矩陣奇異，無法求逆")
    chi2 = 0

# ================================================================
# 4. 逐 tracer 分析
# ================================================================
print(f"\n{'─'*80}")
print("  4. 逐 tracer 分析")
print(f"{'─'*80}")

# 按 tracer 分組
tracers = {
    'BGS': (0, 0),  # z=0.295, DV only
    'LRG1': (1, 2),  # z=0.510, DM+DH
    'LRG2': (3, 4),  # z=0.706, DM+DH
    'LRG+ELG': (5, 6),  # z=0.934, DM+DH
    'ELG2': (7, 8),  # z=1.321, DM+DH
    'QSO': (9, 10),  # z=1.484, DM+DH
    'Lyα': (11, 12),  # z=2.33, DH+DM
}

for name, (i, j) in tracers.items():
    z = desi_data[i][0]
    if i == j:  # DV only
        dv_pred = predictions[i]['pred']
        dv_obs = predictions[i]['obs']
        dv_err = predictions[i]['err']
        sigma = (dv_obs - dv_pred) / dv_err
        print(f"  {name:<8} z={z:<6.3f} DV: IDCM={dv_pred:.4f}, DESI={dv_obs:.4f}±{dv_err:.4f}, Δ/σ={sigma:+.2f}")
    else:
        dm_pred = predictions[i]['pred']
        dm_obs = predictions[i]['obs']
        dm_err = predictions[i]['err']
        dh_pred = predictions[j]['pred']
        dh_obs = predictions[j]['obs']
        dh_err = predictions[j]['err']
        sigma_dm = (dm_obs - dm_pred) / dm_err
        sigma_dh = (dh_obs - dh_pred) / dh_err
        print(f"  {name:<8} z={z:<6.3f} DM: IDCM={dm_pred:.4f}, DESI={dm_obs:.4f}±{dm_err:.4f}, Δ/σ={sigma_dm:+.2f}")
        print(f"  {'':8}   DH: IDCM={dh_pred:.4f}, DESI={dh_obs:.4f}±{dh_err:.4f}, Δ/σ={sigma_dh:+.2f}")

# ================================================================
# 5. 總結
# ================================================================
print(f"\n{'─'*80}")
print("  5. 總結")
print(f"{'─'*80}")

# 計算平均偏差
sigmas = np.array([p['sigma'] for p in predictions])
mean_sigma = np.mean(np.abs(sigmas))
print(f"\n  平均 |Δ/σ| = {mean_sigma:.2f}")
print(f"  最大 |Δ/σ| = {np.max(np.abs(sigmas)):.2f}")

# 睇下有冇系統性偏差
dm_sigmas = [p['sigma'] for p in predictions if p['qty'] == 'DM']
dh_sigmas = [p['sigma'] for p in predictions if p['qty'] == 'DH']
if dm_sigmas:
    print(f"  DM 平均 Δ/σ = {np.mean(dm_sigmas):.2f} ± {np.std(dm_sigmas):.2f}")
if dh_sigmas:
    print(f"  DH 平均 Δ/σ = {np.mean(dh_sigmas):.2f} ± {np.std(dh_sigmas):.2f}")

print(f"\n  DESI DR2 BAO 數據已下載至: ~/IDCM/data/desi_dr2/")
print(f"  包含 7 個 tracer: BGS, LRG×2, LRG+ELG, ELG, QSO, Lyα")

# 儲存結果
output = {
    'constants': {
        'H0': H0_IDCM, 'R_H': R_H, 'lambda_sync': LAMBDA_SYNC,
        'bao_scale': BAO_SCALE
    },
    'desi_data': desi_data,
    'predictions': predictions,
    'chi2': float(chi2), 'dof': dof,
    'chi2_per_dof': float(chi2/dof) if dof > 0 else 0
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/45_desi_bao_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果已儲存至 45_desi_bao_results.json")

print(f"\n{'='*80}")
print(f"  DESI DR2 BAO vs IDCM 比較完成")
print(f"{'='*80}")