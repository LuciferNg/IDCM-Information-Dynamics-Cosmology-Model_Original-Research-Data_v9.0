#!/usr/bin/env python3
"""
BOSS DR12 P(k) — Fourier-Space Harmonic Analysis
===================================================
P(k) has 120 bins (vs 36 in xi(s)). Much finer resolution.
IDCM predicts oscillations at k_n = 2pi*n/lambda_sync = n*0.01547 h/Mpc.

Standard BAO predicts oscillation at k = 2pi/BAO = 0.0309 h/Mpc.
IDCM predicts a SUB-HARMONIC at k = 2pi/lambda_sync = 0.0155 h/Mpc.
This is testable: is there power at k = 0.0155 h/Mpc?
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import sys, os
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

# Load P(k) data
data = np.loadtxt('/tmp/public_material_BAO/Beutleretal_pk_monopole_DR12_NGC_z1_postrecon_120.dat',
                  skiprows=34)
k = data[:, 0]    # k_central
Pk = data[:, 2]   # P_0(k)
err = data[:, 3]  # sig_ii_0

# IDCM parameters
lambda_sync_hinv = LAMBDA_SYNC / H  # 406.1 h^-1 Mpc
dk_idcm = 2 * math.pi / lambda_sync_hinv  # 0.01547 h/Mpc

# Smooth P(k) using a low-order polynomial in log-log space
logk = np.log(k)
logP = np.log(Pk)
# 5th-order polynomial for smooth broadband
smooth_coeffs = np.polyfit(logk, logP, 5)
logP_smooth = np.polyval(smooth_coeffs, logk)
P_smooth = np.exp(logP_smooth)
P_wiggle = Pk / P_smooth - 1  # fractional deviation

# Interpolate
P_wiggle_interp = interp1d(k, P_wiggle, kind='cubic', bounds_error=False, fill_value=0)
err_interp = interp1d(k, err / Pk, kind='linear', bounds_error=False, fill_value=0)

# ============ 1. IDCM HARMONIC POSITIONS ============
# P(k) oscillations at k_n = n * dk_idcm
# Phase: P(k) = P_smooth * [1 + A * cos(2pi*k/dk_idcm + phi)]
# Peaks at k = (m + 0.5 - phi/2pi) * dk_idcm for cosine

# Test 3 phases: k = n*dk, (n+0.25)*dk, (n+0.5)*dk
print("=" * 80)
print("  BOSS DR12 P(k) — FOURIER-SPACE HARMONIC ANALYSIS")
print("  120 bins, post-reconstruction, z=0.2-0.5")
print("=" * 80)

print(f"\n  IDCM fundamental: dk = 2pi/lambda_sync = {dk_idcm:.5f} h/Mpc")
print(f"  Standard BAO:     dk_BAO = 2pi/BAO = {2*math.pi/(lambda_sync_hinv/2):.5f} h/Mpc")
print(f"  Ratio: dk_BAO/dk = 2 (BAO = lambda_sync/2)")

# 1. PEAK: k = n * dk
print(f"\n{'─'*80}")
print("  1. P(k) WIGGLE AT IDCM HARMONIC POSITIONS k = n*dk")
print(f"{'─'*80}")
print(f"\n  {'n':<4} {'k':<12} {'P_wiggle':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*48}")

peak_pass = 0
for n in range(1, 20):
    k_n = n * dk_idcm
    if k_n < k[0] or k_n > k[-1]: continue
    Pw = float(P_wiggle_interp(k_n))
    ev = float(err_interp(k_n))
    sn = Pw / ev if ev > 0 else 0
    st = "PEAK" if sn > 3 else "WEAK" if sn > 2 else "NULL"
    if sn > 3: peak_pass += 1
    print(f"  {n:<4} {k_n:<12.5f} {Pw:<+12.6f} {sn:<+10.2f} {st:<10}")

print(f"\n  {peak_pass}/19 peaks detected (S/N > 3)")

# 2. NULL: k = (n+0.5) * dk
print(f"\n{'─'*80}")
print("  2. NULL TEST: k = (n+0.5)*dk  (anti-harmonic positions)")
print(f"{'─'*80}")
print(f"\n  {'n':<4} {'k':<12} {'P_wiggle':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*48}")

null_pass = 0
for n in range(1, 19):
    k_n = (n + 0.5) * dk_idcm
    if k_n < k[0] or k_n > k[-1]: continue
    Pw = float(P_wiggle_interp(k_n))
    ev = float(err_interp(k_n))
    sn = Pw / ev if ev > 0 else 0
    st = "NULL" if abs(sn) < 2 else "EDGE" if abs(sn) < 3 else "PEAK!"
    if abs(sn) < 2: null_pass += 1
    print(f"  {n:<4} {k_n:<12.5f} {Pw:<+12.6f} {sn:<+10.2f} {st:<10}")

print(f"\n  {null_pass}/18 nulls consistent with P_wiggle=0 (|S/N| < 2)")

# 3. POWER SPECTRUM AT BAO SCALE
print(f"\n{'─'*80}")
print("  3. COMPARISON: IDCM vs STANDARD BAO FREQUENCY")
print(f"{'─'*80}")

# Standard BAO: k_BAO = 2pi/BAO = 0.0309
k_bao = 2 * math.pi / (lambda_sync_hinv / 2)
print(f"\n  Standard BAO: k_BAO = {k_bao:.5f} h/Mpc")
Pw_bao = float(P_wiggle_interp(k_bao))
sn_bao = Pw_bao / float(err_interp(k_bao))
print(f"  P_wiggle(k_BAO) = {Pw_bao:+.6f}, S/N = {sn_bao:+.2f}")

# IDCM fundamental: k_1 = dk = 0.01547
k_idcm = dk_idcm
if k_idcm > k[0] and k_idcm < k[-1]:
    Pw_idcm = float(P_wiggle_interp(k_idcm))
    ev_idcm = float(err_interp(k_idcm))
    sn_idcm = Pw_idcm / ev_idcm if ev_idcm > 0 else 0
    print(f"  IDCM: k_1 = {k_idcm:.5f} h/Mpc")
    print(f"  P_wiggle(k_1) = {Pw_idcm:+.6f}, S/N = {sn_idcm:+.2f}")
else:
    print(f"  IDCM: k_1 = {k_idcm:.5f} h/Mpc (outside data range)")

# 4. ACTUAL PEAKS IN P(k) WIGGLE
print(f"\n{'─'*80}")
print("  4. ALL PEAKS IN P(k) WIGGLE vs IDCM PREDICTION")
print(f"{'─'*80}")

# Find peaks in P_wiggle
peaks_idx, _ = find_peaks(P_wiggle, height=0.01, distance=5)
print(f"\n  {'k':<10} {'P_wiggle':<12} {'S/N':<10} {'Closest n*dk':<16} {'Delta':<10} {'Match':<10}")
print(f"  {'─'*68}")

for idx in peaks_idx:
    Pw_v = P_wiggle[idx]
    sn_v = Pw_v / (err[idx] / Pk[idx])
    best_n = round(k[idx] / dk_idcm)
    delta = k[idx] - best_n * dk_idcm
    match = "IDCM" if abs(delta) < 0.5*dk_idcm else "?"
    print(f"  {k[idx]:<10.5f} {Pw_v:<+12.6f} {sn_v:<+10.2f} n={best_n:<10d} {delta:<+10.5f} {match:<10}")

# 5. SUMMARY
print(f"\n{'─'*80}")
print("  5. STATISTICAL SUMMARY")
print(f"{'─'*80}")

print(f"""
  P(k) analysis (120 bins, post-recon):
  
  IDCM: dk = 2pi/lambda_sync = {dk_idcm:.5f} h/Mpc
  Standard BAO: dk_BAO = 2pi/BAO = {k_bao:.5f} h/Mpc
  
  Peak test:  {peak_pass}/19 IDCM harmonics detected
  Null test:  {null_pass}/18 anti-harmonics consistent with zero
  
  Key distinction:
  - IDCM predicts oscillation at dk = {dk_idcm:.5f} (fundamental)
  - Standard BAO predicts oscillation at dk_BAO = {k_bao:.5f} (2nd harmonic)
  
  If P(k) shows power at dk (NOT dk_BAO), that's evidence for IDCM.
  If P(k) only shows power at dk_BAO, that's consistent with standard BAO.
""")

# Save wiggle for later
np.savetxt('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/pk_wiggle.txt',
           np.column_stack([k, Pk, P_smooth, P_wiggle, err]),
           header='k Pk P_smooth P_wiggle err')