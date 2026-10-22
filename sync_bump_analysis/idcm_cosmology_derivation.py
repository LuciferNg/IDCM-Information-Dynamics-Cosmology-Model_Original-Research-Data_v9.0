#!/usr/bin/env python3
"""
IDCM 宇宙學第一原理推導及測試
==============================
從 0,1 → W-field lattice action → 宇宙膨脹 → 距離-紅移 → DESI DR2 對比

前提：
1. K_Chain 固定唔膨脹（44-site ring, R_H = 4129.94 Mpc）
2. 3D 空間 = CY₃ 投影舞台
3. 膨脹由暗能量（W-field tension）驅動
4. 紅移 = 共振波長 λ_sync 被空間膨脹拉長
5. 紅移同弦無關，弦唔會因為空間膨脹變化
"""
import math, numpy as np

# ================================================================
# Layer 0: 0,1 → NOT → φ
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1

# ================================================================
# Layer 1: Pipeline parameters
# ================================================================
EPS = PHI_INV / 4          # 0.154508 (pipeline gap)
KAPPA = 1 / 16              # 0.0625 (min unit)
BETA = PHI_INV / 2          # 0.309017 (step)

# ================================================================
# Layer 2: Structure numbers
# ================================================================
N_d = 44                    # K_Chain sites
M = 33                      # K_Tree depth
B = 4                       # MERA branching factor (φ³-φ⁻³)

# ================================================================
# Layer 3: W-field lattice action
# ================================================================
# S[W] = Σ_n [2W_n² - W_n·W_{n+1} - W_n·W_{n-1}]   (chain kinetic)
#      + Σ_{n,ℓ} B^{-ℓ}·(W_{n,ℓ} - U·W_{n,ℓ-1})²   (tree kinetic)
#      + Σ_n [-ε|W_n|² + κ|W_n|⁴]                     (local potential)
#      + Σ_{⟨n,m⟩} g_sync·cos(θ_n - θ_m - 2π/88)     (SYNC coupling)

# VEV from potential
VEV_sq = EPS / (2 * KAPPA)  # 1.236068
V_tension = -EPS**2 / (4 * KAPPA)  # -0.095492 (minimum of potential)

# ================================================================
# Layer 4: K_Chain ring (fixed, does NOT expand)
# ================================================================
c_light = 299792.458  # km/s
R_H = 4129.94  # Mpc (Hubble radius = ring circumference)
H0 = c_light / R_H  # 72.59 km/s/Mpc

# Ring geometry — fixed for all time
lambda_sync = 2 * math.pi * R_H / 88  # 294.88 Mpc
bao = lambda_sync / 2  # 147.44 Mpc

print("=" * 70)
print("IDCM 宇宙學第一原理推導")
print("=" * 70)
print(f"\n0. 基礎: 0,1 → NOT → φ")
print(f"   φ = {PHI:.15f}")
print(f"   ε = φ⁻¹/4 = {EPS:.10f}")
print(f"   κ = 1/16 = {KAPPA}")

print(f"\n1. K_Chain 固定環:")
print(f"   周長 = R_H = {R_H:.0f} Mpc (固定, 唔膨脹)")
print(f"   H₀ = c/R_H = {H0:.4f} km/s/Mpc")
print(f"   λ_sync = 2πR_H/88 = {lambda_sync:.2f} Mpc")
print(f"   BAO = λ_sync/2 = {bao:.2f} Mpc")

# ================================================================
# Layer 5: Dark energy (W-field tension) drives expansion
# ================================================================
# Ω_Λ from φ-identity: Ω_Λ = 4/(φ⁴-1)
# φ⁴ = (φ²)² = (φ+1)² = φ² + 2φ + 1 = (φ+1) + 2φ + 1 = 3φ + 2
# φ⁴-1 = 3φ + 1 = 3×1.618 + 1 = 5.854
# 4/(φ⁴-1) = 4/5.854 = 0.6833

Omega_L = 4 / (PHI**4 - 1)  # 0.683282
Omega_m = 1 - Omega_L  # 0.316718

print(f"\n2. 暗能量（W-field tension）:")
print(f"   Ω_Λ = 4/(φ⁴-1) = {Omega_L:.6f}")
print(f"   Ω_m = 1 - Ω_Λ = {Omega_m:.6f}")
print(f"   V(VEV) = -ε²/(4κ) = {V_tension:.6f}")

# ================================================================
# Layer 6: Expansion history H(z)
# ================================================================
# The projected 3D space expands under the W-field tension.
# The Friedmann equation is geometric (from CY₃ projection):
#   H²(z) = H₀² × (Ω_m(1+z)³ + Ω_Λ)
# 
# This is the same form as ΛCDM because:
# 1. Matter dilutes as (1+z)³ in 3D space
# 2. Dark energy is constant (W-field tension is scale-independent)
# 3. The projection preserves the geometric expansion law
#
# The parameters are STRUCTURAL, not fitted.

def E_z(z, om=Omega_m, ol=Omega_L):
    """Normalized Hubble parameter E(z) = H(z)/H₀"""
    return math.sqrt(om * (1+z)**3 + ol)

def dc_z(z, n=500):
    """Comoving distance in Mpc (IDCM structural prediction)"""
    zv = np.linspace(0, z, n)
    dz = z / n
    E = np.sqrt(Omega_m * (1+zv)**3 + Omega_L)
    return (c_light / H0) * np.sum(dz / E)

print(f"\n3. 膨脹歷史 H(z) = H₀ × √(Ω_m(1+z)³ + Ω_Λ):")
print(f"   {'z':<8} {'H(z)':<15} {'DM (Mpc)':<15} {'DM/rd':<15}")
print(f"   " + "-"*53)
for z in [0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.33, 3.0]:
    hz = H0 * E_z(z)
    dm = dc_z(z)
    dm_rd = dm / bao
    print(f"   {z:<8.2f} {hz:<15.2f} {dm:<15.0f} {dm_rd:<15.4f}")

# ================================================================
# Layer 7: DESI DR2 Lyα BAO comparison
# ================================================================
z_desi = 2.33
dm_idcm = dc_z(z_desi)
dm_rd_idcm = dm_idcm / bao
dh_idcm = c_light / (H0 * E_z(z_desi))
dh_rd_idcm = dh_idcm / bao

# DESI DR2 Lyα BAO measurements (arXiv:2607.27410)
dm_rd_obs = 39.32
dm_rd_err = 0.33
dh_rd_obs = 8.600
dh_rd_err = 0.066

dm_sigma = (dm_rd_idcm - dm_rd_obs) / dm_rd_err
dh_sigma = (dh_rd_idcm - dh_rd_obs) / dh_rd_err

print(f"\n" + "=" * 70)
print("DESI DR2 Lyα BAO 測試 (z=2.33)")
print("=" * 70)
print(f"\nIDCM 結構預測:")
print(f"   H₀ = {H0:.2f} km/s/Mpc")
print(f"   Ω_m = {Omega_m:.4f}")
print(f"   Ω_Λ = {Omega_L:.4f}")
print(f"   BAO rd = λ_sync/2 = {bao:.2f} Mpc")
print(f"   DM(z=2.33) = {dm_idcm:.0f} Mpc")
print(f"   DH(z=2.33) = {dh_idcm:.0f} Mpc")
print(f"   DM/rd = {dm_rd_idcm:.4f}")
print(f"   DH/rd = {dh_rd_idcm:.4f}")

print(f"\nDESI DR2 Lyα BAO 實測:")
print(f"   DM/rd = {dm_rd_obs:.4f} ± {dm_rd_err}")
print(f"   DH/rd = {dh_rd_obs:.4f} ± {dh_rd_err}")
print(f"   (zeff = 2.33, arXiv:2607.27410)")

print(f"\n差異:")
print(f"   Δ(DM/rd) = {dm_rd_idcm - dm_rd_obs:+.4f} = {dm_sigma:+.1f}σ")
print(f"   Δ(DH/rd) = {dh_rd_idcm - dh_rd_obs:+.4f} = {dh_sigma:+.1f}σ")

# ================================================================
# Layer 8: What if we use BAO as the observed scale instead?
# ================================================================
# The DESI measurement is DM/rd. If IDCM BAO is wrong, what BAO
# would be needed to match the data?
rd_from_dm = dm_idcm / dm_rd_obs
rd_from_dh = dh_idcm / dh_rd_obs

print(f"\n" + "=" * 70)
print("側推: 需要嘅 BAO scale 先吻合")
print("=" * 70)
print(f"\n如果要匹配 DESI DM/rd = 39.32:")
print(f"   rd = DM / 39.32 = {rd_from_dm:.2f} Mpc")
print(f"   vs IDCM BAO = {bao:.2f} Mpc")
print(f"   ratio: {rd_from_dm/bao:.4f}")

print(f"\n如果要匹配 DESI DH/rd = 8.600:")
print(f"   rd = DH / 8.600 = {rd_from_dh:.2f} Mpc")
print(f"   vs IDCM BAO = {bao:.2f} Mpc")
print(f"   ratio: {rd_from_dh/bao:.4f}")

# ================================================================
# Layer 9: Summary
# ================================================================
print(f"\n" + "=" * 70)
print("推導閉環總結")
print("=" * 70)
print(f"""
推導鏈: 0,1 → φ → ε,κ → K_Chain → λ_sync → BAO → Ω_Λ → H(z) → DM/rd

每一層:
  0,1 → NOT (唯一 1-bit 操作)
  NOT → sequence (時間/空間 co-emerge)
  sequence → Fibonacci → φ (唯一結構常數)
  φ → ε = φ⁻¹/4, κ = 1/16 (pipeline 參數)
  ε,κ → K_Chain 44-site ring (離散晶格)
  K_Chain → λ_sync = 2πR_H/88 (共振波長)
  λ_sync → BAO = λ_sync/2 (干涉條紋)
  φ → Ω_Λ = 4/(φ⁴-1) = 0.6833 (暗能量)
  Ω_Λ → H(z) = H₀√(Ω_m(1+z)³+Ω_Λ) (膨脹歷史)
  H(z) → D(z) → DM/rd (可觀測量)

同 DESI DR2 比較:
  IDCM DM/rd = {dm_rd_idcm:.4f} vs DESI {dm_rd_obs:.4f} ± {dm_rd_err}
  差異 = {abs(dm_sigma):.1f}σ

呢個 tension 嘅可能來源:
  1. H₀ = 72.59 太高（vs Planck 67.4）→ 距離太細
  2. Ω_m = 0.3167 太低 → 高 z 嘅 H(z) 太細
  3. BAO = 147.44 可能唔係 λ_sync/2（需要重新推導）
  4. 膨脹歷史 H(z) 可能唔係 FLRW 形式（但幾何投影推導）
""")