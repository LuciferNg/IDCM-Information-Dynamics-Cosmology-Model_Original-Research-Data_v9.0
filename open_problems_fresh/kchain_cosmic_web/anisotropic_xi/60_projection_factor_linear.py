#!/usr/bin/env python3
"""
60_projection_factor_linear.py — 線性投影拉伸 P(ℓ) = 1 + K × ℓ
=================================================================
從 DESI 數據發現：P(ℓ) = D_C/D_1D ≈ 1 + K × ℓ
ℓ = log₄(1+z) 係遞迴深度。

D_app(ℓ) = (44 - 44/4^ℓ) × (R_H/44) × (1 + K × ℓ)
"""
import math
import numpy as np
from scipy import optimize
import json

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
H0_IDCM = 72.59
C_LIGHT = 299792.458
N_D = 44
BAO = 147.44
R_H = C_LIGHT / H0_IDCM

print("=" * 80)
print("  P(ℓ) = 1 + K × ℓ — 線性投影拉伸因子")
print("=" * 80)

# DESI DM data
desi_dm = [(0.295, 7.94167639), (0.510, 13.58758434), (0.706, 17.35069094),
           (0.934, 21.57563956), (1.321, 27.60085612), (1.484, 30.51190063),
           (2.330, 38.98897396)]

def ell_from_z(z):
    return math.log(1 + z) / math.log(4)

def D_1D(z):
    """1D K_Chain light path = n(z) × R_H/44"""
    n = N_D * z / (1 + z)
    return n * R_H / N_D

# ================================================================
# 1. P(ℓ) = 1 + K × ℓ 驗證
# ================================================================
print(f"\n{'─'*80}")
print("  1. P(ℓ) = 1 + K × ℓ")
print(f"{'─'*80}")

print(f"\n  {'z':<8} {'ℓ':<8} {'P(obs)':<10} {'K=P-1/ℓ':<12} {'1+1.236ℓ':<12}")
K_vals = []
for z, dm_rd in desi_dm:
    ell = ell_from_z(z)
    d1d = D_1D(z)
    dc = dm_rd * BAO
    p = dc / d1d
    K = (p - 1) / ell
    K_vals.append(K)
    p_pred = 1 + 2 * PHI_INV * ell
    print(f"  {z:<8.4f} {ell:<8.4f} {p:<10.4f} {K:<12.4f} {p_pred:<12.4f}")

K_mean = np.mean(K_vals)
K_std = np.std(K_vals)
print(f"\n  K = {K_mean:.4f} ± {K_std:.4f}")
print(f"  2φ⁻¹ = {2*PHI_INV:.4f}")
print(f"  φ⁻¹ + 0.5 = {PHI_INV + 0.5:.4f}")
print(f"  L₅/L₄ = 11/7 = {11/7:.4f}")
print(f"  L₆/L₅ = 18/11 = {18/11:.4f}")
print(f"  h²¹/h¹¹ = 98/36 = {98/36:.4f}")

# ================================================================
# 2. 擬合 K
# ================================================================
print(f"\n{'─'*80}")
print("  2. 擬合最佳 K")
print(f"{'─'*80}")

def D_pred(z, K):
    ell = ell_from_z(z)
    d1d = D_1D(z)
    p = 1 + K * ell
    return d1d * p / BAO

def chi2(K):
    total = 0.0
    for z, dm_rd in desi_dm:
        err = math.sqrt(0.03**2 + (0.02 * dm_rd)**2)  # ~3% DESI error
        pred = D_pred(z, K)
        total += ((dm_rd - pred) / err) ** 2
    return total

r = optimize.minimize_scalar(chi2, bounds=(0.5, 2.0), method='bounded')
K_best = r.x
chi2_best = r.fun

print(f"\n  最佳 K = {K_best:.4f}")
print(f"  χ² = {chi2_best:.1f} (7 dof)")
print(f"  K = 2φ⁻¹ = {2*PHI_INV:.4f} (Δ = {K_best - 2*PHI_INV:+.4f})")

# 完整預測
print(f"\n  完整預測 (K = {K_best:.4f}):")
print(f"  {'z':<8} {'ℓ':<8} {'D_pred':<12} {'DM/rd':<10} {'DESI':<10} {'Δ/σ':<8}")
print(f"  {'─'*56}")
for z, dm_rd in desi_dm:
    err = math.sqrt(0.03**2 + (0.02 * dm_rd)**2)
    pred = D_pred(z, K_best)
    sig = (dm_rd - pred) / err
    print(f"  {z:<8.4f} {ell_from_z(z):<8.4f} {pred*BAO:<12.1f} {pred:<10.4f} {dm_rd:<10.4f} {sig:<+8.2f}")

# ================================================================
# 3. 結構分析: K 嘅形式
# ================================================================
print(f"\n{'─'*80}")
print("  3. K 嘅結構來源分析")
print(f"{'─'*80}")

# K 嘅可能結構表達式
# 從 1D→3D 投影：
# P(ℓ) = 1 + K × ℓ
# K = dP/dℓ = 3D 投影嘅「額外拉伸」每單位遞迴深度
# 
# 喺每一層 ℓ，K_Chain 粗粒化 B^ℓ = 4^ℓ 倍
# 1D 鏈長度 = 44 × R_H/44 = R_H
# 但 3D 投影需要「填充」3D 空間
# 填充因子 = (3D 空間維度) / (1D 投影維度) = 3/1 = 3
# 但 K_Chain 嘅 44 site 係離散，唔係連續
# 加上 CY₃ 嘅 h¹¹=36, h²¹=98 決定投影幾何

# 3 個方向嘅投影: 每個方向貢獻 φ⁻¹（黃金比例壓縮）
# 3 × φ⁻¹ = 1.854. 接近 K.
# 2 × φ⁻¹ = 1.236. 更接近.
# (L₆-L₅)/L₄ = (18-11)/7 = 1.000. 太細.
# h²¹/h¹¹ × φ⁻¹ = 98/36 × 0.618 = 1.683. 太大.
# (h²¹-h¹¹)/h¹¹ = 62/36 = 1.722. 太大.
# sqrt(h²¹/h¹¹) = sqrt(98/36) = 1.650. 太大.
# 1 + φ⁻¹ = 1.618. 接近但偏大.
# φ⁻¹ + φ⁻³ = 0.618 + 0.236 = 0.854. 太細.
# L₅/L₄ × φ⁻¹ = 11/7 × 0.618 = 0.971. 太細.
# L₄/L₃ × φ⁻¹ = 7/4 × 0.618 = 1.082. 接近但偏細.
# 2 × L₀/L₃ = 2 × 2/4 = 1.000. 太細.
# (L₀+L₄)/L₃ = (2+7)/4 = 2.250. 太大.
# L₂ + L₀/L₃ = 3 + 2/4 = 3.5. 太大.
# (L₅+L₃)/L₄ = (11+4)/7 = 2.143. 太大.
# CY₃/L₃ = 134/4 = 33.5. 太大.

# 最接近: 2 × φ⁻¹ = 1.236
# 其次: 1 + φ⁻¹ = 1.618
# 第三: L₄/L₃ × φ⁻¹ = 7/4 × 0.618 = 1.082

candidates = {
    '2 × φ⁻¹': 2 * PHI_INV,
    '1 + φ⁻¹': 1 + PHI_INV,
    'L₄/L₃ × φ⁻¹': 7/4 * PHI_INV,
    '3 × φ⁻¹': 3 * PHI_INV,
    '√(h²¹/h¹¹)': math.sqrt(98/36),
    '(h²¹-h¹¹)/h¹¹': 62/36,
    'h²¹/h¹¹ × φ⁻¹': 98/36 * PHI_INV,
    'L₅/L₄': 11/7,
    'L₆/L₅': 18/11,
    'L₆/L₄ × φ⁻¹': 18/7 * PHI_INV,
}

print(f"\n  {'K 候選':<25} {'值':<10} {'χ²':<10}")
print(f"  {'─'*45}")
for name, k_val in candidates.items():
    c = chi2(k_val)
    print(f"  {name:<25} {k_val:<10.4f} {c:<10.1f}")

# 對比舊結構
print(f"\n  對比:")
print(f"  舊結構 (Ω_L + ζ): χ² = 13.2")
print(f"  matter + ζ:       χ² = 34.9")
print(f"  最佳線性 K:       χ² = {chi2_best:.1f}")

# ================================================================
# 4. 完整公式
# ================================================================
print(f"\n{'─'*80}")
print("  4. 完整公式")
print(f"{'─'*80}")

best_candidate = min(candidates, key=lambda x: chi2(candidates[x]))
print(f"\n  最佳結構候選: {best_candidate} = {candidates[best_candidate]:.4f}")
print(f"  最佳擬合: K = {K_best:.4f}")
print(f"\n  D_app(ℓ) = (44 - 44/4^ℓ) × (R_H/44) × (1 + K × ℓ)")
print(f"  ℓ = log₄(1+z)")
print(f"  K = {best_candidate} = {candidates[best_candidate]:.4f} ← 結構值")
print(f"  K = {K_best:.4f} ← 最佳擬合值")
print(f"\n  DM/rd(ℓ) = [(44 - 44/4^ℓ) × R_H/44 × (1 + K × ℓ)] / BAO")

output = {
    'formula': 'D_app(ℓ) = (44-44/4^ℓ) × R_H/44 × (1 + K × ℓ)',
    'K_best': float(K_best),
    'K_chi2': float(chi2_best),
    'K_structural': {k: float(v) for k, v in candidates.items()},
    'K_2phi_inv': 2*PHI_INV,
    'chi2_2phi_inv': float(chi2(2*PHI_INV)),
    'chi2_old': 13.2,
    'chi2_matter_zeta': 34.9,
    'dof': 7
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/60_linear_projection_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 60_linear_projection_results.json")
print(f"{'='*80}")