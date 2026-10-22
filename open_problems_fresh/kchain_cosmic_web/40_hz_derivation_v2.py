#!/usr/bin/env python3
"""
IDCM H(z) 推導 v2 — 基於 Gemini 嘅 insight
============================================
紅移 = 相位延遲與導波色散，唔係空間膨脹。

核心 insight:
1. 紅移唔係速度，唔係空間膨脹
2. 紅移唔係宇宙年齡嘅刻度（z<1.2 無演化證實）
3. 紅移 = 離散晶格傳播嘅結構性相位累積
4. 紅移 = 因果距離嘅刻度尺 = mapping depth
5. 紅移 = 操作步數（operational steps）

推導方向:
- 從 K_Chain 色散關係推導相位累積
- 紅移 = 光子跨越操作步數嘅相位差
- 距離 = 操作步數 × 投影尺度
"""
import math, sys
import numpy as np

print("=" * 80)
print("  IDCM H(z) 推導 v2 — 紅移 = 相位延遲")
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

c_mpc_gyr = 306.6  # Mpc/Gyr
R_H = 4129.94  # Mpc
H0 = c_mpc_gyr / R_H  # 0.0742 Gyr⁻¹

Omega_L = 4 / (PHI**4 - 1)  # 0.683
Omega_m = 1 - Omega_L  # 0.317

t_site = R_H / (N_d * c_mpc_gyr)  # 0.306 Gyr
tau_depth = N_d * t_site  # 13.47 Gyr
T_SYNC = 2 * N_d * t_site  # 26.94 Gyr

# BAO scale
lambda_sync = 2 * math.pi * R_H / 88
rd = lambda_sync / 2  # 147.44 Mpc

# DESI DR2
z_desi = 2.33
dm_rd_obs = 39.32
dm_rd_err = 0.33

print(f"\n基本參數:")
print(f"  Ω_Λ = {Omega_L:.6f}")
print(f"  Ω_m = {Omega_m:.6f}")
print(f"  R_H = {R_H:.2f} Mpc")
print(f"  BAO rd = {rd:.4f} Mpc")
print(f"  t_site = {t_site:.4f} Gyr")
print(f"  τ_depth = {tau_depth:.4f} Gyr")

# ================================================================
# 1. K_Chain 色散與相位
# ================================================================
print(f"\n{'─'*80}")
print(f"  1. K_Chain 色散關係與相位累積")
print(f"{'─'*80}")

# K_Chain 本徵值
# γ_n = 4 sin²(πn/88)
# 群速度: v_g(n) = cos(πn/88)
# 相位速度: v_p(n) = ω_n/k_n = 2|sin(πn/88)| / (2πn/88) = (88/π) × |sin(πn/88)|/n

# 光子從 site n 傳播到 site 0，經歷嘅相位累積:
# ΔΦ = Σ_{i=1}^{n} Δθ_i = n × 2π/88

# 但紅移唔係簡單嘅相位累積— 佢係色散關係嘅投影效應
# 關鍵: 群速度 v_g(n) 決定咗訊號傳播速度，而唔同 n 嘅 mode 有唔同 v_g
# 高 n (短波長) 傳播得慢，低 n (長波長) 傳播得快
# 呢個色散令到「紅移」隨距離非線性變化

print(f"  K_Chain 色散:")
print(f"  γ_n = 4 sin²(πn/88), n=1..43")
print(f"  v_g(n) = cos(πn/88)")
print(f"  v_p(n) = (88/π) × sin(πn/88)/n\n")

print(f"  {'n':<6} {'γ_n':<12} {'v_g':<12} {'v_p':<12} {'λ_n/R_H':<12}")
print(f"  {'-'*54}")
for n in [1, 2, 5, 11, 22, 33, 43]:
    gamma = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    vp = (88/math.pi) * math.sin(math.pi * n/88) / n if n > 0 else 0
    wl = 1/n
    print(f"  {n:<6} {gamma:<12.6f} {vg:<12.6f} {vp:<12.6f} {wl:<12.6f}")

# ================================================================
# 2. 紅移 = 因果阻尼（Causal Attenuation）
# ================================================================
print(f"\n{'─'*80}")
print(f"  2. 紅移 = 因果阻尼 (Causal Attenuation)")
print(f"{'─'*80}")

# Insight: 紅移係訊號喺離散晶格傳播時嘅阻尼
# 每個 site 嘅 SYNC 相位旋轉: 2π/88
# 經過 n 個 site，總相位旋轉: n × 2π/88
# 呢個相位旋轉表現為「紅移」: 1+z = exp(n × 2π/88 × γ_eff)
# 其中 γ_eff 係有效阻尼系數

# 但之前方法 C 用 DM = (R_H/π) × ln(1+z) 唔 work
# 問題: 距離唔係線性 n × Δx
# 因為 3D 投影嘅尺度同 K_Chain 嘅 1D 尺度唔同

# 新 insight: 投影尺度
# K_Chain 嘅 1D site 投影到 3D 空間
# 每個 site 對應嘅 3D 體積: V_3D = (R_H/44)³ × (4π/3) × (CY₃ factor)
# 距離唔係線性加和，而係體積嘅立方根

# 但更直接: 紅移 = mapping depth (操作步數)
# z = B^ℓ - 1 其中 ℓ = K_Tree level
# 距離 = 累積嘅投影尺度

# Method E: 紅移 = 操作步數，距離 = 投影尺度積分
print(f"\n  方法 E: 紅移 = 操作步數 (Mapping Depth)")
print(f"  z = B^ℓ - 1, ℓ = log_B(1+z)")
print(f"  距離積分: D(z) = ∫₀ᶻ R_H/(1+z') dz' = R_H × ln(1+z)\n")

# 等等，呢個又係 ln(1+z) — 同方法 C 一樣
# 但如果投影尺度係 R_H/(1+z)^2 呢？
# D(z) = ∫₀ᶻ R_H/(1+z')² dz' = R_H × z/(1+z)

# 試唔同嘅投影尺度
print(f"  試唔同投影尺度:")
print(f"  {'z':<8} {'D_1/(1+z)':<14} {'D_1/(1+z)²':<14} {'D_1/(1+z)^k':<14} {'FLRW':<14}")
print(f"  {'-'*70}")

def D_power(z, k):
    """D(z) = R_H × ∫₀ᶻ 1/(1+z')^k dz'"""
    if k == 1:
        return R_H * math.log(1+z)
    else:
        return R_H * ((1+z)**(1-k) - 1) / (1-k)

for z in [0.5, 1.0, 2.33, 3.0, 5.0]:
    print(f"  {z:<8.2f} {D_power(z,1)/rd:<14.4f} {D_power(z,2)/rd:<14.4f} {'':>14} {'':>14}")

# ================================================================
# 3. 關鍵 insight: 紅移 = 空間投影嘅頻率映射
# ================================================================
print(f"\n{'─'*80}")
print(f"  3. 頻率映射: 紅移 = 光子頻率喺投影空間嘅衰減")
print(f"{'─'*80}")

# 光子頻率 ω 喺 K_Chain 上傳播時，受色散關係影響:
# dω/dn = -ω × α(n) 其中 α(n) 係阻尼系數
# α(n) = 1 - v_g(n) = 1 - cos(πn/88)

# 對於細 n（長波長），α(n) ≈ 0，幾乎無衰減
# 對於大 n（短波長），α(n) ≈ 1，強衰減

# 紅移係頻率衰減嘅累積: 1+z = ω_em/ω_obs
# ω_obs = ω_em × exp(-∫ α(n) dn)

# 但呢個需要知道 n 同距離嘅關係，又係循環論證

# ================================================================
# 4. 方法 F: 從 K_Tree 投影尺度推導
# ================================================================
print(f"\n{'─'*80}")
print(f"  4. 方法 F: K_Tree 投影卷積")
print(f"{'─'*80}")

# K_Tree 第 ℓ 層有 4^ℓ 個節點，每個節點代表 R_H/4^ℓ 嘅尺度
# 紅移 z = 4^ℓ - 1
# 累積嘅「投影距離」係各層尺度嘅加權和

# 但 3D 投影體積 = 4^ℓ × (R_H/4^ℓ)³ = R_H³/4^(2ℓ)
# 距離 ∝ 體積^(1/3) = R_H/4^(2ℓ/3) = R_H/(1+z)^(2/3)

# 累積距離: D(z) = Σ_{i=0}^{ℓ} R_H/4^(2i/3)
# 連續極限: D(z) = ∫₀ᶻ R_H/(1+z')^(2/3) × dz'/ln(4) × (1/(1+z'))

# 簡化: D(z) = R_H × ∫₀ᶻ (1+z')^(-5/3) dz' / ln(4)
# = R_H/ln(4) × [(-3/2)(1+z')^(-2/3)]₀ᶻ
# = R_H/ln(4) × (3/2) × (1 - (1+z)^(-2/3))

# 更簡單: D(z) = R_H/ln(4) × (3/2) × (1 - (1+z)^(-2/3))

def D_F(z):
    k = 2/3
    factor = 1/math.log(4) * 3/2
    return R_H * factor * (1 - (1+z)**(-k))

print(f"  D(z) = R_H/ln(4) × (3/2) × (1 - (1+z)^(-2/3))\n")
print(f"  {'z':<8} {'DM/rd':<14} {'DESI':<14} {'sigma':<10}")
print(f"  {'-'*46}")
for z in [0.5, 1.0, 2.33, 3.0, 5.0]:
    dm = D_F(z)/rd
    sigma = (dm - dm_rd_obs)/dm_rd_err if z == z_desi else 0
    print(f"  {z:<8.2f} {dm:<14.4f} {'':>14} {sigma:<+10.1f}")

print(f"\n  DESI z=2.33:")
dm_f = D_F(z_desi)/rd
sigma = (dm_f - dm_rd_obs)/dm_rd_err
print(f"    DM/rd = {dm_f:.4f} vs DESI {dm_rd_obs:.4f} ± {dm_rd_err}")
print(f"    差異 = {sigma:+.1f}σ")

# ================================================================
# 5. 方法 G: 最佳擬合投影指數
# ================================================================
print(f"\n{'─'*80}")
print(f"  5. 方法 G: 搵最佳投影指數")
print(f"{'─'*80}")

# 一般形式: D(z) = R_H × (1 - (1+z)^(-β))
# 搵 β 令 D(2.33)/rd = 39.32

target = dm_rd_obs * rd / R_H  # 目標 D/R_H
print(f"  目標 D/R_H at z=2.33 = {target:.6f}")

# 解 1 - (1+z)^(-β) = target
# (1+z)^(-β) = 1 - target
# -β × ln(1+z) = ln(1-target)
# β = -ln(1-target)/ln(1+z)

beta_opt = -math.log(1 - target) / math.log(1 + z_desi)
print(f"  最佳 β = {beta_opt:.4f}\n")

def D_G(z, beta):
    return R_H * (1 - (1+z)**(-beta))

print(f"  D(z) = R_H × (1 - (1+z)^(-β)), β={beta_opt:.4f}\n")
print(f"  {'z':<8} {'DM/rd':<14} {'DESI':<14} {'sigma':<10}")
print(f"  {'-'*46}")
for z in [0.5, 1.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    dm = D_G(z, beta_opt)/rd
    if z == z_desi:
        sigma = (dm - dm_rd_obs)/dm_rd_err
        print(f"  {z:<8.2f} {dm:<14.4f} {dm_rd_obs:<14.4f} {sigma:<+10.1f}")
    else:
        print(f"  {z:<8.2f} {dm:<14.4f} {'':>14}")

# 呢個 β 代表咩物理意義？
# D(z) = R_H × (1 - (1+z)^(-β))
# H(z) = c / (dD/dz) = c / (R_H × β × (1+z)^(-β-1))
# H(z) = H₀/β × (1+z)^(β+1)

# 如果 β = beta_opt:
H_z_coeff = H0 / beta_opt
print(f"\n  H(z) = H0/β × (1+z)^(β+1)")
print(f"  H(z) = {H0:.4f}/{beta_opt:.4f} × (1+z)^({beta_opt+1:.4f})")
print(f"  H(z) = {H_z_coeff:.4f} × (1+z)^{beta_opt+1:.4f}")

# ================================================================
# 6. 同 ΛCDM 對比
# ================================================================
print(f"\n{'─'*80}")
print(f"  6. 同 ΛCDM 對比")
print(f"{'─'*80}")

# ΛCDM: H(z) = H₀ × √(Ω_m(1+z)³ + Ω_Λ)
# IDCM: H(z) = H₀/β × (1+z)^(β+1)

# 喺低 z，ΛCDM 嘅 H(z) ≈ H₀ × (1 + 1.5Ω_m × z)
# IDCM 嘅 H(z) ≈ H₀/β × (1 + (β+1)z)

# 兩者喺低 z 嘅行為可以比較

print(f"  ΛCDM: H(z) = H₀ × √(Ω_m(1+z)³ + Ω_Λ)")
print(f"  IDCM: H(z) = H₀/β × (1+z)^(β+1), β={beta_opt:.4f}\n")

print(f"  低 z 展開:")
print(f"  ΛCDM: H(z) = H₀ × (1 + {1.5*Omega_m:.4f}z + ...)")
print(f"  IDCM: H(z) = {H0/beta_opt:.4f} × (1 + {beta_opt+1:.4f}z + ...)\n")

# 低 z 嘅 H₀ 值
print(f"  H₀ 值:")
print(f"  ΛCDM: H₀ = {H0:.4f} Gyr⁻¹ = {H0*306.6:.4f} km/s/Mpc")
print(f"  IDCM: H₀_eff = {H0/beta_opt:.4f} Gyr⁻¹ = {H0/beta_opt*306.6:.4f} km/s/Mpc")

# ================================================================
# 7. H(z) 完整對比
# ================================================================
print(f"\n{'─'*80}")
print(f"  7. H(z) 完整對比")
print(f"{'─'*80}")

def H_LCDM(z):
    return H0 * math.sqrt(Omega_m * (1+z)**3 + Omega_L)

def H_IDCM(z):
    return H0 / beta_opt * (1+z)**(beta_opt + 1)

print(f"  {'z':<8} {'H_LCDM':<14} {'H_IDCM':<14} {'ratio':<10}")
print(f"  {'-'*46}")
for z in [0.0, 0.5, 1.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    hl = H_LCDM(z)
    hi = H_IDCM(z)
    print(f"  {z:<8.2f} {hl:<14.4f} {hi:<14.4f} {hl/hi:<10.4f}")

# ================================================================
# 8. 總結
# ================================================================
print(f"\n{'─'*80}")
print(f"  8. 總結")
print(f"{'─'*80}")

print(f"""
方法 G 成功 match DESI DR2!
  D(z) = R_H × (1 - (1+z)^(-β))
  β = {beta_opt:.4f}
  DM/rd(z=2.33) = {D_G(z_desi, beta_opt)/rd:.4f} ✅ (vs DESI {dm_rd_obs:.4f})

但呢個純粹係擬合，唔係結構推導。
β = {beta_opt:.4f} 嘅物理意義未明。
需要從 K_Chain/SYNC 結構推導出 β 嘅來源。

推測: β 可能同 K_Chain 嘅色散指數有關
  v_g(n) ≈ 1 - (πn/88)²/2 for n << 88
  β = 1 + 2/3? 1 + 1/2? ...

目前最佳: D(z) = R_H × (1 - (1+z)^(-β))
  H(z) = H₀/β × (1+z)^(β+1)
  呢個形式同 ΛCDM 嘅 FLRW 完全唔同
  但 DESI 數據只 fit 一個點，需要更多數據驗證
""")