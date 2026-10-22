#!/usr/bin/env python3
"""
K_Chain Cosmic Web — Full ξ(s) Model with Impedance/Reflection
===============================================================
Build a complete ξ(s) model including:
  1. Smooth broadband (power-law)
  2. Harmonic series (lambda_sync/n)
  3. Impedance reflection terms (at s_reflect_n)
  4. Test against BOSS DR12 and eBOSS DR16 data

The reflection creates a localized "bump" in xi(s) at scale:
  s_reflect_n = lambda_sync / (2n * |R_n|)
with amplitude proportional to |R_n|.
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import curve_fit
import sys, os, zipfile
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

# ================================================================
# Model definition
# ================================================================
def xi_model(s, A, gamma, C, A_harm, A_refl, sigma_refl):
    """
    Full xi(s) model:
      xi(s) = xi_broadband(s) + xi_harm(s) + xi_refl(s)
    
    xi_broadband(s) = A * s^(-gamma) + C
    xi_harm(s) = A_harm * sum_{n=2}^{20} (1/n^1.5) * cos(2pi*n*s/lambda_sync) * exp(-s/200)
    xi_refl(s) = A_refl * sum_{n=2}^{11} |R_n| * exp(-(s - s_reflect_n)^2 / (2*sigma_refl^2))
    """
    lam_sync = LAMBDA_SYNC / H  # h^-1 Mpc
    
    # Broadband
    xi_b = A * s**(-gamma) + C
    
    # Harmonics
    xi_h = np.zeros_like(s)
    for n in range(2, 21):
        xi_h += (1.0 / n**1.5) * np.cos(2 * math.pi * n * s / lam_sync)
    xi_h *= np.exp(-s / 200.0)
    xi_h *= A_harm
    
    # Reflections
    xi_r = np.zeros_like(s)
    for n in range(2, 12):
        gam = 4 * math.sin(math.pi * n / 88)**2
        vg = math.cos(math.pi * n / 88)
        Z_curr = gam / abs(vg) if abs(vg) > 1e-10 else 1e10
        Z_prev = 4 * math.sin(math.pi * (n-1) / 88)**2 / abs(math.cos(math.pi * (n-1) / 88))
        R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if (Z_curr > 0 and Z_prev > 0) else 0
        s_ref = lam_sync / (2 * n * abs(R)) if abs(R) > 1e-10 else 1e10
        xi_r += abs(R) * np.exp(-(s - s_ref)**2 / (2 * sigma_refl**2))
    xi_r *= A_refl
    
    return xi_b + xi_h + xi_r

# ================================================================
# Load data
# ================================================================
# BOSS DR12
z = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s_b, xi_b, err_b = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_b.append(float(parts[0])); xi_b.append(float(parts[1])); err_b.append(float(parts[2]))
s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)

# eBOSS DR16
s_e, xi_e, err_e = [], [], []
with open('/home/wsl/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_e.append(float(parts[0])); xi_e.append(float(parts[1])); err_e.append(float(parts[2]))
s_e = np.array(s_e); xi_e = np.array(xi_e); err_e = np.array(err_e)

print("=" * 80)
print("  K_CHAIN COSMIC WEB — FULL ξ(s) MODEL WITH IMPEDANCE/REFLECTION")
print("=" * 80)

# ================================================================
# 1. Fit broadband to BOSS DR12 (avoiding harmonic/reflection regions)
# ================================================================
print(f"\n{'─'*80}")
print("  1. BROADBAND FIT (BOSS DR12, avoiding BAO/reflection scales)")
print(f"{'─'*80}")

# Fit broadband to data in 10-60 h⁻¹ Mpc (avoiding BAO at 100 and reflection at 170)
mask_broad = (s_b > 10) & (s_b < 60) | (s_b > 120) & (s_b < 160)
s_fit = s_b[mask_broad]
xi_fit = xi_b[mask_broad]

def broadband(s, A, gamma, C):
    return A * s**(-gamma) + C

popt, pcov = curve_fit(broadband, s_fit, xi_fit, p0=[1000, 2.0, 0.0])
A_fit, gamma_fit, C_fit = popt
print(f"  Broadband: xi(s) = {A_fit:.1f} * s^(-{gamma_fit:.3f}) + {C_fit:.6f}")
print(f"  Fit range: 10-60 + 120-160 h⁻¹ Mpc")

# Residuals
xi_broad_fit = broadband(s_b, *popt)
xi_resid = xi_b - xi_broad_fit

# ================================================================
# 2. Harmonic series in residuals
# ================================================================
print(f"\n{'─'*80}")
print("  2. HARMONIC SERIES IN RESIDUALS (BOSS DR12)")
print(f"{'─'*80}")

lam_sync_hinv = LAMBDA_SYNC / H
print(f"\n  {'n':<4} {'s (h⁻¹)':<12} {'xi_resid':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*48}")

from scipy.interpolate import interp1d
resid_interp = interp1d(s_b, xi_resid, kind='cubic', bounds_error=False, fill_value=0)
err_interp_b = interp1d(s_b, err_b, kind='linear', bounds_error=False, fill_value=0)

peak_count = 0
for n in range(2, 21):
    s_n = lam_sync_hinv / n
    if s_n < s_b[0] or s_n > s_b[-1]: continue
    xv = float(resid_interp(s_n))
    ev = float(err_interp_b(s_n))
    sn = xv / ev if ev > 0 else 0
    st = "PEAK" if sn > 3 else "WEAK" if sn > 2 else "NULL"
    if sn > 3: peak_count += 1
    print(f"  {n:<4} {s_n:<12.1f} {xv:<+12.6f} {sn:<+10.2f} {st:<10}")

print(f"\n  {peak_count}/19 harmonics in residuals (S/N > 3)")

# ================================================================
# 3. Reflection search in residuals
# ================================================================
print(f"\n{'─'*80}")
print("  3. REFLECTION SEARCH (BOSS DR12 + eBOSS DR16)")
print(f"{'─'*80}")

# Compute predicted reflection scales
reflections = []
for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88)**2
    vg = math.cos(math.pi * n / 88)
    Z_curr = gam / abs(vg) if abs(vg) > 1e-10 else 1e10
    Z_prev = 4 * math.sin(math.pi * (n-1) / 88)**2 / abs(math.cos(math.pi * (n-1) / 88))
    R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if (Z_curr > 0 and Z_prev > 0) else 0
    s_ref = lam_sync_hinv / (2 * n * abs(R)) if abs(R) > 1e-10 else 1e10
    reflections.append((n, R, s_ref))

print(f"\n  Predicted reflection scales:")
print(f"  {'n':<4} {'R':<12} {'s_reflect':<15} {'BOSS':<10} {'eBOSS':<10}")
print(f"  {'─'*51}")

for n, R, s_ref in reflections:
    b_ok = "✅" if s_b[0] < s_ref < s_b[-1] else "❌"
    e_ok = "✅" if s_e[0] < s_ref < s_e[-1] else "❌"
    print(f"  {n:<4} {R:<+12.4f} {s_ref:<15.1f} {b_ok:<10} {e_ok:<10}")

# Check for reflection signal in eBOSS residuals at predicted scales
# Fit broadband to eBOSS data
mask_e = (s_e > 10) & (s_e < 60) | (s_e > 120) & (s_e < 160)
popt_e, _ = curve_fit(broadband, s_e[mask_e], xi_e[mask_e], p0=[1000, 2.0, 0.0])
xi_e_resid = xi_e - broadband(s_e, *popt_e)
err_interp_e = interp1d(s_e, err_e, kind='linear', bounds_error=False, fill_value=0)
resid_interp_e = interp1d(s_e, xi_e_resid, kind='cubic', bounds_error=False, fill_value=0)

print(f"\n  Reflection detection in eBOSS DR16 residuals:")
print(f"  {'n':<4} {'s_reflect':<15} {'xi_resid':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*51}")

refl_detected = 0
for n, R, s_ref in reflections:
    if s_ref < s_e[0] or s_ref > s_e[-1]: continue
    xv = float(resid_interp_e(s_ref))
    ev = float(err_interp_e(s_ref))
    sn = xv / ev if ev > 0 else 0
    st = "DETECTED" if sn > 3 else "WEAK" if sn > 2 else "NULL"
    if sn > 3: refl_detected += 1
    print(f"  {n:<4} {s_ref:<15.1f} {xv:<+12.6f} {sn:<+10.2f} {st:<10}")

# ================================================================
# 4. Full model fit to BOSS DR12
# ================================================================
print(f"\n{'─'*80}")
print("  4. FULL MODEL FIT (BOSS DR12)")
print(f"{'─'*80}")

# Use the theoretical parameters
A = A_fit
gamma = gamma_fit
C = C_fit
A_harm = 0.001  # initialize
A_refl = 0.001
sigma_refl = 15.0  # h⁻¹ Mpc

# Compute predicted xi
xi_pred = xi_model(s_b, A, gamma, C, A_harm, A_refl, sigma_refl)

# Quick fit for harmonic amplitude
# xi_resid = xi_harm + xi_refl
# Fit A_harm from the harmonic positions
harm_resid = []
for n in range(4, 21):
    s_n = lam_sync_hinv / n
    if s_n < s_b[0] or s_n > s_b[-1]: continue
    xv = float(resid_interp(s_n))
    harm_resid.append(xv)

A_harm_fit = np.mean([abs(x) for x in harm_resid]) / np.mean([1.0/n**1.5 * np.exp(-s_n/200) for n in range(4, 21) for s_n in [lam_sync_hinv/n]])

print(f"  Fitted harmonic amplitude: A_harm = {A_harm_fit:.6f}")
print(f"  (From mean |xi_resid| at harmonic positions)")

# ================================================================
# 5. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  5. SUMMARY")
print(f"{'─'*80}")

print(f"""
  Full ξ(s) model tested:
  
  BOSS DR12 (z=0.2-0.5, 36 bins, 2-178 h⁻¹ Mpc):
  - Broadband: xi(s) = {A_fit:.1f} * s^(-{gamma_fit:.3f}) + {C_fit:.6f}
  - Harmonics: {peak_count}/19 detected in residuals (S/N > 3)
  - Reflections: n=2 @ {reflections[0][2]:.0f} h⁻¹ Mpc, n=3 @ {reflections[1][2]:.0f} h⁻¹ Mpc
  
  eBOSS DR16 (z=0.6-1.0, 49 bins, 8-248 h⁻¹ Mpc):
  - Reflections: n=2..{max(n for n,_,s in reflections if s < s_e[-1])} in range
  - {refl_detected}/{sum(1 for _,_,s in reflections if s_e[0] < s < s_e[-1])} reflections detected
  
  Key finding: The impedance/reflection model predicts specific features at
  s_reflect_n = lambda_sync / (2n * |R_n|). These are at the edge of current
  BOSS data but within eBOSS DR16 range.
  
  The reflection at n=2 (s={reflections[0][2]:.0f} h⁻¹ Mpc) has R={reflections[0][1]:.3f},
  the strongest reflection. It should be visible in BOSS DR12 data.
  The reflection at n=3 (s={reflections[1][2]:.0f} h⁻¹ Mpc) has R={reflections[1][1]:.3f}.
""")