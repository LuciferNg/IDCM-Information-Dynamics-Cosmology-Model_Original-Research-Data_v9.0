#!/usr/bin/env python3
"""
K_Chain Cosmic Web — H(z) Verification Without FLRW
======================================================
Takes DESI DR1/DR2 BAO measurements at all redshifts,
converts to DM and DH using IDCM's rd = λ_sync/2 = 147.44 Mpc,
computes H(z) = c/DH from the data (model-independent).

No FLRW formula used. No fitting. Pure data vs structure comparison.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import *

# ================================================================
# DESI DR1 BAO Data (from 01_sync_bump_observer_relative.md)
# ================================================================
# Sample | z_eff | DM/rd | err | DH/rd | err | corr(DM,DH)
DESI_DR1 = [
    # (sample, z, DM/rd, eDM, DH/rd, eDH, corr)
    ("LRG1",  0.510, 13.62, 0.25, 20.98, 0.61, -0.445),
    ("LRG2",  0.706, 16.85, 0.32, 20.08, 0.60, -0.420),
    ("LRG3+ELG1", 0.930, 21.71, 0.28, 17.88, 0.35, -0.389),
    ("ELG2",  1.317, 27.79, 0.69, 13.82, 0.42, -0.444),
    ("LyA",   2.330, 39.71, 0.94,  8.52, 0.17, -0.477),
]

# DESI DR2 Lyα BAO (updated): DM/rd = 39.32 ± 0.33, DH/rd = 8.600 ± 0.066
# This replaces the DR1 LyA value
DESI_DR2_LYA = (2.330, 39.32, 0.33, 8.600, 0.066)

# ================================================================
# IDCM structural predictions
# ================================================================
# All from x²+x-1=0 → φ → K_Chain → λ_sync/2
rd_idcm = BAO_MPC  # 147.44 Mpc (λ_sync/2)
H0_idcm = H0_IDCM  # 72.59 km/s/Mpc

# ================================================================
# Section 1: Model-independent H(z) from DESI data
# ================================================================
print("=" * 80)
print("  K_CHAIN COSMIC WEB — H(z) VERIFICATION WITHOUT FLRW")
print("  Fresh verification: DESI data → H(z) → IDCM structure comparison")
print("  No FLRW/ΛCDM formula used. No fitting.")
print("=" * 80)

print(f"\n{'─' * 80}")
print(f"  IDCM STRUCTURAL PREDICTIONS (from x²+x-1=0)")
print(f"{'─' * 80}")
print(f"  rd = BAO = λ_sync/2 = π·R_H/88 = {rd_idcm:.4f} Mpc")
print(f"  H₀ = c/R_H = {H0_idcm:.4f} km/s/Mpc")
print(f"  R_H = {R_H:.4f} Mpc")
print(f"  λ_sync = {LAMBDA_SYNC:.4f} Mpc")
print(f"  Harmonic spacing Δk = {DELTA_K:.6f} h/Mpc")
print(f"  Ω_Λ = 4/(φ⁴-1) = {Omega_L:.6f}")
print(f"  Free parameters: 0 (all from x²+x-1=0)")

# ================================================================
# Section 2: Convert DESI measurements to physical quantities
# ================================================================
print(f"\n{'─' * 80}")
print(f"  DESI DATA → PHYSICAL QUANTITIES (using IDCM rd = {rd_idcm:.2f} Mpc)")
print(f"{'─' * 80}")

# For each DESI bin, compute:
# DM = (DM/rd) × rd_idcm     (comoving distance in Mpc)
# DH = (DH/rd) × rd_idcm     (Hubble distance in Mpc)
# H(z) = c / DH              (Hubble parameter in km/s/Mpc)
# DM(z) in FLRW: c/H₀ × ∫ dz'/E(z') — but we DON'T use this

print(f"  {'Sample':<12} {'z':<6} {'DM/rd':<10} {'DM (Mpc)':<14} {'DH/rd':<10} {'DH (Mpc)':<14} {'H(z)':<12} {'err':<8}")
print(f"  {'─' * 80}")

results = []
for sample, z, dm_rd, e_dm, dh_rd, e_dh, corr in DESI_DR1:
    dm = dm_rd * rd_idcm
    dh = dh_rd * rd_idcm
    hz = C_LIGHT / dh
    e_hz = hz * e_dh / dh_rd  # error propagation
    
    results.append((sample, z, dm, dh, hz, e_hz, dm_rd, e_dm, dh_rd, e_dh))
    
    print(f"  {sample:<12} {z:<6.3f} {dm_rd:<10.2f} {dm:<14.0f} {dh_rd:<10.2f} {dh:<14.0f} {hz:<12.2f} ±{e_hz:<6.2f}")

# Also add DR2 LyA
z_dr2 = DESI_DR2_LYA[0]
dm_rd_dr2 = DESI_DR2_LYA[1]
e_dm_dr2 = DESI_DR2_LYA[2]
dh_rd_dr2 = DESI_DR2_LYA[3]
e_dh_dr2 = DESI_DR2_LYA[4]
dm_dr2 = dm_rd_dr2 * rd_idcm
dh_dr2 = dh_rd_dr2 * rd_idcm
hz_dr2 = C_LIGHT / dh_dr2
e_hz_dr2 = hz_dr2 * e_dh_dr2 / dh_rd_dr2

results.append(("LyA (DR2)", z_dr2, dm_dr2, dh_dr2, hz_dr2, e_hz_dr2, dm_rd_dr2, e_dm_dr2, dh_rd_dr2, e_dh_dr2))
print(f"  {'LyA (DR2)':<12} {z_dr2:<6.3f} {dm_rd_dr2:<10.2f} {dm_dr2:<14.0f} {dh_rd_dr2:<10.2f} {dh_dr2:<14.0f} {hz_dr2:<12.2f} ±{e_hz_dr2:<6.2f}")

# ================================================================
# Section 3: Compare H(z) to IDCM structural predictions
# ================================================================
print(f"\n{'─' * 80}")
print(f"  H(z) COMPARISON — IDCM Structure vs DESI Data")
print(f"{'─' * 80}")
print(f"  IDCM H₀ = {H0_idcm:.2f} km/s/Mpc (structural, from c/R_H)")
print(f"")

# IDCM structural predictions for H(z):
# We DON'T have a derived H(z) from first principles yet.
# What we know:
# 1. H₀ = c/R_H = 72.59 (structural)
# 2. The expansion is driven by W-field tension (dark energy)
# 3. The K_Chain ring is fixed (doesn't expand)
# 4. Redshift = wavelength stretching
#
# For comparison, we show:
# 1. The observed H(z) from DESI (model-independent)
# 2. FLRW with Planck parameters (for reference, NOT fitting)
# 3. FLRW with IDCM parameters (for reference, NOT fitting)
# 4. The ratio H(z)/H₀

# FLRW for reference
Omega_L_IDCM = 4 / (PHI**4 - 1)
Omega_m_IDCM = 1 - Omega_L_IDCM
Omega_m_Planck = 0.315
Omega_L_Planck = 0.685
H0_Planck = 67.4

def e_flrw(z, om, ol):
    return math.sqrt(om * (1+z)**3 + ol)

print(f"  {'z':<6} {'H(z)_DESI':<15} {'H/H₀':<12} {'FLRW(IDCM)':<15} {'FLRW(Planck)':<15} {'Note':<20}")
print(f"  {'─' * 83}")

# At z=0, H₀ comparison
print(f"  {0.0:<6.2f} {H0_idcm:<15.2f} {1.0:<12.4f} {H0_idcm:<15.2f} {H0_Planck:<15.2f} {'IDCM structural':<20}")

for sample, z, dm, dh, hz, e_hz, dm_rd, e_dm, dh_rd, e_dh in results:
    h_flrw_idcm = H0_idcm * e_flrw(z, Omega_m_IDCM, Omega_L_IDCM)
    h_flrw_planck = H0_Planck * e_flrw(z, Omega_m_Planck, Omega_L_Planck)
    ratio = hz / H0_idcm
    
    # Check if DESI H(z) is closer to IDCM or Planck prediction
    diff_idcm = abs(hz - h_flrw_idcm) / e_hz
    diff_planck = abs(hz - h_flrw_planck) / e_hz
    note = ""
    if diff_idcm < diff_planck:
        note = f"Closer to IDCM ({diff_idcm:.1f}σ vs {diff_planck:.1f}σ)"
    else:
        note = f"Closer to Planck ({diff_planck:.1f}σ vs {diff_idcm:.1f}σ)"
    
    print(f"  {z:<6.3f} {hz:<15.2f} {ratio:<12.4f} {h_flrw_idcm:<15.2f} {h_flrw_planck:<15.2f} {note:<20}")

# ================================================================
# Section 4: DM(z) comparison
# ================================================================
print(f"\n{'─' * 80}")
print(f"  DM(z) COMPARISON — IDCM Structure vs DESI Data")
print(f"{'─' * 80}")

# FLRW comoving distance integral
def dc_flrw(z, H0, om, ol, n=1000):
    """Comoving distance in FLRW"""
    zv = [i * z / n for i in range(n)]
    dz = z / n
    integrand = sum(1.0 / math.sqrt(om * (1+zi)**3 + ol) for zi in zv)
    return (C_LIGHT / H0) * dz * integrand

print(f"  {'z':<6} {'DM/DESl':<14} {'DM/IDCM':<14} {'ratio':<10} {'Note':<20}")
print(f"  {'─' * 64}")

for sample, z, dm, dh, hz, e_hz, dm_rd, e_dm, dh_rd, e_dh in results:
    dm_idcm_rd = dm / rd_idcm  # This is the DESI DM/rd value
    # FLRW with IDCM params for reference
    dm_flrw_idcm = dc_flrw(z, H0_idcm, Omega_m_IDCM, Omega_L_IDCM)
    dm_flrw_planck = dc_flrw(z, H0_Planck, Omega_m_Planck, Omega_L_Planck)
    dm_rd_flrw_idcm = dm_flrw_idcm / rd_idcm
    dm_rd_flrw_planck = dm_flrw_planck / rd_idcm
    
    # How much would rd need to change to match?
    # If DM(z) is correct, then rd_required = DM_obs / (DM/rd)_obs
    # But we don't know DM(z) independently...
    
    note = f"DESI DM/rd={dm_rd:.2f}"
    print(f"  {z:<6.3f} {dm:<14.0f} {dm_flrw_idcm:<14.0f} {dm/dm_flrw_idcm:<10.4f} {note:<20}")

# ================================================================
# Section 5: The REAL H(z) problem
# ================================================================
print(f"\n{'─' * 80}")
print(f"  THE REAL H(z) PROBLEM — What IDCM Must Explain")
print(f"{'─' * 80}")

print(f"""
  The DESI data gives us H(z) at 5 redshifts (DR1) + 1 more (DR2 LyA).
  These are MODEL-INDEPENDENT — they come from the BAO angular scale
  and the Alcock-Paczynski effect, not from FLRW.
  
  Key observations:
  
  1. H(z) INCREASES with z: H(0.51) ≈ 96 km/s/Mpc → H(2.33) ≈ 236 km/s/Mpc
     This is consistent with an expanding universe.
  
  2. The K_Chain ring is FIXED (R_H = {R_H:.0f} Mpc).
     The ring does NOT expand. So what is "expansion"?
  
  3. IDCM insight: "膨脹由暗能量驅動", "紅移 = 波長被拉長"
     The expansion is NOT geometry expanding (FLRW).
     It's the W-field tension driving wavelength stretching.
  
  4. What must be derived:
     H(z) = ?  (from W-field dynamics, NOT from FLRW)
     
     The W-field has:
     - Constant tension → dark energy (Ω_Λ)
     - Mode excitations → matter (Ω_m)
     - SYNC coupling → bump at z=0.6
     - K_Tree hierarchy → scale-dependent evolution
  
  5. The H(z) function must satisfy:
     - H(0) = H₀ = {H0_idcm:.2f} (structural)
     - H(z) increases with z (observed)
     - H(z=2.33) ≈ {hz_dr2:.0f} (DESI DR2)
     - Bump at z=0.6 (SYNC transition)
     - Smooth transition to high-z
""")

# ================================================================
# Section 6: What's the IDCM H(z)? A fresh approach
# ================================================================
print(f"{'─' * 80}")
print(f"  TOWARDS IDCM H(z) — First Principles")
print(f"{'─' * 80}")

print(f"""
  The K_Chain ring has fixed circumference R_H = {R_H:.0f} Mpc.
  The SYNC mode has wavelength λ_sync = {LAMBDA_SYNC:.1f} Mpc.
  The BAO = λ_sync/2 = {rd_idcm:.2f} Mpc.
  
  The "expansion" is NOT the ring expanding.
  The ring is a fixed physical object.
  
  What IS "expansion" in IDCM?
  
  Hypothesis: The projection of the 1D K_Chain interference pattern
  onto 3D space creates the illusion of expanding space.
  
  At higher z (earlier times), the interference pattern is projected
  differently because the K_Tree coarse-graining level is different.
  
  The relation between K_Tree level ℓ and redshift z:
    z = B^ℓ - 1 = 4^ℓ - 1
    ℓ = log₄(z + 1)
  
  At each level ℓ, the effective scale is:
    s_ℓ = R_H / B^ℓ = R_H / 4^ℓ
    s_ℓ = R_H / (z + 1)
  
  This is exactly the FLRW scale factor: a = 1/(1+z) = s_ℓ/R_H
  
  But the EXPANSION RATE (how fast the scale changes) depends on
  the W-field dynamics, not on FLRW.
  
  The W-field expansion equation (from the lattice action):
    (∂²W/∂t²) + 3H·(∂W/∂t) = Δ_chain W - εW + 2κ|W|²W
  
  This is NOT the FLRW equation. It's a discrete nonlinear
  Schrödinger equation on the K_Chain lattice.
  
  The H(z) can be derived from the W-field energy density:
    H² = (8πG/3) · ρ_W
    ρ_W = ρ_Λ + ρ_m(z)
    ρ_Λ = constant (W-field tension)
    ρ_m(z) = Σ γ_n · f_n(z)  (mode occupation)
  
  Where f_n(z) is the mode occupation function — the fraction
  of modes n that are active at redshift z.
  
  The key: f_n(z) is NOT (1+z)³. It's determined by the
  K_Tree hierarchy and the SYNC transition.
  
  This is where IDCM must derive H(z) from first principles.
  The previous attempt (n_active = N_d/B^ℓ) was wrong because
  the mode occupation follows a different law.
""")

# ================================================================
# Section 7: Summary
# ================================================================
print(f"{'─' * 80}")
print(f"  SUMMARY")
print(f"{'─' * 80}")
print(f"""
  What we KNOW (structural, from x²+x-1=0):
  ✅  BAO = λ_sync/2 = {rd_idcm:.2f} Mpc (0.24% from DESI DR2)
  ✅  H₀ = c/R_H = {H0_idcm:.2f} km/s/Mpc
  ✅  Harmonic spacing Δk = {DELTA_K:.6f} h/Mpc
  ✅  Bump at z=0.6 (SYNC transition)
  ✅  K_Tree 33-level nested hierarchy
  
  What we DON'T KNOW (need derivation):
  🔴  H(z) from W-field dynamics
  🔴  f_n(z) — mode occupation function
  🔴  DM(z) — comoving distance (not FLRW)
  
  The DESI data gives us the TARGET: H(z) values at 6 redshifts.
  The IDCM must derive H(z) from the W-field lattice action,
  NOT from FLRW. The previous attempt was wrong because it
  assumed the wrong mode occupation law.
  
  The correct approach: derive ρ_m(z) from the K_Chain mode
  spectrum with the SYNC transition at z=0.6, then compute
  H²(z) = (8πG/3) × [ρ_Λ + ρ_m(z)].
""")

PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✅ {name}")
    else: FAIL += 1; print(f"  ❌ {name}")

print(f"{'─' * 80}")
print(f"  VERIFICATION CHECKS")
print(f"{'─' * 80}")

# Check 1: IDCM BAO vs DESI DR2
check(f"IDCM BAO ({rd_idcm:.2f} Mpc) vs DESI DR2 (147.09 Mpc): {abs(rd_idcm/147.09-1)*100:.2f}%",
      abs(rd_idcm/147.09 - 1) * 100 < 1)

# Check 2: DESI H(z) increases with z
hz_values = [(r[1], r[4]) for r in results]
check(f"DESI H(z) increases with z: H(0.51)={hz_values[0][1]:.1f}→H(2.33)={hz_values[-1][1]:.1f}",
      all(hz_values[i][1] < hz_values[i+1][1] for i in range(len(hz_values)-1)))

# Check 3: H(z=2.33) from DESI DR2
check(f"DESI DR2 H(z=2.33) = {hz_dr2:.1f} km/s/Mpc",
      abs(hz_dr2 - 236.4) < 5)

# Check 4: H₀ from c/R_H
check(f"IDCM H₀ = c/R_H = {H0_idcm:.4f} km/s/Mpc",
      abs(H0_idcm - 72.59) < 0.01)

# Check 5: FLRW with Planck matches H(z=2.33)
h_planck_233 = H0_Planck * e_flrw(2.33, Omega_m_Planck, Omega_L_Planck)
check(f"FLRW(Planck) H(z=2.33) = {h_planck_233:.1f} ≈ {hz_dr2:.1f}",
      abs(h_planck_233 - hz_dr2) < 5)

# Check 6: FLRW with IDCM does NOT match H(z=2.33)
h_idcm_233 = H0_idcm * e_flrw(2.33, Omega_m_IDCM, Omega_L_IDCM)
check(f"FLRW(IDCM) H(z=2.33) = {h_idcm_233:.1f} ≠ {hz_dr2:.1f} (gap = {abs(h_idcm_233-hz_dr2):.0f})",
      abs(h_idcm_233 - hz_dr2) > 10)

print(f"\n  {PASS}/{PASS+FAIL} checks passed" + (" ✅" if FAIL == 0 else f" ❌ ({FAIL} failed)"))
print(f"  H(z) derivation: OPEN (need W-field mode occupation)")
print(f"{'─' * 80}")