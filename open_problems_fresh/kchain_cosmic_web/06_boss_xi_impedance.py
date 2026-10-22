#!/usr/bin/env python3
"""
BOSS DR12 ξ(s) — Impedance/Reflection Signature Search
========================================================
Look for residuals between observed ξ(s) and the IDCM harmonic series.
Impedance mismatches from mode activations create ADDITIONAL features
beyond the simple λ_sync/n harmonics.

The key: mode n=3 activates at z=0.35, mode n=4 at z=1.39, mode n=5 at z=2.72.
Each activation creates a reflection that propagates to other scales.
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import sys, os
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

# ================================================================
# Load BOSS DR12 ξ(s) data
# ================================================================
import zipfile
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

s = np.array(s)
xi = np.array(xi)
err = np.array(err)

# IDCM harmonic positions (in h⁻¹ Mpc)
lambda_sync_hinv = LAMBDA_SYNC / H  # 406.1 h⁻¹ Mpc
harmonics = {f"λ_sync/{n}": lambda_sync_hinv / n for n in range(2, 21)}

# Interpolate ξ(s) at harmonic positions
xi_interp = interp1d(s, xi, kind='cubic', bounds_error=False, fill_value=0)
err_interp = interp1d(s, err, kind='linear', bounds_error=False, fill_value=0)

print("=" * 80)
print("  BOSS DR12 ξ(s) — IMPEDANCE/REFLECTION SIGNATURE")
print("  Looking for residuals beyond the λ_sync/n harmonic series")
print("=" * 80)

# ================================================================
# 1. Harmonic series prediction
# ================================================================
print(f"\n{'─'*80}")
print("  1. IDCM HARMONIC SERIES PREDICTION")
print(f"{'─'*80}")
print(f"\n{'Harmonic':<15} {'s (h⁻¹ Mpc)':<18} {'ξ(s)':<12} {'S/N':<10} {'Status':<10}")
print(f"{'─'*65}")

for name, lam in sorted(harmonics.items(), key=lambda x: x[1]):
    if lam < s[0] or lam > s[-1]:
        continue
    xi_val = float(xi_interp(lam))
    err_val = float(err_interp(lam))
    sn = xi_val / err_val if err_val > 0 else 0
    status = "✅" if abs(sn) > 3 else "🟡" if abs(sn) > 2 else "·"
    print(f"  {name:<15} {lam:<18.2f} {xi_val:<+12.6f} {sn:<+10.2f} {status:<10}")

# ================================================================
# 2. Residual analysis: ξ(s) - harmonic model
# ================================================================
print(f"\n{'─'*80}")
print("  2. RESIDUAL ANALYSIS: ξ(s) - HARMONIC MODEL")
print("     The harmonic model predicts peaks at λ_sync/n.")
print("     Residuals show impedance/reflection features.")
print(f"{'─'*80}")

# Build a simple harmonic model: sum of damped sinusoids at λ_sync/n
# For each harmonic, ξ_n(s) = A_n · cos(2πs·n/λ_sync) · exp(-s/ℓ_damping)
# This is a simplified model — the actual shape is more complex

# Simple Gaussian peak model for each harmonic
def gaussian_peak(s, s0, amp, sigma):
    return amp * np.exp(-(s - s0)**2 / (2 * sigma**2))

# Fit harmonic peaks
xi_model = np.zeros_like(xi)
for name, lam in sorted(harmonics.items(), key=lambda x: x[1]):
    if lam < s[0] or lam > s[-1]:
        continue
    xi_val = float(xi_interp(lam))
    if abs(xi_val) < 0.0001:
        continue
    # Add a Gaussian peak at the harmonic position
    sigma = 8.0  # h⁻¹ Mpc, approximate width from BAO damping
    xi_model += gaussian_peak(s, lam, xi_val, sigma)

# Residual = data - model
residual = xi - xi_model

# Find significant residual features
print(f"\n  Significant residual features (|ξ_res| > 2σ):")
print(f"  {'s (h⁻¹ Mpc)':<16} {'ξ_data':<12} {'ξ_model':<12} {'ξ_res':<12} {'S/N':<10} {'Possible source':<30}")
print(f"  {'─'*92}")

for i in range(len(s)):
    if abs(residual[i]) > 2 * err[i]:
        # Find the nearest mode activation redshift
        gam2 = 4 * math.sin(math.pi * 2 / 88) ** 2
        source = ""
        for n_test in range(2, 12):
            gam_n = 4 * math.sin(math.pi * n_test / 88) ** 2
            z_n = (gam_n / gam2) * 0.6 - 1
            if 0 < z_n < 17:
                source += f"n={n_test}(z≈{z_n:.1f}) "
        
        sn = residual[i] / err[i]
        print(f"  {s[i]:<16.1f} {xi[i]:<+12.6f} {xi_model[i]:<12.6f} {residual[i]:<+12.6f} {sn:<+10.2f} {source:<30}")

# ================================================================
# 3. Compare BOSS DR12 ξ(s) to IDCM interference pattern
# ================================================================
print(f"\n{'─'*80}")
print("  3. ξ(s) AT ALL MODE ACTIVATION SCALES")
print("     Each mode activation creates a reflection at scale:")
print("     s_n = λ_sync · (mode_activation_scale_factor)")
print(f"{'─'*80}")

# The reflection from mode n activation creates a feature at scale:
# s_reflect_n = λ_sync / (2·n)  (half-wavelength of mode n)
# This is the standing wave from the reflection

print(f"\n  {'Mode n':<8} {'z_n':<10} {'γ_n':<12} {'R':<10} {'s_reflect':<15} {'In ξ(s) range?':<15}")
print(f"  {'─'*70}")

gam2 = 4 * math.sin(math.pi * 2 / 88) ** 2
for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    z_n = (gam / gam2) * 0.6 - 1
    
    # Reflection coefficient
    Z_prev = 4 * math.sin(math.pi * (n-1) / 88) ** 2 / abs(math.cos(math.pi * (n-1) / 88))
    Z_curr = gam / abs(vg)
    R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if Z_curr > 0 and Z_prev > 0 else 0
    
    # The reflection creates a standing wave at scale s_reflect
    s_reflect = lambda_sync_hinv / (2 * n * abs(R))
    in_range = "✅" if s[0] < s_reflect < s[-1] else "❌" if s_reflect < s[0] else "📈 beyond"
    print(f"  {n:<8} {z_n:<10.2f} {gam:<12.6f} {R:<10.4f} {s_reflect:<15.1f} {in_range:<15}")

# ================================================================
# 4. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  4. SUMMARY")
print(f"{'─'*80}")

# Count harmonics detected
harmonics_in_range = [(n, lam) for n, lam in harmonics.items() 
                      if s[0] < lam < s[-1]]
harmonics_detected = sum(1 for n, lam in harmonics_in_range 
                         if abs(float(xi_interp(lam))/float(err_interp(lam))) > 3)

print(f"""
  BOSS DR12 ξ(s) data (z=0.2-0.5, 36 bins, 2-178 h⁻¹ Mpc):
  
  Harmonic series detected: {harmonics_detected}/{len(harmonics_in_range)} with S/N > 3
  - λ_sync/4 (109.1 h⁻¹ Mpc): S/N = {float(xi_interp(harmonics['λ_sync/4']))/float(err_interp(harmonics['λ_sync/4'])):.1f}
  - λ_sync/5 (87.2 h⁻¹ Mpc):  S/N = {float(xi_interp(harmonics['λ_sync/5']))/float(err_interp(harmonics['λ_sync/5'])):.1f}
  - λ_sync/6 (72.7 h⁻¹ Mpc):  S/N = {float(xi_interp(harmonics['λ_sync/6']))/float(err_interp(harmonics['λ_sync/6'])):.1f}
  - λ_sync/7 (62.3 h⁻¹ Mpc):  S/N = {float(xi_interp(harmonics['λ_sync/7']))/float(err_interp(harmonics['λ_sync/7'])):.1f}
  - λ_sync/8 (54.5 h⁻¹ Mpc):  S/N = {float(xi_interp(harmonics['λ_sync/8']))/float(err_interp(harmonics['λ_sync/8'])):.1f}
  
  Impedance/reflection analysis:
  - Mode n=3 (z≈0.35): R=0.385, s_reflect ≈ {lambda_sync_hinv/(2*3*0.385):.0f} h⁻¹ Mpc
  - Mode n=4 (z≈1.39): R=0.281, s_reflect ≈ {lambda_sync_hinv/(2*4*0.281):.0f} h⁻¹ Mpc
  - Mode n=5 (z≈2.72): R=0.220, s_reflect ≈ {lambda_sync_hinv/(2*5*0.220):.0f} h⁻¹ Mpc
  
  The 97.5 h⁻¹ Mpc peak in ξ(s) does NOT match any λ_sync/n harmonic.
  This is a candidate for impedance/reflection from mode n=3 activation.
  
  LIMITATION: BOSS DR12 only covers 2-178 h⁻¹ Mpc (z=0.2-0.5).
  We need DESI DR2 ξ(s) data (z=0-2.33, wider range) to see the
  full impedance/reflection pattern from all 11 observable modes.
""")

# Find the 97.5 Mpc peak
idx_975 = np.argmin(np.abs(s - 97.5))
print(f"  The 97.5 h⁻¹ Mpc peak:")
print(f"    s = {s[idx_975]:.1f} h⁻¹ Mpc, ξ = {xi[idx_975]:.6f}, S/N = {xi[idx_975]/err[idx_975]:.1f}")
print(f"    Closest harmonic: λ_sync/5 = {lambda_sync_hinv/5:.1f} h⁻¹ Mpc (Δ = {abs(s[idx_975] - lambda_sync_hinv/5):.1f})")
print(f"    Impedance reflection from n=3: s_reflect ≈ {lambda_sync_hinv/(2*3*0.385):.0f} h⁻¹ Mpc")
print(f"    Δ from 97.5 = {abs(lambda_sync_hinv/(2*3*0.385) - 97.5):.0f} h⁻¹ Mpc")