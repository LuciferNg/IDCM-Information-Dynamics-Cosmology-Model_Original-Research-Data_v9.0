#!/usr/bin/env python3
"""
BOSS DR12 Post-Reconstruction — Peak/Null/Impedance Test
==========================================================
BOSS DR12 is post-reconstruction: broadband is already subtracted.
xi(s) IS the wiggle component. Direct peak/null/impedance test.
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import sys, os, zipfile
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

# Load BOSS DR12 post-recon data
z = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s, xi, err = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s.append(float(parts[0]))
        xi.append(float(parts[1]))
        err.append(float(parts[2]))
s = np.array(s); xi = np.array(xi); err = np.array(err)

xi_interp = interp1d(s, xi, kind='cubic', bounds_error=False, fill_value=0)
err_interp = interp1d(s, err, kind='linear', bounds_error=False, fill_value=0)

lambda_sync_hinv = LAMBDA_SYNC / H

# 1. PEAK TEST
peaks = {}
for n in range(2, 21):
    s_p = lambda_sync_hinv / n
    if s_p < s[0] or s_p > s[-1]: continue
    xiv = float(xi_interp(s_p))
    ev = float(err_interp(s_p))
    sn = xiv / ev if ev > 0 else 0
    peaks[n] = (s_p, xiv, ev, sn)

# 2. NULL TEST
nulls = {}
for n in range(2, 20):
    s_n = lambda_sync_hinv / (n + 0.5)
    if s_n < s[0] or s_n > s[-1]: continue
    xiv = float(xi_interp(s_n))
    ev = float(err_interp(s_n))
    sn = xiv / ev if ev > 0 else 0
    nulls[n] = (s_n, xiv, ev, sn)

# 3. IMPEDANCE
gam2 = 4 * math.sin(math.pi * 2 / 88) ** 2
reflections = {}
for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    z_n = (gam / gam2) * 0.6 - 1
    Z_prev = 4 * math.sin(math.pi * (n-1) / 88) ** 2 / abs(math.cos(math.pi * (n-1) / 88))
    Z_curr = gam / abs(vg) if abs(vg) > 1e-10 else 1e10
    R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if Z_curr > 0 and Z_prev > 0 else 0
    s_r = lambda_sync_hinv / (2 * n * abs(R) + 1e-10)
    if s_r > s[0] and s_r < s[-1]:
        xiv = float(xi_interp(s_r))
        ev = float(err_interp(s_r))
        sn = xiv / ev if ev > 0 else 0
        reflections[n] = (s_r, z_n, R, xiv, ev, sn)

# 4. ACTUAL PEAKS
xi_smooth = gaussian_filter1d(xi, sigma=1.5, mode='nearest')
actual_peaks = []
for i in range(2, len(s)-2):
    if xi_smooth[i] > xi_smooth[i-1] and xi_smooth[i] > xi_smooth[i-2] and \
       xi_smooth[i] > xi_smooth[i+1] and xi_smooth[i] > xi_smooth[i+2]:
        actual_peaks.append((s[i], xi[i], err[i]))

# PRINT
line = "-" * 80
hdr = "=" * 80

print(hdr)
print("  BOSS DR12 POST-RECON — PEAK + NULL + IMPEDANCE TEST")
print("  z=0.2-0.5, 36 bins, post-reconstruction (xi = wiggle)")
print(hdr)

# 1. PEAK
print(f"\n{line}")
print("  1. PEAK TEST: lambda_sync/n  harmonic positions")
print("     Post-recon -> xi(s) IS the wiggle. Direct test.")
print(line)
print(f"\n  {'n':<4} {'s':<10} {'xi(s)':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*46}")

peak_pass = 0
for n in sorted(peaks.keys()):
    sp, xiv, ev, sn = peaks[n]
    st = "PEAK" if sn > 3 else "WEAK" if sn > 2 else "NULL"
    if sn > 3: peak_pass += 1
    print(f"  {n:<4} {sp:<10.1f} {xiv:<+12.6f} {sn:<+10.2f} {st:<10}")
print(f"\n  {peak_pass}/{len(peaks)} peaks detected (S/N > 3)")

# 2. NULL
print(f"\n{line}")
print("  2. NULL TEST: lambda_sync/(n+0.5)  anti-harmonic positions")
print(line)
print(f"\n  {'n':<4} {'s':<10} {'xi(s)':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*46}")

null_pass = 0
for n in sorted(nulls.keys()):
    sn, xiv, ev, snv = nulls[n]
    st = "NULL" if abs(snv) < 2 else "EDGE" if abs(snv) < 3 else "PEAK!"
    if abs(snv) < 2: null_pass += 1
    print(f"  {n:<4} {sn:<10.1f} {xiv:<+12.6f} {snv:<+10.2f} {st:<10}")
print(f"\n  {null_pass}/{len(nulls)} nulls consistent with xi=0 (|S/N| < 2)")

# 3. IMPEDANCE
print(f"\n{line}")
print("  3. IMPEDANCE/REFLECTION: mode activation reflections")
print(line)
print(f"\n  {'n':<4} {'z_n':<8} {'R':<10} {'s_refl':<10} {'xi(s)':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*64}")

for n in sorted(reflections.keys()):
    sr, zr, Rr, xiv, ev, snv = reflections[n]
    st = "REFL" if snv > 3 else "WEAK" if snv > 2 else "."
    print(f"  {n:<4} {zr:<8.2f} {Rr:<+10.4f} {sr:<10.1f} {xiv:<+12.6f} {snv:<+10.2f} {st:<10}")

# 4. ACTUAL PEAKS
print(f"\n{line}")
print("  4. ACTUAL PEAKS IN xi(s) vs HARMONIC PREDICTION")
print(line)
print(f"\n  {'s':<10} {'xi(s)':<12} {'S/N':<10} {'Closest lambda_sync/n':<25} {'Delta':<10} {'Note':<20}")
print(f"  {'─'*77}")

for sp, xip, errp in actual_peaks:
    sn = xip/errp if errp > 0 else 0
    best_n = min(peaks.keys(), key=lambda k: abs(sp - peaks[k][0]))
    best_lam = peaks[best_n][0]
    delta = sp - best_lam
    note = "lambda_sync/"+str(best_n) if abs(delta) < 8 else "?"
    print(f"  {sp:<10.1f} {xip:<+12.6f} {sn:<+10.2f} lambda_sync/{best_n:<14d} {delta:<+10.1f} {note:<20}")

# 5. SUMMARY
print(f"\n{line}")
print("  5. STATISTICAL SUMMARY")
print(line)

peak_sns = [v[3] for v in peaks.values()]
null_sns = [v[3] for v in nulls.values()]
refl_sns = [v[3] for v in reflections.values()]

print(f"\n  TEST                COUNT   MEAN S/N   PASS RATE")
print(f"  {'─'*50}")
print(f"  Peak (lambda_sync/n)  {len(peaks):<6d} {np.mean(peak_sns):<+9.2f}  {peak_pass}/{len(peaks)}")
print(f"  Null (midpoints)     {len(nulls):<6d} {np.mean(null_sns):<+9.2f}  {null_pass}/{len(nulls)}")
print(f"  Reflection (R_n)     {len(reflections):<6d} {np.mean(refl_sns):<+9.2f}  N/A")

print(f"\n  BOSS DR12 ACTUAL PEAKS: {len(actual_peaks)}")
for sp, xip, errp in actual_peaks:
    best_n = min(peaks.keys(), key=lambda k: abs(sp - peaks[k][0]))
    delta = sp - peaks[best_n][0]
    sn = xip/errp if errp > 0 else 0
    print(f"    s={sp:<6.1f} xi={xip:<+8.6f} S/N={sn:<+6.2f} -> lambda_sync/{best_n} (delta={delta:+.1f})")

# BONUS: probability
from scipy.stats import binom
p_random = binom.sf(peak_pass-1, len(peaks), 0.001)
print(f"\n  Probability of {peak_pass}/{len(peaks)} harmonics by random chance:")
print(f"    p < {p_random:.2e} (assuming 0.1% false positive rate per bin)")