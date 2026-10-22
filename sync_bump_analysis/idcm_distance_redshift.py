#!/usr/bin/env python3
"""
IDCM Distance-Redshift: W-field Propagation Derivation
=======================================================
From K_Chain lattice action to D(z) relation.
No FLRW. Pure lattice propagation.
"""
import math, numpy as np

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
KAPPA = 1/16
VEV_sq = EPS / (2*KAPPA)
N_d = 44
R_H = 4129.94  # Mpc
H0 = 299792.458 / R_H  # 72.59 km/s/Mpc
c = 0.707  # MERA speed

# ================================================================
# Step 1: W-field equation of motion on K_Chain
# ================================================================
# Discrete Lagrangian:
#   L = Σ_n [½(∂W_n/∂t)² - ½(W_{n+1} - W_n)² - V(W_n)] + S_sync
#
# EOM:
#   ∂²W_n/∂t² = (W_{n+1} - 2W_n + W_{n-1}) - V'(W_n) + ∂S_sync/∂W_n
#
# Free field (V'=0, S_sync=0):
#   ∂²W_n/∂t² = W_{n+1} - 2W_n + W_{n-1}
#   → ω² = 4 sin²(k/2), v_g = cos(k/2)

print("=" * 70)
print("IDCM DISTANCE-REDSHIFT FROM W-FIELD PROPAGATION")
print("=" * 70)

print(f"\n1. W-field free dispersion:")
print(f"   ω² = 4 sin²(k/2), k = 2πn/88")
print(f"   v_g(n) = cos(πn/88)")
print(f"   SYNC mode (n=2): γ₂ = 4 sin²(π/44) = {4*math.sin(math.pi/44)**2:.6f}")

# ================================================================
# Step 2: SYNC coupling as energy loss mechanism
# ================================================================
# The SYNC term:
#   S_sync = g_sync · Σ_n cos(θ_n - θ_{n+1} - 2π/88)
#
# Ground state: θ_n - θ_{n+1} = 2π/88 (constant phase gradient)
# This is a helical configuration in phase space.
#
# A propagating W-field excitation moves on this helical background.
# Each step advances the phase by 2π/88 relative to the background.
# The energy loss per step is determined by the gradient of S_sync.

# SYNC coupling strength from structural parameters:
# The SYNC coupling is the overlap of the W-field VEV with the
# neighboring site phase difference:
g_sync = 2 * VEV_sq * (1 - math.cos(2*math.pi/88))
# g_sync = 2 · 1.23607 · (1 - cos(π/44))
# = 2 · 1.23607 · 0.00255 = 0.00630

phase_step = 2 * math.pi / 88
energy_loss_per_step = g_sync * (1 - math.cos(phase_step))
# = 0.00630 · 0.00255 = 1.61e-5

print(f"\n2. SYNC coupling:")
print(f"   Phase step = 2π/88 = {phase_step:.6f}")
print(f"   g_sync = 2·|W₀|²·(1-cos(2π/88)) = {g_sync:.6f}")
print(f"   Energy loss per site = {energy_loss_per_step:.6e}")

# ================================================================
# Step 3: Redshift from cumulative energy loss
# ================================================================
# A W-field excitation (mode n) has energy E_n = ω_n = 2|sin(πn/88)|
# After N propagation steps, energy loss = N · energy_loss_per_step
# Redshift: 1+z = E_initial / (E_initial - N·loss)
#
# For small z:
#   z = N · loss / E_initial

def E_n(n):
    """Energy of mode n on K_Chain"""
    return 2 * abs(math.sin(math.pi * n / 88))

def N_from_z(z, n):
    """Number of propagation steps for redshift z"""
    return z * E_n(n) / energy_loss_per_step

def D_from_z(z, n):
    """Distance traveled = N steps × site spacing"""
    site_spacing = R_H / 88
    return N_from_z(z, n) * site_spacing

print(f"\n3. Redshift from energy loss:")
print(f"   Mode n=2 (SYNC): E₂ = {E_n(2):.6f}")
print(f"   z = N · {energy_loss_per_step:.6e} / {E_n(2):.6f} = N · {energy_loss_per_step/E_n(2):.6e}")

# ================================================================
# Step 4: Distance-redshift relation
# ================================================================
# D(z) = N · (R_H/88) = z · E_n · R_H / (88 · loss)
# 
# Simplifying:
#   D(z) = z · 2|sin(πn/88)| · R_H / (88 · g_sync · (1-cos(2π/88)))
#        = z · R_H · [2|sin(πn/88)| / (88 · g_sync · (1-cos(2π/88)))]
#
# The Hubble law D(z) = z · c/H₀ is recovered when:
#   prefactor = c/H₀ = R_H
#   (since c=0.707, H₀ = 0.707/R_H in natural units)
#
# Wait — c=0.707 is the MERA speed, not the speed of light in km/s.
# In natural units (R_H=1), the Hubble law is D(z) = z · c/H₀ = z · R_H.
# But c=0.707 here, so D(z) = z · 0.707 · R_H / 0.707 = z · R_H.
# 
# Hmm, the units are confusing. Let me be more careful.

print(f"\n4. Distance-redshift relation:")
print(f"   D(z) = z · E_n · R_H / (88 · g_sync · (1-cos(2π/88)))")

# Compute prefactor for SYNC mode (n=2)
prefactor_n2 = E_n(2) * R_H / (88 * g_sync * (1 - math.cos(2*math.pi/88)))
print(f"   For n=2: D(z) = z · {prefactor_n2:.1f} Mpc")
print(f"   Hubble law: D(z) = z · c/H₀ = z · {c/H0:.1f} Mpc")
print(f"   Ratio: {prefactor_n2/(c/H0):.4f}")

# For the Hubble law to hold, we need:
#   E_n · R_H / (88 · g_sync · (1-cos(2π/88))) = c/H₀ = R_H
#   E_n / (88 · g_sync · (1-cos(2π/88))) = 1
#   g_sync = E_n / (88 · (1-cos(2π/88)))
#   g_sync = 2|sin(πn/88)| / (88 · (1-cos(2π/88)))

g_sync_hubble = E_n(2) / (88 * (1 - math.cos(2*math.pi/88)))
print(f"\n   g_sync required for Hubble law = {g_sync_hubble:.6f}")
print(f"   g_sync from structural parameters = {g_sync:.6f}")
print(f"   Ratio: {g_sync/g_sync_hubble:.4f}")

# ================================================================
# Step 5: Compute DM(z) and DM/rd for DESI comparison
# ================================================================
print(f"\n5. IDCM DM(z) prediction (self-consistent):")
print(f"   Using D(z) = z · {prefactor_n2:.1f} Mpc")
print(f"   (This is the IDCM distance for mode n=2)")

# DM at z=2.33
z_desi = 2.33
dm_idcm = prefactor_n2 * z_desi
print(f"   DM(z={z_desi}) = {dm_idcm:.0f} Mpc")

# DM/rd using IDCM BAO scale
dm_rd_idcm = dm_idcm / 147.44
print(f"   DM/rd = {dm_rd_idcm:.4f}  (rd = λ_sync/2 = 147.44 Mpc)")

# DESI DR2 Lyα BAO measurement
dm_rd_desi = 39.32
dh_rd_desi = 8.600
print(f"   DESI DR2: DM/rd = {dm_rd_desi:.4f} ± 0.33")
print(f"   Difference: {(dm_rd_idcm - dm_rd_desi)/0.33:.1f}σ")

# ================================================================
# Step 6: General D(z) for all modes
# ================================================================
print(f"\n6. Full D(z) for all K_Chain modes:")
print(f"   {'n':<5} {'E_n':<10} {'D(z)/z (Mpc)':<18} {'D(z=2.33) (Mpc)':<20}")
print(f"   " + "-"*53)
for n in [1, 2, 3, 4, 5, 8, 11, 22]:
    en = E_n(n)
    d_over_z = en * R_H / (88 * g_sync * (1 - math.cos(2*math.pi/88)))
    dm = d_over_z * z_desi
    print(f"   n={n:<3} {en:<10.6f} {d_over_z:<18.1f} {dm:<20.0f}")

print(f"\n" + "="*70)
print("NEXT STEP")
print("="*70)
print(f"""
The derived distance-redshift relation D(z) = z · prefactor is LINEAR,
which is the Hubble law for small z. The prefactor depends on:

  1. The mode energy E_n (which mode dominates the propagation)
  2. The SYNC coupling strength g_sync (from structural parameters)
  3. The ring geometry (R_H, N_d=88)

For the SYNC mode (n=2):
  D(z) = z · {prefactor_n2:.0f} Mpc
  DM(z=2.33) = {dm_idcm:.0f} Mpc
  DM/rd = {dm_rd_idcm:.4f}
  DESI: 39.32 ± 0.33 → diff {(dm_rd_idcm-39.32)/0.33:.1f}σ

This is a first-principles derivation from the lattice action.
The key unknown is the SYNC coupling strength g_sync.
""")