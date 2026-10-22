#!/usr/bin/env python3
"""
CMB 低階多極矩：從渲染邊界幾何推導角功率譜
==============================================
核心假設：CMB 不是原始遺蹟，而是渲染邊界 (Rendering Boundary) 的角功率譜。
推導從 MERA 深度 + 觀察者運動出發，而非假設 φ^(-ℓ) 冪律。
"""
import math, json
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI
EPS = PHI_INV / 4
KAPPA = 1/16

print("=" * 72)
print("  CMB Low-ℓ: Rendering Boundary Angular Power Spectrum Derivation")
print("=" * 72)

# ══════════════════════════════════════════════════════════════════
# Part 1: Rendering Boundary Geometry
# ══════════════════════════════════════════════════════════════════
print("\n" + "─" * 72)
print("  Part 1: 渲染邊界幾何")
print("─" * 72)

# MERA tree parameters
B = 4    # branching factor
L = 53/8  # depth = 6.625
N_d = 44  # channel count

# Number of sites on the boundary sphere
N_boundary = B**L  # 4^6.625
print(f"""
  MERA Branching:  B = {B}
  MERA Depth:      L = {L} = {L:.3f}
  N_d (channels):  N_d = {N_d}
  
  Boundary sites:  N_boundary = B^L = 4^{L:.3f} = {N_boundary:.1f}
  Max ℓ resolvable: ℓ_max ≈ √(N_boundary/2) ≈ {math.sqrt(N_boundary/2):.0f}
""")

# Boundary sphere radius = τ_depth
# From IDCM: τ_depth = 0.958 × H₀⁻¹ ≈ 13.8 Gyr
# (0.958 = 1 - ε/e, the sync function at z=0)
H0_inv = 13.8  # Gyr
tau_depth = 13.8  # Gyr
R = tau_depth * 299792.458 / 1000  # Mpc (c × τ_depth)

print(f"  Rendering radius: R = {R:.0f} Mpc (c × τ_depth)")

# ══════════════════════════════════════════════════════════════════
# Part 2: Rendering Correlation Function
# ══════════════════════════════════════════════════════════════════
print("\n" + "─" * 72)
print("  Part 2: 渲染相關函數 → 角功率譜")
print("─" * 72)

# The rendering boundary has N_boundary sites distributed on a sphere.
# The angular correlation function between two points separated by angle θ:
# C(θ) = ⟨T(n̂₁)T(n̂₂)⟩ = σ² · f(θ)

# f(θ) depends on the MERA tree structure.
# At the boundary (depth L), each site is connected to B children at depth L-1.
# The correlation between two boundary sites depends on their nearest common ancestor.

# For a MERA tree with branching B, the correlation at angular separation θ:
# θ → 0:  highly correlated (nearby sites share MERA ancestors)
# θ → π:  weakly correlated (far apart sites have different ancestors)

# The angular power spectrum is the Legendre transform of C(θ):
# C_ℓ = 2π ∫_{-1}^{1} C(θ) P_ℓ(cos θ) d(cos θ)

# CRITICAL: The rendering boundary is not isotropic.
# Observer motion (CMB dipole) creates a preferred direction.
# The rendering depth at angle θ from the motion direction:
# L_eff(θ) = L + β · cos(θ) · L
# where β = v/c ≈ 0.00123

# This creates a dipole modulation of the effective resolution:
# Resolution at θ: Δθ_eff(θ) = π / B^L_eff(θ)

# The angular power spectrum for a dipole-modulated sphere:
# C_ℓ = C_ℓ^0 + A_dipole · C_ℓ^1 · cos(θ_dipole)

# where:
# - C_ℓ^0: isotropic component (from rendering boundary)
# - C_ℓ^1: dipole-modulated component (from observer motion)
# - A_dipole: amplitude = β · L · ln(B) ≈ 0.00123 × 6.625 × 1.386 ≈ 0.0113

# But this is TINY (1% effect). The observed quadrupole deficit is 80%.
# So the dipole modulation of rendering depth is NOT the dominant effect.

beta = 0.00123  # v/c
A_dipole = beta * L * math.log(B)
print(f"""
  Observer motion:  β = v/c = {beta:.5f}
  Dipole modulation of MERA depth:
    A_dipole = β · L · ln(B) = {A_dipole:.6f}
    → Only {A_dipole*100:.2f}% effect — TOO SMALL for quadrupole defect

  CONCLUSION: The quadrupole anomaly is NOT from dipole modulation of
  rendering resolution. The effect is 2 orders of magnitude too small.
""")

# ══════════════════════════════════════════════════════════════════
# Part 3: The REAL Mechanism — Rendering Boundary as Frame Buffer
# ══════════════════════════════════════════════════════════════════
print("─" * 72)
print("  Part 3: 真正機制 — 渲染邊界等價於 Frame Buffer")
print("─" * 72)

# The CMB is the "default clear color" of the rendering frame buffer.
# When SYNC_cost reaches W_site_max = 44, the system returns a
# DEFAULT_CLEAR_COLOR instead of continuing the rendering.

# This DEFAULT_CLEAR_COLOR is NOT a random field — it's the
# trace of the Fibonacci scheduling pattern at the boundary.

# The Fibonacci scheduling at step k=5 (SNC instruction):
# Cumulative allocation C_5 = F_4/F_5 = 3/5 = 0.6

# The CMB quadrupole (ℓ=2) is the lowest ℓ mode.
# Its power should be suppressed by the SAME Fibonacci ratio:
# C₂/C₂_model = 1 - F_4/F_5 = 1 - 3/5 = 2/5 = 0.4

# The octopole (ℓ=3) should be suppressed less:
# C₃/C₃_model = 1 - F_5/F_6 = 1 - 5/8 = 3/8 = 0.375

# But wait — these are both close to 0.4, which doesn't match the data.

# Let me try a different approach: the suppression is NOT in C_ℓ space
# but in SPATIAL CORRELATION space.

# The CMB temperature correlation function at angular separation θ:
# C(θ) = Σ_ℓ (2ℓ+1)/(4π) · C_ℓ · P_ℓ(cos θ)

# If the rendering boundary has a finite correlation length ξ_CMB,
# then C(θ) should be suppressed at θ > ξ_CMB/R.

# The rendering boundary correlation length is determined by the
# MERA tree's branching structure:
# ξ_CMB = R · B^(-L/2) = R · 4^(-L/2) = R · 2^(-L) = R · 2^(-6.625) = R/99

xi_CMB = R / (2**L)
theta_xi = math.degrees(xi_CMB / R)  # radians

print(f"""
  Rendering correlation length:
    ξ_CMB = R · 2^(-L) = R / 2^{L:.3f} = R / {2**L:.1f}
    ξ_CMB = {xi_CMB:.1f} Mpc
    θ_ξ = {theta_xi:.2f}° (angular scale)
    
  This is the scale where rendering boundary effects become important.
  At θ > θ_ξ, the CMB correlation function should be suppressed.
  
  The quadrupole (ℓ=2) corresponds to θ ≈ 90°.
  The octopole (ℓ=3) corresponds to θ ≈ 60°.
  
  ℓ=2 scale: θ₂ = 90° >> θ_ξ = {theta_xi:.2f}° → strongly suppressed
  ℓ=3 scale: θ₃ = 60° >> θ_ξ = {theta_xi:.2f}° → suppressed
  ℓ=10 scale: θ₁₀ = 18° >> θ_ξ = {theta_xi:.2f}° → suppressed
  ℓ=100 scale: θ₁₀₀ = 1.8° → still > θ_ξ
  ℓ=1000 scale: θ₁₀₀₀ = 0.18° → comparable to θ_ξ
""")

# This doesn't work either — the correlation length is ~0.01°, which
# corresponds to ℓ ~ 18000. At ℓ=2, the effect should be negligible.

# THE ACTUAL MECHANISM:
# The CMB is NOT a "rendering boundary" in the spatial sense.
# It's a rendering boundary in the REDSHIFT sense (z ≈ 1100).
# The angular power spectrum at low ℓ is determined by the geometry
# of the LIGHT CONE, not the spatial boundary.

# At low ℓ (large angular scales), the CMB temperature fluctuations
# are dominated by the Sachs-Wolfe effect and ISW effect.
# These are affected by the rendering boundary because they involve
# INTEGRALS along the line of sight.

# Key insight: the ISW effect at low ℓ is a DIRECT function of
# the rendering throughput. The ISW integral:
# ΔT_ISW/T ∝ ∫ dΦ/dt · dt
# where Φ is the gravitational potential.

# In IDCM, Φ is the W-field rendering output. At low ℓ,
# the rendering throughput is limited by the Fibonacci scheduling.
# The ISW contribution at low ℓ should be SUPPRESSED by the
# same factor as the sync bump (ε/e).

# ISW suppression factor:
# F_ISW = 1 - ε/e = 1 - 0.05684 = 0.9432

# The ISW contributes to C_ℓ at ℓ ≲ 10.
# The ISW-suppressed C_ℓ:
# C_ℓ_ISW = C_ℓ_SW + F_ISW² · C_ℓ_ISW_ΛCDM
# (F_ISW² because power spectrum = (ΔT)²)

F_ISW = 1 - EPS / math.e
F_ISW_sq = F_ISW**2

print(f"""
  THE CORRECT MECHANISM: ISW Suppression from Sync Dip
  ====================================================
  
  The ISW (Integrated Sachs-Wolfe) effect at low ℓ is suppressed
  by the sync dip amplitude ε = φ⁻¹/4:
  
  F_ISW = 1 - ε/e = {F_ISW:.6f}
  F_ISW² = {F_ISW_sq:.6f} (power spectrum suppression)
  
  The ISW contributes ~50% of the C_ℓ power at ℓ=2, and ~20% at ℓ=3.
  
  Predicted C_ℓ/C_ℓ_model:
    ℓ=2: C₂/C₂_model = (C_SW + F_ISW² · C_ISW) / (C_SW + C_ISW)
    ℓ=3: C₃/C₃_model = (C_SW + F_ISW² · C_ISW) / (C_SW + C_ISW)
""")

# ISW fraction at low ℓ (from Planck 2018 + CMB lensing)
# ℓ=2: ISW fraction ≈ 50%, SW fraction ≈ 50%
# ℓ=3: ISW fraction ≈ 20%, SW fraction ≈ 80%
# ℓ=4: ISW fraction ≈ 10%, SW fraction ≈ 90%
# ℓ≳10: ISW fraction ≈ 0%, SW fraction ≈ 100%

isw_frac = {2: 0.50, 3: 0.20, 4: 0.10, 5: 0.05, 10: 0.01}

for ell in [2, 3, 4, 5, 10]:
    f_isw = isw_frac[ell]
    f_sw = 1 - f_isw
    C_ratio = (f_sw + F_ISW_sq * f_isw) / (f_sw + f_isw)
    print(f"    ℓ={ell}: ISW={f_isw*100:.0f}%, SW={f_sw*100:.0f}% → C_ℓ/C_ℓ_model = {C_ratio:.4f}")

# Compare with observed data
planck_data = {2: 0.200, 3: 0.839, 4: 0.907, 5: 1.000}

print(f"\n  Comparison with Planck 2018 data:")
for ell in [2, 3, 4, 5]:
    f_isw = isw_frac[ell]
    f_sw = 1 - f_isw
    C_pred = (f_sw + F_ISW_sq * f_isw) / (f_sw + f_isw)
    C_obs = planck_data[ell]
    print(f"    ℓ={ell}: predicted = {C_pred:.4f}, observed = {C_obs:.4f}, Δ = {abs(C_pred-C_obs):.4f}")

# The ISW prediction gives:
# ℓ=2: predicted = (0.5 + 0.9432² × 0.5) / 1.0 = (0.5 + 0.445) = 0.945
# But observed = 0.200. This is COMPLETELY wrong.

# So the ISW suppression is also not the right mechanism.

# ══════════════════════════════════════════════════════════════════
# HONEST ASSESSMENT
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  HONEST ASSESSMENT")
print("=" * 72)

print("""
  THREE ATTEMPTED MECHANISMS — ALL FAILED:
  
  1. φ^(-ℓ) power law:
     ℓ=2: predicted 0.618, observed 0.200 → ❌ factor 3 off
     
  2. Dipole modulation of MERA depth:
     Effect size: 1.1% → ❌ 2 orders too small
     
  3. ISW suppression from sync dip:
     ℓ=2: predicted 0.945, observed 0.200 → ❌ factor 5 off
  
  CONCLUSION: The CMB quadrupole anomaly at ℓ=2 is NOT easily
  explained by any simple IDCM structural mechanism.
  
  POSSIBLE EXPLANATIONS:
  
  A. Cosmic variance (63% at ℓ=2) makes the "anomaly" insignificant
     → The quadrupole is within 1.3σ of ΛCDM when cosmic variance
     is properly accounted for → NOT an anomaly at all.
  
  B. The quadrupole is a real anomaly but ITS ORIGIN IS NOT
     IN THE IDCM RENDERING FRAMEWORK → it's a different phenomenon.
  
  C. The quadrupole is a real anomaly requiring a MORE COMPLEX
     rendering boundary geometry than the simple spherical model.
  
  RECOMMENDATION: 
  The CMB low-ℓ test is NOT a clean verification path for the
  observer-relative hypothesis. Focus on the VERIFIABLE tests:
  - JWST high-z galaxy maturity (test 1)
  - H₀ environmental modulation (test 3)
  - DESI DR2 cross-correlation (when available)
""")

# Save results
with open("verification/cmb_derivation_results.json", "w") as f:
    json.dump({
        "attempted_mechanisms": {
            "phi_power_law": {"status": "failed", "reason": "ℓ=2 factor 3 off"},
            "dipole_modulation": {"status": "failed", "reason": "2 orders too small"},
            "isw_suppression": {"status": "failed", "reason": "ℓ=2 factor 5 off"}
        },
        "verdict": "CMB low-ℓ is NOT a clean test for observer-relative hypothesis",
        "recommendation": "Focus on JWST high-z and H₀ environmental tests"
    }, f, indent=2)
print("  Results saved to verification/cmb_derivation_results.json")