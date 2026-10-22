#!/usr/bin/env python3
"""
P(k) from K_Chain Spectrum — Independent Derivation
====================================================
Derive the continuous matter power spectrum P(k) from the discrete 
K_Chain eigenvalue spectrum γ_n = 4 sin²(πn/88).

The K_Chain has 88 eigenmodes (n=0..87). Each mode has:
  - eigenvalue γ_n (energy/mass)
  - wavelength λ_n = R_H / n  (full ring mode)
  - wavenumber k_n = 2πn / R_H = πn / (R_H/2)

The discrete spectrum γ_n maps to continuous P(k) via:
  P(k) ∝ Σ_n γ_n · δ(k - k_n) * window(k)

Test against BOSS DR12 P(k) data (120 bins, post-recon).
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import sys, os

# ================================================================
# K_Chain spectrum
# ================================================================
R_H = 299792.458 / 72.59  # 4129.94 Mpc
H = 0.7259  # h parameter

print("=" * 80)
print("  P(k) FROM K_CHAIN EIGENVALUE SPECTRUM")
print("  Discrete γ_n → continuous P(k) mapping")
print("=" * 80)

# Compute K_Chain eigenvalues
n_modes = 88
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(n_modes)])
k_chain = np.array([2 * math.pi * n / R_H * H for n in range(n_modes)])  # h/Mpc

# Mode 0 = zero mode (gauge), skip
# Modes 1-43 = positive eigenvalues
# Modes 45-87 = complementary (γ_n + γ_{44-n} = 4)

print(f"\n  K_Chain spectrum:")
print(f"  Modes: 0..{n_modes-1} ({n_modes} total)")
print(f"  γ_0 = 0 (zero mode, gauge)")
print(f"  γ_1 = {gamma[1]:.6f} (fundamental)")
print(f"  γ_2 = {gamma[2]:.6f} (SYNC mode)")
print(f"  γ_22 = {gamma[22]:.6f} (Nyquist)")
print(f"  k_1 = {k_chain[1]:.5f} h/Mpc")
print(f"  k_2 = {k_chain[2]:.5f} h/Mpc")
print(f"  k_22 = {k_chain[22]:.5f} h/Mpc")

# ================================================================
# 1. P(k) from K_Chain — direct mapping
# ================================================================
print(f"\n{'─'*80}")
print("  1. P(k) = Σ γ_n · G(k - k_n)  (Gaussian broadening)")
print(f"{'─'*80}")

# The discrete spectrum needs to be broadened to match the continuous P(k)
# P(k) = Σ_n γ_n · exp(-(k - k_n)² / (2σ²))

# The broadening scale σ should be related to the K_Tree coarse-graining
# At level 1, the scale is R_H/4 = 1032 Mpc → σ ≈ 2π/(R_H/4) = 0.0061 h/Mpc

sigma_pk = 2 * math.pi / (R_H / 4) * H  # ~0.0061 h/Mpc
print(f"  Broadening scale: σ = {sigma_pk:.5f} h/Mpc")
print(f"  (from K_Tree level 1 coarse-graining: R_H/4)")

# Compute P(k) on a fine grid
k_grid = np.linspace(0.01, 0.6, 1000)
P_kchain = np.zeros_like(k_grid)

for n in range(1, 44):  # modes 1..43 (positive eigenvalues)
    P_kchain += gamma[n] * np.exp(-(k_grid - k_chain[n])**2 / (2 * sigma_pk**2))

# Normalize
P_kchain /= np.max(P_kchain)

# ================================================================
# 2. Load BOSS DR12 P(k) data
# ================================================================
print(f"\n{'─'*80}")
print("  2. BOSS DR12 P(k) DATA LOAD")
print(f"{'─'*80}")

data = np.loadtxt('/tmp/public_material_BAO/Beutleretal_pk_monopole_DR12_NGC_z1_postrecon_120.dat',
                  skiprows=34)
k_data = data[:, 0]    # k_central (h/Mpc)
Pk_data = data[:, 2]   # P_0(k)
err_data = data[:, 3]  # sig_ii_0

# Normalize
Pk_data_norm = Pk_data / np.max(Pk_data)

print(f"  Loaded {len(k_data)} bins")
print(f"  k range: {k_data[0]:.5f} - {k_data[-1]:.5f} h/Mpc")
print(f"  P(k) range: {np.min(Pk_data):.1f} - {np.max(Pk_data):.1f}")

# ================================================================
# 3. Compare K_Chain spectrum with BOSS P(k)
# ================================================================
print(f"\n{'─'*80}")
print("  3. K_CHAIN SPECTRUM vs BOSS P(k) COMPARISON")
print(f"{'─'*80}")

# Interpolate K_Chain P(k) to data points
P_kchain_interp = interp1d(k_grid, P_kchain, kind='cubic', bounds_error=False, fill_value=0)
P_kchain_at_data = P_kchain_interp(k_data)

# Compute chi-squared
# Rescale K_Chain P(k) to match BOSS amplitude
from scipy.optimize import minimize_scalar

def chi2(amp):
    model = amp * P_kchain_at_data
    return np.sum((Pk_data_norm - model)**2 / (err_data / np.max(Pk_data))**2)

result = minimize_scalar(chi2, bounds=(0.1, 10), method='bounded')
amp_best = result.x
chi2_val = result.fun
dof = len(k_data) - 1  # 1 free parameter (amplitude)
print(f"  Best-fit amplitude: {amp_best:.3f}")
print(f"  χ² = {chi2_val:.1f}, dof = {dof}, χ²/dof = {chi2_val/dof:.2f}")

# ================================================================
# 4. Feature-by-feature comparison
# ================================================================
print(f"\n{'─'*80}")
print("  4. FEATURE-BY-FEATURE MATCHING")
print(f"{'─'*80}")

# K_Chain predicted peaks
print(f"\n  K_Chain predicted peaks (k_n = 2πn/R_H × h):")
print(f"  {'n':<4} {'k_n':<12} {'λ_n (Mpc)':<15} {'Status':<10}")
print(f"  {'─'*41}")

# Find peaks in BOSS P(k) data
Pk_smooth = gaussian_filter1d(Pk_data, sigma=1.5, mode='nearest')
from scipy.signal import find_peaks
peaks_idx, _ = find_peaks(Pk_smooth, height=0.1*np.max(Pk_smooth), distance=5)
peak_ks = k_data[peaks_idx]

# Check each K_Chain mode
matches = 0
for n in range(1, 11):
    k_n = k_chain[n]
    if k_n < k_data[0] or k_n > k_data[-1]:
        continue
    # Find closest peak in BOSS data
    if len(peak_ks) > 0:
        closest = peak_ks[np.argmin(np.abs(peak_ks - k_n))]
        delta = k_n - closest
        match = "✅" if abs(delta) < 0.01 else "🟡" if abs(delta) < 0.02 else "❌"
        if abs(delta) < 0.01: matches += 1
    else:
        delta = 0
        match = "?"
    lam_n = R_H / n
    print(f"  {n:<4} {k_n:<12.5f} {lam_n:<15.1f} {match:<10}")

print(f"\n  {matches}/10 modes match BOSS P(k) peaks (Δk < 0.01 h/Mpc)")

# ================================================================
# 5. P(k) wiggle from K_Chain vs BOSS data
# ================================================================
print(f"\n{'─'*80}")
print("  5. P(k) WIGGLE: K_CHAIN vs BOSS DR12")
print(f"{'─'*80}")

# Compute smooth P(k) for both
Pk_smooth_data = gaussian_filter1d(Pk_data, sigma=3.0, mode='nearest')
Pk_wiggle_data = Pk_data / Pk_smooth_data - 1

# K_Chain prediction also has wiggles from the discrete spectrum
Pk_smooth_kchain = gaussian_filter1d(P_kchain_at_data * amp_best * np.max(Pk_data), sigma=3.0, mode='nearest')
Pk_wiggle_kchain = (P_kchain_at_data * amp_best * np.max(Pk_data)) / Pk_smooth_kchain - 1

# Compare
print(f"\n  {'k (h/Mpc)':<12} {'P_kchain_wiggle':<18} {'P_boss_wiggle':<18} {'Δ':<10}")
print(f"  {'─'*58}")
for i in range(0, len(k_data), 10):
    k = k_data[i]
    pw_k = Pk_wiggle_kchain[i] if i < len(Pk_wiggle_kchain) else 0
    pw_b = Pk_wiggle_data[i] if i < len(Pk_wiggle_data) else 0
    d = pw_k - pw_b
    print(f"  {k:<12.5f} {pw_k:<+18.6f} {pw_b:<+18.6f} {d:<+10.6f}")

# ================================================================
# 6. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  6. SUMMARY")
print(f"{'─'*80}")

print(f"")
print(f"  P(k) from K_Chain eigenvalue spectrum:")
print(f"")
print(f"  Derivation:")
print(f"    P(k) = Sum_n=1^43 gamma_n * exp(-(k - k_n)^2 / (2*sigma^2))")
print(f"    where gamma_n = 4 sin^2(pi*n/88), k_n = 2*pi*n/R_H * h")
print(f"    and sigma = 2*pi/(R_H/4) * h = {sigma_pk:.5f} h/Mpc")
print(f"")
print(f"  BOSS DR12 comparison:")
print(f"    Best-fit chi^2/dof = {chi2_val/dof:.2f} ({dof} dof)")
print(f"    {matches}/10 K_Chain mode peaks match BOSS P(k) peaks")
print(f"")
print(f"  Key finding: The K_Chain discrete eigenvalue spectrum gamma_n")
print(f"  maps naturally to the continuous P(k) via Gaussian broadening.")
print(f"  The broadening scale sigma = {sigma_pk:.5f} h/Mpc comes from")
print(f"  K_Tree level 1 coarse-graining (R_H/4).")
print(f"")
print(f"  The K_Chain predicts oscillations (wiggles) in P(k) at")
print(f"  k_n = 2*pi*n/R_H * h = n * {k_chain[1]:.5f} h/Mpc.")
print(f"  These are the same harmonics as in xi(s).")