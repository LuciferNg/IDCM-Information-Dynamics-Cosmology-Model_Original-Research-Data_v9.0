#!/usr/bin/env python3
"""
59_projection_factor.py — 從 DESI 數據反推投影拉伸因子 P(ℓ)
=================================================================
放棄 H(z) 框架。改用：
  D_1D(ℓ) = n(ℓ) × R_H/44  (1D K_Chain 上嘅光行路徑)
  n(ℓ) = 44 - 44/4^ℓ = 44z/(1+z)  (經過嘅 site 數)
  P(ℓ) = D_C(ℓ) / D_1D(ℓ)  (1D→3D 投影拉伸因子)
  D_C(ℓ) = DESI DM/rd × BAO  (觀測嘅 comoving distance)

P(ℓ) 嘅結構推導：
  P(ℓ) = 1 + K × sqrt(γ_avg(ℓ)) × 4^ℓ
  gamma_avg(ell) = Sum_{n <= 4^ell} gamma_n / 4^ell  (粗粒化後嘅平均本徵值)
  K = CY₃ 投影因子（由 h¹¹, h²¹ 決定？）
"""
import math
import numpy as np
import json

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
H0_IDCM = 72.59
C_LIGHT = 299792.458
N_D = 44
BAO = 147.44
R_H = C_LIGHT / H0_IDCM
h11, h21 = 36, 98
CY3 = h11 + h21

print("=" * 80)
print("  投影拉伸因子 P(ℓ) = D_C / D_1D — 1D K_Chain→3D 幾何畸變")
print("=" * 80)

# ================================================================
# 1. 從 DESI 數據提取 P(ℓ)
# ================================================================
print(f"\n{'─'*80}")
print("  1. DESI 數據 → P(ℓ)")
print(f"{'─'*80}")

desi_dm = [(0.295, 7.94167639), (0.510, 13.58758434), (0.706, 17.35069094),
           (0.934, 21.57563956), (1.321, 27.60085612), (1.484, 30.51190063),
           (2.330, 38.98897396)]

def ell_from_z(z):
    return math.log(1 + z) / math.log(4)

def n_sites(z):
    """光經過嘅 K_Chain site 數"""
    return N_D * z / (1 + z)

def D_1D(z):
    """1D K_Chain 上嘅光行距離"""
    return n_sites(z) * R_H / N_D

def D_C_desi(dm_rd):
    """DESI comoving distance"""
    return dm_rd * BAO

gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_D)])

print(f"\n  {'z':<8} {'ℓ':<8} {'n_sites':<10} {'D_1D(Mpc)':<12} {'D_C(Mpc)':<12} {'P=D_C/D_1D':<12}")
print(f"  {'─'*62}")
for z, dm_rd in desi_dm:
    ell = ell_from_z(z)
    ns = n_sites(z)
    d1d = D_1D(z)
    dc = D_C_desi(dm_rd)
    p = dc / d1d
    print(f"  {z:<8.4f} {ell:<8.4f} {ns:<10.2f} {d1d:<12.1f} {dc:<12.1f} {p:<12.4f}")

# ================================================================
# 2. 結構推導 P(ℓ) = 1 + K × sqrt(γ_avg) × 4^ℓ
# ================================================================
print(f"\n{'─'*80}")
print("  2. 結構形式驗證: P(ℓ) = 1 + K × sqrt(γ_avg(ℓ)) × 4^ℓ")
print(f"{'─'*80}")

def gamma_avg(ell):
    """喺 ℓ 層粗粒化後嘅平均本徵值"""
    block_size = max(int(round(4 ** ell)), 1)
    n_blocks = N_D // block_size
    if n_blocks == 0:
        n_blocks = 1
    block_size = N_D // n_blocks
    total = 0.0
    for b in range(n_blocks):
        start = b * block_size
        end = min((b + 1) * block_size, N_D - 1)
        if end > start:
            total += gamma_n[start:end].sum()
    return total / n_blocks

# 計算 X(ℓ) = sqrt(γ_avg(ℓ)) × 4^ℓ
print(f"\n  {'z':<8} {'ℓ':<8} {'P(obs)':<10} {'sqrt(γ_avg)':<12} {'4^ℓ':<10} {'X=sqrt(γ_avg)×4^ℓ':<18} {'K=P-1/X':<10}")
print(f"  {'─'*76}")
Ks = []
for z, dm_rd in desi_dm:
    ell = ell_from_z(z)
    p = D_C_desi(dm_rd) / D_1D(z)
    sg = math.sqrt(gamma_avg(ell))
    f4 = 4 ** ell
    X = sg * f4
    K = (p - 1) / X if X > 0 else 0
    Ks.append(K)
    print(f"  {z:<8.4f} {ell:<8.4f} {p:<10.4f} {sg:<12.6f} {f4:<10.4f} {X:<18.6f} {K:<10.4f}")

K_mean = np.mean(Ks)
K_std = np.std(Ks)
print(f"\n  K = {K_mean:.4f} ± {K_std:.4f} (標準偏差)")
print(f"  K 從 CY₃ = √(h¹¹×h²¹)/CY₃ = {math.sqrt(h11*h21)/CY3:.4f}")
print(f"  K 從 φ⁻¹ = {PHI_INV:.4f}")
print(f"  K 從 L₃/CY₃ = {4/CY3:.4f}")

# ================================================================
# 3. 用 K 結構值預測
# ================================================================
print(f"\n{'─'*80}")
print("  3. 用 K = CY₃ 結構嘅預測能力")
print(f"{'─'*80}")

# K 應該有結構來源，唔係 free parameter
# 可能 K = √(h¹¹×h²¹)/CY₃ × φ^(-k) 或類似
# 試幾個候選
candidates = {
    'K = √(h¹¹h²¹)/CY₃': math.sqrt(h11 * h21) / CY3,
    'K = 2·√(h¹¹h²¹)/CY₃': 2 * math.sqrt(h11 * h21) / CY3,
    'K = 4·√(h¹¹h²¹)/CY₃': 4 * math.sqrt(h11 * h21) / CY3,
    'K = √(h¹¹/h²¹)': math.sqrt(h11 / h21),
    'K = φ⁻¹': PHI_INV,
    'K = 2/φ': 2 * PHI_INV,
    'K = √(h¹¹h²¹)/CY₃ × φ⁻¹': math.sqrt(h11 * h21) / CY3 * PHI_INV,
    'K = L₃/CY₃': 4 / CY3,
    'K = 2·L₃/CY₃': 8 / CY3,
}

print(f"\n  {'K 候選':<35} {'值':<10} {'χ²(DESI)':<10}")
print(f"  {'─'*55}")
best = (None, 1e12)
for name, k_val in candidates.items():
    # 預測 P(ℓ) = 1 + k_val × sqrt(γ_avg) × 4^ℓ
    # D_pred = D_1D × (1 + k_val × sqrt(γ_avg) × 4^ℓ)
    chi2 = 0.0
    for z, dm_rd in desi_dm:
        ell = ell_from_z(z)
        d1d = D_1D(z)
        sg = math.sqrt(gamma_avg(ell))
        X = sg * (4 ** ell)
        p_pred = 1 + k_val * X
        d_pred = d1d * p_pred
        dm_pred = d_pred / BAO
        # 用 DESI DM error 做粗略 χ²
        err = 0.33  # 近似
        chi2 += ((dm_rd - dm_pred) / err) ** 2
    print(f"  {name:<35} {k_val:<10.6f} {chi2:<10.1f}")
    if chi2 < best[1]:
        best = (name, k_val, chi2)

print(f"\n  最佳 K: {best[0]} = {best[1]:.6f}, χ² = {best[2]:.1f}")

# 用最佳 K 做完整預測
K_best = best[1]
print(f"\n  完整預測 (K = {K_best:.6f}):")
print(f"  {'z':<8} {'ℓ':<8} {'D_pred(Mpc)':<14} {'DM/rd_pred':<12} {'DESI':<12} {'Δ/σ':<8}")
print(f"  {'─'*62}")
chi2_total = 0.0
for z, dm_rd in desi_dm:
    ell = ell_from_z(z)
    d1d = D_1D(z)
    sg = math.sqrt(gamma_avg(ell))
    X = sg * (4 ** ell)
    p_pred = 1 + K_best * X
    d_pred = d1d * p_pred
    dm_pred = d_pred / BAO
    err = 0.33
    sig = (dm_rd - dm_pred) / err
    chi2_total += sig ** 2
    print(f"  {z:<8.4f} {ell:<8.4f} {d_pred:<14.1f} {dm_pred:<12.4f} {dm_rd:<12.4f} {sig:<+8.2f}")

print(f"\n  χ²(DESI) = {chi2_total:.1f} (7 dof), χ²/dof = {chi2_total/7:.1f}")
print(f"  對比: 舊結構 χ²=13.2, matter+ζ χ²=34.9")

# ================================================================
# 4. 結論
# ================================================================
print(f"\n{'─'*80}")
print("  4. 誠實結論")
print(f"{'─'*80}")

print(f"""
  P(ℓ) = 1 + K × √(γ_avg(ℓ)) × 4^ℓ
  K = {K_best:.6f} ← 需要結構確認

  gamma_avg(ell) = Sum_{n <= 4^ell} gamma_n / 4^ell
  γ_n = 4sin²(πn/88)

  呢個係第一個「非 H(z)」嘅 IDCM 原生距離公式：
  D_app(ℓ) = D_1D(ℓ) × P(ℓ)
            = (44 - 44/4^ℓ) × (R_H/44) × (1 + K × √(γ_avg(ℓ)) × 4^ℓ)

  零熱耗散、零 Ω_L、零 ζ — 純粹幾何投影。
  但 K 仍需結構推導確認（唔係 fit 出來）。
""")

output = {
    'formula': 'D_app(ℓ) = (44-44/4^ℓ) × R_H/44 × (1 + K × √(γ_avg(ℓ)) × 4^ℓ)',
    'K_best': float(K_best),
    'K_candidates': {k: float(v) for k, v in candidates.items()},
    'chi2_best': float(chi2_total),
    'dof': 7
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/59_projection_factor_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"  結果: 59_projection_factor_results.json")
print(f"{'='*80}")