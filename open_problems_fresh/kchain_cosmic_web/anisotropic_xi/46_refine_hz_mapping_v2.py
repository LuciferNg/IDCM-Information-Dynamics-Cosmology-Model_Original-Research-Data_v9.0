#!/usr/bin/env python3
"""
46_refine_hz_mapping_v2.py — 雙區阻抗校正算子
====================================================
v1 發現 ζ(z) 嘅單指數形式唔夠：
- 低紅移 H(z) 太高（DM 同 DH 都偏低）
- 高紅移 H(z) 太低（z=2.33 Lyα 嘅 DH 太高）

改用雙區校正：
ζ(z) = 1 + ζ₀·exp(-z/z_s) - ζ₁·(1 - exp(-z/z_l))

- ζ₀·exp(-z/z_s): 低紅移阻抗效應（壓低 H）
- ζ₁·(1 - exp(-z/z_l)): 高紅移色散修正（提高 H）
"""
import math
import numpy as np
from scipy import stats, optimize
import json

# ================================================================
# 0. 常數
# ================================================================
C_LIGHT = 299792.458
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
H0_IDCM = 72.59
LAMBDA_SYNC = 2 * math.pi * (C_LIGHT / H0_IDCM) / 88
BAO_SCALE = LAMBDA_SYNC / 2  # 147.44 Mpc

print("=" * 80)
print("  IDCM H(z) 雙區阻抗校正 — v2")
print("=" * 80)

# ================================================================
# 1. DESI DR2 數據（同 v1）
# ================================================================
desi_z = [0.295, 0.510, 0.510, 0.706, 0.706, 
          0.934, 0.934, 1.321, 1.321, 1.484, 1.484, 2.33, 2.33]
desi_qty = ['DV', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DH', 'DM']
desi_val = [7.94167639, 13.58758434, 21.86294686, 17.35069094, 19.45534918,
            21.57563956, 17.64149464, 27.60085612, 14.17602155, 30.51190063,
            12.81699964, 8.63154567, 38.98897396]

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
# 2. 雙區阻抗校正
# ================================================================
print(f"\n{'─'*80}")
print("  2. 雙區阻抗校正算子")
print(f"{'─'*80}")

def hz_idcm_base(z):
    """IDCM baseline H(z)"""
    eps = PHI_INV / 4
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_dual(z, zeta0, zs, zeta1, zl):
    """
    雙區阻抗校正：
    ζ(z) = 1 + ζ₀·exp(-z/z_s) - ζ₁·(1 - exp(-z/z_l))
    
    - ζ₀·exp(-z/z_s): 低紅移阻抗（壓低 H → 增大 DH、DM）
    - ζ₁·(1 - exp(-z/z_l)): 高紅移色散（提高 H → 減小 DH）
    """
    low_z = zeta0 * math.exp(-z / zs)
    high_z = zeta1 * (1 - math.exp(-z / zl))
    return 1.0 + low_z - high_z

def hz_corrected(z, zeta0, zs, zeta1, zl):
    zeta = zeta_dual(z, zeta0, zs, zeta1, zl)
    return hz_idcm_base(z) / zeta

# 測試形狀
print(f"  ζ(z) = 1 + ζ₀·exp(-z/z_s) - ζ₁·(1 - exp(-z/z_l))")
print(f"\n  範例 (ζ₀=0.3, zs=0.3, ζ₁=0.15, zl=1.0):")
for z_test in [0, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0]:
    zeta = zeta_dual(z_test, 0.3, 0.3, 0.15, 1.0)
    print(f"    z={z_test:.1f}: ζ={zeta:.4f}")

# ================================================================
# 3. 預測值
# ================================================================
def compute_dm(z, zeta0, zs, zeta1, zl):
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_corrected(zp, zeta0, zs, zeta1, zl)
    return C_LIGHT * integral / BAO_SCALE

def compute_dh(z, zeta0, zs, zeta1, zl):
    return C_LIGHT / hz_corrected(z, zeta0, zs, zeta1, zl) / BAO_SCALE

def compute_dv(z, zeta0, zs, zeta1, zl):
    dm = compute_dm(z, zeta0, zs, zeta1, zl)
    dh = compute_dh(z, zeta0, zs, zeta1, zl)
    return (z * dm**2 * dh) ** (1/3)

# ================================================================
# 4. 損失函數
# ================================================================
def chi2_desi(params):
    zeta0, zs, zeta1, zl = params
    if any(p < 0 for p in params):
        return 1e12
    
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]
        qty = desi_qty[i]
        if qty == 'DM': pred = compute_dm(z, zeta0, zs, zeta1, zl)
        elif qty == 'DH': pred = compute_dh(z, zeta0, zs, zeta1, zl)
        elif qty == 'DV': pred = compute_dv(z, zeta0, zs, zeta1, zl)
        model.append(pred)
    
    delta = np.array(desi_val) - np.array(model)
    return delta @ cov_inv @ delta

def total_loss(params):
    return chi2_desi(params)

# Baseline
chi2_base = chi2_desi([0, 1, 0, 1])
print(f"\n  Baseline χ² = {chi2_base:.1f} / 13 dof = {chi2_base/13:.1f}")

# ================================================================
# 5. 優化
# ================================================================
print(f"\n{'─'*80}")
print("  5. 梯度下降優化（4 參數）")
print(f"{'─'*80}")

bounds = [(0, 2), (0.05, 2), (0, 1), (0.1, 5)]

best_result = None
best_loss = 1e12

guesses = [
    (0.3, 0.3, 0.1, 1.0), (0.5, 0.2, 0.15, 0.5), (0.2, 0.5, 0.08, 2.0),
    (0.4, 0.25, 0.12, 0.8), (0.25, 0.4, 0.1, 1.5), (0.35, 0.35, 0.2, 0.6),
    (0.15, 0.6, 0.05, 3.0), (0.45, 0.2, 0.18, 0.4), (0.28, 0.3, 0.14, 1.2),
    (0.32, 0.28, 0.09, 1.8)
]

for guess in guesses:
    result = optimize.minimize(total_loss, guess, method='L-BFGS-B',
                               bounds=bounds, options={'maxiter': 500})
    if result.fun < best_loss:
        best_loss = result.fun
        best_result = result

zeta0, zs, zeta1, zl = best_result.x
print(f"\n  最佳擬合:")
print(f"    ζ₀ = {zeta0:.4f}  (低紅移阻抗振幅)")
print(f"    z_s = {zs:.4f}    (低紅移衰減尺度)")
print(f"    ζ₁ = {zeta1:.4f}  (高紅移色散振幅)")
print(f"    z_l = {zl:.4f}    (高紅移增長尺度)")
print(f"    χ² = {best_loss:.1f}")
print(f"    dof = 9")
print(f"    χ²/dof = {best_loss/9:.1f}")

# ================================================================
# 6. 結果
# ================================================================
print(f"\n{'─'*80}")
print("  6. 逐 tracer 對比")
print(f"{'─'*80}")

print(f"\n  {'z':<8} {'量':<8} {'Baseline':<12} {'修正後':<12} {'DESI':<12} {'Δ/σ₀':<10} {'Δ/σ_c':<10}")
print(f"  {'─'*70}")

results = []
for i in range(len(desi_z)):
    z = desi_z[i]; qty = desi_qty[i]
    if qty == 'DM':
        pb = compute_dm(z, 0, 1, 0, 1)
        pc = compute_dm(z, zeta0, zs, zeta1, zl)
    elif qty == 'DH':
        pb = compute_dh(z, 0, 1, 0, 1)
        pc = compute_dh(z, zeta0, zs, zeta1, zl)
    elif qty == 'DV':
        pb = compute_dv(z, 0, 1, 0, 1)
        pc = compute_dv(z, zeta0, zs, zeta1, zl)
    obs = desi_val[i]; err = math.sqrt(cov[i, i])
    sb = (obs - pb) / err; sc = (obs - pc) / err
    results.append({'z': z, 'qty': qty, 'obs': obs, 'err': err,
                    'base': pb, 'corr': pc, 'sigma_base': sb, 'sigma_corr': sc})
    print(f"  {z:<8.3f} {qty:<8} {pb:<12.4f} {pc:<12.4f} {obs:<12.4f} {sb:<+10.2f} {sc:<+10.2f}")

# ζ(z) 形狀
print(f"\n  ζ(z) 形狀:")
print(f"  {'z':<8} {'ζ(z)':<12} {'H_base':<12} {'H_corr':<12} {'DH_base':<12} {'DH_corr':<12}")
for zt in [0, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0]:
    zeta = zeta_dual(zt, zeta0, zs, zeta1, zl)
    hb = hz_idcm_base(zt); hc = hz_corrected(zt, zeta0, zs, zeta1, zl)
    print(f"  {zt:<8.1f} {zeta:<12.4f} {hb:<12.1f} {hc:<12.1f} "
          f"{C_LIGHT/hb/BAO_SCALE:<12.4f} {C_LIGHT/hc/BAO_SCALE:<12.4f}")

# 儲存
output = {
    'correction': {
        'form': 'ζ(z) = 1 + ζ₀·exp(-z/z_s) - ζ₁·(1-exp(-z/z_l))',
        'zeta0': zeta0, 'z_s': zs, 'zeta1': zeta1, 'z_l': zl
    },
    'chi2': {'baseline': float(chi2_base), 'corrected': float(best_loss), 'dof': 9},
    'per_tracer': results
}
path = '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/46_refine_hz_v2_results.json'
with open(path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 46_refine_hz_v2_results.json")
print(f"  χ²: {chi2_base:.0f} → {best_loss:.0f} (Δχ²={chi2_base-best_loss:.0f})")
print(f"{'='*80}")