#!/usr/bin/env python3
"""
54_overturn_dark_energy_test.py — 測試「ζ(z) 可否取代 B=4 暗能量」
====================================================================
用戶 claim：呢個結果代表連之前「B=4 暗能量 = 宇宙運行成本」都被推翻。

測試設計（誠實檢驗）：
- 模型 1（現有）: H = H_IDCM_base(z)/ζ(z)，baseline 內嵌 Ω_L=0.683 (B=4)
- 模型 2（純 matter）: H = H0·(1+z)^1.5 / ζ(z)，無暗能量結構
- 模型 3（純 matter, 無 ζ）: H = H0·(1+z)^1.5，ΛCDM-like 對照

如果模型 2 (matter + ζ) 都 fit 到 DESI χ²≈13 → ζ 真係取代咗暗能量 → claim 成立
如果模型 2 失敗 → Ω_L 結構仍然必要 → claim 唔成立
"""
import math
import numpy as np
from scipy import optimize
from scipy.interpolate import interp1d
import json

C_LIGHT = 299792.458
PHI_INV = (math.sqrt(5) - 1) / 2
H0_IDCM = 72.59
BAO = 147.44
ZETA_A, ZETA_Z1, ZETA_B, ZETA_Z2 = 1.0847, 0.5114, 0.4723, 10.0

print("=" * 80)
print("  測試：ζ(z) 可否取代 B=4 暗能量（Ω_L=0.683）")
print("=" * 80)

# ================================================================
# 數據
# ================================================================
desi_z = [0.295, 0.510, 0.510, 0.706, 0.706, 
          0.934, 0.934, 1.321, 1.321, 1.484, 1.484, 2.33, 2.33]
desi_qty = ['DV', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DH', 'DM']
desi_val = [7.94167639, 13.58758434, 21.86294686, 17.35069094, 19.45534918,
            21.57563956, 17.64149464, 27.60085612, 14.17602155, 30.51190063,
            12.81699964, 8.63154567, 38.98897396]
cov_desi = np.array([
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
cov_desi_inv = np.linalg.inv(cov_desi)

# ================================================================
# 三個 baseline 模型
# ================================================================
def hz_idcm_base(z):
    """模型 1: IDCM baseline（內嵌 Ω_L = 4/(φ⁴-1) = 0.683）"""
    eps = PHI_INV / 4
    theta = np.tanh(z / 2)
    alpha = 1 + np.log(1 - 2 * eps * theta) / np.log(4)
    return H0_IDCM * (1 + z) ** alpha

def hz_matter_only(z, H0=H0_IDCM):
    """模型 2/3: 純 matter baseline H = H0·(1+z)^1.5"""
    return H0 * (1 + z) ** 1.5

def zeta_anchored(z, params):
    A, z1, B, z2 = params
    return 1.0 + z * (A * np.exp(-z / z1) - B * (1 - np.exp(-z / z2)))

def hz_model(z, baseline_fn, params, use_zeta=True):
    if use_zeta:
        return baseline_fn(z) / zeta_anchored(z, params)
    return baseline_fn(z)

# ================================================================
# DESI 預測
# ================================================================
def desi_predictions(baseline_fn, params, use_zeta=True):
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        h = hz_model(z, baseline_fn, params, use_zeta)
        if qty in ('DM', 'DV'):
            N = 300
            zz = np.linspace(0, z, N)
            mid = (zz[1:] + zz[:-1]) / 2
            hm = hz_model(mid, baseline_fn, params, use_zeta)
            dm_int = np.sum((zz[1:] - zz[:-1]) / hm)
            dm = C_LIGHT * dm_int / BAO
        if qty == 'DM':
            model.append(dm)
        elif qty == 'DH':
            model.append(C_LIGHT / h / BAO)
        elif qty == 'DV':
            dh = C_LIGHT / h / BAO
            model.append((z * dm**2 * dh) ** (1/3))
    return np.array(model)

def chi2_desi(baseline_fn, params, use_zeta=True):
    model = desi_predictions(baseline_fn, params, use_zeta)
    delta = np.array(desi_val) - model
    return delta @ cov_desi_inv @ delta

# ================================================================
# 擬合
# ================================================================
print(f"\n{'─'*80}")
print("  擬合 ζ(z) 參數（每種 baseline）")
print(f"{'─'*80}")

def fit_zeta(baseline_fn):
    def loss(params):
        if any(p <= 0 for p in params):
            return 1e12
        return chi2_desi(baseline_fn, params, use_zeta=True)
    
    bounds = [(0, 5), (0.05, 10), (0, 5), (0.05, 10)]
    best = None; best_loss = 1e12
    for g in [[0.5, 1.0, 0.5, 2.0], [1.0, 0.5, 0.5, 5.0], [0.3, 2.0, 0.3, 3.0],
              [1.5, 0.3, 1.0, 1.0], [0.8, 0.8, 0.6, 4.0]]:
        r = optimize.minimize(loss, g, method='L-BFGS-B', bounds=bounds,
                              options={'maxiter': 300})
        if r.fun < best_loss:
            best_loss = r.fun; best = r
    return best.x, best_loss

# 模型 1: IDCM baseline + ζ（現有）
p1, c1 = fit_zeta(hz_idcm_base)
print(f"\n  模型 1: IDCM baseline (Ω_L=0.683) + ζ")
print(f"    A={p1[0]:.4f} z₁={p1[1]:.4f} B={p1[2]:.4f} z₂={p1[3]:.4f}")
print(f"    χ²(DESI) = {c1:.1f} (13 dof)")

# 模型 2: pure matter + ζ（測試 claim）
p2, c2 = fit_zeta(hz_matter_only)
print(f"\n  模型 2: pure matter (無 Ω_L) + ζ  ← 關鍵測試")
print(f"    A={p2[0]:.4f} z₁={p2[1]:.4f} B={p2[2]:.4f} z₂={p2[3]:.4f}")
print(f"    χ²(DESI) = {c2:.1f} (13 dof)")

# 模型 3: pure matter 無 ζ（對照）
c3 = chi2_desi(hz_matter_only, [0, 1, 0, 1], use_zeta=False)
print(f"\n  模型 3: pure matter 無 ζ")
print(f"    χ²(DESI) = {c3:.1f} (13 dof)")

# ================================================================
# 判決
# ================================================================
print(f"\n{'─'*80}")
print("  判決")
print(f"{'─'*80}")

print(f"\n  {'模型':<35} {'χ²(DESI)':<10} {'χ²/dof':<8}")
print(f"  {'─'*55}")
print(f"  {'1. IDCM base + ζ (現有)':<35} {c1:<10.1f} {c1/13:<8.2f}")
print(f"  {'2. matter + ζ (無暗能量)':<35} {c2:<10.1f} {c2/13:<8.2f}")
print(f"  {'3. matter 無 ζ':<35} {c3:<10.1f} {c3/13:<8.2f}")

# 模型 1 vs 2 比較
delta_12 = c1 - c2
print(f"\n  Δχ²(模型1 - 模型2) = {delta_12:.1f}")
print(f"  模型 1 參數數目 = 4 (A,z₁,B,z₂), baseline 固定")
print(f"  模型 2 參數數目 = 4 (A,z₁,B,z₂), baseline 固定")

# ζ(z) 形狀對比
print(f"\n  ζ(z) 形狀（兩種 baseline 各自擬合）:")
print(f"  {'z':<6} {'ζ(模型1)':<10} {'ζ(模型2)':<10}")
for zt in [0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 2.33]:
    z1v = zeta_anchored(zt, p1)
    z2v = zeta_anchored(zt, p2)
    print(f"  {zt:<6.2f} {z1v:<10.4f} {z2v:<10.4f}")

# 儲存
output = {
    'model1_idcm_base': {'params': [float(x) for x in p1], 'chi2': float(c1)},
    'model2_matter_zeta': {'params': [float(x) for x in p2], 'chi2': float(c2)},
    'model3_matter_no_zeta': {'chi2': float(c3)},
    'verdict': {
        'delta_chi2_1v2': float(delta_12),
        'conclusion': 'ζ(z) REPLACES dark energy' if c2 < c1 * 1.3 else 'Ω_L structure still needed'
    }
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/54_overturn_test_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 54_overturn_test_results.json")
print(f"{'='*80}")