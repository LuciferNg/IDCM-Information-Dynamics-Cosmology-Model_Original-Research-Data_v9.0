#!/usr/bin/env python3
"""
K_Chain Standing Wave Interference — Cosmic Web as Interference Pattern
========================================================================
Model: 44-site closed ring with SYNC coupling
Multiple standing wave modes superpose → interference pattern
Projected to 3D → cosmic web (filament network)
"""

import math
import sys
sys.path.insert(0, '/home/wsl/.hermes/skills/idcm/idcm-structural-derivation/scripts')
import importlib, idcm_core; importlib.reload(idcm_core)

PHI = idcm_core.PHI
BETA = idcm_core.BETA
N_d = 44
H0 = idcm_core.H0_idcm
R_H = 299792.458 / H0  # Mpc

print("="*70)
print("K_CHAIN STANDING WAVE INTERFERENCE PATTERN")
print("="*70)

# ================================================================
# 1. Standing wave modes on the 88-site ring
# ================================================================
# n = 1..44 modes (the 44 distinct eigenvalues)
# Each mode has wavelength λ_n = 2π·R_H / (88·n/88) = 2π·R_H / n
# Wait, let me recalculate.
# K_Chain has 88 sites (44 dual). The dispersion is γ_n = 4 sin²(πn/88).
# The physical wavelength of mode n on a ring of circumference R_H:
# λ_n = 2π·R_H / (88) * (88/n) = 2π·R_H / n
# No, that's not right either.
# 
# Actually, the K_Chain is a 44-site ring. The SYNC coupling has phase 2π/88.
# The fundamental mode has wavelength λ_sync = 2π·R_H/88 = 294.88 Mpc.
# Mode n has wavelength λ_n = λ_sync / n = 2π·R_H / (88n)
# Wait no. On a discrete ring with N=88 sites, the wavelength of mode k is:
# λ_k = 2π·R_H / k, where k = 1, 2, ..., 44
# 
# The fundamental (k=1): λ_1 = 2π·R_H = 25944 Mpc (entire circumference)
# But the SYNC coupling has phase 2π/88, so its fundamental wavelength is λ_sync = 2π·R_H/88 = 294.9 Mpc
# 
# I think the confusion is: the K_Chain dispersion gives eigenmodes of the chain itself,
# while the SYNC coupling is a specific interaction term on the chain.
#
# The K_Chain eigenmodes: γ_n = 4 sin²(πn/88), n=1..44
#  → physical wavelength of mode n: λ_n = 2π·R_H / n
#  → n=1: λ_1 = 25944 Mpc (full ring circumference, the zero mode/monopole)
#  → n=2: λ_2 = 12972 Mpc (dipole)
#  → n=44: λ_44 = 589.6 Mpc (shortest mode)
#
# The SYNC coupling: cos(θ_n - θ_m - 2π/88) has phase 2π/88
#  → fundamental wavelength: λ_sync = 2π·R_H/88 = 294.9 Mpc
#  → This is the distance between adjacent sites on the 88-site dual ring
#  → BAO = λ_sync/2 = 147.44 Mpc (first harmonic of the SYNC coupling)
#
# So the eigenmode wavelengths are λ_n = 2π·R_H/n, and the SYNC wavelength is λ_sync = 2π·R_H/88.
# The BAO = λ_sync/2 = 2π·R_H/176.
#
# For the interference pattern, all modes n=1..44 superpose.
# The characteristic scales in the interference come from:
#  - Mode spacing: Δk = 1/R_H (in k-space)
#  - SYNC modulation: λ_sync = 2π·R_H/88
#  - BAO = λ_sync/2 = π·R_H/88

R_H = 4129.94  # Mpc

print(f"\nK_Chain Parameters:")
print(f"  Ring circumference = {R_H:.0f} Mpc")
print(f"  Sites = 44 (88 with dual)")
print(f"  λ_sync = 2π·R_H/88 = {2*math.pi*R_H/88:.1f} Mpc")
print(f"  BAO = λ_sync/2 = {2*math.pi*R_H/88/2:.1f} Mpc")
print()

# ================================================================
# 2. Standing wave mode table
# ================================================================
print("="*70)
print("STANDING WAVE MODES ON 88-SITE RING")
print("="*70)
print(f"{'n':<4} {'λ_n (Mpc)':<15} {'λ_n (h⁻¹ Mpc)':<18} {'γ_n = 4sin²(πn/88)':<25} {'Physical':<15}")
print("-"*72)

h = H0/100
for n in [1, 2, 3, 4, 5, 8, 11, 22, 44, 88]:
    lam = 2*math.pi*R_H / n
    gamma = 4 * math.sin(math.pi*n/88)**2
    phys = ""
    if n == 1: phys = "Full ring (monopole)"
    elif n == 2: phys = "Dipole"
    elif n == 22: phys = "Midpoint"
    elif n == 44: phys = "Nyquist mode"
    elif n == 88: phys = "Lattice spacing"
    print(f"{n:<4} {lam:<15.1f} {lam/h:<18.1f} {gamma:<25.6f} {phys:<15}")

print()

# ================================================================
# 3. SYNC coupling harmonics
# ================================================================
print("="*70)
print("SYNC COUPLING HARMONICS (Interference Fringes)")
print("="*70)
print(f"{'Harmonic':<12} {'λ (Mpc)':<15} {'λ (h⁻¹ Mpc)':<18} {'k (h/Mpc)':<15}")
print("-"*60)

for n in range(1, 15):
    lam = 2*math.pi*R_H / (88) / n  # λ_sync / n
    k = 2*math.pi / lam * h
    label = f"λ_sync/{n}"
    if n == 2: label += " ← BAO"
    print(f"{label:<12} {lam:<15.1f} {lam/h:<18.1f} {k:<15.5f}")

print()

# ================================================================
# 4. Interference pattern — the cosmic web
# ================================================================
print("="*70)
print("COSMIC WEB AS INTERFERENCE PATTERN")
print("="*70)
print("""
If the K_Chain is a closed string with SYNC coupling, multiple
standing wave modes coexist simultaneously. Their superposition
creates an interference pattern in the projected 3D space.

This interference pattern IS the cosmic web:
  - Constructive interference → galaxy filaments (density peaks)
  - Destructive interference → voids (density minima)
  - Standing wave nodes → cluster positions

The 33 K_Tree levels give a self-similar hierarchy of void scales:
""")

# K_Tree void hierarchy
print(f"{'K_Tree Level':<15} {'Scale (Mpc)':<15} {'Structure':<25}")
print("-"*55)
for level in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 33]:
    scale = R_H / (4**level)
    if scale >= 1:
        desc = f"{scale:.0f} Mpc"
    elif scale >= 0.001:
        desc = f"{scale*1000:.0f} kpc"
    else:
        desc = f"{scale*1000*1000:.0f} pc"
    print(f"Level {level:<9} {scale:<15.2f} {desc:<25}")

print()
print("="*70)
print("KEY INSIGHT")
print("="*70)
print(f"""
1. The cosmic web is the INTERFERENCE PATTERN of the K_Chain
   standing wave modes.

2. The BAO at 147 Mpc is the FIRST HARMONIC (λ_sync/2) of the
   SYNC coupling — the strongest interference fringe.

3. Higher harmonics at λ_sync/3, λ_sync/4, λ_sync/5, ... should
   appear as SUBDOMINANT FRINGES in the galaxy correlation function.

4. The 33 K_Tree levels give a NESTED VOID HIERARCHY — each level
   is a coarse-graining of the interference pattern by factor 4.

5. This predicts that the cosmic web should have preferential scales
   at λ_sync/n for n=2,3,4,5,... — a HARMONIC SERIES, not random.

6. TESTABLE: Measure the galaxy correlation function ξ(s) and look
   for SUBDOMINANT PEAKS at λ_sync/3 = 98 Mpc, λ_sync/4 = 74 Mpc,
   λ_sync/5 = 59 Mpc, etc. with the exact harmonic spacing
   Δk = 2π/λ_sync = 0.0213 h/Mpc.
""")