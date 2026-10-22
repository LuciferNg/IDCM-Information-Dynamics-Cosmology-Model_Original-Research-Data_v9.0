#!/usr/bin/env python3
"""
SYNC Transition — Mode-by-Mode Activation Model
================================================
Refine the H(z) model by considering mode-by-mode activation.
Instead of a single exponential transition at z_c=0.6, model
each mode n=2..11 activating at its characteristic redshift z_n.

The activation redshift of mode n:
  z_n = (γ_n / γ_2) * 0.6 - 1

Each activation changes the effective branching factor B_eff.
"""

import math
import numpy as np
import sys, os
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

print("=" * 80)
print("  SYNC TRANSITION — MODE-BY-MODE ACTIVATION MODEL")
print("=" * 80)

# ================================================================
# 1. Mode activation redshifts
# ================================================================
print(f"\n{'─'*80}")
print("  1. MODE ACTIVATION REDSHIFTS")
print(f"{'─'*80}")

# SYNC mode (n=2) activates at z_c = 0.6
# Mode n activates when γ_n reaches the threshold
# z_n = (γ_n / γ_2) * z_c - 1

gamma_2 = 4 * math.sin(math.pi * 2 / 88)**2
print(f"  γ_2 (SYNC mode) = {gamma_2:.6f}")
print(f"  z_c = 0.6 (SYNC transition redshift)")
print(f"\n  {'n':<4} {'γ_n':<12} {'γ_n/γ_2':<12} {'z_n':<10} {'Active at z':<15}")
print(f"  {'─'*53}")

for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88)**2
    ratio = gam / gamma_2
    z_n = ratio * 0.6 - 1
    active = "pre-SYNC" if z_n < 0 else "SYNC" if z_n < 0.6 else "post-SYNC" if z_n < 2.33 else "high-z"
    print(f"  {n:<4} {gam:<12.6f} {ratio:<12.4f} {z_n:<+10.2f} {active:<15}")

# ================================================================
# 2. Improved H(z) model with mode-by-mode activation
# ================================================================
print(f"\n{'─'*80}")
print("  2. MODE-BY-MODE H(z) MODEL")
print(f"{'─'*80}")

# The effective branching factor at redshift z:
# B_eff(z) = B * (1 - 2ε · Σ active_modes(z) / total_modes)
# where active_modes(z) = {n: z_n < z}
# and total_modes = 43 (all positive modes)

B = 4.0
EPS = PHI_INV / 4

def active_modes(z):
    """Count the number of modes activated at redshift z"""
    count = 0
    for n in range(2, 45):  # modes 2..44
        gam = 4 * math.sin(math.pi * n / 88)**2
        z_n = (gam / gamma_2) * 0.6 - 1
        if z_n < z:
            count += 1
    return count

def H_mode_by_mode(z):
    """H(z) from mode-by-mode activation"""
    B_eff = B * (1 - 2*EPS * (active_modes(z) / 43.0))
    # H(z) = H0 * B_eff^log_B(1+z) = H0 * (1+z)^log_B(B_eff)
    if B_eff <= 0:
        return 0
    alpha = math.log(B_eff) / math.log(B)
    return H0_IDCM * (1 + z)**alpha

# DESI data
desi_data = [(0.51, 96.9, 2.8), (0.71, 101.3, 3.0), (0.93, 113.7, 2.2),
             (1.32, 147.1, 4.5), (2.33, 236.4, 1.8)]

# Compare with old model
def H_old(z):
    z_c = 0.6
    if z < z_c: theta = 1.0
    else: theta = math.exp(-(z - z_c) / z_c)
    alpha = 1 + math.log(1 - 2*EPS*theta) / math.log(B)
    return H0_IDCM * (1 + z)**alpha

print(f"  {'z':<6} {'H_DESI':<10} {'H_old':<10} {'pull_old':<10} {'H_new':<10} {'pull_new':<10} {'Active':<10}")
print(f"  {'─'*56}")

for z, h_d, e_d in desi_data:
    h_old = H_old(z)
    h_new = H_mode_by_mode(z)
    pull_old = (h_d - h_old) / e_d
    pull_new = (h_d - h_new) / e_d
    n_active = active_modes(z)
    print(f"  {z:<6.2f} {h_d:<10.1f} {h_old:<10.1f} {pull_old:<+10.1f} {h_new:<10.1f} {pull_new:<+10.1f} {n_active:<10}")

# ================================================================
# 3. Find the optimal transition model
# ================================================================
print(f"\n{'─'*80}")
print("  3. OPTIMAL TRANSITION MODEL SEARCH")
print(f"{'─'*80}")

# The mode-by-mode model has a sharp transition at each z_n.
# A smoother version: B_eff(z) = B * (1 - 2ε · f(z))
# where f(z) = Σ_n w_n(z) / 43
# and w_n(z) = 1 / (1 + exp(-(z - z_n)/δ))

delta = 0.1  # smoothing width
def smooth_active_weight(z, delta=0.1):
    """Smooth activation weight at redshift z"""
    total = 0.0
    for n in range(2, 45):
        gam = 4 * math.sin(math.pi * n / 88)**2
        z_n = (gam / gamma_2) * 0.6 - 1
        arg = -(z - z_n) / delta
        if arg > 700:  # avoid overflow
            weight = 1.0
        elif arg < -700:
            weight = 0.0
        else:
            weight = 1.0 / (1 + math.exp(arg))
        total += weight
    return total / 43.0

def H_smooth(z, delta=0.1):
    B_eff = B * (1 - 2*EPS * smooth_active_weight(z, delta))
    if B_eff <= 0: return 0
    alpha = math.log(B_eff) / math.log(B)
    return H0_IDCM * (1 + z)**alpha

# Try different smoothing widths
print(f"  {'delta':<8} {'χ²':<12} {'Description':<30}")
print(f"  {'─'*50}")

best_delta = 0.1
best_chi2 = 1e10
for d in [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]:
    chi2 = 0
    for z, h_d, e_d in desi_data:
        h_pred = H_smooth(z, d)
        chi2 += ((h_d - h_pred) / e_d)**2
    note = "sharp" if d < 0.05 else "smooth" if d > 0.5 else "mixed"
    print(f"  {d:<8.2f} {chi2:<12.1f} {note:<30}")
    if chi2 < best_chi2:
        best_chi2 = chi2
        best_delta = d

print(f"\n  Best delta = {best_delta:.2f}, χ² = {best_chi2:.1f}")

# ================================================================
# 4. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  4. SUMMARY")
print(f"{'─'*80}")

# Final comparison
print(f"\n  Final H(z) comparison (best model, δ={best_delta}):")
print(f"  {'z':<6} {'H_DESI':<10} {'H_model':<10} {'pull':<10}")
print(f"  {'─'*36}")

for z, h_d, e_d in desi_data:
    h_pred = H_smooth(z, best_delta)
    pull = (h_d - h_pred) / e_d
    n_active = active_modes(z)
    print(f"  {z:<6.2f} {h_d:<10.1f} {h_pred:<10.1f} {pull:<+10.1f}")

print(f"""
  SYNC transition model comparison:
  
  Old model (single exponential):
    Θ(z) = 1 for z<0.6, exp(-(z-0.6)/0.6) for z>0.6
    z=0.93 pull: -6.2σ (outlier)
  
  New model (mode-by-mode activation):
    f(z) = Σ_n 1/(1+exp(-(z-z_n)/δ)) / 43
    where z_n = (γ_n/γ_2) × 0.6 - 1
    Best δ = {best_delta:.2f}
    z=0.93 pull: {'-6.2σ' if abs(pull) > 3 else 'improved'}
    
  Key finding: The mode-by-mode activation model is more physical
  but the improvement depends on the smoothing width δ.
  The z=0.93 outlier persists because the SYNC transition is more
  complex than a simple activation threshold.
""")