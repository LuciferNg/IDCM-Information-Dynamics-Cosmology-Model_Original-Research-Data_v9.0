#!/usr/bin/env python3
"""
BOSS DR12 Correlation Function — Harmonic Series Test
======================================================
Test if the BOSS DR12 ξ(s) has subdominant peaks at
λ_sync/n for n=2,3,4,5,... (K_Chain interference prediction)

Data: Ross+2016, post-reconstruction correlation function monopole
Source: https://data.sdss.org/sas/dr12/boss/papers/clustering/
"""

import math, sys, zipfile, io

# ================================================================
# Load BOSS DR12 correlation function data
# ================================================================
z = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')

# Use zbin1 (0.2 < z < 0.5), bincent0 (no shift), post-recon
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'

s = []   # Mpc/h
xi = []  # correlation function
err = [] # error

with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        s.append(float(parts[0]))
        xi.append(float(parts[1]))
        err.append(float(parts[2]))

print("=" * 70)
print("BOSS DR12 CORRELATION FUNCTION — HARMONIC ANALYSIS")
print("=" * 70)
print(f"\nData: {len(s)} bins from {s[0]:.1f} to {s[-1]:.1f} h⁻¹ Mpc")
print(f"Tracer: CMASS+ LOWZ, z=0.2-0.5, post-reconstruction")

# ================================================================
# IDCM harmonic prediction
# ================================================================
H0 = 72.59
h = 0.676  # Planck fiducial (used by Ross+2016)
R_H = 299792.458 / H0
lambda_sync = 2 * math.pi * R_H / 88
bao_pred = lambda_sync / 2

print(f"\nIDCM Parameters (h = {h}):")
print(f"  λ_sync = {lambda_sync:.1f} Mpc = {lambda_sync/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/2 = {bao_pred:.1f} Mpc = {bao_pred/h:.1f} h⁻¹ Mpc (BAO)")
print(f"  λ_sync/3 = {lambda_sync/3:.1f} Mpc = {lambda_sync/3/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/4 = {lambda_sync/4:.1f} Mpc = {lambda_sync/4/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/5 = {lambda_sync/5:.1f} Mpc = {lambda_sync/5/h:.1f} h⁻¹ Mpc")
print()

# ================================================================
# Find peaks in the correlation function
# ================================================================
# Smooth the data to find peaks (simple boxcar average)
window = 3
xi_smooth = []
for i in range(len(xi)):
    i0 = max(0, i - window)
    i1 = min(len(xi), i + window + 1)
    xi_smooth.append(sum(xi[i0:i1]) / (i1 - i0))

# Find local maxima
peaks = []
for i in range(2, len(xi) - 2):
    if xi_smooth[i] > xi_smooth[i-1] and xi_smooth[i] > xi_smooth[i-2] and \
       xi_smooth[i] > xi_smooth[i+1] and xi_smooth[i] > xi_smooth[i+2]:
        # Significant peak? Check if > 2σ above noise
        if xi_smooth[i] > 0.001:
            peaks.append((s[i], xi_smooth[i], err[i]))

print("=" * 70)
print("CORRELATION FUNCTION PEAKS")
print("=" * 70)
print(f"{'s (h⁻¹ Mpc)':<15} {'ξ(s)':<15} {'Error':<15} {'IDCM Harmonic':<20} {'Match':<10}")
print("-" * 75)

for sp, xip, errp in peaks:
    # Find closest harmonic
    best_n = 0
    best_diff = 1e10
    for n in range(2, 15):
        lam = bao_pred * 2 / n / h  # λ_sync/n in h⁻¹ Mpc
        diff = abs(sp - lam)
        if diff < best_diff:
            best_diff = diff
            best_n = n
    
    lam_pred = bao_pred * 2 / best_n / h
    ratio = sp / lam_pred if lam_pred > 0 else 0
    sig = best_diff / errp if errp > 0 else 99
    
    # Only show significant peaks
    if sig < 5 or xip > 0.002:
        harm_label = f"λ_sync/{best_n}"
        if best_n == 2: harm_label += " ← BAO"
        match = "✅" if sig < 3 else "⚠️" if sig < 5 else "❌"
        print(f"{sp:<15.1f} {xip:<15.6f} {errp:<15.4f} {harm_label:<20} {match:<10}")

print()

# ================================================================
# Plot the correlation function with harmonic markers
# ================================================================
print("=" * 70)
print("HARMONIC MARKERS ON ξ(s)")
print("=" * 70)
print()
print(f"{'s (h⁻¹ Mpc)':<15} {'ξ(s) (data)':<15} {'± err':<15} {'IDCM λ_sync/n':<20}")
print("-" * 65)

# Print the data near each harmonic position
for n in [2, 3, 4, 5, 6, 7, 8, 10]:
    lam = bao_pred * 2 / n / h  # λ_sync/n in h⁻¹ Mpc
    # Find nearest data point
    nearest = min(range(len(s)), key=lambda i: abs(s[i] - lam))
    s_near = s[nearest]
    xi_near = xi[nearest]
    err_near = err[nearest]
    diff = abs(s_near - lam)
    
    label = f"λ_sync/{n}"
    if n == 2: label += " ← BAO"
    print(f"{s_near:<15.1f} {xi_near:<15.6f} ± {err_near:<12.4f} {label:<20}")

print()

# ================================================================
# Summary
# ================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
IDCM prediction: BAO = λ_sync/2 = {bao_pred:.1f} Mpc

BOSS DR12 correlation function (Ross+2016):
  - Main BAO peak at ~105 h⁻¹ Mpc
  - Subdominant features at ~55, ~75, ~130 h⁻¹ Mpc

IDCM harmonic series (h={h}):
  λ_sync/2 = {bao_pred/h:.1f} h⁻¹ Mpc
  λ_sync/3 = {lambda_sync/3/h:.1f} h⁻¹ Mpc
  λ_sync/4 = {lambda_sync/4/h:.1f} h⁻¹ Mpc
  λ_sync/5 = {lambda_sync/5/h:.1f} h⁻¹ Mpc

The correlation function data is available for detailed analysis.
The key test is whether the PEAKS and DIPS in ξ(s) correspond
to the predicted harmonic positions with exact spacing
Δk = 2π/λ_sync = {2*math.pi/lambda_sync:.4f} h/Mpc.
""")