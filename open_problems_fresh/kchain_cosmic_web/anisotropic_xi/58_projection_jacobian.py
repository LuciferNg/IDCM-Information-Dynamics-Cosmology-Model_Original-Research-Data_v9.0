#!/usr/bin/env python3
"""
58_projection_jacobian.py — 從 1D→3D 投影雅可比推導 apparent 距離
====================================================================
範式斷裂：放棄 H(z)（膨脹率），改為推導投影雅可比（幾何畸變率）。

核心 insight：
  宇宙冇膨脹。K_Chain 44-site 閉合環固定。
  觀測者嘅「紅移-距離關係」= 1D 離散鏈投影到 3D 嘅幾何畸變率。
  
  遞迴深度 ℓ = log₄(1+z) 決定粗粒化尺度。
  每層 ℓ，K_Chain 嘅 44 個 site 被粗粒化為 44/4^ℓ 個 super-site。
  每個 super-site 嘅「3D 投影體積」由 K_Chain 本徵值 γ_n 同 SYNC 相位 θ_n 決定。
  
  投影雅可比 J(ℓ) = 1D 切向量喺 3D 嘅「拉伸因子」。
  累積 D_app(ℓ) = ∫₀^ℓ J(ℓ') dℓ' = 觀測者睇到嘅 apparent 距離。
  
  呢個 D_app(ℓ) 就係 DESI 量度嘅 DM/rd（冇空間膨脹假設）。
"""
import math
import numpy as np
from scipy import integrate
import json

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
H0_IDCM = 72.59
C_LIGHT = 299792.458
N_D = 44
BAO = 147.44
R_H = C_LIGHT / H0_IDCM  # 4129.94 Mpc

print("=" * 80)
print("  投影雅可比 — 1D K_Chain → 3D 觀測者嘅幾何畸變率")
print("=" * 80)

# ================================================================
# 1. K_Chain 結構（固定於 ℓ=0 嘅原始鏈）
# ================================================================
print(f"\n{'─'*80}")
print("  1. K_Chain 44-site 結構")
print(f"{'─'*80}")

gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_D)])
v_g_n = np.array([math.cos(math.pi * n / 88) for n in range(1, N_D)])
# SYNC 相位: θ_n = n × 2π/88
theta_n = np.array([n * 2 * math.pi / 88 for n in range(N_D)])  # n=0..43

# CY₃ 投影算子: h¹¹=36, h²¹=98
h11, h21 = 36, 98
CY3 = h11 + h21  # 134

print(f"  K_Chain: {N_D} sites, γ_n = 4sin²(πn/88), n=1..43")
print(f"  SYNC 相位: θ_n = n × 2π/88")
print(f"  CY₃: h¹¹={h11}, h²¹={h21}, total={CY3}")

# ================================================================
# 2. 遞迴深度 ℓ 同粗粒化
# ================================================================
print(f"\n{'─'*80}")
print("  2. 遞迴深度 ℓ = log₄(1+z) 同粗粒化")
print(f"{'─'*80}")

def ell_from_z(z):
    """recursion depth ℓ = log₄(1+z)"""
    if z < 0:
        return 0.0
    return math.log(1 + z) / math.log(4)

def z_from_ell(ell):
    """z = 4^ℓ - 1"""
    return 4**ell - 1

# 每層 ℓ 嘅粗粒化
# 原始 K_Chain: 44 sites
# 粗粒化後: N_eff(ℓ) = 44 / 4^ℓ 個 super-site
# 每個 super-site 嘅「能量」= Σ_{n in block} γ_n

def N_eff(ell):
    """有效 super-site 數"""
    ne = N_D / (4 ** ell)
    return max(ne, 1.0)

def gamma_at_ell(ell):
    """
    喺 ℓ 層，有效本徵值 = 粗粒化後嘅平均能量。
    每個 super-site 覆蓋 4^ℓ 個原始 site。
    平均能量 = (1/4^ℓ) × Σ_{n in block} γ_n
    """
    block_size = int(max(round(4 ** ell), 1))
    # 逐 block 計算
    n_blocks = N_D // block_size
    if n_blocks == 0:
        n_blocks = 1
    block_gammas = []
    for b in range(n_blocks):
        start = b * block_size
        end = min((b + 1) * block_size, N_D - 1)
        if end > start:
            avg = gamma_n[start:end].sum() / (end - start)
        else:
            avg = 0.0
        block_gammas.append(avg)
    return np.array(block_gammas)

# ================================================================
# 3. 投影雅可比 J(ℓ)
# ================================================================
print(f"\n{'─'*80}")
print("  3. 投影雅可比 J(ℓ) — 1D→3D 幾何畸變率")
print(f"{'─'*80}")

# 核心推導：
# K_Chain 喺 3D 嘅投影，每個 site n 貢獻振幅 √γ_n × cos(θ_n)
# 切向量 (Tangent) 喺 site n: T(n) = √γ_n × ∇θ_n
# 其中 ∇θ_n = dθ_n/dn = 2π/88 (phase gradient)
# 
# 喺 ℓ 層（粗粒化咗），有效切向量 = block average
# J(ℓ) = |T_eff(ℓ)| = 粗粒化後嘅切向量模長
#
# 物理意義：J(ℓ) 係「1D 單位長度 → 3D 投影長度」嘅拉伸因子
# H_app(ℓ) = c × (1+z) × ln(4) / J(ℓ) — apparent H(z)

def J_ell(ell):
    """
    投影雅可比喺 ℓ 層。
    J(ℓ) = sqrt(mean_gamma(ℓ)) × (4^ℓ × 2π/88) × CY₃_factor
    
    - sqrt(mean_gamma): 平均 mode 振幅
    - 4^ℓ × 2π/88: 粗粒化後嘅有效相位梯度
    - CY₃_factor: CY₃ 投影嘅幾何因子
    """
    block_size = int(max(round(4 ** ell), 1))
    n_blocks = N_D // block_size
    if n_blocks == 0:
        n_blocks = 1
    block_size = N_D // n_blocks
    
    # 每 block 嘅平均 γ
    block_avg = 0.0
    for b in range(n_blocks):
        start = b * block_size
        end = min((b + 1) * block_size, N_D - 1)
        if end > start:
            block_avg += gamma_n[start:end].sum()
    block_avg /= n_blocks
    
    # 有效相位梯度
    grad_eff = (4 ** ell) * 2 * math.pi / 88
    
    # CY₃ 投影因子: h¹¹/h²¹ 比率決定投影嘅幾何
    # 3D 投影 = 3 個方向嘅叉積
    # 每個方向嘅貢獻 = √(h¹¹) × φ^{-k} 或者類似的
    # 簡化：用 h¹¹ × h²¹ / CY₃² 作為平均投影因子
    cy3_factor = math.sqrt(h11 * h21) / CY3  # ~0.453
    
    # J(ℓ) = sqrt(avg_γ) × grad_eff × cy3_factor × site_spacing(ℓ)
    # site_spacing(ℓ) = (R_H/44) × 4^ℓ (物理尺度)
    site_spacing = (R_H / N_D) * (4 ** ell)
    j = math.sqrt(block_avg) * grad_eff * cy3_factor * site_spacing
    
    return j

# 驗證 J(ℓ) 形狀
print(f"\n  {'ℓ':<6} {'z(ℓ)':<10} {'N_eff':<10} {'J(ℓ)':<12} {'H_app':<12}")
print(f"  {'─'*50}")
for ell in np.arange(0, 2.5, 0.25):
    z = z_from_ell(ell)
    ne = N_eff(ell)
    j = J_ell(ell)
    # H_app = c × (1+z) × ln(4) / J(ℓ)
    h_app = C_LIGHT * (1 + z) * math.log(4) / j if j > 0 else float('inf')
    print(f"  {ell:<6.2f} {z:<10.4f} {ne:<10.1f} {j:<12.4f} {h_app:<12.1f}")

# ================================================================
# 4. 累積 apparent 距離 D_app(ℓ)
# ================================================================
print(f"\n{'─'*80}")
print("  4. Apparent 距離 D_app(ℓ) = ∫₀^ℓ J(ℓ') dℓ'")
print(f"{'─'*80}")

def D_app_ell(ell):
    """累積 apparent 距離"""
    if ell <= 0:
        return 0.0
    N = 200
    ells = np.linspace(0, ell, N)
    d_ell = ell / N
    js = np.array([J_ell(e) for e in ells])
    return np.sum(d_ell * js)

# 對比 DESI DM/rd
print(f"\n  {'z':<8} {'ℓ':<8} {'D_app(Mpc)':<14} {'DM/rd':<12} {'DESI':<12}")
print(f"  {'─'*54}")
desi_test = [(0.295, 7.94, 'DV'), (0.510, 13.59, 'DM'), (0.510, 21.86, 'DH'),
             (0.706, 17.35, 'DM'), (0.934, 21.58, 'DM'), (1.321, 27.60, 'DM'),
             (1.484, 30.51, 'DM'), (2.330, 38.99, 'DM')]
for z, val, qty in desi_test:
    ell = ell_from_z(z)
    da = D_app_ell(ell)
    dm_rd = da / BAO
    print(f"  {z:<8.4f} {ell:<8.4f} {da:<14.1f} {dm_rd:<12.4f} {val:<12.4f}")

# ================================================================
# 5. 誠實分析
# ================================================================
print(f"\n{'─'*80}")
print("  5. 誠實分析：J(ℓ) 形狀同 DESI 嘅匹配度")
print(f"{'─'*80}")

# 計算 J(ℓ) 嘅 analytic form（如果可能）
# 對於大 ℓ，block_size = 4^ℓ 大，block_avg → 2.0（所有 γ_n 嘅平均）
# J(ℓ) ∝ sqrt(2) × 4^ℓ × 2π/88 × cy3_factor
# J(ℓ) = K × 4^ℓ, K = sqrt(2) × 2π/88 × cy3_factor

K = math.sqrt(2) * 2 * math.pi / 88 * math.sqrt(h11 * h21) / CY3
print(f"\n  J(ℓ) 高 ℓ 漸近形式: J(ℓ) ≈ {K:.4f} × 4^ℓ")
print(f"  D_app(ℓ) ≈ ∫ {K:.4f} × 4^ℓ dℓ = {K:.4f} × 4^ℓ / ln(4) + const")
print(f"  DM/rd ≈ ({K_asy:.4f} / ln(4)) × 4^ℓ / BAO ≈ {(K_asy/math.log(4)/BAO):.6f} × 4^ℓ")

# 對比 DESI: DM/rd vs 4^ℓ
print(f"\n  {'z':<8} {'ℓ':<8} {'DM/rd':<10} {'4^ℓ':<10} {'ratio':<10}")
print(f"  {'─'*46}")
for z, val, qty in desi_test:
    if qty == 'DM':
        ell = ell_from_z(z)
        ratio = val / (4 ** ell)
        print(f"  {z:<8.4f} {ell:<8.4f} {val:<10.4f} {4**ell:<10.4f} {ratio:<10.4f}")

output = {
    'method': 'projection Jacobian J(ℓ) from K_Chain→3D',
    'J_ell': 'sqrt(mean_γ(ℓ)) × 4^ℓ × 2π/88 × √(h¹¹h²¹)/CY₃',
    'asymptotic': f'J(ℓ) ≈ {K:.4f} × 4^ℓ',
    'note': '形狀未 normalize（J(0) 同 H₀ 嘅關係需要進一步推導）'
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/58_jacobian_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 58_jacobian_results.json")
print(f"{'='*80}")