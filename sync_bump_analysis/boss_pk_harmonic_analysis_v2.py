#!/usr/bin/env python3
"""
BOSS DR12 Power Spectrum — BAO Wiggle Harmonic Analysis v2
===========================================================
Fix: properly average duplicate k-bins before smoothing.
Test if BAO wiggles have exact harmonic spacing Δk = 2π/λ_sync.
"""
import math, tarfile, numpy as np
from scipy.ndimage import gaussian_filter1d

# ===== IDCM params =====
H0 = 72.59
h = 0.676
R_H = 299792.458 / H0
lambda_sync = 2 * math.pi * R_H / 88  # Mpc
dk_pred = 2 * math.pi / lambda_sync * h  # h/Mpc fundamental spacing

print("=" * 70)
print("BOSS DR12 P(k) BAO WIGGLE HARMONIC ANALYSIS v2")
print("=" * 70)
print(f"\nIDCM:")
print(f"  λ_sync = {lambda_sync:.1f} Mpc")
print(f"  BAO = λ_sync/2 = {lambda_sync/2:.1f} Mpc")
print(f"  Δk = {dk_pred:.4f} h/Mpc  (fundamental)")
print(f"  BAO at k = 2·Δk = {2*dk_pred:.4f} h/Mpc")

# ===== Load data =====
t = tarfile.open('/home/wsl/IDCM/sync_bump_analysis/beutler_dr12_powspec.tar.gz')
all_k, all_P, all_err = [], [], []
for zbin in ['z1', 'z2', 'z3']:
    for region in ['NGC', 'SGC']:
        fname = f'public_material_BAO/Beutleretal_pk_monopole_DR12_{region}_{zbin}_postrecon_120.dat'
        if fname not in t.getnames():
            continue
        data = t.extractfile(fname).read().decode('latin-1')
        lines = data.strip().split('\n')
        data_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('###'):
                data_start = i + 1
        for i in range(data_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 4:
                try:
                    all_k.append(float(parts[1]))
                    all_P.append(float(parts[2]))
                    all_err.append(float(parts[3]))
                except:
                    pass

# ===== Average duplicate k-bins =====
k_arr = np.array(all_k)
P_arr = np.array(all_P)
err_arr = np.array(all_err)

# Sort by k
idx = np.argsort(k_arr)
k_arr = k_arr[idx]; P_arr = P_arr[idx]; err_arr = err_arr[idx]

# Average identical k values
unique_k = np.unique(k_arr)
k = unique_k.copy()
P = np.array([np.mean(P_arr[k_arr == uk]) for uk in unique_k])
err = np.array([np.sqrt(np.mean(err_arr[k_arr == uk]**2)) for uk in unique_k])

print(f"\nLoaded {len(all_k)} raw pts → {len(k)} unique k bins")
print(f"k range: {k[0]:.4f} to {k[-1]:.4f} h/Mpc")
print(f"k step: ~{np.mean(np.diff(k)):.4f} h/Mpc")

# ===== Smooth =====
logP = np.log(P)
P_smooth = np.exp(gaussian_filter1d(logP, sigma=3, mode='nearest'))
wiggle = P / P_smooth - 1

print("\n" + "="*70)
print("BAO WIGGLES (averaged)")
print("="*70)
print(f"{'k (h/Mpc)':<15} {'P(k)':<15} {'P_smooth':<15} {'Wiggle':<15} {'IDCM n':<10}")
print("-"*70)
for i in range(len(k)):
    if 0.02 <= k[i] <= 0.30:
        best_n = min(range(2, 20), key=lambda n: abs(k[i] - n*dk_pred))
        print(f"{k[i]:<15.4f} {P[i]:<15.1f} {P_smooth[i]:<15.1f} {wiggle[i]:<+15.4f} n={best_n:<6}")

# ===== Find wiggle peaks (zero-crossings of derivative) =====
# Use interpolated wiggle to find peak positions
from scipy.interpolate import interp1d
k_fine = np.linspace(k.min(), k.max(), 500)
wiggle_interp = interp1d(k, wiggle, kind='cubic')(k_fine)
wiggle_interp_smooth = gaussian_filter1d(wiggle_interp, sigma=2)

# Find peaks: where derivative crosses zero (positive to negative)
dwiggle = np.gradient(wiggle_interp_smooth)
peaks = []
for i in range(1, len(dwiggle)-1):
    if dwiggle[i-1] > 0 and dwiggle[i] <= 0:
        if 0.02 <= k_fine[i] <= 0.30 and wiggle_interp_smooth[i] > 0.005:
            peaks.append(k_fine[i])

print("\n" + "="*70)
print("WIGGLE PEAKS vs HARMONIC PREDICTION")
print("="*70)
print(f"IDCM Δk = {dk_pred:.4f} h/Mpc")
print(f"Found {len(peaks)} peaks\n")
print(f"{'k_peak':<15} {'IDCM n·Δk':<18} {'n':<6} {'Match?':<10}")
print("-"*49)
good_peaks = []
for kp in peaks:
    best_n = min(range(2, 20), key=lambda n: abs(kp - n*dk_pred))
    pred = best_n * dk_pred
    diff = abs(kp - pred)
    good_peaks.append((kp, best_n, diff))
    match = "✅" if diff < 0.005 else "⚠️" if diff < 0.01 else "❌"
    print(f"{kp:<15.4f} {pred:<18.4f} n={best_n:<3} {match:<10}")

# ===== Harmonic spacing test =====
print("\n" + "="*70)
print("HARMONIC SPACING TEST")
print("="*70)
if len(good_peaks) >= 3:
    spacings = [good_peaks[i+1][0] - good_peaks[i][0] for i in range(len(good_peaks)-1)]
    mean_dk = np.mean(spacings)
    std_dk = np.std(spacings)
    print(f"Measured mean Δk = {mean_dk:.4f} ± {std_dk:.4f} h/Mpc")
    print(f"IDCM prediction: Δk = {dk_pred:.4f} h/Mpc")
    print(f"Deviation: {abs(mean_dk - dk_pred):.4f} ({abs(mean_dk/dk_pred - 1)*100:.1f}%)")
    if abs(mean_dk - dk_pred) < 2*std_dk:
        print("✅ Consistent with IDCM harmonic spacing")
    else:
        print("⚠️ Deviation > 2σ — not conclusive with this data")

# ===== BAO position =====
print("\n" + "="*70)
print("BAO PEAK POSITION")
print("="*70)
# The BAO is the strongest wiggle — find the max wiggle near k ~ 0.03-0.06
bao_region = [(k[i], wiggle[i]) for i in range(len(k)) if 0.025 <= k[i] <= 0.06]
if bao_region:
    k_bao, wiggle_bao = zip(*bao_region)
    k_bao_arr = np.array(k_bao); wiggle_bao_arr = np.array(wiggle_bao)
    # Interpolate to find peak
    k_bao_fine = np.linspace(k_bao_arr.min(), k_bao_arr.max(), 200)
    wiggle_bao_interp = interp1d(k_bao_arr, wiggle_bao_arr, kind='cubic')(k_bao_fine)
    wiggle_bao_smooth = gaussian_filter1d(wiggle_bao_interp, sigma=3)
    bao_peak_k = k_bao_fine[np.argmax(wiggle_bao_smooth)]
    print(f"BAO peak at k = {bao_peak_k:.4f} h/Mpc")
    print(f"IDCM predicts n=2: k = {2*dk_pred:.4f} h/Mpc")
    print(f"   → λ = {2*math.pi/bao_peak_k/h:.1f} h⁻¹ Mpc")
    print(f"   → IDCM λ_sync/2 = {lambda_sync/2/h:.1f} h⁻¹ Mpc")

print(f"\nWiggle data saved to: boss_dr12_bao_wiggles.txt")
with open('/home/wsl/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt', 'w') as f:
    f.write('# k (h/Mpc)  P(k)  P_smooth  Wiggle\n')
    for i in range(len(k)):
        if 0.01 <= k[i] <= 0.40:
            f.write(f"{k[i]:.6f} {P[i]:.1f} {P_smooth[i]:.1f} {wiggle[i]:.6f}\n")