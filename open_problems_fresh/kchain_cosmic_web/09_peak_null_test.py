#!/usr/bin/env python3
"""
最精細 ξ(s) 測量 — PEAK + NULL + IMPEDANCE 三層檢驗（wiggle-only）
先減 smooth broadband，再測 wiggle 嘅 peak/null/reflection。

ξ(s) = B(s) + ξ_wiggle(s)
B(s) = poly in log(s) (smooth broadband)
Peak test: λ_sync/n 位置應有 ξ_wiggle > 0
Null test: λ_sync/(n+0.5) 位置應有 ξ_wiggle ≈ 0
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import sys, os
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

# Load eBOSS DR16 data
s_data, xi_data, err_data = [], [], []
with open('/home/wsl/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt') as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_data.append(float(parts[0]))
        xi_data.append(float(parts[1]))
        err_data.append(float(parts[2]))
s = np.array(s_data); xi = np.array(xi_data); err = np.array(err_data)

xi_interp = interp1d(s, xi, kind='cubic', bounds_error=False, fill_value=0)
err_interp = interp1d(s, err, kind='linear', bounds_error=False, fill_value=0)

# Fit smooth broadband: 3rd-order poly in log(s)
def broadband_poly(log_s, a0, a1, a2, a3):
    return a0 + a1*log_s + a2*log_s**2 + a3*log_s**3

mask = s > 10
log_s = np.log(s[mask])
popt, _ = curve_fit(broadband_poly, log_s, xi[mask], 
                     p0=[1, -0.5, -0.1, 0.01],
                     sigma=err[mask], maxfev=10000)
xi_broad = broadband_poly(np.log(s), *popt)
xi_wiggle = xi - xi_broad
xi_wiggle_interp = interp1d(s, xi_wiggle, kind='cubic', bounds_error=False, fill_value=0)

# IDCM parameters
lambda_sync_hinv = LAMBDA_SYNC / H

# 1. Peak positions in wiggle: lambda_sync/n
peaks = {}
for n in range(2, 21):
    s_peak = lambda_sync_hinv / n
    if s_peak < s[0] or s_peak > s[-1]: continue
    xi_w = float(xi_wiggle_interp(s_peak))
    err_val = float(err_interp(s_peak))
    sn = xi_w / err_val if err_val > 0 else 0
    peaks[n] = (s_peak, xi_w, err_val, sn)

# 2. Null positions in wiggle: lambda_sync/(n + 0.5)
nulls = {}
for n in range(2, 20):
    s_null = lambda_sync_hinv / (n + 0.5)
    if s_null < s[0] or s_null > s[-1]: continue
    xi_w = float(xi_wiggle_interp(s_null))
    err_val = float(err_interp(s_null))
    sn = xi_w / err_val if err_val > 0 else 0
    nulls[n] = (s_null, xi_w, err_val, sn)

# 3. Impedance/reflection positions in wiggle
gam2 = 4 * math.sin(math.pi * 2 / 88) ** 2
reflections = {}
for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88) ** 2
    vg = math.cos(math.pi * n / 88)
    z_n = (gam / gam2) * 0.6 - 1
    Z_prev = 4 * math.sin(math.pi * (n-1) / 88) ** 2 / abs(math.cos(math.pi * (n-1) / 88))
    Z_curr = gam / abs(vg) if abs(vg) > 1e-10 else 1e10
    R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if Z_curr > 0 and Z_prev > 0 else 0
    s_reflect = lambda_sync_hinv / (2 * n * abs(R) + 1e-10)
    if s_reflect > s[0] and s_reflect < s[-1]:
        xi_w = float(xi_wiggle_interp(s_reflect))
        err_val = float(err_interp(s_reflect))
        sn = xi_w / err_val if err_val > 0 else 0
        reflections[n] = (s_reflect, z_n, R, xi_w, err_val, sn)

# Print
print("=" * 80)
print("  最精細 xi(s) 測量 — WIGGLE-ONLY PEAK + NULL + IMPEDANCE")
print("  eBOSS DR16 (z=0.6-1.0, 50 bins)")
print("=" * 80)
print(f"  Broadband poly coeffs: a0={popt[0]:.3f}, a1={popt[1]:.3f}, a2={popt[2]:.3f}, a3={popt[3]:.3f}")

# 1. PEAK TEST
print(f"\n{'─'*80}")
print("  1. PEAK TEST (wiggle) — lambda_sync/n harmonic positions")
print(f"{'─'*80}")
print(f"\n  {'n':<4} {'s':<10} {'xi_wiggle':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*46}")

peak_pass = 0
peak_fail = 0
for n in sorted(peaks.keys()):
    s_p, xi_w, err_p, sn_p = peaks[n]
    status = "PEAK" if sn_p > 3 else "WEAK" if sn_p > 2 else "NULL"
    if sn_p > 3: peak_pass += 1
    else: peak_fail += 1
    print(f"  {n:<4} {s_p:<10.1f} {xi_w:<+12.6f} {sn_p:<+10.2f} {status:<10}")

print(f"\n  RESULT: {peak_pass}/{peak_pass+peak_fail} peaks detected (S/N > 3)")

# 2. NULL TEST
print(f"\n{'─'*80}")
print("  2. NULL TEST (wiggle) — lambda_sync/(n+0.5) anti-harmonic positions")
print(f"{'─'*80}")
print(f"\n  {'n':<4} {'s':<10} {'xi_wiggle':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*46}")

null_pass = 0
null_fail = 0
for n in sorted(nulls.keys()):
    s_n, xi_w, err_n, sn_n = nulls[n]
    status = "NULL" if abs(sn_n) < 2 else "EDGE" if abs(sn_n) < 3 else "PEAK!"
    if abs(sn_n) < 2: null_pass += 1
    else: null_fail += 1
    print(f"  {n:<4} {s_n:<10.1f} {xi_w:<+12.6f} {sn_n:<+10.2f} {status:<10}")

print(f"\n  RESULT: {null_pass}/{null_pass+null_fail} nulls consistent with xi_wiggle=0 (|S/N| < 2)")

# 3. IMPEDANCE TEST
print(f"\n{'─'*80}")
print("  3. IMPEDANCE/REFLECTION TEST (wiggle) — mode activation reflections")
print(f"{'─'*80}")
print(f"\n  {'n':<4} {'z_n':<8} {'R':<10} {'s_refl':<10} {'xi_wiggle':<12} {'S/N':<10} {'Status':<10}")
print(f"  {'─'*64}")

for n in sorted(reflections.keys()):
    s_r, z_r, R_r, xi_w, err_r, sn_r = reflections[n]
    status = "REFL" if sn_r > 3 else "WEAK" if sn_r > 2 else "."
    print(f"  {n:<4} {z_r:<8.2f} {R_r:<+10.4f} {s_r:<10.1f} {xi_w:<+12.6f} {sn_r:<+10.2f} {status:<10}")

# 4. SUMMARY
peak_sns = [sn for _, _, _, sn in peaks.values()]
null_sns = [sn for _, _, _, sn in nulls.values()]
refl_sns = [sn for _, _, _, _, _, sn in reflections.values()]

print(f"\n{'─'*80}")
print("  4. STATISTICAL SUMMARY")
print(f"{'─'*80}")
print(f"\n  TEST                COUNT   MEAN S/N  PASS RATE")
print(f"  {'─'*50}")
print(f"  Peak (lambda_sync/n)  {len(peaks):<6d} {np.mean(peak_sns):<+9.2f} {peak_pass}/{peak_pass+peak_fail}")
print(f"  Null (midpoints)     {len(nulls):<6d} {np.mean(null_sns):<+9.2f} {null_pass}/{null_pass+null_fail}")
print(f"  Reflection (R_n)     {len(reflections):<6d} {np.mean(refl_sns):<+9.2f} N/A")

# 5. DETAILED TABLE
print(f"\n{'─'*80}")
print("  5. ALL DATA POINTS — Wiggle + Labels")
print(f"{'─'*80}")
print(f"\n  {'s':<8} {'xi_raw':<12} {'xi_wiggle':<12} {'S/N':<10} {'Label':<30}")
print(f"  {'─'*72}")

for i in range(len(s)):
    label = ""
    for n, (s_p, _, _, _) in peaks.items():
        if abs(s[i] - s_p) < 5:
            label = f"PEAK lambda_sync/{n}"
            break
    for n, (s_n, _, _, _) in nulls.items():
        if abs(s[i] - s_n) < 5 and not label:
            label = f"NULL lambda_sync/({n}+0.5)"
            break
    for n, (s_r, _, _, _, _, _) in reflections.items():
        if abs(s[i] - s_r) < 5 and not label:
            label = f"REFL n={n}"
            break
    if not label:
        label = "-"
    
    sn = xi_wiggle[i] / err[i] if err[i] > 0 else 0
    if abs(sn) > 2 or label not in ["-"]:
        print(f"  {s[i]:<8.1f} {xi[i]:<+12.6f} {xi_wiggle[i]:<+12.6f} {sn:<+10.2f} {label:<30}")