#!/usr/bin/env python3
"""
φ-Ratio Test — EMD Recovery of Harmonic Amplitudes
====================================================
The φ-ratio pattern was used to predict z=17 as the cosmic
horizon cutoff. But it was based on polynomial-fit amplitudes
(only 4/19 harmonics). EMD now gives clean amplitudes for
17/19 harmonics.

Test: Do the EMD amplitudes follow a Fibonacci/φ ratio?
If yes → φ-ratio is real, z=17 is structural
If no  → φ-ratio was a selection effect, z=17 is ad-hoc
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import sys, os, zipfile
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/wavelet_toolbox')
from _core import *
from emd_engine import *

print("=" * 80)
print("  φ-RATIO TEST — EMD RECOVERY OF HARMONIC AMPLITUDES")
print("=" * 80)

# ================================================================
# Load BOSS DR12 ξ(s) data
# ================================================================
z = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s_b, xi_b, err_b = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_b.append(float(parts[0])); xi_b.append(float(parts[1])); err_b.append(float(parts[2]))
s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)

lam_sync_hinv = LAMBDA_SYNC / H

# ================================================================
# 1. EMD decomposition of BOSS data
# ================================================================
print(f"\n{'─'*80}")
print("  1. EMD DECOMPOSITION")
print(f"{'─'*80}")

xi_emd, imfs, resid, n_imf = emd_apply_to_survey(s_b, xi_b, "BOSS", aggressive=False)
print(f"  {n_imf} IMFs extracted")
print(f"  EMD residual std: {np.std(xi_emd):.6f}")

# ================================================================
# 2. Harmonic amplitude extraction
# ================================================================
print(f"\n{'─'*80}")
print("  2. HARMONIC AMPLITUDE EXTRACTION (EMD)")
print(f"{'─'*80}")

# Find the amplitude at each λ_sync/n position
harmonics = []
for n in range(2, 21):
    s_n = lam_sync_hinv / n
    if s_n < s_b[0] or s_n > s_b[-1]:
        continue
    
    # Interpolate EMD residual at this position
    xi_n = np.interp(s_n, s_b, xi_emd)
    err_n = np.interp(s_n, s_b, err_b)
    sn = xi_n / err_n if err_n > 0 else 0
    
    # Also find the actual peak near this position
    idx = np.argmin(np.abs(s_b - s_n))
    s_actual = s_b[idx]
    xi_actual = xi_emd[idx]
    err_actual = err_b[idx]
    sn_actual = xi_actual / err_actual if err_actual > 0 else 0
    
    harmonics.append({
        'n': n, 's_pred': s_n, 's_actual': s_actual,
        'xi_pred': xi_n, 'xi_actual': xi_actual,
        'sn_pred': sn, 'sn_actual': sn_actual
    })

print(f"  {'n':<6} {'s_pred':<12} {'s_actual':<12} {'A_EMD':<12} {'S/N':<10} {'φ^n':<12} {'A_EMD/φ^n':<12}")
print(f"  {'─'*64}")

for h in harmonics:
    n = h['n']
    phi_n = PHI ** n
    ratio = abs(h['xi_actual'] / phi_n) if phi_n > 0 else 0
    print(f"  {n:<6} {h['s_pred']:<12.1f} {h['s_actual']:<12.1f} {h['xi_actual']:<+12.6f} {h['sn_actual']:<+10.2f} {phi_n:<12.6f} {ratio:<12.6f}")

# ================================================================
# 3. φ-ratio test
# ================================================================
print(f"\n{'─'*80}")
print("  3. φ-RATIO TEST")
print(f"{'─'*80}")

amplitudes = np.array([h['xi_actual'] for h in harmonics if h['sn_actual'] > 3])
n_values = np.array([h['n'] for h in harmonics if h['sn_actual'] > 3])

# Test 1: Does A_n ∝ φ^n?
phi_n_vals = PHI ** n_values
corr_phi = np.corrcoef(np.log(np.abs(amplitudes)), np.log(phi_n_vals))[0, 1] if len(amplitudes) > 2 else 0

# Test 2: Does A_n ∝ A_{n-1} + A_{n-2}? (Fibonacci recurrence)
if len(amplitudes) >= 3:
    A_n = np.abs(amplitudes[2:])
    dp = np.abs(amplitudes[1:-1]) + np.abs(amplitudes[:-2])  # A_{n-1} + A_{n-2}
    # Check if A_n ≈ A_{n-1} + A_{n-2} (Fibonacci)
    fib_ratio = A_n / dp
    fib_valid = np.mean(fib_ratio[fib_ratio > 0.1])
    corr_fib = np.corrcoef(A_n, dp)[0, 1]
else:
    fib_valid = 0
    corr_fib = 0

# Test 3: Does A_n / A_{n-1} ≈ φ?
if len(amplitudes) >= 2:
    ratios = np.abs(amplitudes[1:] / amplitudes[:-1])
    mean_ratio = np.mean(ratios)
    std_ratio = np.std(ratios)
    phi_consistency = 1 - abs(mean_ratio - PHI) / PHI
else:
    mean_ratio = 0
    std_ratio = 0
    phi_consistency = 0

print(f"  Test 1: A_n ∝ φ^n")
print(f"    Correlation: r = {corr_phi:.4f}")
print(f"    {'✅ A_n follows φ^n' if abs(corr_phi) > 0.7 else '🟡 Weak correlation' if abs(corr_phi) > 0.3 else '❌ No correlation'}")

print(f"\n  Test 2: Fibonacci recurrence A_n ≈ A_{n-1} + A_{n-2}")
print(f"    Mean A_n/(A_{n-1}+A_{n-2}): {fib_valid:.4f}")
print(f"    Correlation: r = {corr_fib:.4f}")
print(f"    {'✅ Fibonacci recurrence' if abs(fib_valid - 1) < 0.3 else '🟡 Weak' if abs(fib_valid - 1) < 0.5 else '❌ Not Fibonacci'}")

print(f"\n  Test 3: A_n/A_{n-1} ≈ φ = {PHI:.4f}")
print(f"    Mean ratio: {mean_ratio:.4f} ± {std_ratio:.4f}")
print(f"    φ-consistency: {phi_consistency*100:.1f}%")
print(f"    {'✅ A_n ratio follows φ' if phi_consistency > 0.7 else '🟡 Weak' if phi_consistency > 0.3 else '❌ A_n ratio ≠ φ'}")

# ================================================================
# 4. Extrapolate to z=17 cutoff
# ================================================================
print(f"\n{'─'*80}")
print("  4. EXTRAPOLATION TO z=17 CUTOFF")
print(f"{'─'*80}")

# If A_n ∝ φ^n, the cutoff is at n where A_n → noise level
noise_level = np.std(xi_emd[:5])  # noise at smallest scales
print(f"  Noise level: {noise_level:.6f}")

# Extrapolate φ^n to find n_cutoff
if abs(corr_phi) > 0.7:
    # Fit A_n = C × φ^n
    logA = np.log(np.abs(amplitudes) + 1e-10)
    log_phi_n = n_values * np.log(PHI)
    # Linear fit
    A_fit = np.polyfit(log_phi_n, logA, 1)
    C = np.exp(A_fit[1])
    print(f"  Fit: A_n = {C:.6f} × φ^n")
    
    # Find n where A_n = noise_level
    n_cutoff = math.log(noise_level / C) / np.log(PHI) if C > 0 and noise_level > 0 else 0
    print(f"  Cutoff: n_cutoff = {n_cutoff:.1f}")
    
    # Convert to redshift
    z_cutoff = 4**n_cutoff - 1 if n_cutoff > 0 else 0
    print(f"  z_cutoff = {z_cutoff:.1f}")
    print(f"  {'✅ Matches z=17' if abs(z_cutoff - 17) < 5 else '🟡 Close' if abs(z_cutoff - 17) < 10 else '❌ Does not match z=17'}")
else:
    print(f"  φ-ratio not confirmed, cannot extrapolate to z=17")
    print(f"  z=17 cutoff has no structural foundation")

# ================================================================
# 5. Alternative: extrapolate from Fibonacci recurrence
# ================================================================
print(f"\n{'─'*80}")
print("  5. ALTERNATIVE EXTRAPOLATION")
print(f"{'─'*80}")

if abs(corr_fib) > 0.7 and fib_valid > 0.3:
    # Fibonacci: A_n = A_{n-1} + A_{n-2}
    # Extrapolate forward
    A_ext = list(np.abs(amplitudes))
    n_ext = list(n_values)
    while n_ext[-1] < 44:
        next_n = n_ext[-1] + 1
        next_A = A_ext[-1] + A_ext[-2]  # Fibonacci
        n_ext.append(next_n)
        A_ext.append(next_A)
    
    # Find where A_n < noise_level
    n_cutoff_fib = n_ext[0]
    for i, a in enumerate(A_ext):
        if a < noise_level:
            n_cutoff_fib = n_ext[i]
            break
    
    z_cutoff_fib = 4**n_cutoff_fib - 1
    print(f"  Fibonacci extrapolation:")
    print(f"  n_cutoff = {n_cutoff_fib}")
    print(f"  z_cutoff = {z_cutoff_fib:.1f}")
    print(f"  {'✅ Matches z=17' if abs(z_cutoff_fib - 17) < 5 else '🟡 Close' if abs(z_cutoff_fib - 17) < 10 else '❌ Does not match z=17'}")
else:
    print(f"  Fibonacci recurrence not confirmed, cannot extrapolate")

# ================================================================
# 6. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  6. SUMMARY")
print(f"{'─'*80}")

print(f"""
  φ-ratio test results:
  
  EMD harmonic amplitudes ({len(amplitudes)}/{len(harmonics)} detected):
  
  φ^n correlation:     r = {corr_phi:.4f}  {'✅' if abs(corr_phi) > 0.7 else '🟡' if abs(corr_phi) > 0.3 else '❌'}
  Fibonacci recurrence: r = {corr_fib:.4f}  {'✅' if abs(corr_fib) > 0.7 else '🟡' if abs(corr_fib) > 0.3 else '❌'}
  A_n/A_{{n-1}} ≈ φ:    {mean_ratio:.4f} ± {std_ratio:.4f}  {'✅' if phi_consistency > 0.7 else '🟡' if phi_consistency > 0.3 else '❌'}
  
  Conclusion:
    {'The φ-ratio IS confirmed by EMD' if abs(corr_phi) > 0.7 or abs(corr_fib) > 0.7 else 'The φ-ratio was a selection effect (polynomial fit bias)'}
    {'z=17 has structural foundation' if abs(z_cutoff - 17) < 5 or abs(z_cutoff_fib - 17) < 5 else 'z=17 is ad-hoc without φ-ratio'}
""")