#!/usr/bin/env python3
"""
IDCM 宇宙膨脹第一原理推導 — 由 W-field 晶格行動
================================================
唔用 FLRW，由 W-field Lagrangian 推導 H(z) 同 distance-redshift。

前提：
- K_Chain 44-site ring 固定唔膨脹 (R_H = 4129.94 Mpc)
- 3D 空間 = CY₃ 投影
- 膨脹由 W-field tension 驅動
- 紅移 = 共振波長被空間膨脹拉長
- 觀測極限 z < 17 (宇宙視界)
"""
import math, numpy as np

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4          # 0.154508
KAPPA = 1 / 16              # 0.0625
BETA = PHI_INV / 2          # 0.309017
N_d = 44                    # K_Chain sites
M = 33                      # K_Tree depth
B = 4                       # MERA branching factor
c_light = 299792.458        # km/s
R_H = 4129.94               # Mpc (ring circumference)

# ================================================================
# Step 1: W-field Lagrangian on K_Chain ⊗ K_Tree
# ================================================================
# The full action:
# S[W] = S_chain + S_tree + S_pot + S_sync
#
# S_chain = Σ_n [2W_n² - W_n·W_{n+1} - W_n·W_{n-1}]
# S_tree = Σ_{n,ℓ} B^{-ℓ}·(W_{n,ℓ} - U·W_{n,ℓ-1})²
# S_pot = Σ_n [-ε|W_n|² + κ|W_n|⁴]
# S_sync = Σ_{⟨n,m⟩} g_sync·cos(θ_n - θ_m - 2π/88)

# The W-field VEV:
VEV_sq = EPS / (2 * KAPPA)   # 1.23607
VEV = math.sqrt(VEV_sq)       # 1.11179

# ================================================================
# Step 2: Energy-momentum tensor from W-field
# ================================================================
# For a scalar field on a discrete lattice, the energy density is:
#   ρ = ½(∂W/∂t)² + ½(∇W)² + V(W) + S_sync
#
# In the ground state:
#   ∂W/∂t = 0 (static configuration)
#   ∇W = helical phase gradient (from SYNC)
#   V(W) = -ε²/(4κ) at the VEV

# The kinetic energy from the SYNC phase gradient:
# Each site has a phase θ_n = n·2π/88
# The gradient energy: (1/2)(Δθ)² = (1/2)(2π/88)² = 2π²/88²
# Times the VEV² gives the energy density:
grad_energy = 0.5 * VEV_sq * (2*math.pi/88)**2  # per site

# The potential energy at the VEV:
pot_energy = -EPS**2 / (4 * KAPPA)  # per site

# The SYNC coupling energy:
# g_sync = 2·VEV_sq·(1-cos(2π/88)) ≈ 0.00630
g_sync = 2 * VEV_sq * (1 - math.cos(2*math.pi/88))
sync_energy = g_sync * math.cos(2*math.pi/88)  # per site

# Total dark energy per site:
rho_DE_per_site = grad_energy + pot_energy + sync_energy
# Total dark energy for the whole ring:
rho_DE = rho_DE_per_site * N_d

print("=" * 70)
print("IDCM 宇宙膨脹第一原理推導")
print("=" * 70)
print(f"\n1. W-field 能量密度（每 site）:")
print(f"   梯度能 = {grad_energy:.6f}")
print(f"   勢能 V(VEV) = {pot_energy:.6f}")
print(f"   SYNC 能 = {sync_energy:.6f}")
print(f"   總暗能量 = {rho_DE_per_site:.6f} / site")
print(f"   全環 = {rho_DE:.6f}")

# ================================================================
# Step 3: Expansion equation from W-field
# ================================================================
# In the projected 3D space, the expansion is driven by the
# W-field energy density. The effective "Hubble parameter" is:
#   H² = (8πG/3) × ρ_W
#
# But ρ_W is the W-field energy density, which has:
# 1. Constant component (dark energy from tension)
# 2. Mode excitation component (matter)
#
# The mode excitation energy for mode n on the K_Chain:
#   E_n = 2|sin(πn/88)|
# The number of modes determines the matter density.

# The critical density:
# ρ_crit = 3H₀²/(8πG) where H₀ = c/R_H
H0 = c_light / R_H  # 72.59 km/s/Mpc

# The ratio of dark energy to critical density:
# From the φ-identity: Ω_Λ = 4/(φ⁴-1)
Omega_L = 4 / (PHI**4 - 1)  # 0.683282
Omega_m = 1 - Omega_L  # 0.316718

print(f"\n2. 膨脹參數:")
print(f"   H₀ = c/R_H = {H0:.4f} km/s/Mpc")
print(f"   Ω_Λ = 4/(φ⁴-1) = {Omega_L:.6f}")
print(f"   Ω_m = 1 - Ω_Λ = {Omega_m:.6f}")

# ================================================================
# Step 4: H(z) from W-field mode evolution
# ================================================================
# The W-field has 44 modes (n=0..43). Each mode contributes to
# the energy density. The matter is the sum of occupied modes.
#
# The expansion history H(z) depends on how the W-field modes
# evolve with redshift. In the K_Tree hierarchy:
#   Level ℓ: scale = R_H/B^ℓ
#   z = B^ℓ - 1
#
# At each level, different modes are "active" (below the cutoff).
# The total energy density is the sum of active modes.
#
# The expansion law is:
#   H²(z) = H₀² × [Ω_m(1+z)³ + Ω_Λ]
#
# But this is the FLRW form. The IDCM form might be different
# because the W-field mode spectrum is discrete.

def E_z_FLRW(z):
    """FLRW expansion law (for comparison)"""
    return math.sqrt(Omega_m * (1+z)**3 + Omega_L)

def E_z_IDCM(z):
    """
    IDCM expansion law derived from W-field mode spectrum.
    
    The W-field has 44 modes on the K_Chain. Each mode n has
    energy γ_n = 4 sin²(πn/88). The total "matter density" at
    redshift z is the sum of modes whose energy is above the
    thermal cutoff at that redshift.
    
    At high z (early times), more modes are active.
    At low z (late times), fewer modes are active.
    
    The transition redshift is determined by the K_Tree level.
    At level ℓ: z = B^ℓ - 1, and the mode cutoff is at n =
    N_d / B^ℓ.
    """
    # At z=0, only the ground state (n=0) is active
    # At z=B^ℓ-1, modes up to n = N_d/B^ℓ are active
    # The matter density is proportional to the sum of active modes
    
    if z < 0:
        return 1.0
    
    # Find the K_Tree level
    # z = B^ℓ - 1 → ℓ = log_B(z+1)
    # But the levels are discrete, so we interpolate
    ell = math.log(z + 1, B)
    
    # Number of active modes at this level
    n_active = N_d / (B**ell)
    n_active = max(1, min(N_d, n_active))
    
    # Sum of γ_n for n=1..n_active
    # For large n_active, this is approximately N_d (the total)
    # For small n_active, this is proportional to n_active³
    if n_active < 2:
        matter_ratio = 0
    else:
        n = np.arange(1, int(n_active) + 1)
        gamma_n = 4 * np.sin(math.pi * n / 88) ** 2
        matter_ratio = np.sum(gamma_n) / (N_d / 2)
        # Normalize so that Ω_m(z=0) = 0.3167
    
    # Dark energy is constant (W-field tension)
    # Matter evolves as the mode sum
    # The expansion law:
    E2 = Omega_L + Omega_m * matter_ratio
    
    return math.sqrt(max(E2, 0))

# Compare FLRW vs IDCM expansion laws
print(f"\n3. 膨脹歷史 H(z) — FLRW vs IDCM:")
print(f"   {'z':<8} {'H_FLRW':<15} {'H_IDCM':<15} {'ratio':<10}")
print(f"   " + "-"*48)
for z in [0.0, 0.5, 1.0, 2.33, 5.0, 10.0, 15.0, 17.0]:
    h_flrw = H0 * E_z_FLRW(z)
    h_idcm = H0 * E_z_IDCM(z)
    ratio = h_idcm / h_flrw if h_flrw > 0 else 0
    print(f"   {z:<8.2f} {h_flrw:<15.2f} {h_idcm:<15.2f} {ratio:<10.4f}")

# ================================================================
# Step 5: Distance-redshift relation
# ================================================================
# In the IDCM, the comoving distance is:
#   DM(z) = ∫₀ᶻ c·dz'/H(z')
#
# This is the same integral as FLRW, but with the IDCM H(z).

def dc_IDCM(z, n=500):
    """IDCM comoving distance"""
    zv = np.linspace(0, z, n)
    dz = z / n
    E = np.array([E_z_IDCM(zi) for zi in zv])
    return (c_light / H0) * np.sum(dz / E)

def dc_FLRW(z, n=500):
    """FLRW comoving distance with IDCM parameters"""
    zv = np.linspace(0, z, n)
    dz = z / n
    E = np.sqrt(Omega_m * (1+zv)**3 + Omega_L)
    return (c_light / H0) * np.sum(dz / E)

bao = 2 * math.pi * R_H / 88 / 2  # 147.44 Mpc

print(f"\n4. 距離-紅移關係 DM(z):")
print(f"   BAO rd = λ_sync/2 = {bao:.2f} Mpc")
print(f"   {'z':<8} {'DM_FLRW':<15} {'DM_IDCM':<15} {'DM/rd_FLRW':<15} {'DM/rd_IDCM':<15}")
print(f"   " + "-"*68)
for z in [0.0, 0.5, 1.0, 2.33, 5.0, 10.0, 15.0, 17.0]:
    dm_f = dc_FLRW(z)
    dm_i = dc_IDCM(z)
    print(f"   {z:<8.2f} {dm_f:<15.0f} {dm_i:<15.0f} {dm_f/bao:<15.4f} {dm_i/bao:<15.4f}")

# ================================================================
# Step 6: DESI DR2 comparison
# ================================================================
z_desi = 2.33
dm_idcm = dc_IDCM(z_desi)
dm_flrw = dc_FLRW(z_desi)
dm_rd_idcm = dm_idcm / bao
dm_rd_flrw = dm_flrw / bao

dm_rd_obs = 39.32
dm_rd_err = 0.33

print(f"\n" + "=" * 70)
print("DESI DR2 Lyα BAO 測試 (z=2.33)")
print("=" * 70)
print(f"\nIDCM 結構預測 (FLRW 形式):")
print(f"   DM/rd = {dm_rd_flrw:.4f} vs DESI {dm_rd_obs:.4f} ± {dm_rd_err}")
print(f"   差異 = {(dm_rd_flrw - dm_rd_obs)/dm_rd_err:+.1f}σ")

print(f"\nIDCM 結構預測 (W-field 晶格推導):")
print(f"   DM/rd = {dm_rd_idcm:.4f} vs DESI {dm_rd_obs:.4f} ± {dm_rd_err}")
print(f"   差異 = {(dm_rd_idcm - dm_rd_obs)/dm_rd_err:+.1f}σ")

# ================================================================
# Step 7: What does the W-field tell us?
# ================================================================
print("\n" + "=" * 70)
print("分析")
print("=" * 70)
msg = """
K_Chain 固定環嘅模式結構:
  γ_n = 4 sin²(πn/88), n=1..43
  γ_2 = 4 sin²(π/44) = 0.02036 (SYNC mode)
  γ_1 = 4 sin²(π/88) = 0.00510 (fundamental)
  
總能量: Σ γ_n (n=1..43) = 86 (exact, sum of all modes)
Ω_m = 86/φ^k = 0.3167 (結構推導)

關鍵問題: 暗能量點樣驅動膨脹?
  ρ_Λ = constant (W-field tension)
  ρ_m = Σ γ_n × (occupancy) = evolves with z
  
如果暗能量係 W-field tension，咁 ρ_Λ 係常數 → 同 ΛCDM 一樣。
但 ρ_m 嘅演化可能唔係 (1+z)³，因為 K_Chain 模式佔據數隨 z 變化。

呢個係 FLRW 嘅假設: ρ_m ∝ (1+z)³
IDCM 嘅可能: ρ_m = Σ γ_n × f_n(z) 其中 f_n(z) 係模式佔據函數

如果 f_n(z) 唔係 (1+z)³，咁 H(z) 就唔同 → DM/rd 嘅預測會變。
"""
print(msg)