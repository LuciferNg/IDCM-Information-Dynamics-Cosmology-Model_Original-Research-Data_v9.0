#!/usr/bin/env python3
"""
BOSS DR12 Power Spectrum — BAO Wiggle Harmonic Analysis
========================================================
Test if the BAO wiggles in P(k) have exact harmonic spacing
Δk = 2π/λ_sync = 0.0213 h/Mpc (K_Chain interference prediction)

Data: Beutler+2016, BOSS DR12 combined, post-reconstruction
Source: https://data.sdss.org/sas/dr12/boss/papers/clustering/
"""

import math, sys, tarfile, numpy as np

# ================================================================
# IDCM parameters
# ================================================================
H0 = 72.59
h = 0.676  # Planck fiducial (BOSS uses similar)
R_H = 299792.458 / H0
lambda_sync = 2 * math.pi * R_H / 88  # Mpc
bao_pred = lambda_sync / 2

dk_pred = 2 * math.pi / lambda_sync * h  # h/Mpc (fundamental spacing)

print("=" * 70)
print("BOSS DR12 POWER SPECTRUM — BAO WIGGLE HARMONIC ANALYSIS")
print("=" * 70)
print(f"\nIDCM Parameters:")
print(f"  λ_sync = {lambda_sync:.1f} Mpc")
print(f"  λ_sync/2 = {bao_pred:.1f} Mpc (BAO)")
print(f"  Δk = 2π/λ_sync × h = {dk_pred:.4f} h/Mpc (fundamental spacing)")
print(f"  BAO at k = 2·Δk = {2*dk_pred:.4f} h/Mpc")
print(f"  λ_sync/3 at k = 3·Δk = {3*dk_pred:.4f} h/Mpc")
print(f"  λ_sync/4 at k = 4·Δk = {4*dk_pred:.4f} h/Mpc")
print()

# ================================================================
# Load BOSS DR12 power spectrum
# ================================================================
t = tarfile.open('/home/wsl/IDCM/sync_bump_analysis/beutler_dr12_powspec.tar.gz')

# Load all redshift bins/NGC+SGC, post-recon monopole
all_k, all_P, all_err = [], [], []
for zbin in ['z1', 'z2', 'z3']:
    for region in ['NGC', 'SGC']:
        fname = f'public_material_BAO/Beutleretal_pk_monopole_DR12_{region}_{zbin}_postrecon_120.dat'
        if fname not in t.getnames():
            continue
        data = t.extractfile(fname).read().decode('latin-1')
        lines = data.strip().split('\n')
        # Find the data section (after the last ### header line)
        data_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('###'):
                data_start = i + 1
        # The data is after the last ### header
        for i in range(data_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 4:
                try:
                    k = float(parts[1])
                    P = float(parts[2])
                    err = float(parts[3])
                    all_k.append(k)
                    all_P.append(P)
                    all_err.append(err)
                except ValueError:
                    continue

# Convert to numpy arrays and average overlapping k values
k_arr = np.array(all_k)
P_arr = np.array(all_P)
err_arr = np.array(all_err)

# Average overlapping k values (from different z-bins and regions)
unique_k = np.unique(k_arr)
P_avg = np.array([np.mean(P_arr[k_arr == k]) for k in unique_k])
err_avg = np.array([np.sqrt(np.mean(err_arr[k_arr == k]**2)) for k in unique_k])

k = unique_k
P = P_avg
err = err_avg

print(f"Loaded {len(all_k)} raw data points, averaged to {len(k)} unique k values")
print(f"k range: {k.min():.4f} to {k.max():.4f} h/Mpc")
print()

# ================================================================
# Compute the BAO wiggle component (P/P_smooth)
# ================================================================
# Smooth the power spectrum with a wide Gaussian kernel
# to isolate the wiggles
from scipy.ndimage import gaussian_filter1d

# Sort by k
idx = np.argsort(k_arr)
k = k_arr[idx]
P = P_arr[idx]
err = err_arr[idx]

# Log-transform for better smoothing
logP = np.log(P)
# Smooth with sigma=5 (in bins) to get the broadband shape
P_smooth = np.exp(gaussian_filter1d(logP, sigma=5, mode='nearest'))

# Wiggle = P/P_smooth - 1
wiggle = P / P_smooth - 1

print("=" * 70)
print("BAO WIGGLE ANALYSIS")
print("=" * 70)
print(f"\n{'k (h/Mpc)':<15} {'P(k) (data)':<18} {'P_smooth':<18} {'Wiggle':<15}")
print("-" * 66)

# Print wiggles in the BAO region (k = 0.02-0.3 h/Mpc)
for i in range(len(k)):
    if 0.02 <= k[i] <= 0.30:
        wiggle_str = f"{wiggle[i]:+.4f}"
        print(f"{k[i]:<15.4f} {P[i]:<18.1f} {P_smooth[i]:<18.1f} {wiggle_str:<15}")

print()

# ================================================================
# Find wiggle peaks in k-space
# ================================================================
print("=" * 70)
print("WIGGLE PEAKS vs HARMONIC PREDICTION")
print("=" * 70)
print(f"\nIDCM predicts BAO wiggles at k = n·Δk, where Δk = {dk_pred:.4f} h/Mpc")
print()

# Find zero-crossings of the wiggle (where peaks/dips occur)
# Find wiggle maxima in the BAO region
peak_ks = []
for i in range(2, len(k) - 2):
    if 0.02 <= k[i] <= 0.30:
        if wiggle[i] > wiggle[i-1] and wiggle[i] > wiggle[i-2] and \
           wiggle[i] > wiggle[i+1] and wiggle[i] > wiggle[i+2]:
            if wiggle[i] > 0.01:  # significant
                peak_ks.append(k[i])

print(f"Found {len(peak_ks)} wiggle peaks in k=[0.02, 0.30] h/Mpc")
print()

print(f"{'k_peak (h/Mpc)':<18} {'IDCM n·Δk':<18} {'Δk spacing':<15} {'Harmonic n':<12} {'Match?':<10}")
print("-" * 73)

for kp in peak_ks:
    # Find closest harmonic
    best_n = 0
    best_diff = 1e10
    for n in range(2, 16):
        pred = n * dk_pred
        diff = abs(kp - pred)
        if diff < best_diff:
            best_diff = diff
            best_n = n
    
    pred = best_n * dk_pred
    dk = kp - (peak_ks[peak_ks.index(kp) - 1] if peak_ks.index(kp) > 0 else 0)
    match = "✅" if best_diff < 0.005 else "⚠️" if best_diff < 0.01 else "❌"
    harm_label = f"n={best_n}"
    if best_n == 2: harm_label += " ← BAO"
    print(f"{kp:<18.4f} {pred:<18.4f} {dk:<15.4f} {harm_label:<12} {match:<10}")

print()

# ================================================================
# Statistical test: Are the wiggles equally spaced?
# ================================================================
print("=" * 70)
print("HARMONIC SPACING TEST")
print("=" * 70)
print()
if len(peak_ks) >= 3:
    spacings = [peak_ks[i+1] - peak_ks[i] for i in range(len(peak_ks)-1)]
    mean_dk = np.mean(spacings)
    std_dk = np.std(spacings)
    print(f"Measured mean Δk = {mean_dk:.4f} ± {std_dk:.4f} h/Mpc")
    print(f"IDCM prediction: Δk = {dk_pred:.4f} h/Mpc")
    print(f"Deviation: {abs(mean_dk - dk_pred):.4f} h/Mpc ({abs(mean_dk/dk_pred - 1)*100:.1f}%)")
    print()
    if abs(mean_dk - dk_pred) < std_dk:
        print("✅ Consistent with IDCM harmonic spacing")
    else:
        print("⚠️  Deviation > 1σ — needs further investigation")
else:
    print(f"Need at least 3 peaks to test spacing (found {len(peak_ks)})")
    print("Monochromatic test: check if peaks match n·Δk")

print()

# ================================================================
# Summary
# ================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
IDCM prediction: BAO wiggles in P(k) at k = n·Δk, Δk = {dk_pred:.4f} h/Mpc

BOSS DR12 power spectrum (Beutler+2016):
  - Post-reconstruction monopole, 3 redshift bins, NGC+SGC
  - k range: 0.015-0.6 h/Mpc
  - BAO wiggles visible in k = 0.02-0.30 h/Mpc

The key test: the wiggles should be EQUALLY SPACED in k-space
with spacing Δk = {dk_pred:.4f} h/Mpc.

This is a falsifiable prediction of the K_Chain interference model.
""")


# ================================================================
# Also save the wiggle data for plotting
# ================================================================
output = []
for i in range(len(k)):
    if 0.01 <= k[i] <= 0.40:
        output.append(f"{k[i]:.6f} {P[i]:.1f} {P_smooth[i]:.1f} {wiggle[i]:.6f}\n")

output_path = '/home/wsl/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt'
with open(output_path, 'w') as f:
    f.write('# k (h/Mpc)  P(k)  P_smooth  Wiggle\n')
    f.writelines(output)
print(f"Wiggle data saved to: {output_path}")