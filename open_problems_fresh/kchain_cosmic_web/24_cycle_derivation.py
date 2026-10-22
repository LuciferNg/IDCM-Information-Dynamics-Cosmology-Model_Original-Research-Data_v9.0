#!/usr/bin/env python3
"""
Re-derivation of t_cycle — Cosmic Restart Time
================================================
t_cycle = τ₀ × e^(1/κ) = τ₀ × e^16

κ = 1/16 (exact, from (εφ)²)
e^16 = 8,886,110 (exact)

The question: what is τ₀?
"""

import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

print("=" * 80)
print("  RE-DERIVATION: t_cycle = τ₀ × e^(1/κ)")
print("=" * 80)

c = 0.3066  # Mpc/Myr

# ================================================================
# 1. Fixed constants
# ================================================================
print(f"\n{'─'*80}")
print("  1. FIXED CONSTANTS")
print(f"{'─'*80}")

print(f"  κ = 1/16 = 0.0625 (exact)")
print(f"  e^(1/κ) = e^16 = {math.exp(16):.0f} (exact)")
print(f"")

# ================================================================
# 2. τ₀ from different physical processes
# ================================================================
print(f"  2. τ₀ FROM DIFFERENT PHYSICAL PROCESSES")
print(f"{'─'*80}")

# 2a. SYNC time
T_SYNC = 88 * LAMBDA_SYNC / c / 1e3
print(f"\n  2a. SYNC time:")
print(f"     τ₀ = T_SYNC = {T_SYNC:.4f} Gyr")
print(f"     t_cycle = {T_SYNC * math.exp(16):.2e} Gyr = {T_SYNC * math.exp(16) / 1e3:.2e} trillion Gyr")

# 2b. Hubble time
H0_inv = 13.8  # Gyr
print(f"\n  2b. Hubble time:")
print(f"     τ₀ = H₀⁻¹ = {H0_inv:.1f} Gyr")
print(f"     t_cycle = {H0_inv * math.exp(16):.2e} Gyr")

# 2c. Domain fluctuation time (original doc)
xi = LAMBDA_SYNC / 2  # correlation length = λ_sync/2
R_h = C_LIGHT / H0_IDCM
tau_domain = H0_inv * xi / R_h
print(f"\n  2c. Domain fluctuation time (original):")
print(f"     ξ = λ_sync/2 = {xi:.2f} Mpc")
print(f"     R_h = {R_h:.2f} Mpc")
print(f"     ξ/R_h = {xi/R_h:.6f}")
print(f"     τ₀ = H₀⁻¹ × ξ/R_h = {tau_domain:.4f} Gyr")
print(f"     t_cycle = {tau_domain * math.exp(16):.2e} Gyr")

# 2d. N_sync × SYNC time
N_sync = int(4 / EPS)  # 42
print(f"\n  2d. N_sync × SYNC time:")
print(f"     N_sync = ⌊4/ε⌋ = {N_sync}")
print(f"     τ₀ = N_sync × T_SYNC = {N_sync * T_SYNC:.2f} Gyr")
print(f"     t_cycle = {N_sync * T_SYNC * math.exp(16):.2e} Gyr")

# 2e. K_Tree level ℓ
print(f"\n  2e. K_Tree levels:")
for ell in [0, 3, 5, 7, 9, 10, 11, 12, 15]:
    scale = R_H / (L3 ** ell)
    tau_ell = T_SYNC * (L3 ** ell)
    t_cycle_ell = tau_ell * math.exp(16)
    if scale > 1:
        phys = f"{scale:.1f} Mpc"
    elif scale > 1e-3:
        phys = f"{scale*1e3:.1f} kpc"
    elif scale > 1e-6:
        phys = f"{scale*1e6:.1f} pc"
    else:
        phys = f"{scale:.2e} Mpc"
    print(f"     ℓ={ell:2d}: τ₀={tau_ell:.2e} Gyr, scale={phys}, t_cycle={t_cycle_ell:.2e} Gyr")

# ================================================================
# 3. The escape condition
# ================================================================
print(f"\n{'─'*80}")
print("  3. ESCAPE FROM THE ATTRACTOR")
print(f"{'─'*80}")

# The recursion: C_{n+1} = 1/(1+C_n)
# Fixed point: C = φ⁻¹ ≈ 0.618
# Escape: C ≤ 0 or C ≤ -1-φ⁻¹ ≈ -1.618
# Fluctuation per domain: ΔC ∼ √κ = 1/4

PHI_INV = PHI - 1
escape_to_zero = 0 - PHI_INV  # need to go from φ⁻¹ to 0
escape_to_neg = -1 - PHI_INV - PHI_INV  # need to go from φ⁻¹ to -1-φ⁻¹

print(f"  Attractor: C = φ⁻¹ = {PHI_INV:.6f}")
print(f"  Escape to C=0: ΔC = {escape_to_zero:.6f}")
print(f"  Escape to C=-1-φ⁻¹: ΔC = {escape_to_neg:.6f}")
print(f"  Fluctuation per domain: √κ = {math.sqrt(KAPPA):.6f}")
print(f"")
print(f"  Random walk: N_domains = (ΔC_escape / √κ)²")
print(f"  N_domains (to zero) = ({escape_to_zero:.4f}/{math.sqrt(KAPPA):.4f})² = {(escape_to_zero/math.sqrt(KAPPA))**2:.1f}")
print(f"  N_domains (to -1-φ⁻¹) = ({escape_to_neg:.4f}/{math.sqrt(KAPPA):.4f})² = {(escape_to_neg/math.sqrt(KAPPA))**2:.1f}")

# ================================================================
# 4. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  4. SUMMARY")
print(f"{'─'*80}")

print(f"""
  t_cycle = τ₀ × e^(1/κ) = τ₀ × e^16
  
  τ₀ depends on the physical escape process:
  
  (a) Single SYNC cycle:     τ₀ = {T_SYNC:.2f} Gyr
      → t_cycle = {T_SYNC * math.exp(16):.2e} Gyr
      
  (b) Domain fluctuation:    τ₀ = {tau_domain:.4f} Gyr
      → t_cycle = {tau_domain * math.exp(16):.2e} Gyr
      
  (c) N_sync cycles:         τ₀ = {N_sync * T_SYNC:.2f} Gyr
      → t_cycle = {N_sync * T_SYNC * math.exp(16):.2e} Gyr
      
  (d) K_Tree ℓ=10:           τ₀ = {T_SYNC * L3**10:.2e} Gyr
      → t_cycle = {T_SYNC * L3**10 * math.exp(16):.2e} Gyr
      ≈ 2.7 × 10¹⁴ Gyr
  
  The original doc says τ₀ ∼ 0.1-3 Gyr, giving t_cycle ∼ 3×10⁵-⁷ Gyr.
  But the user's number (2.7×10¹⁴ Gyr) requires τ₀ = 2.7e14/e^16 = 3.04e7 Gyr.
  
  This τ₀ = 3.04e7 Gyr corresponds to K_Tree level ℓ=10:
  T_SYNC × 4^10 = {T_SYNC * L3**10:.2e} Gyr
  Scale at ℓ=10: {R_H/L3**10*1e3:.1f} kpc (galaxy scale)
  
  The question: which τ₀ is physically correct for the
  quantum fluctuation escape process?
""")