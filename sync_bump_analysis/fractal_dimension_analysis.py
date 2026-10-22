#!/usr/bin/env python3
"""Compute fractal dimension D of CEERS DR1 redshift distribution at aliasing points."""

import gzip, io, json, math
import numpy as np
from astropy.io import fits

# Path
path = '/home/wsl/IDCM/sync_bump_analysis/ceers_dr1_catalog.fits.gz'

# Read catalog
with gzip.open(path, 'rb') as f:
    with fits.open(io.BytesIO(f.read())) as hdul:
        data = hdul[1].data

print(f"Number of galaxies: {len(data)}")
print(f"Column names: {list(data.columns.names)}")

# Extract redshift
z = data['LP_Z_MED']
print(f"z range: {z.min():.4f} to {z.max():.4f}")
print(f"z median: {np.median(z):.4f}")
print(f"z < 0: {(z < 0).sum()} galaxies with z < 0")
print(f"z > 15: {(z > 15).sum()} galaxies with z > 15")

# Valid redshifts (z >= 0)
z_valid = z[z >= 0]
print(f"Valid z (>=0): {len(z_valid)} galaxies")

# ============================================================
# Fibonacci aliasing series
# ============================================================
fib_aliasing = [0.5, 0.8, 1.3, 2.1, 3.4, 5.5, 8.9]
# IDCM aliasing points
idcm_aliasing = [5.6, 6.9, 7.7, 8.2, 8.5, 8.9, 9.2, 9.5, 10.0, 13.5, 14.0]

delta = 0.3  # window half-width

def count_around(redshifts, center, half_width=0.3):
    """Count galaxies within [center - half_width, center + half_width]"""
    mask = (redshifts >= center - half_width) & (redshifts <= center + half_width)
    return mask.sum()

def count_above(redshifts, threshold):
    """Count galaxies with z >= threshold"""
    return (redshifts >= threshold).sum()

print("\n" + "="*70)
print("FRACTAL DIMENSION ANALYSIS - CEERS DR1")
print("="*70)

# ============================================================
# Fibonacci aliasing points
# ============================================================
print("\n--- Fibonacci Aliasing Series (z = F_n/10) ---")
print(f"{'Point':>8}  {'Count':>8}  {'Cumul':>8}  {'log z':>8}  {'log N(>z)':>10}")
print("-"*55)

fib_points = []
fib_cumul = []
fib_logz = []
fib_logc = []

for pt in fib_aliasing:
    cnt = count_around(z_valid, pt, delta)
    cum = count_above(z_valid, pt)
    logz = math.log10(pt)
    logc = math.log10(cum) if cum > 0 else float('nan')
    fib_points.append(pt)
    fib_cumul.append(cum)
    fib_logz.append(logz)
    fib_logc.append(logc)
    print(f"{pt:>8.1f}  {cnt:>8}  {cum:>8}  {logz:>8.4f}  {logc:>10.4f}")

# Linear fit to log N(>z) = D * log z + const
A = np.vstack([fib_logz, np.ones_like(fib_logz)]).T
valid = ~np.isnan(fib_logc)
A_v = A[valid]
y_v = np.array(fib_logc)[valid]
coeffs, residuals, rank, sv = np.linalg.lstsq(A_v, y_v, rcond=None)
D_fib = coeffs[0]
const_fib = coeffs[1]
print(f"\nPower-law fit: log N(>z) = {D_fib:.4f} * log z + {const_fib:.4f}")
print(f"Fractal dimension D (Fibonacci) = {D_fib:.4f}")

# Compute predicted counts and residuals
predicted_logc = D_fib * np.array(fib_logz) + const_fib
predicted_cumul = 10**predicted_logc
print(f"\nPredicted vs actual:")
for i, pt in enumerate(fib_points):
    r = fib_cumul[i]/predicted_cumul[i] if predicted_cumul[i] > 0 else 0
    print(f"  z={pt:.1f}: N(>z)={fib_cumul[i]}, predicted={predicted_cumul[i]:.0f}, ratio={r:.4f}")

# ============================================================
# φ ratio check between consecutive Fibonacci points
# ============================================================
phi = (1 + math.sqrt(5)) / 2  # 1.618...

print("\n--- φ Ratio Check on Cumulative Counts (Fibonacci) ---")
print(f"{'From':>6}  {'To':>6}  {'N(>z1)':>8}  {'N(>z2)':>8}  {'Ratio':>8}  {'φ':>6}  {'Diff%':>8}")
print("-"*56)

for i in range(len(fib_points)-1):
    z1 = fib_points[i]
    z2 = fib_points[i+1]
    n1 = fib_cumul[i]
    n2 = fib_cumul[i+1]
    if n2 > 0:
        ratio = n1 / n2
        diff_pct = (ratio - phi) / phi * 100
        print(f"{z1:>6.1f}  {z2:>6.1f}  {n1:>8}  {n2:>8}  {ratio:>8.4f}  {phi:>6.4f}  {diff_pct:>+8.2f}%")

# ============================================================
# IDCM aliasing points
# ============================================================
print("\n\n--- IDCM Aliasing Points ---")
print(f"{'Point':>8}  {'Count':>8}  {'Cumul':>8}  {'log z':>8}  {'log N(>z)':>10}")
print("-"*55)

idcm_points = []
idcm_cumul = []
idcm_logz = []
idcm_logc = []

for pt in idcm_aliasing:
    cnt = count_around(z_valid, pt, delta)
    cum = count_above(z_valid, pt)
    logz = math.log10(pt)
    logc = math.log10(cum) if cum > 0 else float('nan')
    idcm_points.append(pt)
    idcm_cumul.append(cum)
    idcm_logz.append(logz)
    idcm_logc.append(logc)
    print(f"{pt:>8.1f}  {cnt:>8}  {cum:>8}  {logz:>8.4f}  {logc:>10.4f}")

# Fit
A = np.vstack([idcm_logz, np.ones_like(idcm_logz)]).T
valid = ~np.isnan(idcm_logc)
A_v = A[valid]
y_v = np.array(idcm_logc)[valid]
coeffs2, residuals2, rank2, sv2 = np.linalg.lstsq(A_v, y_v, rcond=None)
D_idcm = coeffs2[0]
const_idcm = coeffs2[1]
print(f"\nPower-law fit: log N(>z) = {D_idcm:.4f} * log z + {const_idcm:.4f}")
print(f"Fractal dimension D (IDCM) = {D_idcm:.4f}")

# Predicted
predicted_logc2 = D_idcm * np.array(idcm_logz) + const_idcm
predicted_cumul2 = 10**predicted_logc2
print(f"\nPredicted vs actual:")
for i, pt in enumerate(idcm_points):
    r = idcm_cumul[i]/predicted_cumul2[i] if predicted_cumul2[i] > 0 else 0
    print(f"  z={pt:.1f}: N(>z)={idcm_cumul[i]}, predicted={predicted_cumul2[i]:.0f}, ratio={r:.4f}")

# ============================================================
# φ ratio check between consecutive IDCM points
# ============================================================
print("\n--- φ Ratio Check on Cumulative Counts (IDCM) ---")
print(f"{'From':>6}  {'To':>6}  {'N(>z1)':>8}  {'N(>z2)':>8}  {'Ratio':>8}  {'φ':>6}  {'Diff%':>8}")
print("-"*56)

for i in range(len(idcm_points)-1):
    z1 = idcm_points[i]
    z2 = idcm_points[i+1]
    n1 = idcm_cumul[i]
    n2 = idcm_cumul[i+1]
    if n2 > 0:
        ratio = n1 / n2
        diff_pct = (ratio - phi) / phi * 100
        print(f"{z1:>6.1f}  {z2:>6.1f}  {n1:>8}  {n2:>8}  {ratio:>8.4f}  {phi:>6.4f}  {diff_pct:>+8.2f}%")

# ============================================================
# Also check count-in-window (local density) ratio
# ============================================================
print("\n\n--- φ Ratio Check on Local Counts (Fibonacci, ±0.3 window) ---")
print(f"{'From':>6}  {'To':>6}  {'N(z1)':>8}  {'N(z2)':>8}  {'Ratio':>8}  {'φ':>6}  {'Diff%':>8}")
print("-"*56)

for i in range(len(fib_points)-1):
    z1 = fib_points[i]
    z2 = fib_points[i+1]
    n1 = count_around(z_valid, z1, delta)
    n2 = count_around(z_valid, z2, delta)
    if n2 > 0:
        ratio = n1 / n2
        diff_pct = (ratio - phi) / phi * 100
        print(f"{z1:>6.1f}  {z2:>6.1f}  {n1:>8}  {n2:>8}  {ratio:>8.4f}  {phi:>6.4f}  {diff_pct:>+8.2f}%")

print("\n\n--- φ Ratio Check on Local Counts (IDCM, ±0.3 window) ---")
print(f"{'From':>6}  {'To':>6}  {'N(z1)':>8}  {'N(z2)':>8}  {'Ratio':>8}  {'φ':>6}  {'Diff%':>8}")
print("-"*56)

for i in range(len(idcm_points)-1):
    z1 = idcm_points[i]
    z2 = idcm_points[i+1]
    n1 = count_around(z_valid, z1, delta)
    n2 = count_around(z_valid, z2, delta)
    if n2 > 0:
        ratio = n1 / n2
        diff_pct = (ratio - phi) / phi * 100
        print(f"{z1:>6.1f}  {z2:>6.1f}  {n1:>8}  {n2:>8}  {ratio:>8.4f}  {phi:>6.4f}  {diff_pct:>+8.2f}%")

# ============================================================
# z > 15 check
# ============================================================
print(f"\n\n--- z > 15 Check ---")
print(f"Galaxies with z > 15: {(z > 15).sum()}")
print(f"Galaxies with z > 15 and z valid: {(z_valid > 15).sum()}")

# ============================================================
# Summary statistics
# ============================================================
print("\n\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Total galaxies: {len(data)}")
print(f"Valid z (>=0): {len(z_valid)}")
print(f"z > 15: {(z > 15).sum()}")
print(f"Fibonacci D: {D_fib:.4f}")
print(f"IDCM D: {D_idcm:.4f}")
print(f"φ: {phi:.6f}")

# Save results
results = {
    "total_galaxies": len(data),
    "valid_redshifts": len(z_valid),
    "z_gt_15": int((z > 15).sum()),
    "fractal_dimension_fibonacci": float(D_fib),
    "fractal_dimension_idcm": float(D_idcm),
    "phi": float(phi),
    "fibonacci_aliasing": [
        {"z": float(p), "n_around": int(count_around(z_valid, p, delta)), "n_cumul": int(c)}
        for p, c in zip(fib_points, fib_cumul)
    ],
    "idcm_aliasing": [
        {"z": float(p), "n_around": int(count_around(z_valid, p, delta)), "n_cumul": int(c)}
        for p, c in zip(idcm_points, idcm_cumul)
    ]
}
with open('/home/wsl/IDCM/sync_bump_analysis/fractal_dimension_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to fractal_dimension_results.json")