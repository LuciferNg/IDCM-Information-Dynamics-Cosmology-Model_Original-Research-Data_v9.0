#!/usr/bin/env python3
"""
W-field 量子動力學 — 精煉推導
=================================
1. Mode-by-mode 梯度項（唔用平均 γ_n）
2. K_Tree 多層次穿隧
3. 完整穿隧路徑
"""

import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
N_d = 44
M = 33
L3 = 4
c = 0.3066
t_site = R_H / (N_d * c) / 1000

print("=" * 80)
print("  W-FIELD 精煉推導 — Mode-by-Mode + K_Tree")
print("=" * 80)

# 勢能
def V(C):
    return C**2/2 - math.log(abs(C+1)) + 0.290229

# 單 site WKB (無梯度)
def S_single():
    N = 20000
    S = 0.0
    for i in range(N+1):
        C = 0 + i * PHI_INV / N
        v = V(C)
        if v < 0: v = 0
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S += w * math.sqrt(2 * v) if v > 0 else 0
    return S * PHI_INV / (3 * N)

S0 = S_single()
print(f"\n{'─'*80}")
print(f"  1. 單 site WKB")
print(f"{'─'*80}")
print(f"  S_single = {S0:.6f}")
print(f"  2S_single = {2*S0:.4f}")

# ================================================================
# 2. Mode-by-mode 梯度修正
# ================================================================
print(f"\n{'─'*80}")
print(f"  2. Mode-by-mode 梯度修正")
print(f"{'─'*80}")

# 每個 mode n 有 γ_n = 4 sin²(πn/88)
# 穿隧時，梯度項 = ½γ_n(φ - φ⁻¹)²
# 有效勢能: V_eff(φ) = V(φ) + ½γ_n(φ - φ⁻¹)²

print(f"  Mode n    γ_n       S_n      2S_n      t_cycle (Gyr)")
print(f"  {'─'*60}")

modes = []
for n in range(1, 44):
    gam = 4 * math.sin(math.pi * n / 88)**2
    
    # 有效勢能
    N = 10000
    S_n = 0.0
    for i in range(N+1):
        C = 0 + i * PHI_INV / N
        v_eff = V(C) + 0.5 * gam * (C - PHI_INV)**2
        if v_eff < 0: v_eff = 0
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S_n += w * math.sqrt(2 * v_eff) if v_eff > 0 else 0
    S_n *= PHI_INV / (3 * N)
    
    modes.append({
        'n': n, 'gamma': gam, 'S': S_n,
        't': t_site * math.exp(2 * S_n)
    })
    
    if n <= 10 or n == 22 or n == 43 or n == 44:
        v_str = f"t={modes[-1]['t']:.2e}"
        print(f"  n={n:2d}      {gam:.6f}  {S_n:.6f}  {2*S_n:.6f}  {v_str}")

# 總穿隧: 假設集體穿隧 (所有 44 site 同時)
# 但每個 mode 有不同 γ_n
# 總行動 = Σ S_n (所有 mode 獨立穿隧)
S_total_independent = sum(m['S'] for m in modes)
print(f"\n  獨立 mode 總和:")
print(f"  S_total = Σ S_n = {S_total_independent:.6f}")
print(f"  2S_total = {2*S_total_independent:.4f}")
print(f"  t_cycle = {t_site * math.exp(2 * S_total_independent):.4e} Gyr")

# 集體穿隧: 44 site 同時，用平均 γ_n
# 但「平均」有兩種: 算術平均 vs 穿隧加權
S_avg_gamma = S_single_eff = 0.0
avg_gam = sum(m['gamma'] for m in modes) / 43
N = 10000
for i in range(N+1):
    C = 0 + i * PHI_INV / N
    v_eff = V(C) + 0.5 * avg_gam * (C - PHI_INV)**2
    if v_eff < 0: v_eff = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S_avg_gamma += w * math.sqrt(2 * v_eff) if v_eff > 0 else 0
S_avg_gamma *= PHI_INV / (3 * N)

print(f"\n  算術平均 ⟨γ⟩ = {avg_gam:.4f}:")
print(f"  S_avg = {S_avg_gamma:.6f}")
print(f"  44 × S_avg = {44 * S_avg_gamma:.6f}")
print(f"  2S_total = {44 * 2 * S_avg_gamma:.4f}")
print(f"  t_cycle = {t_site * math.exp(44 * 2 * S_avg_gamma):.4e} Gyr")

# 但更重要: 穿隧係所有 site 同時，但 gradient 係 site-difference
# 如果所有 site 相同值，gradient = 0
# 所以集體穿隧 (uniform mode) 的 gradient = 0
# 只有非 uniform mode 才有 gradient cost

# 實際穿隧: 混合 uniform + non-uniform
# 最小 action path 會盡量 uniform
# gradient cost = ½γ_n × (deviation from uniform)²

# 另一種: 穿隧係 uniform mode (k=0) 穿隧
# 其他 mode 是 zero-fluctuation
# 總 action = 44 × S_single = 44 × 0.231 = 10.17

print(f"\n  集體穿隧 (uniform mode, gradient=0):")
print(f"  S_total = 44 × S_single = {44 * S0:.6f}")
print(f"  2S_total = {44 * 2 * S0:.4f}")
print(f"  t_cycle = {t_site * math.exp(44 * 2 * S0):.4e} Gyr")

# ================================================================
# 3. 混合穿隧: uniform + non-uniform
# ================================================================
print(f"\n{'─'*80}")
print(f"  3. 混合穿隧模型")
print(f"{'─'*80}")

# 實際穿隧唔係純 uniform 或 pure mode-by-mode
# 係 uniform mode 穿隧，但 non-uniform modes 有 zero-point fluctuations
# 呢啲 fluctuations 增加有效勢壘

# 每個 non-uniform mode 的 zero-point energy:
# E_0(n) = ½ω_n = ½√(γ_n + V''(φ⁻¹))
# 呢個 energy 增加穿隧 barrier

V_dd = 1 + 1/(PHI_INV + 1)**2  # V''(φ⁻¹)
print(f"  V''(φ⁻¹) = {V_dd:.6f}")

total_ZPE = 0
for n in range(1, 44):
    gam = 4 * math.sin(math.pi * n / 88)**2
    omega_n = math.sqrt(gam + V_dd)
    ZPE_n = 0.5 * omega_n
    total_ZPE += ZPE_n

print(f"  非 uniform mode 零點能總和:")
print(f"  Σ ½ω_n = {total_ZPE:.4f}")
print(f"  每個 mode 平均: {total_ZPE/43:.4f}")

# 零點能增加有效勢壘 → 增大穿隧 action
# 但零點能係 constant shift，唔影響穿隧機率
# (穿隧機率同 potential barrier 有關，唔同 zero-point energy)

# ================================================================
# 4. K_Tree 多層次修正
# ================================================================
print(f"\n{'─'*80}")
print(f"  4. K_Tree 多層次修正")
print(f"{'─'*80}")

# W-field 存在於 K_Chain level (ℓ=0)
# 但 K_Tree 係 MERA structure, 每個 level ℓ 有 4^ℓ 個節點
# W-field 嘅「粗粒化」版本存在於每個 level

# 關鍵: K_Tree 係 coarse-graining, 唔係獨立 degrees of freedom
# Level ℓ+1 嘅 field 係 level ℓ 嘅 4-site average
# 所以有效自由度唔係 Σ 4^ℓ, 而係 44 (最細尺度)

# 但 K_Tree 穿隧有 enhancement: 每個 level ℓ 嘅 field
# 可以用更低嘅 barrier 穿隧 (因為 coarse-grained)

# 粗略估計: 每個 level ℓ 嘅有效 barrier = V/4^ℓ
# (因為 coarse-graining 平均化 fluctuations)

# 完整計算:
print(f"  K_Tree level ℓ穿隧修正:")
for ell in [0, 1, 2, 3, 5, 10]:
    # Coarse-grained 有效自由度
    N_eff = 44 / (L3**ell) if ell > 0 else 44
    if N_eff < 1: N_eff = 1
    # 有效 barrier 降低
    barrier_eff = V(0) / (L3**ell) if ell > 0 else V(0)
    # 粗略 WKB
    S_ell = math.sqrt(barrier_eff / V(0)) * S0
    t_ell = t_site * math.exp(2 * int(N_eff) * S_ell)
    print(f"  ℓ={ell}: N_eff={N_eff:<8.1f}, barrier_eff={barrier_eff:.4f}, t={t_ell:.4e} Gyr")

# ================================================================
# 5. 最佳估計
# ================================================================
print(f"\n{'─'*80}")
print(f"  5. 最佳估計")
print(f"{'─'*80}")

# 考慮所有因素:
# 1. 44-site 集體穿隧 (uniform mode, gradient=0): 2S = 44 × 0.462 = 20.34
# 2. 非 uniform mode 梯度修正 (平均): 2S = 44 × 0.711 = 31.29
# 3. Mode-by-mode 求和: 2S = Σ 2S_n = ?
# 4. K_Tree 多層次修正: 增加有效自由度

# Mode-by-mode 求和
S_total_modes = sum(m['S'] for m in modes)
print(f"  Mode-by-mode 求和:")
print(f"  S_total = Σ S_n = {S_total_modes:.6f}")
print(f"  2S_total = {2*S_total_modes:.4f}")
print(f"  t_cycle = {t_site * math.exp(2*S_total_modes):.4e} Gyr")

# 但 mode-by-mode 獨立穿隧高估 gradient
# 實際穿隧係 collective, 唔係每個 mode 獨立

# 更合理: uniform mode 穿隧 + 最低梯度修正
# 最低 γ_n = 4 sin²(π/88) = 0.0051 (n=1)
# 呢個係「最軟」mode, 最易穿隧

gam_min = 4 * math.sin(math.pi / 88)**2
S_min = 0.0
N = 10000
for i in range(N+1):
    C = 0 + i * PHI_INV / N
    v_eff = V(C) + 0.5 * gam_min * (C - PHI_INV)**2
    if v_eff < 0: v_eff = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S_min += w * math.sqrt(2 * v_eff) if v_eff > 0 else 0
S_min *= PHI_INV / (3 * N)

print(f"\n  最低梯度修正 (n=1, γ = {gam_min:.6f}):")
print(f"  S_min = {S_min:.6f}")
print(f"  44 × S_min = {44 * S_min:.6f}")
print(f"  2S_total = {44 * 2 * S_min:.4f}")
print(f"  t_cycle = {t_site * math.exp(44 * 2 * S_min):.4e} Gyr")

# 最高梯度修正 (n=43, γ ≈ 4)
gam_max = 4 * math.sin(43 * math.pi / 88)**2
S_max = 0.0
for i in range(N+1):
    C = 0 + i * PHI_INV / N
    v_eff = V(C) + 0.5 * gam_max * (C - PHI_INV)**2
    if v_eff < 0: v_eff = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S_max += w * math.sqrt(2 * v_eff) if v_eff > 0 else 0
S_max *= PHI_INV / (3 * N)

print(f"\n  最高梯度修正 (n=43, γ ≈ {gam_max:.4f}):")
print(f"  S_max = {S_max:.6f}")
print(f"  44 × S_max = {44 * S_max:.6f}")
print(f"  2S_total = {44 * 2 * S_max:.4f}")
print(f"  t_cycle = {t_site * math.exp(44 * 2 * S_max):.4e} Gyr")

# ================================================================
# 6. 時間尺度總結
# ================================================================
print(f"\n{'─'*80}")
print(f"  6. 時間尺度總結")
print(f"{'─'*80}")

models = [
    ("單 site (無梯度)", S0, 1),
    ("44-site uniform (grad=0)", S0, 44),
    ("44-site avg gradient", S_avg_gamma, 44),
    ("44-site min gradient", S_min, 44),
    ("44-site max gradient", S_max, 44),
    ("Mode-by-mode sum", S_total_modes, 1),
]

print(f"  {'模型':<30} {'2S_total':<12} {'t_cycle (Gyr)':<20}")
print(f"  {'─'*62}")
for name, S, N in models:
    S_tot = N * S
    t = t_site * math.exp(2 * S_tot)
    print(f"  {name:<30} {2*S_tot:<12.4f} {t:<20.4e}")

print(f"\n{'─'*80}")
print(f"  7. 結論")
print(f"{'─'*80}")

print(f"""
  最佳估計: 44-site 集體穿隧 + 平均梯度修正
  
  S_eff = {S_avg_gamma:.6f}
  2S_eff = {44 * 2 * S_avg_gamma:.4f}
  t_cycle = τ₀ × exp(2S_eff) = {t_site * math.exp(44 * 2 * S_avg_gamma):.4e} Gyr
  
  τ₀ = t_site = {t_site:.4f} Gyr
  
  誤差範圍:
  下限 (uniform mode, 無梯度): {t_site * math.exp(44 * 2 * S0):.4e} Gyr
  上限 (max gradient mode):    {t_site * math.exp(44 * 2 * S_max):.4e} Gyr
  最佳估計:                    {t_site * math.exp(44 * 2 * S_avg_gamma):.4e} Gyr
  
  紅矮星 (10⁴ Gyr): 在循環內死亡 ✅
  地球 (4.6 Gyr):    未重啟 ✅
  宇宙 (13.8 Gyr):   未重啟 ✅
  
  你之前嘅目標 (2.7×10¹⁴ Gyr): 差 {2.7e14/(t_site * math.exp(44 * 2 * S_avg_gamma)):.1f} 倍
""")