#!/usr/bin/env python3
"""
IDCM H(z) 第一原理推導
=======================
從 K_Chain fixed ring 出發，推導距離-紅移關係。
暗能量唔係「神秘力量」，係 SYNC 張力嘅結構常數。

前提:
- K_Chain = 44-site fixed ring，唔膨脹
- 時間 = 操作維（遞迴 C_{n+1}=1/(1+C_n)）
- 紅移 = 波長拉伸，唔係空間膨脹
- 3D 空間 = CY₃ projection from 1D K_Chain
- Ω_Λ = 4/(φ⁴-1) = 0.683 (結構常數)
- Ω_m = 1 - Ω_Λ = 0.317 (結構常數)

方法:
1. 從 K_Chain 色散關係推導能量密度
2. 從 SYNC 張力推導暗能量密度
3. 從 K_Tree 層次推導物質密度隨 z 嘅變化
4. 推導 H(z) 形式
5. 測試 DESI DR2
"""
import math, sys
import numpy as np

print("=" * 80)
print("  IDCM H(z) 第一原理推導")
print("=" * 80)

# ================================================================
# 0. 基本參數
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
KAP = 1 / 16
N_d = 44
B = 4
M = 33

# 物理常數
c_km_s = 299792.458
c_mpc_gyr = c_km_s * 3.15576e16 / 3.085677581e19  # 306.6 Mpc/Gyr
R_H = 4129.94  # Mpc
H0 = c_mpc_gyr / R_H  # 72.59 km/s/Mpc

# 結構參數
Omega_L = 4 / (PHI**4 - 1)  # 0.683
Omega_m = 1 - Omega_L  # 0.317

# 時間尺度
t_site = R_H / (N_d * c_mpc_gyr)  # 0.306 Gyr
tau_depth = N_d * t_site  # 13.47 Gyr
T_SYNC = 2 * N_d * t_site  # 26.94 Gyr

# BAO scale
lambda_sync = 2 * math.pi * R_H / 88  # 294.88 Mpc
rd = lambda_sync / 2  # 147.44 Mpc

print(f"\n基本參數:")
print(f"  φ = {PHI:.10f}")
print(f"  Ω_Λ = {Omega_L:.6f} = 4/(φ⁴-1)")
print(f"  Ω_m = {Omega_m:.6f}")
print(f"  H₀ = {H0:.4f} km/s/Mpc")
print(f"  R_H = {R_H:.2f} Mpc")
print(f"  BAO rd = {rd:.4f} Mpc")
print(f"  t_site = {t_site:.4f} Gyr")
print(f"  τ_depth = {tau_depth:.4f} Gyr")

# ================================================================
# 1. K_Chain 能量結構
# ================================================================
print(f"\n{'─'*80}")
print(f"  1. K_Chain 能量結構")
print(f"{'─'*80}")

# K_Chain 本徵值
gamma = [4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d)]
gamma_total = sum(gamma)
print(f"  K_Chain 總能量: Σγ_n = {gamma_total:.0f}")

# 每個 mode 嘅能量分佈
print(f"\n  Mode 能量分佈:")
print(f"  {'n':<6} {'γ_n':<12} {'累積':<12} {'累積比':<12}")
print(f"  {'-'*42}")
cum = 0
for n in range(1, N_d):
    cum += gamma[n-1]
    ratio = cum / gamma_total
    if n <= 5 or n % 5 == 0 or n == N_d-1:
        print(f"  {n:<6} {gamma[n-1]:<12.6f} {cum:<12.4f} {ratio:<12.6f}")

# K_Chain 模式截止
# 喺 K_Tree level ℓ，有效模式數 = N_d / B^ℓ
# 第 ℓ 層嘅「物質能量」= Σ_{n < N_d/B^ℓ} γ_n
print(f"\n  K_Tree 層次物質能量:")

def sum_gamma_up_to(n_max):
    if n_max < 1:
        return 0.0
    n_max = min(n_max, N_d - 1)
    return sum(gamma[:int(n_max)])

for ell in range(0, 8):
    n_active = N_d / (B ** ell)
    z_level = B ** ell - 1
    if z_level > 17:
        print(f"  ℓ={ell}: z={z_level:.1f}, n_active={n_active:.1f} → z>17 Nyquist cutoff")
        continue
    energy = sum_gamma_up_to(n_active)
    ratio = energy / gamma_total
    print(f"  ℓ={ell}: z={z_level:.1f}, n_active={n_active:.2f}, Σγ={energy:.4f}, ratio={ratio:.6f}")

# ================================================================
# 2. SYNC 張力 = 暗能量
# ================================================================
print(f"\n{'─'*80}")
print(f"  2. SYNC 張力 = 暗能量嘅結構來源")
print(f"{'─'*80}")

# SYNC 相位梯度: Δθ = 2π/88
# 張力所能 = 梯度項 × VE V²
# VEV = φ⁻¹? 定係 other?

# From W-field: V(C) = C²/2 - ln|C+1| + const
# 真空喺 C = φ⁻¹
# 張力 = (dC/dn)² × (coupling)

# 相位梯度: dθ/dn = 2π/88
# 模擬: 每個 site 嘅能量 = ½(dθ/dn)² × φ⁻¹² × N_d
# 呢個係 SYNC 張力能

sync_gradient = 2 * math.pi / (2 * N_d)  # 2π/88
sync_tension = 0.5 * sync_gradient**2 * PHI_INV**2 * N_d
print(f"  SYNC 相位梯度: Δθ = 2π/88 = {sync_gradient:.6f} rad/site")
print(f"  SYNC 張力能: E_sync = {sync_tension:.6f}")

# 同總能量嘅比例
# K_Chain 總能量 = Σγ_n = 86
# 物質能 = 86 (所有 mode)
# 暗能量 = SYNC 張力能
# Omega_L = E_sync / (E_sync + E_matter)

# 但 86 係 mode 能量，SYNC 張力係另一種能量
# 真正嘅比例: Ω_Λ = 4/(φ⁴-1) = 0.683
# 呢個係結構數，唔係由能量直接計算

# 驗證: 如果 Ω_Λ = E_sync / (E_sync + E_matter)
# 咁 E_matter = E_sync × (1/Ω_Λ - 1) = E_sync × 0.464
E_matter_from_sync = sync_tension * (1/Omega_L - 1)
print(f"  從 Ω_Λ 反推物質能: E_matter = {E_matter_from_sync:.6f}")

# ================================================================
# 3. H(z) 推導
# ================================================================
print(f"\n{'─'*80}")
print(f"  3. H(z) 推導")
print(f"{'─'*80}")

# 喺 IDCM，K_Chain 固定唔膨脹
# H(z) 唔係「膨脹率」，而係「紅移隨距離嘅變化率」
# 
# 紅移 = 光喺 SYNC 相位梯度中傳播嘅頻率偏移
# 
# 考慮一個光子從 site n 傳播到 site 0：
# - 光子頻率 ω 隨時間變化：dω/dt = -ω × d(sync_phase)/dt
# - 但 SYNC 相位係靜態（θ_n = n×2π/88 固定）
# - 所以頻率偏移來自 K_Chain 嘅色散

# 方法 A: 從色散關係推導 H(z)
# ω_n = 2|sin(πn/88)| (K_Chain 頻率)
# 光子從 site n 到 site 0，頻率變化：
# ω_obs = ω_em × (ω_0/ω_n) ← 但呢個係 mode 頻率，唔係光子頻率

# 方法 B: 從 K_Tree 層次推導
# 喺 K_Tree level ℓ，z = B^ℓ - 1
# 有效「物質密度」Ω_m(z) = Ω_m × (Σ_{n < N_d/B^ℓ} γ_n) / (Σ_{n < N_d} γ_n)
# H(z) = H₀ × √(Ω_Λ + Ω_m(z))

print(f"\n  方法 B: K_Tree 層次 H(z)\n")
print(f"  H(z) = H0 × sqrt(Omega_L + Omega_m(z))")
print(f"  其中 Omega_m(z) = Omega_m × f(z)，f(z) = sum gamma_n / sum gamma_total")
print(f"  (n < N_d/(1+z) 嘅 mode 能量總和 / 所有 mode 能量總和)\n")

# 計算 f(z) 對唔同 z
def f_z(z):
    """物質密度隨 z 嘅變化: 高 z = 少 mode = 低物質密度"""
    if z < 0:
        return 1.0
    n_active = N_d / (1 + z)
    if n_active <= 1:
        return 0.0
    n_active = min(n_active, N_d - 1)
    return sum_gamma_up_to(n_active) / gamma_total

def H_z_B(z):
    """方法 B: K_Tree 層次 H(z)"""
    f = f_z(z)
    Omega_m_z = Omega_m * f
    return H0 * math.sqrt(max(Omega_L + Omega_m_z, 0))

# 標準 FLRW 做對比
def H_z_FLRW(z):
    return H0 * math.sqrt(Omega_m * (1+z)**3 + Omega_L)

print(f"  {'z':<8} {'H_FLRW':<12} {'H_B':<12} {'ratio':<10} {'f(z)':<10} {'Ω_m(z)':<10}")
print(f"  {'-'*62}")
for z in [0.0, 0.5, 1.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    hf = H_z_FLRW(z)
    hb = H_z_B(z)
    f = f_z(z)
    omz = Omega_m * f
    print(f"  {z:<8.2f} {hf:<12.2f} {hb:<12.2f} {hf/hb if hb>0 else 0:<10.4f} {f:<10.6f} {omz:<10.6f}")

# ================================================================
# 4. 距離-紅移關係
# ================================================================
print(f"\n{'─'*80}")
print(f"  4. 距離-紅移關係 DM(z)")
print(f"{'─'*80}")

def DM(z, H_func, n=1000):
    """Comoving distance"""
    if z <= 0:
        return 0.0
    zv = np.linspace(0, z, n)
    H_vals = np.array([H_func(zi) for zi in zv])
    dz = z / n
    return (c_mpc_gyr / H0) * np.sum(dz / (H_vals / H0))

print(f"\n  DM(z) 對比:")
print(f"  {'z':<8} {'DM_FLRW':<14} {'DM_IDCM_B':<14} {'(DM/rd)_FLRW':<14} {'(DM/rd)_IDCM':<14}")
print(f"  {'-'*70}")
for z in [0.5, 1.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    dm_f = DM(z, H_z_FLRW)
    dm_b = DM(z, H_z_B)
    print(f"  {z:<8.2f} {dm_f:<14.0f} {dm_b:<14.0f} {dm_f/rd:<14.4f} {dm_b/rd:<14.4f}")

# ================================================================
# 5. DESI DR2 測試
# ================================================================
print(f"\n{'─'*80}")
print(f"  5. DESI DR2 Lyα BAO 測試 (z=2.33)")
print(f"{'─'*80}")

z_desi = 2.33
dm_obs = 39.32  # DM/rd observed
dm_err = 0.33

dm_f = DM(z_desi, H_z_FLRW)
dm_b = DM(z_desi, H_z_B)

print(f"\n  觀測: DM/rd = {dm_obs:.4f} ± {dm_err}")
print(f"\n  FLRW (IDCM 參數):")
print(f"    DM/rd = {dm_f/rd:.4f}")
print(f"    差異 = {(dm_f/rd - dm_obs)/dm_err:+.1f}σ")
print(f"\n  方法 B (K_Tree 層次):")
print(f"    DM/rd = {dm_b/rd:.4f}")
print(f"    差異 = {(dm_b/rd - dm_obs)/dm_err:+.1f}σ")

# ================================================================
# 6. 分析
# ================================================================
print(f"\n{'─'*80}")
print(f"  6. 分析")
print(f"{'─'*80}")

print(f"""
方法 B 嘅問題:
  K_Tree 層次嘅物質密度隨 z 下降（高 z = 少 mode = 低物質密度）
  但 FLRW 嘅物質密度隨 z 上升（高 z = 早期 = 高密度）
  方向相反 → DM/rd 差更遠

方法 B 嘅 H(z) 隨 z 遞減（因為 Ω_m(z) 遞減），
FLRW 嘅 H(z) 隨 z 遞增（因為 (1+z)³ 項）。
呢個係根本嘅分別。

需要新嘅 insight：
  物質密度點解隨 z 上升？
  如果 K_Chain 固定，咩機制令高 z 睇到更高密度？
""")

# ================================================================
# 7. 嘗試方法 C: 紅移 = SYNC 相位累積
# ================================================================
print(f"{'─'*80}")
print(f"  7. 方法 C: 紅移 = SYNC 相位累積")
print(f"{'─'*80}")

# 新 insight: 紅移 = 光喺 SYNC 相位梯度中傳播嘅相位累積
# 相位差 Δθ = 2π/88 per site
# 經過 n 個 site，總相位累積 Φ = n × 2π/88
# 紅移: 1+z = exp(Φ) = exp(n × 2π/88)

# 距離: D = n × Δx = n × R_H/44
# 所以: D = (R_H/44) × (88/2π) × ln(1+z) = (R_H/π) × ln(1+z)

# 呢個形式: DM ∝ ln(1+z)，同 ΛCDM 嘅 DM ∝ z (低 z) 好唔同

print(f"\n  紅移 = SYNC 相位累積:")
print(f"  1+z = exp(n × 2π/88)")
print(f"  其中 n = 經過嘅 K_Chain site 數\n")

print(f"  DM(z) = (R_H/π) × ln(1+z)\n")

def DM_C(z):
    """方法 C: 紅移 = SYNC 相位累積"""
    return (R_H / math.pi) * math.log(1 + z)

print(f"  {'z':<8} {'DM_C':<14} {'(DM/rd)_C':<14} {'(DM/rd)_FLRW':<14}")
print(f"  {'-'*50}")
for z in [0.5, 1.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    dm_c = DM_C(z)
    dm_f = DM(z, H_z_FLRW)
    print(f"  {z:<8.2f} {dm_c:<14.0f} {dm_c/rd:<14.4f} {dm_f/rd:<14.4f}")

print(f"\n  DESI DR2 z=2.33:")
print(f"    DM/rd_C = {DM_C(z_desi)/rd:.4f} vs DESI {dm_obs:.4f} ± {dm_err}")
print(f"    差異 = {(DM_C(z_desi)/rd - dm_obs)/dm_err:+.1f}σ")

# ================================================================
# 8. 方法 D: 指數拉伸
# ================================================================
print(f"\n{'─'*80}")
print(f"  8. 方法 D: 紅移 = 波長指數拉伸")
print(f"{'─'*80}")

# 如果紅移係波長喺 K_Chain 上嘅指數拉伸：
# 1+z = exp(α × D)
# 其中 α = SYNC 拉伸率
# DM(z) = (1/α) × ln(1+z)

# 但同方法 C 其實一樣，只係常數唔同

# 咁如果紅移係幂律拉伸？
# 1+z = (1 + D/R_H)^β
# DM(z) = R_H × ((1+z)^(1/β) - 1)

# 試 β = 3 (ΛCDM-like)
def DM_D(z, beta):
    return R_H * ((1+z)**(1/beta) - 1)

print(f"\n  DM(z) = R_H × ((1+z)^(1/β) - 1)\n")
print(f"  {'z':<8} {'β=1':<14} {'β=2':<14} {'β=3':<14} {'FLRW':<14}")
print(f"  {'-'*68}")
for z in [0.5, 1.0, 2.33, 3.0, 5.0]:
    dm_f = DM(z, H_z_FLRW)
    print(f"  {z:<8.2f} {DM_D(z,1)/rd:<14.4f} {DM_D(z,2)/rd:<14.4f} {DM_D(z,3)/rd:<14.4f} {dm_f/rd:<14.4f}")

print(f"\n  DESI DR2 z=2.33:")
for beta in [1, 2, 3, 4]:
    dm_d = DM_D(z_desi, beta)
    sigma = (dm_d/rd - dm_obs)/dm_err
    print(f"    β={beta}: DM/rd = {dm_d/rd:.4f}, 差異 = {sigma:+.1f}σ")

# ================================================================
# 9. 總結
# ================================================================
print(f"\n{'─'*80}")
print(f"  9. 總結")
print(f"{'─'*80}")

print(f"""
IDCM H(z) 推導 — 嘗試 4 個方法:

方法 A: 色散關係 → 未完成，需要更多 insight
方法 B: K_Tree 層次 → H(z) 隨 z 遞減 ❌ (同觀測相反)
方法 C: SYNC 相位累積 → DM ∝ ln(1+z) ❌ (太慢)
方法 D: 指數拉伸 → DM = R_H((1+z)^(1/β)-1) 
   β=3: DM/rd = {DM_D(z_desi,3)/rd:.4f} vs DESI {dm_obs:.4f}

目前最佳:
  FLRW + IDCM 參數: DM/rd = {dm_f/rd:.4f} vs DESI {dm_obs:.4f} (差 {(dm_f/rd-dm_obs)/dm_err:.1f}σ)
  方法 D β=3: DM/rd = {DM_D(z_desi,3)/rd:.4f} vs DESI {dm_obs:.4f} (差 {(DM_D(z_desi,3)/rd-dm_obs)/dm_err:.1f}σ)

結論: 所有簡單方法都唔 work。
需要更深入嘅 insight 先可以推導出正確嘅 H(z)。
""")