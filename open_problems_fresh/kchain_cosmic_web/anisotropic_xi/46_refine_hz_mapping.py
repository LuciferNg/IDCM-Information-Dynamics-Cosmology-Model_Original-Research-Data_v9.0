#!/usr/bin/env python3
"""
46_refine_hz_mapping.py — 阻抗校正算子 ζ(z) 低紅移投影校準
============================================================
核心問題：IDCM 嘅 H(z) 喺低紅移（z<1）同 DESI 觀測有系統性偏差
（DM: +10-23σ, DH: +6-10σ），但高紅移（z>1.4）收斂（-0.35σ）。

物理原因：低紅移處「離散相位」投影到「稠密觀測空間」時，
局域結構嘅非線性阻抗響應未被考慮。

修正：引入阻抗校正算子 ζ(z) = 1 + ζ₀ · exp(-z/z_s)
H_corr(z) = H_IDCM(z) / ζ(z)

ζ(z) 嘅物理意義：
- 低紅移：ζ > 1，H(z) 被壓低（阻抗效應使有效膨脹率變慢）
- 高紅移：ζ → 1，純 IDCM 結構（無需修正）

損失函數：
1. χ²(DM, DH) 對 DESI DR2 7 tracers
2. 高紅移收斂性懲罰（QSO z=1.484, Lyα z=2.33）
3. eBOSS 諧波位置錨點（約束 ζ(z) 唔可以破壞諧波對齊）
"""
import math
import numpy as np
from scipy import stats, optimize
import json
import sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import LAMBDA_SYNC, BAO_MPC, H, H0_IDCM, R_H, PHI, PHI_INV

# ================================================================
# 0. 常數
# ================================================================
C_LIGHT = 299792.458
L3 = 4  # MERA branching
BAO_SCALE = BAO_MPC  # 147.44 Mpc = IDCM standard ruler

print("=" * 80)
print("  IDCM H(z) 阻抗校正算子 ζ(z) — 低紅移投影校準")
print("=" * 80)
print(f"\n  IDCM baseline: H₀={H0_IDCM:.2f}, BAO_scale={BAO_SCALE:.2f} Mpc")

# ================================================================
# 1. DESI DR2 BAO 數據
# ================================================================
print(f"\n{'─'*80}")
print("  1. DESI DR2 BAO 數據")
print(f"{'─'*80}")

# DESI DR2 BAO data (from GitHub)
# Index: [0]z=0.295 DV, [1]z=0.510 DM, [2]z=0.510 DH, [3]z=0.706 DM, [4]z=0.706 DH,
#        [5]z=0.934 DM, [6]z=0.934 DH, [7]z=1.321 DM, [8]z=1.321 DH,
#        [9]z=1.484 DM, [10]z=1.484 DH, [11]z=2.33 DH, [12]z=2.33 DM
desi_z = [0.295, 0.510, 0.510, 0.706, 0.706, 
          0.934, 0.934, 1.321, 1.321, 1.484, 1.484, 2.33, 2.33]
desi_qty = ['DV', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DH', 'DM']
desi_val = [7.94167639, 13.58758434, 21.86294686, 17.35069094, 19.45534918,
            21.57563956, 17.64149464, 27.60085612, 14.17602155, 30.51190063,
            12.81699964, 8.63154567, 38.98897396]

# Covariance matrix (13x13)
cov = np.array([
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
])
cov_inv = np.linalg.inv(cov)

# ================================================================
# 2. IDCM H(z) 同阻抗校正算子 ζ(z)
# ================================================================
print(f"\n{'─'*80}")
print("  2. 阻抗校正算子 ζ(z) 定義")
print(f"{'─'*80}")

def hz_idcm_base(z):
    """IDCM baseline H(z) from K_Tree projection"""
    eps = PHI_INV / 4  # 0.1545
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_correction(z, zeta0, z_s):
    """
    阻抗校正算子 ζ(z) = 1 + ζ₀ · exp(-z/z_s)
    
    ϵ(z) = 1/ζ(z) 係阻抗乘數
    H_corr(z) = H_base(z) / ζ(z) = H_base(z) · ϵ(z)
    
    物理意義：
    - ζ₀: z=0 時嘅最大校正幅度
    - z_s: 校正衰減尺度（高 z → 0）
    """
    return 1.0 + zeta0 * math.exp(-z / z_s)

def hz_corrected(z, zeta0, z_s):
    """Correction: 用 ζ(z) 修正 H(z)"""
    zeta = zeta_correction(z, zeta0, z_s)
    return hz_idcm_base(z) / zeta  # 除以 ζ → 壓低低紅移 H(z)

# 測試 ζ(z) 形狀
print(f"  ζ(z) = 1 + ζ₀ · exp(-z/z_s)")
print(f"  物理: 低紅移阻抗效應 → H(z) 壓低")
print(f"  高紅移: ζ → 1, 回復純 IDCM")
print(f"\n  ζ(z) 範例形狀 (ζ₀=0.3, z_s=0.5):")
for z_test in [0, 0.2, 0.5, 1.0, 2.0, 5.0]:
    zeta = zeta_correction(z_test, 0.3, 0.5)
    h_base = hz_idcm_base(z_test)
    h_corr = hz_corrected(z_test, 0.3, 0.5)
    print(f"    z={z_test:.1f}: ζ={zeta:.4f}, H_base={h_base:.1f}, H_corr={h_corr:.1f}")

# ================================================================
# 3. IDCM 預測值（DM/rd, DH/rd, DV/rd）
# ================================================================
def compute_dm(z, zeta0, z_s):
    """DM = ∫₀ᶻ c·dz'/H(z')"""
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_corrected(zp, zeta0, z_s)
    return C_LIGHT * integral / BAO_SCALE

def compute_dh(z, zeta0, z_s):
    """DH = c/H(z)"""
    return C_LIGHT / hz_corrected(z, zeta0, z_s) / BAO_SCALE

def compute_dv(z, zeta0, z_s):
    """DV = (z · DM² · DH)^{1/3}"""
    dm = compute_dm(z, zeta0, z_s)
    dh = compute_dh(z, zeta0, z_s)
    return (z * dm**2 * dh) ** (1/3)

# ================================================================
# 4. 損失函數
# ================================================================
print(f"\n{'─'*80}")
print("  4. 損失函數定義")
print(f"{'─'*80}")

def chi2_desi(params):
    """χ² 對 DESI DR2 7 tracers"""
    zeta0, z_s = params
    if zeta0 < 0 or z_s < 0:
        return 1e12
    
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]
        qty = desi_qty[i]
        if qty == 'DM':
            pred = compute_dm(z, zeta0, z_s)
        elif qty == 'DH':
            pred = compute_dh(z, zeta0, z_s)
        elif qty == 'DV':
            pred = compute_dv(z, zeta0, z_s)
        else:
            pred = 0
        model.append(pred)
    
    model = np.array(model)
    delta = np.array(desi_val) - model
    return delta @ cov_inv @ delta

def highz_penalty(params):
    """
    高紅移收斂性懲罰：
    - QSO (z=1.484): DH Δ/σ 應該 < 1
    - Lyα (z=2.33): DH Δ/σ 應該 < 2
    - 用 sigmoid 做平滑懲罰
    """
    zeta0, z_s = params
    
    # QSO z=1.484 DH
    dh_qso_pred = compute_dh(1.484, zeta0, z_s)
    dh_qso_obs = 12.81699964
    dh_qso_err = math.sqrt(cov[10, 10])  # 0.5180
    dh_qso_sigma = (dh_qso_obs - dh_qso_pred) / dh_qso_err
    
    # Lyα z=2.33 DH
    dh_lya_pred = compute_dh(2.33, zeta0, z_s)
    dh_lya_obs = 8.63154567
    dh_lya_err = math.sqrt(cov[11, 11])  # 0.1011
    dh_lya_sigma = (dh_lya_obs - dh_lya_pred) / dh_lya_err
    
    # Sigmoid penalty: 如果 |Δ/σ| > 1, 開始懲罰
    penalty = 0
    for sigma in [dh_qso_sigma, dh_lya_sigma]:
        penalty += 10 * (math.exp(abs(sigma) - 1) - 1) if abs(sigma) > 1 else 0
    
    return penalty

def eboss_anchor_penalty(params):
    """
    eBOSS 諧波位置錨點懲罰：
    ζ(z) 修正唔應該改變諧波嘅物理位置（λ_sync/n 係結構常數）
    即係 ζ(z) 喺 z>0.6 必須接近 1
    """
    zeta0, z_s = params
    # 喺 z=0.6（eBOSS 有效紅移），ζ(z) 應該 < 1.05
    zeta_at_06 = zeta_correction(0.6, zeta0, z_s)
    penalty = 100 * max(0, zeta_at_06 - 1.05) ** 2
    return penalty

def total_loss(params):
    """總損失函數"""
    c2 = chi2_desi(params)
    hp = highz_penalty(params)
    ep = eboss_anchor_penalty(params)
    return c2 + hp + ep

# 測試 baseline（無修正）
print(f"\n  Baseline (ζ₀=0, 無修正):")
chi2_base = chi2_desi([0, 1])
print(f"    χ²(DESI) = {chi2_base:.1f}")
print(f"    dof = 13")
print(f"    χ²/dof = {chi2_base/13:.1f}")

# ================================================================
# 5. 梯度下降優化
# ================================================================
print(f"\n{'─'*80}")
print("  5. 梯度下降優化")
print(f"{'─'*80}")

# 參數邊界
bounds = [(0.01, 2.0), (0.05, 2.0)]  # ζ₀, z_s

# 多起始點避免局部最小值
best_result = None
best_loss = 1e12
best_params = None

initial_guesses = [
    (0.3, 0.5), (0.5, 0.3), (0.2, 0.8), (0.4, 0.4), (0.6, 0.6),
    (0.15, 1.0), (0.8, 0.2), (0.25, 0.6), (0.35, 0.7), (0.45, 0.35)
]

for guess in initial_guesses:
    result = optimize.minimize(total_loss, guess, method='L-BFGS-B', 
                               bounds=bounds, options={'maxiter': 200})
    if result.fun < best_loss:
        best_loss = result.fun
        best_params = result.x
        best_result = result

zeta0_opt, zs_opt = best_params
print(f"\n  最佳擬合:")
print(f"    ζ₀ = {zeta0_opt:.4f}")
print(f"    z_s = {zs_opt:.4f}")
print(f"    總損失 = {best_loss:.1f}")
print(f"    迭代次數 = {best_result.nit}")
print(f"    收斂 = {best_result.success}")

# ================================================================
# 6. 結果對比
# ================================================================
print(f"\n{'─'*80}")
print("  6. 結果對比 — Baseline vs 修正後")
print(f"{'─'*80}")

# 計算每 tracer 嘅偏差
print(f"\n  {'z':<8} {'量':<8} {'Baseline':<12} {'修正後':<12} {'DESI':<12} {'Δ/σ_base':<10} {'Δ/σ_corr':<10}")
print(f"  {'─'*70}")

results = []
for i in range(len(desi_z)):
    z = desi_z[i]
    qty = desi_qty[i]
    
    if qty == 'DM':
        pred_base = compute_dm(z, 0, 1)
        pred_corr = compute_dm(z, zeta0_opt, zs_opt)
    elif qty == 'DH':
        pred_base = compute_dh(z, 0, 1)
        pred_corr = compute_dh(z, zeta0_opt, zs_opt)
    elif qty == 'DV':
        pred_base = compute_dv(z, 0, 1)
        pred_corr = compute_dv(z, zeta0_opt, zs_opt)
    
    obs = desi_val[i]
    err = math.sqrt(cov[i, i])
    sigma_base = (obs - pred_base) / err
    sigma_corr = (obs - pred_corr) / err
    
    results.append({
        'z': z, 'qty': qty, 'obs': obs, 'err': err,
        'pred_base': pred_base, 'pred_corr': pred_corr,
        'sigma_base': sigma_base, 'sigma_corr': sigma_corr
    })
    
    print(f"  {z:<8.3f} {qty:<8} {pred_base:<12.4f} {pred_corr:<12.4f} {obs:<12.4f} "
          f"{sigma_base:<+10.2f} {sigma_corr:<+10.2f}")

# χ² 對比
chi2_0 = chi2_desi([0, 1])
chi2_opt = chi2_desi(best_params)
print(f"\n  χ²(DESI):")
print(f"    Baseline: {chi2_0:.1f} / 13 dof = {chi2_0/13:.1f}")
print(f"    修正後:   {chi2_opt:.1f} / 11 dof = {chi2_opt/11:.1f}")
print(f"    改善:     Δχ² = {chi2_0 - chi2_opt:.1f}")

# 高紅移收斂性檢查
dh_qso_corr = compute_dh(1.484, zeta0_opt, zs_opt)
dh_qso_sigma = (12.81699964 - dh_qso_corr) / math.sqrt(cov[10, 10])
dh_lya_corr = compute_dh(2.33, zeta0_opt, zs_opt)
dh_lya_sigma = (8.63154567 - dh_lya_corr) / math.sqrt(cov[11, 11])
print(f"\n  高紅移收斂性:")
print(f"    QSO (z=1.484) DH Δ/σ: {dh_qso_sigma:.2f}")
print(f"    Lyα (z=2.33)  DH Δ/σ: {dh_lya_sigma:.2f}")

# eBOSS 諧波錨點檢查
zeta_at_06 = zeta_correction(0.6, zeta0_opt, zs_opt)
print(f"\n  eBOSS 諧波錨點:")
print(f"    ζ(z=0.6) = {zeta_at_06:.4f} (should be < 1.05)")

# ================================================================
# 7. ζ(z) 形狀輸出
# ================================================================
print(f"\n{'─'*80}")
print("  7. 阻抗校正算子 ζ(z) 形狀")
print(f"{'─'*80}")

print(f"\n  {'z':<8} {'ζ(z)':<12} {'H_base':<12} {'H_corr':<12} {'DH_base':<12} {'DH_corr':<12}")
print(f"  {'─'*60}")
for z_test in [0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]:
    zeta = zeta_correction(z_test, zeta0_opt, zs_opt)
    h_base = hz_idcm_base(z_test)
    h_corr = hz_corrected(z_test, zeta0_opt, zs_opt)
    dh_base = C_LIGHT / h_base / BAO_SCALE
    dh_corr = C_LIGHT / h_corr / BAO_SCALE
    print(f"  {z_test:<8.1f} {zeta:<12.4f} {h_base:<12.1f} {h_corr:<12.1f} {dh_base:<12.4f} {dh_corr:<12.4f}")

# ================================================================
# 8. 儲存結果
# ================================================================
output = {
    'constants': {
        'H0': H0_IDCM, 'BAO_scale': BAO_SCALE,
        'lambda_sync': LAMBDA_SYNC, 'R_H': R_H
    },
    'correction_operator': {
        'form': 'ζ(z) = 1 + ζ₀ · exp(-z/z_s)',
        'zeta0': zeta0_opt,
        'z_s': zs_opt,
        'description': 'Nonlinear impedance correction at low z'
    },
    'results': {
        'chi2_baseline': float(chi2_0),
        'chi2_corrected': float(chi2_opt),
        'dof': 11,
        'chi2_per_dof_corrected': float(chi2_opt / 11)
    },
    'per_tracer': results,
    'highz_convergence': {
        'QSO_DH_sigma': dh_qso_sigma,
        'Lya_DH_sigma': dh_lya_sigma
    }
}
path = '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/46_refine_hz_results.json'
with open(path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果已儲存至 46_refine_hz_results.json")

print(f"\n{'='*80}")
print(f"  H(z) 阻抗校正完成 — 低紅移投影校準")
print(f"  ζ₀ = {zeta0_opt:.4f}, z_s = {zs_opt:.4f}")
print(f"  χ²: {chi2_0:.0f} → {chi2_opt:.0f}")
print(f"{'='*80}")