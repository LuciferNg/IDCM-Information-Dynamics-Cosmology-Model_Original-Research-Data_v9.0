#!/usr/bin/env python3
"""
BOSS DR12 Correlation Function — Harmonic Peak Analysis
========================================================
Use Ross+2016 BOSS DR12 ξ(s) post-reconstruction data.
Test for subdominant harmonic peaks at λ_sync/n for n=2,3,4,...
"""
import math, zipfile, numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d

# ===== IDCM params =====
H0 = 72.59
h = 0.676
R_H = 299792.458 / H0
lambda_sync = 2 * math.pi * R_H / 88  # Mpc
bao_pred = lambda_sync / 2  # Mpc

print("=" * 70)
print("BOSS DR12 ξ(s) CORRELATION FUNCTION — HARMONIC ANALYSIS")
print("=" * 70)
print(f"\nIDCM:")
print(f"  λ_sync = {lambda_sync:.1f} Mpc = {lambda_sync/h:.1f} h⁻¹ Mpc")
print(f"  BAO = λ_sync/2 = {bao_pred:.1f} Mpc = {bao_pred/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/3 = {lambda_sync/3:.1f} Mpc = {lambda_sync/3/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/4 = {lambda_sync/4:.1f} Mpc = {lambda_sync/4/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/5 = {lambda_sync/5:.1f} Mpc = {lambda_sync/5/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/6 = {lambda_sync/6:.1f} Mpc = {lambda_sync/6/h:.1f} h⁻¹ Mpc")

# ===== Load Ross+2016 BOSS DR12 correlation function =====
z = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s, xi, err = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        s.append(float(parts[0]))
        xi.append(float(parts[1]))
        err.append(float(parts[2]))

s = np.array(s); xi = np.array(xi); err = np.array(err)
print(f"\nData: {len(s)} bins, s = {s[0]:.0f}–{s[-1]:.0f} h⁻¹ Mpc")

# ===== Harmonic markers =====
print("\n" + "="*70)
print("HARMONIC MARKERS ON ξ(s)")
print("="*70)
print(f"{'Harmonic':<15} {'λ (h⁻¹ Mpc)':<18} {'ξ(s) at λ':<15} {'S/N':<10}")
print("-"*58)
for n in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
    lam = lambda_sync / n / h  # h⁻¹ Mpc
    nearest = np.argmin(np.abs(s - lam))
    sn = xi[nearest] / err[nearest] if err[nearest] > 0 else 0
    label = f"λ_sync/{n}"
    if n == 2: label += " ← BAO"
    marker = "✅" if abs(sn) > 2 else "⚠️" if abs(sn) > 1 else "·"
    print(f"{label:<15} {lam:<18.2f} {xi[nearest]:<+15.6f} {sn:<+10.2f} {marker}")

# ===== Find ALL peaks in ξ(s) =====
print("\n" + "="*70)
print("ALL PEAKS IN ξ(s) vs HARMONIC PREDICTION")
print("="*70)
# Smooth with Gaussian
xi_smooth = gaussian_filter1d(xi, sigma=1.5, mode='nearest')
# Find peaks
peaks = []
for i in range(2, len(s)-2):
    if xi_smooth[i] > xi_smooth[i-1] and xi_smooth[i] > xi_smooth[i-2] and \
       xi_smooth[i] > xi_smooth[i+1] and xi_smooth[i] > xi_smooth[i+2]:
        peaks.append((s[i], xi_smooth[i], err[i], i))

print(f"{'s (h⁻¹ Mpc)':<15} {'ξ(s)':<15} {'S/N':<10} {'IDCM n':<12} {'λ_sync/n':<15} {'Match?':<10}")
print("-"*77)
for sp, xip, errp, idx in peaks:
    # Find closest harmonic
    best_n = min(range(2, 15), key=lambda n: abs(sp - lambda_sync/n/h))
    lam_pred = lambda_sync / best_n / h
    diff = abs(sp - lam_pred)
    sn = xip / errp if errp > 0 else 0
    match = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
    label = f"λ_sync/{best_n}"
    if best_n == 2: label += " ← BAO"
    if sn > 1:  # Only show significant peaks
        print(f"{sp:<15.1f} {xip:<+15.6f} {sn:<+10.2f} n={best_n:<8} {label:<15} {match:<10}")

# ===== Interpolated harmonic comparison =====
print("\n" + "="*70)
print("INTERPOLATED ξ(s) AT HARMONIC POSITIONS")
print("="*70)
# Interpolate ξ(s) to get values at exact harmonic positions
xi_interp = interp1d(s, xi, kind='cubic', bounds_error=False, fill_value=0)
print(f"{'Harmonic':<15} {'s (h⁻¹ Mpc)':<15} {'ξ(s) interp':<15} {'± err':<15}")
print("-"*60)
for n in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
    lam = lambda_sync / n / h
    nearest = np.argmin(np.abs(s - lam))
    xi_val = xi_interp(lam)
    err_val = err[nearest]
    label = f"λ_sync/{n}"
    if n == 2: label += " ← BAO"
    print(f"{label:<15} {lam:<15.2f} {xi_val:<+15.6f} ± {err_val:<.4f}")

# ===== Summary =====
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"""
IDCM harmonic series:
  λ_sync/{2} = BAO = {lambda_sync/2:.1f} Mpc = {lambda_sync/2/h:.1f} h⁻¹ Mpc
  λ_sync/{3} = {lambda_sync/3:.1f} Mpc = {lambda_sync/3/h:.1f} h⁻¹ Mpc
  λ_sync/{4} = {lambda_sync/4:.1f} Mpc = {lambda_sync/4/h:.1f} h⁻¹ Mpc
  λ_sync/{5} = {lambda_sync/5:.1f} Mpc = {lambda_sync/5/h:.1f} h⁻¹ Mpc
  λ_sync/{6} = {lambda_sync/6:.1f} Mpc = {lambda_sync/6/h:.1f} h⁻¹ Mpc

BOSS DR12 (Ross+2016) ξ(s) z=0.2-0.5 post-recon:
  Main BAO peak at ~105 h⁻¹ Mpc
  Subdominant features at ~55, ~75, ~130 h⁻¹ Mpc

Key test: do the subdominant peaks match λ_sync/n?
""")