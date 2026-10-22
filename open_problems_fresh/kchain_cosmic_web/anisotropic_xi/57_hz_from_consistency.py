#!/usr/bin/env python3
"""
57_hz_from_consistency.py — 重新推導 v3：從 2步一致性回朔 + 熱耗散
====================================================================
用戶指明推導鏈：
  W-field 2步一致性回朔方程
  → 維持一致性需要熱耗散 (SYNC cost=2, JMP cost=7)
  → 熱耗散 = 暗能量
  → B=4 = K_Tree 分支因子 = 結構成本

W-field 方程：
  Φ_i(t+1) - 2Φ_i(t) + Φ_i(t-1) = Σ_j K_ij Φ_j(t) - φ Φ_i(t)
  左：2步回朔（二階時間差分）
  右：K_chain⊗K_tree 一致性 + 自交互

SYNC cost = 2（熱耗散，每步基礎成本）
JMP cost = 7（結構跳躍成本）
Total cycle cost = 16 → κ = 1/16

暗能量 = 系統維持一致性所需嘅熱耗散
H(z) = 呢個熱耗散隨深度 z 嘅累積效應

關鍵：唔應該有「Ω_L baseline + ζ」兩層
應該直接從「2步回朔 → 熱耗散 → effective H(z)」推導
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
SYNC_COST = 2
JMP_COST = 7
KAPPA = 1 / 16

print("=" * 80)
print("  重新推導 v3 — H(z) from 2-step consistency + thermal dissipation")
print("=" * 80)

# ================================================================
# 1. 結構基礎
# ================================================================
print(f"\n{'─'*80}")
print("  1. 從 2步回朔方程到熱耗散結構")
print(f"{'─'*80}")

# W-field: Φ_i(t+1) - 2Φ_i(t) + Φ_i(t-1) = Σ_j K_ij Φ_j(t) - φ Φ_i(t)
# K_chain 本徵值: γ_n = 4sin²(πn/88)
# 2步回朔 ⇒ 每步需要 SYNC = 2 熱耗散
# 深度 z 時，活躍模式數 n_active(z) = ?

# 核心 insight: 紅移 z = 操作步數
# z=0: 只有本地 site (N_d=44 中 1 個活躍)
# z→∞: 全部 44 個 site 活躍
# 活躍數 = 已解鎖嘅 site = 44 - 44/(1+z) = 44z/(1+z)
# （41 號文件嘅 n_eff = 28/(1+z) 係未解鎖模式，呢度係反轉）

def n_active(z):
    """已解鎖 site 數：z=0→0, z→∞→44"""
    return N_D - N_D / (1 + z)  # 44 - 44/(1+z) = 44z/(1+z)

# 熱耗散密度 = 每步 SYNC cost × 活躍 site 數
# 但仲有 JMP cost（結構跳躍）
# Total cycle cost = SYNC + JMP = 2 + 7 = 9? 定係 16?
# 04_rendering_boundary.md: Total cycle cost = 16 → κ = 1/16

print(f"\n  2步回朔方程: Φ_i(t+1) - 2Φ_i(t) + Φ_i(t-1) = Σ_j K_ij Φ_j(t) - φ Φ_i(t)")
print(f"  SYNC cost = {SYNC_COST} (熱耗散/步)")
print(f"  JMP cost = {JMP_COST} (結構跳躍/步)")
print(f"  Total cycle = {SYNC_COST + JMP_COST} = κ⁻¹ = {KAPPA}⁻¹ = {1/KAPPA}")
print(f"  κ = 1/16 = {KAPPA}")
print(f"\n  n_active(z) = N_d - N_d/(1+z) = {N_D}z/(1+z)")
print(f"  z=0: n_active = {n_active(0):.0f}")
print(f"  z=2.33: n_active = {n_active(2.33):.1f}")
print(f"  z→∞: n_active → {N_D}")

# ================================================================
# 2. 從熱耗散推 H(z)
# ================================================================
print(f"\n{'─'*80}")
print("  2. H(z) = 熱耗散嘅累積效應")
print(f"{'─'*80}")

# 核心假設: H(z) ∝ 累積熱耗散能量
# 每個活躍 site 貢獻 SYNC_cost = 2 嘅熱耗散
# 但隨著深度 z 增加，耗散唔係簡單線性疊加
# 因為 2步回朔方程嘅本徵值 γ_n 決定每步嘅「效率」

# 更精確：每個 mode n 有能量 γ_n = 4sin²(πn/88)
# 活躍 mode 嘅能量疊加 = Σ_{n ≤ n_active} γ_n
# 呢個係 40 號方法 B 嘅方向，但 n_active 方向反轉咗

# H²(z) ∝ E_base + Σ_{n ≤ n_active(z)} γ_n
# 其中 E_base = 維持最少一致性嘅成本（z=0 時）

gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_D)])
gamma_total = gamma_n.sum()  # 86

def energy_active(z):
    """已解鎖 mode 嘅總能量"""
    na = int(round(n_active(z)))
    if na <= 0:
        return 0.0
    if na >= N_D - 1:
        return gamma_total
    return gamma_n[:na].sum()

# E_base = 最低成本 = SYNC_cost × 1 site = 2
# 或者 E_base = SYNC_cost + JMP_cost = 9
# 或者 E_base = κ⁻¹ = 16

E_base = 16.0  # Total cycle cost = 16
print(f"\n  E_base = {E_base} (最小 cycle cost)")
print(f"  γ_total = {gamma_total:.0f} (K_Chain 總能量)")

# H²(z) = H₀² × (E_base + energy_active(z)) / E_base
def hz_dissipation(z):
    """H(z) from dissipation energy"""
    ea = energy_active(z)
    return H0_IDCM * math.sqrt((E_base + ea) / E_base)

def hz_dissipation_v2(z):
    """
    v2: 每個 mode 嘅貢獻 = γ_n × (SYNC_cost/JMP_cost factor)
    因為熱耗散效率隨 mode 數變化
    """
    na = int(round(n_active(z)))
    if na <= 0:
        return H0_IDCM
    if na >= N_D - 1:
        na = N_D - 2
    # 加權：低 n mode 嘅群速度高，效率高
    total = E_base
    for n in range(1, na + 1):
        # 每個 mode 嘅貢獻 = γ_n × (v_g(n) 效率因子)
        vg = math.cos(math.pi * n / 88)
        if vg < 0.05:
            vg = 0.05
        total += gamma_n[n-1] * vg
    return H0_IDCM * math.sqrt(total / E_base)

print(f"\n  {'z':<6} {'n_active':<10} {'E_active':<12} {'H(v1)':<10} {'H(v2)':<10} {'H_ΛCDM':<10}")
print(f"  {'─'*58}")
for zt in [0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 2.33]:
    na = n_active(zt)
    ea = energy_active(zt)
    h1 = hz_dissipation(zt)
    h2 = hz_dissipation_v2(zt)
    h_lcdm = 67.4 * math.sqrt(0.315 * (1+zt)**3 + 0.685)
    print(f"  {zt:<6.2f} {na:<10.2f} {ea:<12.1f} {h1:<10.1f} {h2:<10.1f} {h_lcdm:<10.1f}")

# ================================================================
# 3. DESI 驗證
# ================================================================
print(f"\n{'─'*80}")
print("  3. DESI DR2 驗證")
print(f"{'─'*80}")

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

def desi_pred(h_func, N=300):
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        h = h_func(z)
        if qty in ('DM', 'DV'):
            zz = np.linspace(0, z, N)
            mid = (zz[1:] + zz[:-1]) / 2
            hm = np.array([h_func(zm) for zm in mid])
            dm = C_LIGHT * np.sum((zz[1:] - zz[:-1]) / hm) / BAO
        if qty == 'DM':
            model.append(dm)
        elif qty == 'DH':
            model.append(C_LIGHT / h / BAO)
        elif qty == 'DV':
            dh = C_LIGHT / h / BAO
            model.append((z * dm**2 * dh) ** (1/3))
    return np.array(model)

m1 = desi_pred(hz_dissipation)
m2 = desi_pred(hz_dissipation_v2)
d1 = np.array(desi_val) - m1
d2 = np.array(desi_val) - m2
c1 = d1 @ cov_desi_inv @ d1
c2 = d2 @ cov_desi_inv @ d2

print(f"\n  {'z':<8} {'量':<6} {'H(v1)':<12} {'H(v2)':<12} {'DESI':<12}")
print(f"  {'─'*50}")
for i in range(len(desi_z)):
    print(f"  {desi_z[i]:<8.3f} {desi_qty[i]:<6} {m1[i]:<12.4f} {m2[i]:<12.4f} {desi_val[i]:<12.4f}")

print(f"\n  χ²(v1) = {c1:.1f} (13 dof)")
print(f"  χ²(v2) = {c2:.1f} (13 dof)")
print(f"  對比: 舊結構 χ²=13.2, matter+ζ χ²=34.9")

# ================================================================
# 4. 分析
# ================================================================
print(f"\n{'─'*80}")
print("  4. 誠實分析")
print(f"{'─'*80}")

# 如果 v1 或 v2 接近 χ²=13.2 → 推導成功
# 如果差好遠 → 需要進一步 insight

print(f"\n  {'v1 (E_base + γ sum)':<30} χ² = {c1:<.1f}")
print(f"  {'v2 (v_g weighted)':<30} χ² = {c2:<.1f}")
print(f"  {'舊結構 (Ω_L + ζ)':<30} χ² = 13.2")
print(f"  {'matter + ζ':<30} χ² = 34.9")

output = {
    'method': 'W-field 2-step consistency + thermal dissipation',
    'n_active': '44 - 44/(1+z)',
    'E_base': 16.0,
    'chi2_v1': float(c1),
    'chi2_v2': float(c2),
    'dof': 13
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/57_consistency_hz_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 57_consistency_hz_results.json")
print(f"{'='*80}")