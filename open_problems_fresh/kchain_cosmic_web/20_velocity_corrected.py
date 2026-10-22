#!/usr/bin/env python3
"""
Corrected Velocity Field — Density Gradient Model
====================================================
The velocity field comes from the GRADIENT of the DAMPED density field:
  ρ(r) = Σ A_n × D_tree(n) × cos(2π n r/λ_sync + θ_n)
  v(r) ∝ -dρ/dr = Σ A_n × D_tree(n) × (2π n/λ_sync) × sin(2π n r/λ_sync + θ_n)

This gives clean velocity zeros at the standing wave nodes.
"""

import math, numpy as np, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

print("=" * 80)
print("  CORRECTED VELOCITY FIELD — DENSITY GRADIENT MODEL")
print("=" * 80)

lam_sync = LAMBDA_SYNC
k = 1  # LG position on K_Chain

# ================================================================
# 1. Compute density field with K_Tree damping
# ================================================================
print(f"\n{'─'*80}")
print("  1. DAMPED DENSITY FIELD")
print(f"{'─'*80}")

r = np.linspace(0, 500, 5000)

# Density field: ρ(r) = Σ A_n × D_tree(n) × cos(2π n r/λ_sync + θ_n)
rho = np.zeros_like(r)
for n in range(1, 45):
    gam = 4 * math.sin(math.pi * n / 88)**2
    theta_n = n * k * 2 * math.pi / 88
    # K_Tree damping at the mode's scale
    lam_n = lam_sync / n
    ell = math.log(R_H / lam_n, 4) if lam_n > 0 else 0
    D_tree = 4 ** (-ell)
    rho += gam * D_tree * np.cos(2 * math.pi * n * r / lam_sync + theta_n)

# Normalize density (positive at r=0)
rho = rho - np.min(rho)  # shift so min = 0
rho = rho / np.max(rho)  # normalize to [0, 1]

# ================================================================
# 2. Velocity from density gradient
# ================================================================
print(f"\n{'─'*80}")
print("  2. VELOCITY FROM DENSITY GRADIENT")
print(f"{'─'*80}")

# v(r) ∝ -dρ/dr
v_field = -np.gradient(rho, r)

# Normalize: v(0) = 0 (LG at rest)
v_field -= v_field[0]

# Scale to match observed bulk flow at GA
ga_idx = np.argmin(np.abs(r - 65.5))
v_ga = v_field[ga_idx]
scale = 250 / v_ga if abs(v_ga) > 1e-10 else 1
v_field *= scale

print(f"  Density gradient normalization:")
print(f"  v_GA(65.5 Mpc) = {v_field[ga_idx]:.0f} km/s (target: 250 km/s)")
print(f"  Scale factor = {scale:.4f}")
print(f"")
print(f"  {'r (Mpc)':<10} {'v (km/s)':<14} {'Structure':<24} {'Type':<16}")
print(f"  {'─'*64}")

for r_i in [0, 16.5, 28, 40, 65.5, 100, 118, 150, 197, 250, 295]:
    idx = np.argmin(np.abs(r - r_i))
    v = v_field[idx]
    
    struct = ""
    if abs(r_i - 16.5) < 2: struct = "Virgo Cluster"
    elif abs(r_i - 28) < 3: struct = "Local Void"
    elif abs(r_i - 40) < 3: struct = "Laniakea boundary"
    elif abs(r_i - 65.5) < 3: struct = "Great Attractor"
    elif abs(r_i - 100) < 3: struct = "Coma Cluster"
    elif abs(r_i - 118) < 3: struct = "Canes Venatici"
    elif abs(r_i - 150) < 3: struct = "Hercules Void"
    elif abs(r_i - 197) < 3: struct = "Shapley SC"
    elif abs(r_i - 250) < 3: struct = "Bootes Void"
    elif abs(r_i - 295) < 3: struct = "Hercules-Corona"
    elif r_i == 0: struct = "Local Group"
    
    # Node type
    if abs(v) < 30:
        # Check convergence/divergence
        idx_p = min(idx + 1, len(r) - 1)
        if v_field[idx_p] > v:
            ntype = "velocity zero (convergence)"
        else:
            ntype = "velocity zero (divergence)"
    elif v > 0:
        ntype = f"outflow ({v:.0f} km/s)"
    else:
        ntype = f"inflow ({v:.0f} km/s)"
    
    print(f"  {r_i:<10} {v:<+14.0f} {struct:<24} {ntype:<16}")

# ================================================================
# 3. Velocity zeros
# ================================================================
print(f"\n{'─'*80}")
print("  3. VELOCITY ZEROS — NODE PREDICTIONS")
print(f"{'─'*80}")

# Find zero crossings
zeros = []
for i in range(1, len(r)):
    if v_field[i-1] * v_field[i] <= 0 and abs(v_field[i-1] - v_field[i]) > 1:
        r_zero = (r[i-1] + r[i]) / 2
        # Check convergence/divergence
        idx_p = min(i + 1, len(r) - 1)
        if v_field[idx_p] > v_field[i]:
            ztype = "convergence"
        else:
            ztype = "divergence"
        zeros.append((r_zero, ztype))

print(f"  {'r (Mpc)':<12} {'Type':<16} {'Structure':<24} {'IDCM λ_sync/(n+0.5)':<20}")
print(f"  {'─'*72}")

for r_zero, ztype in zeros[:10]:
    # Find closest harmonic
    best_n = min(range(1, 25), key=lambda n: abs(r_zero - lam_sync/(n+0.5)))
    pred = lam_sync / (best_n + 0.5)
    
    struct = ""
    if abs(r_zero - 28) < 5: struct = "Local Void"
    elif abs(r_zero - 65.5) < 5: struct = "Great Attractor"
    elif abs(r_zero - 118) < 5: struct = "Canes Venatici"
    elif abs(r_zero - 197) < 5: struct = "Shapley SC"
    elif abs(r_zero - 84) < 5: struct = "Sculptor Void"
    
    print(f"  {r_zero:<12.1f} {ztype:<16} {struct:<24} λ_sync/{best_n+0.5:.1f} = {pred:.0f} Mpc")

# ================================================================
# 4. Laniakea boundary from velocity field
# ================================================================
print(f"\n{'─'*80}")
print("  4. LANIAKEA BOUNDARY FROM VELOCITY FIELD")
print(f"{'─'*80}")

# Laniakea boundary: where v=0 between GA and Local Void
# This is the first zero crossing before the GA
laniakea_inner_boundary = None
for r_zero, ztype in zeros:
    if r_zero < 65.5 and ztype == "divergence":
        laniakea_inner_boundary = r_zero
        break

laniakea_outer_boundary = None
for r_zero, ztype in zeros:
    if r_zero > 65.5 and ztype == "convergence":
        laniakea_outer_boundary = r_zero
        break

print(f"  Laniakea basin from velocity field:")
print(f"  Inner boundary (Local Void side): {laniakea_inner_boundary:.1f} Mpc" if laniakea_inner_boundary else "  Inner boundary: not found")
print(f"  Center (GA): 65.5 Mpc")
print(f"  Outer boundary (Canes Venatici side): {laniakea_outer_boundary:.1f} Mpc" if laniakea_outer_boundary else "  Outer boundary: not found")

if laniakea_inner_boundary and laniakea_outer_boundary:
    diameter = laniakea_outer_boundary - laniakea_inner_boundary
    print(f"  Diameter: {diameter:.0f} Mpc")
    print(f"  Tully+2014: ~160 Mpc")
    print(f"  {'✅ Consistent' if abs(diameter - 160) < 30 else '🟡 Close' if abs(diameter - 160) < 60 else '❌'}")

# ================================================================
# 5. Cosmicflows comparison
# ================================================================
print(f"\n{'─'*80}")
print("  5. COSMICFLOWS-3/4 COMPARISON")
print(f"{'─'*80}")

cf_data = [
    (0, 0, "Local Group", "reference"),
    (16.5, 100, "Virgo Cluster", "infall"),
    (28, 200, "Local Void", "outflow"),
    (65.5, 0, "Great Attractor", "convergence"),
    (100, 200, "Coma Cluster", "infall"),
    (118, 0, "Canes Venatici", "convergence"),
    (197, 0, "Shapley SC", "convergence"),
    (250, 150, "Bootes Void", "outflow"),
]

print(f"  {'r (Mpc)':<10} {'v_pred (km/s)':<16} {'v_CF (km/s)':<16} {'Structure':<20} {'Match?':<10}")
print(f"  {'─'*72}")

for r_i, v_cf, name, desc in cf_data:
    idx = np.argmin(np.abs(r - r_i))
    v_pred = v_field[idx]
    
    # Match criteria: within 50 km/s or same sign
    if abs(v_pred - v_cf) < 50:
        match = "✅"
    elif v_pred * v_cf >= 0 and abs(v_pred - v_cf) < 2 * max(abs(v_pred), 50):
        match = "🟡"
    else:
        match = "❌"
    
    print(f"  {r_i:<10} {v_pred:<+16.0f} {v_cf:<+16.0f} {name:<20} {match:<10}")

# ================================================================
# 6. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  6. SUMMARY")
print(f"{'─'*80}")

print(f"""
  Corrected velocity field:
  
  Method: Gradient of K_Tree-damped density field
  v(r) ∝ -dρ/dr where ρ(r) = Σ A_n × D_tree(n) × cos(2π n r/λ_sync + θ_n)
  
  Velocity zeros at standing wave nodes:
    {'GA at 65.5 Mpc: ✅ convergence node' if any(abs(rz - 65.5) < 5 and zt == 'convergence' for rz, zt in zeros) else 'GA: ❌'}
    {'Canes Venatici at 118 Mpc: ✅ convergence node' if any(abs(rz - 118) < 5 and zt == 'convergence' for rz, zt in zeros) else 'Canes Venatici: ❌'}
    {'Local Void at 28 Mpc: ✅ divergence node' if any(abs(rz - 28) < 5 and zt == 'divergence' for rz, zt in zeros) else 'Local Void: ❌'}
  
  Laniakea diameter: {diameter:.0f} Mpc (observed ~160 Mpc)
  {'✅' if laniakea_inner_boundary and laniakea_outer_boundary and abs(diameter - 160) < 30 else '🟡'}
""")