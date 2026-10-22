#!/usr/bin/env python3
"""
從頭開始 — 完全結構推導，無舊公式，無物理假設
================================================
只用：
  x² + x - 1 = 0 → φ
  ε = φ⁻¹/4
  κ = (εφ)² = 1/16
  N_d = 44
  M = 33
  L3 = 4
"""

import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
KAP = 1/16
N_d = 44
M = 33
L3 = 4

print("=" * 80)
print("  完全結構推導：從 0,1 到時間尺度")
print("=" * 80)

# ================================================================
# 1. 從結構推導嘅量（無自由參數）
# ================================================================
print(f"\n{'─'*80}")
print("  1. 從結構推導的量（無自由參數）")
print(f"{'─'*80}")

print(f"  φ = {PHI:.10f}")
print(f"  ε = φ⁻¹/4 = {EPS:.10f}")
print(f"  κ = (εφ)² = 1/16 = {KAP}")
print(f"  N_d = {N_d}")
print(f"  M = {M}")
print(f"  L3 = {L3}")
print(f"  R_H = c/H₀ = {R_H:.2f} Mpc")
print(f"  λ_sync = 2πR_H/88 = {LAMBDA_SYNC:.2f} Mpc")
print(f"  γ_n = 4 sin²(πn/88) — K_Chain 本徵值")

# ================================================================
# 2. 幾何時間尺度
# ================================================================
print(f"\n{'─'*80}")
print("  2. 幾何時間尺度（純環幾何）")
print(f"{'─'*80}")

c = 0.3066  # Mpc/Myr
t_site = R_H / (N_d * c) / 1000  # Gyr
t_round = N_d * t_site            # Gyr
T_SYNC = 88 * t_site              # Gyr
T_1 = LAMBDA_SYNC / c / 1000      # Gyr

print(f"  t_site = R_H/(44c)          = {t_site:.4f} Gyr")
print(f"          光走一個 site 間距 ({R_H/N_d:.2f} Mpc)")
print(f"")
print(f"  t_round = N_d × t_site       = {t_round:.4f} Gyr")
print(f"          光繞環一圈 = Hubble 時間")
print(f"")
print(f"  T_SYNC = 88 × t_site         = {T_SYNC:.4f} Gyr")
print(f"          88 步完成相位循環")
print(f"")
print(f"  T_1 = λ_sync/c               = {T_1:.4f} Gyr")
print(f"        fundamental mode 週期")

# ================================================================
# 3. K_Tree 時間尺度
# ================================================================
print(f"\n{'─'*80}")
print("  3. K_Tree 時間尺度")
print(f"{'─'*80}")

# 每個 K_Tree level ℓ 有 4^ℓ 個節點
# 全部節點數 = Σ_{ℓ=0}^{M} 4^ℓ = (4^{M+1} - 1)/3
total_nodes = (L3**(M+1) - 1) // 3
print(f"  K_Tree 總節點數: {total_nodes:.2e}")

# 時間 = 節點數 × t_site
t_tree = total_nodes * t_site
print(f"  全部節點遍歷: {t_tree:.2e} Gyr")

# 特定 level ℓ 嘅節點數
print(f"")
print(f"  Level ℓ:   節點數 4^ℓ    時間 = 4^ℓ × t_site")
for ell in [0, 3, 5, 7, 9, 10, 11, 12, 15, 20, 22, 24, 33]:
    nodes = L3 ** ell
    t_level = nodes * t_site
    scale = R_H / nodes if nodes > 0 else R_H
    if scale > 1:
        phys = f"{scale:.1f} Mpc"
    elif scale > 1e-3:
        phys = f"{scale*1e3:.1f} kpc"
    elif scale > 1e-6:
        phys = f"{scale*1e6:.1f} pc"
    elif scale > 1e-9:
        phys = f"{scale*1e9:.1f} AU"
    else:
        phys = f"{scale:.2e} Mpc"
    print(f"  ℓ={ell:2d}:  {nodes:<12.2e}   {t_level:<12.4e} Gyr  ({phys})")

# ================================================================
# 4. K_Chain ⊗ K_Tree 組合時間尺度
# ================================================================
print(f"\n{'─'*80}")
print("  4. K_Chain ⊗ K_Tree 組合時間尺度")
print(f"{'─'*80}")

# 88 SYNC 步 × 4^ℓ K_Tree 節點
print(f"  88 × 4^ℓ × t_site:")
for ell in [0, 5, 10, 15, 20, 21, 22, 23, 24, 30, 33]:
    t = 88 * (L3**ell) * t_site
    print(f"  ℓ={ell:2d}:  {t:.2e} Gyr")

print(f"")
print(f"  44 × 4^ℓ × t_site:")
for ell in [0, 5, 10, 15, 20, 21, 22, 23, 24, 30, 33]:
    t = N_d * (L3**ell) * t_site
    print(f"  ℓ={ell:2d}:  {t:.2e} Gyr")

# ================================================================
# 5. 全部結構時間尺度
# ================================================================
print(f"\n{'─'*80}")
print("  5. 全部結構時間尺度一覽")
print(f"{'─'*80}")

scales = [
    ("t_site", t_site, "光走相鄰 site", "環幾何"),
    ("T_1", T_1, "fundamental mode 週期", "環幾何"),
    ("t_round", t_round, "光繞環一圈 = H₀⁻¹", "環幾何"),
    ("T_SYNC", T_SYNC, "88 步相位循環", "環幾何"),
    ("44×t_round", N_d * t_round, "44 次繞環", "組合"),
    ("88×t_round", 88 * t_round, "88 次繞環", "組合"),
    ("4^10×t_site", L3**10 * t_site, "K_Tree ℓ=10 節點遍歷", "K_Tree"),
    ("4^22×t_site", L3**22 * t_site, "K_Tree ℓ=22 節點遍歷", "K_Tree"),
    ("44×4^22×t_site", N_d * L3**22 * t_site, "K_Chain×K_Tree ℓ=22", "組合"),
    ("44×4^24×t_site", N_d * L3**24 * t_site, "K_Chain×K_Tree ℓ=24", "組合"),
    ("K_Tree 全節點", total_nodes * t_site, "全部 K_Tree 節點遍歷", "K_Tree"),
    ("Poincaré recurrence", 0, "LCM(1..44)×T_SYNC/44", "動力學"),
]

# Poincaré recurrence
def lcm_range(n):
    l = 1
    for i in range(2, n+1):
        l = l * i // math.gcd(l, i)
    return l

lcm44 = lcm_range(44)
t_poincare = lcm44 * T_SYNC / 44

scales[11] = ("Poincaré recurrence", t_poincare, "LCM(1..44)×T_SYNC/44", "動力學")

for name, val, desc, src in scales:
    if val < 1:
        val_str = f"{val*1e3:.2f} Myr"
    elif val < 1e6:
        val_str = f"{val:.4e} Gyr"
    else:
        val_str = f"{val:.4e} Gyr"
    print(f"  {name:<25s} {val_str:<20s}  {desc:<30s}  [{src}]")

# ================================================================
# 6. 結論
# ================================================================
print(f"\n{'─'*80}")
print("  6. 結構推導結論")
print(f"{'─'*80}")

print(f"""
  從 0,1 出發，唯一能嚴格推導的時間尺度：
  
  t_site = R_H/(44c) = {t_site:.4f} Gyr      ← 最基礎，環幾何
  t_round = 44×t_site = {t_round:.4f} Gyr     ← 繞環一圈
  T_SYNC = 88×t_site = {T_SYNC:.4f} Gyr       ← 相位循環
  T_1 = λ_sync/c = {T_1:.4f} Gyr              ← 基本波週期
  
  以上全部來自環幾何，無自由參數。
  
  循環時間 t_cycle 需要額外物理假設才能確定：
  - 如果係量子穿隧：需要 WKB 勢能
  - 如果係 Poincaré recurrence：t ≈ 10²⁰ Gyr
  - 如果係 K_Tree 節點遍歷：t ≈ 4^ℓ × t_site
  
  邊個係正確嘅「循環」定義？
  (1) SYNC 相位循環 → T_SYNC = 26.94 Gyr？
  (2) 所有 mode 回到原位 → 1.27 × 10²⁰ Gyr？
  (3) 遞迴收斂 → 8×t_round = 107.8 Gyr？
  (4) 其他？
""")