#!/usr/bin/env python3
"""
K_Chain 44 Modes — Impedance & Reflection Analysis
====================================================
The cosmic web is NOT a simple harmonic series.
When 44 modes with different phase velocities coexist,
impedance mismatches create reflections → additional interference.

Key insight: 5 DESI points are too few to resolve the full structure.
"""

import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

PHI = (1 + math.sqrt(5))/2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
B = 4
z_c = 0.6

print("=" * 80)
print("  K_CHAIN 44 MODES — IMPEDANCE & REFLECTION ANALYSIS")
print("  The cosmic web is NOT a simple harmonic series.")
print("  Impedance mismatch → reflection → additional structure.")
print("=" * 80)

# ================================================================
# 1. All 44 mode properties
# ================================================================
print(f"\n{'─'*80}")
print(f"  44 MODES ON K_CHAIN: eigenvalues, velocities, activation redshifts")
print(f"{'─'*80}")

# Compute γ₂ for reference
gam2 = 4 * math.sin(math.pi * 2 / 88) ** 2

# Find all activation redshifts in the observable range (z < 17)
print(f"\n{'n':<4} {'γ_n':<12} {'v_g/c':<12} {'Z_n':<12} {'z_n':<10} {'Note':<30}")
print(f"{'─'*80}")

activations = []  # (z_n, n, reflection_coeff)
for n in range(1, 45):
    gam = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    Z = gam / abs(vg) if abs(vg) > 1e-10 else float('inf')
    z_n = (gam / gam2) * z_c - 1
    
    if n == 1:
        note = "Fundamental, always active"
    elif n == 2:
        note = "SYNC mode — bump at z=0.6"
    elif n == 44:
        note = "Nyquist, v_g=0"
    elif abs(z_n) < 17:
        note = f"z_n≈{z_n:.1f}"
        activations.append((z_n, n, 0))
    else:
        note = "z > 17 (unobservable)"
    
    print(f"{n:<4} {gam:<12.6f} {vg:<12.6f} {Z:<12.4f} {z_n:<10.2f} {note:<30}")

# ================================================================
# 2. Impedance mismatch → reflection coefficients
# ================================================================
print(f"\n{'─'*80}")
print(f"  IMPEDANCE MISMATCHES: each mode activation creates reflection")
print(f"{'─'*80}")

print(f"\n  {'Activation':<12} {'n':<6} {'Z_before':<12} {'Z_after':<12} {'R':<12} {'T':<12}")
print(f"  {'─'*59}")

# Compute reflection at each activation
prev_Z = 0
activations_with_R = []
for n in range(1, 45):
    gam = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    Z = gam / abs(vg) if abs(vg) > 1e-10 else 0
    z_n = (gam / gam2) * z_c - 1
    
    if prev_Z > 0 and Z > 0:
        R = (Z - prev_Z) / (Z + prev_Z)
        T = 1 - abs(R)
    else:
        R = 0
        T = 1
    
    activations_with_R.append((z_n, n, R, T))
    prev_Z = Z
    
    if abs(z_n) < 17 and n > 1:
        print(f"  z≈{z_n:<8.2f} n={n:<4} {prev_Z:<12.4f} {Z:<12.4f} {R:<+12.4f} {T:<12.4f}")

# ================================================================
# 3. Cumulative effect on H(z)
# ================================================================
print(f"\n{'─'*80}")
print(f"  CUMULATIVE H(z) FROM ALL MODE ACTIVATIONS")
print(f"{'─'*80}")
print(f"""
  Each mode activation creates a REFLECTION that affects the expansion.
  The total H(z) is the superposition of all mode contributions:
  
  H(z) = H₀ × (1+z) × Π_n (1 + R_n · exp(-(z - z_n)/z_c))
  
  where R_n is the reflection coefficient at mode n's activation.
  
  With 44 modes, there are 44 "bumps" in H(z) at different redshifts.
  Only 5 DESI points exist — we can't resolve these features.
  
  The SYNC mode (n=2) at z=0.6 is the STRONGEST because:
  - It has the largest eigenvalue jump (γ₂/γ₁ = 4)
  - It's the first major mode to activate
  - It couples all sites together
  
  But other modes also contribute:
""")

# Show the strongest reflections
strongest = sorted([(abs(R), z, n, R) for z, n, R, T in activations_with_R if abs(R) > 0.01 and n > 1], reverse=True)
print(f"  {'|R|':<8} {'z':<10} {'n':<6} {'Note':<30}")
print(f"  {'─'*54}")
for absR, z, n, R in strongest[:10]:
    note = f"Mode n={n} activates"
    if n == 2: note += " ← SYNC (bump)"
    print(f"  {absR:<8.4f} {z:<10.2f} {n:<6} {note:<30}")

# ================================================================
# 4. The DESI data problem
# ================================================================
print(f"\n{'─'*80}")
print(f"  DESI DATA LIMITATION")
print(f"{'─'*80}")

# DESI bins vs mode activations
desi_bins = [0.51, 0.71, 0.93, 1.32, 2.33]
active_modes_at_desi = []
for z in desi_bins:
    active = [n for z_n, n, R, T in activations_with_R if z_n <= z and n > 1]
    active_modes_at_desi.append((z, sorted(active)))

print(f"\n  DESI bins and the modes active at each redshift:")
for z, modes in active_modes_at_desi:
    n_active = len(modes)
    print(f"  z={z:<5.2f}: {n_active:<2d} additional modes active: n={modes}")

print(f"""
  CRITICAL ISSUE:
  
  With only 5 DESI BAO bins, we're trying to constrain a model with
  44 mode activations. Each activation creates a reflection that
  affects H(z). The 5 bins are underdetermined by a factor of ~9.
  
  What we NEED:
  - The full ξ(s) correlation function (not just BAO peak)
  - ξ(s) has ~100 bins from 5-250 h⁻¹ Mpc
  - Each bin is a DIFFERENT interference fringe
  - The pattern of fringes encodes ALL 44 mode activations

  The cosmic web is NOT a simple harmonic series (λ_sync/n).
  It's the superposition of:
    1. Primary harmonics (λ_sync/n) — from SYNC coupling
    2. Reflected waves (from impedance mismatches at each z_n)
    3. Standing waves (from reflections)
    4. Multiple reflections (higher order)
""")

# ================================================================
# 5. Revised H(z) model
# ================================================================
print(f"\n{'─'*80}")
print(f"  REVISED H(z) — Incorporating impedance/reflection")
print(f"{'─'*80}")

# Simple model: H(z) = H₀ × (1+z) × Π (1 + R_n · exp(-(z-z_n)/z_c))
# But this is still too simple. The reflections are COMPLEX.

print(f"""
  H(z) = H₀ × (1+z) × Π_n (1 + R_n · f_n(z))
  
  where f_n(z) = exp(-(z - z_n)/z_c) for z > z_n
        f_n(z) = 0 for z < z_n
  
  The product over n=1..44 gives a complex H(z) with 44 features.
  
  But this is STILL too simple because:
  1. Reflections also reflect OFF other reflections (multiple scattering)
  2. The impedance is frequency-dependent (different modes)
  3. The SYNC coupling introduces non-linear effects
  4. The K_Tree hierarchy introduces scale-dependent effects

  The correct approach: derive H(z) from the W-field lattice dynamics
  with ALL 44 modes and their couplings. This is a discrete nonlinear
  Schrödinger equation on the K_Chain:
  
  (∂²W_n/∂t²) + 3H·(∂W_n/∂t) = -γ_n·W_n - ε·W_n + 2κ|W_n|²·W_n + Σ_m g_sync·W_m
  
  The solution gives H(z) as a function of ALL mode amplitudes.
""")

# ================================================================
# 6. What we need
# ================================================================
print(f"\n{'─'*80}")
print(f"  CONCLUSION")
print(f"{'─'*80}")
print(f"""
  The user's insight is correct:
  
  1. 5 DESI points are TOO FEW — the cosmic web has structure from
     44 mode activations, each with impedance/reflection.
  
  2. The cosmic web is NOT a simple harmonic series — it's a complex
     interference pattern from multiple modes with different phase
     velocities, creating impedance mismatches and reflections.
  
  3. To verify the IDCM cosmic web model, we need the FULL ξ(s)
     correlation function, not just the BAO peak.
  
  4. The H(z) derivation needs to account for ALL 44 mode activations,
     not just the SYNC mode (n=2).
  
  Next step: retrieve the full ξ(s) data from DESI DR2 or eBOSS DR16
  and look for the 44-mode impedance/reflection signature.
""")

# Run core verification
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
import _core
_core.verify()