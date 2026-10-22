#!/usr/bin/env python3
"""
eBOSS DR16 LRG Correlation Function — Fast Version
===================================================
Compute ξ(s) from eBOSS DR16 LRG data (NGC + SGC, 0.6<z<1.0)
Compare with IDCM K_Chain harmonic predictions.
"""
import math, numpy as np, time, os
from astropy.io import fits
from scipy.spatial import cKDTree

# ===== IDCM params =====
H0 = 72.59
h = H0 / 100
c = 299792.458
R_H = c / H0
lambda_sync = 2 * math.pi * R_H / 88
bao_pred = lambda_sync / 2

print("=" * 70)
print("eBOSS DR16 LRG ξ(s) — IDCM HARMONIC ANALYSIS")
print("=" * 70)
print(f"\nIDCM: H₀={H0}, h={h:.4f}")
print(f"  λ_sync = {lambda_sync:.1f} Mpc")
print(f"  BAO = λ_sync/2 = {bao_pred:.1f} Mpc = {bao_pred/h:.1f} h⁻¹ Mpc")
print(f"  λ_sync/3 = {lambda_sync/3:.1f} Mpc = {lambda_sync/3/h:.1f} h⁻¹ Mpc")

# ===== Cosmology =====
Omega_m = 0.3167
Omega_L = 1 - Omega_m

# Precompute comoving distance table (fast interpolation)
z_table = np.linspace(0, 2, 1000)
D_table = np.zeros_like(z_table)
for i, z in enumerate(z_table):
    z_v = np.linspace(0, z, 200)
    dz = z / 200
    E_z = np.sqrt(Omega_m * (1+z_v)**3 + Omega_L)
    D_table[i] = (c / H0) * np.sum(dz / E_z)

def comoving_distance(z):
    return np.interp(z, z_table, D_table)

# ===== Load data =====
def load_fits(path):
    hdul = fits.open(path)
    d = hdul[1].data
    hdul.close()
    return d

print(f"\nLoading data...")
t0 = time.time()
d_ngc = load_fits('/tmp/eboss_lrg_ngc.fits')
d_sgc = load_fits('/tmp/eboss_lrg_sgc.fits')
ra = np.concatenate([d_ngc['RA'], d_sgc['RA']])
dec = np.concatenate([d_ngc['DEC'], d_sgc['DEC']])
z = np.concatenate([d_ngc['Z'], d_sgc['Z']])
w = np.concatenate([d_ngc['WEIGHT_FKP'] * d_ngc['WEIGHT_SYSTOT'],
                    d_sgc['WEIGHT_FKP'] * d_sgc['WEIGHT_SYSTOT']])
N_gal = len(ra)
print(f"  {N_gal} galaxies, z=[{z.min():.4f},{z.max():.4f}], μ={z.mean():.4f}")

# Convert to Cartesian
pos = np.column_stack([
    comoving_distance(z) * np.cos(np.radians(dec)) * np.cos(np.radians(ra)),
    comoving_distance(z) * np.cos(np.radians(dec)) * np.sin(np.radians(ra)),
    comoving_distance(z) * np.sin(np.radians(dec))
])
print(f"  Dist range: {np.linalg.norm(pos,axis=1).min():.0f}-{np.linalg.norm(pos,axis=1).max():.0f} Mpc")
print(f"  Loaded in {time.time()-t0:.1f}s")

# ===== Load random catalog (subsample) =====
rand_path = '/tmp/eboss_lrg_ngc_random.fits'
rand_sgc_path = '/tmp/eboss_lrg_sgc_random.fits'

print(f"\nLoading random catalog...")
t0 = time.time()
d_rand_ngc = load_fits(rand_path)
d_rand_sgc = load_fits(rand_sgc_path)
ra_r = np.concatenate([d_rand_ngc['RA'], d_rand_sgc['RA']])
dec_r = np.concatenate([d_rand_ngc['DEC'], d_rand_sgc['DEC']])
z_r = np.concatenate([d_rand_ngc['Z'], d_rand_sgc['Z']])
w_r_full = np.concatenate([d_rand_ngc['WEIGHT_FKP'] * d_rand_ngc['WEIGHT_SYSTOT'],
                           d_rand_sgc['WEIGHT_FKP'] * d_rand_sgc['WEIGHT_SYSTOT']])
N_rand_total = len(ra_r)
print(f"  Total random: {N_rand_total}")

# Subsample for computational efficiency
N_rand = 300000
idx = np.random.choice(N_rand_total, N_rand, replace=False)
ra_r = ra_r[idx]; dec_r = dec_r[idx]; z_r = z_r[idx]; w_r = w_r_full[idx]
print(f"  Subsampled to {N_rand}")

# Convert random to Cartesian
pos_r = np.column_stack([
    comoving_distance(z_r) * np.cos(np.radians(dec_r)) * np.cos(np.radians(ra_r)),
    comoving_distance(z_r) * np.cos(np.radians(dec_r)) * np.sin(np.radians(ra_r)),
    comoving_distance(z_r) * np.sin(np.radians(dec_r))
])
print(f"  Loaded in {time.time()-t0:.1f}s")

# ===== Build kd-trees =====
print(f"\nBuilding kd-trees...")
t0 = time.time()
tree_data = cKDTree(pos)
tree_rand = cKDTree(pos_r)
print(f"  Done in {time.time()-t0:.1f}s")

# ===== Define bins =====
s_bins = np.linspace(5, 250, 35)  # 7 Mpc bins → 34 bins
s_centers = (s_bins[:-1] + s_bins[1:]) / 2
ns = len(s_centers)
max_dist = 250 * h  # Mpc

print(f"\nCounting pairs: {ns} bins, max_dist={max_dist:.0f} Mpc...")

# ===== Fast pair counting =====
# Use query_ball_tree for bulk pair counting
def count_pairs(tree1, tree2, w1, w2, s_bins, max_dist, label=""):
    """Count weighted pairs between two trees"""
    ns = len(s_bins) - 1
    counts = np.zeros(ns, dtype=np.float64)
    # query_ball_tree returns indices of pairs within max_dist
    pairs = tree1.query_ball_tree(tree2, max_dist)
    t0 = time.time()
    for i, neighbors in enumerate(pairs):
        wi = w1[i]
        for j in neighbors:
            # Compute distance
            d = np.linalg.norm(tree1.data[i] - tree2.data[j])
            s_val = d / h  # h⁻¹ Mpc
            if s_bins[0] <= s_val <= s_bins[-1]:
                bin_idx = np.searchsorted(s_bins, s_val) - 1
                if 0 <= bin_idx < ns:
                    counts[bin_idx] += wi * w2[j]
    dt = time.time() - t0
    print(f"  {label}: {len(pairs)} roots, {int(counts.sum())} pairs, {dt:.1f}s")
    return counts

# DD pairs
DD = count_pairs(tree_data, tree_data, w, w, s_bins, max_dist, "DD")
# DR pairs
DR = count_pairs(tree_data, tree_rand, w, w_r, s_bins, max_dist, "DR")
# RR pairs  
RR = count_pairs(tree_rand, tree_rand, w_r, w_r, s_bins, max_dist, "RR")

# ===== Normalization =====
alpha = np.sum(w) / np.sum(w_r)  # data/random ratio

# ===== Landy-Szalay estimator =====
xi = np.zeros(ns)
xi_err = np.zeros(ns)
for i in range(ns):
    if RR[i] > 0:
        xi[i] = (DD[i] - 2*alpha*DR[i] + alpha**2*RR[i]) / (alpha**2*RR[i])
        xi_err[i] = np.sqrt(1 + xi[i]) / np.sqrt(RR[i]) if RR[i] > 0 else 0

# ===== Print results =====
print("\n" + "=" * 70)
print("eBOSS DR16 LRG ξ(s) — HARMONIC COMPARISON")
print("=" * 70)
print(f"{'s (h⁻¹ Mpc)':<15} {'ξ(s)':<15} {'± err':<15} {'S/N':<10} {'IDCM':<18} {'Match?':<10}")
print("-" * 83)

for n in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
    lam = bao_pred * 2 / n / h
    nearest = np.argmin(np.abs(s_centers - lam))
    sn = xi[nearest] / xi_err[nearest] if xi_err[nearest] > 0 else 0
    label = f"λ_sync/{n}"
    if n == 2: label += " ← BAO"
    m = "✅" if abs(sn) > 2 else "⚠️" if abs(sn) > 1 else "·"
    print(f"{s_centers[nearest]:<15.1f} {xi[nearest]:<+15.4f} {xi_err[nearest]:<15.4f} {sn:<+10.2f} {label:<18} {m:<10}")

# ===== Find all peaks =====
print("\n" + "=" * 70)
print("ALL PEAKS IN ξ(s) vs HARMONIC PREDICTION")
print("=" * 70)
peaks = []
for i in range(2, ns-2):
    if xi[i] > xi[i-1] and xi[i] > xi[i-2] and xi[i] > xi[i+1] and xi[i] > xi[i+2]:
        if xi[i] > 0.001:
            peaks.append((s_centers[i], xi[i], xi_err[i]))

print(f"{'s (h⁻¹ Mpc)':<15} {'ξ(s)':<15} {'S/N':<10} {'IDCM n':<12} {'λ_sync/n':<15} {'Match?':<10}")
print("-" * 77)
for sp, xip, errp in peaks:
    best_n = min(range(2, 15), key=lambda n: abs(sp - bao_pred*2/n/h))
    lam_pred = bao_pred * 2 / best_n / h
    diff = abs(sp - lam_pred)
    sn = xip / errp if errp > 0 else 0
    m = "✅" if diff < 5 else "⚠️" if diff < 10 else "❌"
    if sn > 1.5:
        label = f"λ_sync/{best_n}"
        if best_n == 2: label += " ← BAO"
        print(f"{sp:<15.1f} {xip:<+15.4f} {sn:<+10.2f} n={best_n:<8} {label:<15} {m:<10}")

# ===== Save =====
out = '/home/wsl/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt'
with open(out, 'w') as f:
    f.write('# s (h⁻¹ Mpc)  xi(s)  err  DD  DR  RR\n')
    for i in range(ns):
        f.write(f"{s_centers[i]:.2f} {xi[i]:.6f} {xi_err[i]:.6f} {DD[i]:.0f} {DR[i]:.0f} {RR[i]:.0f}\n")
print(f"\nSaved to: {out}")

# ===== Summary =====
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
eBOSS DR16 LRG (0.6<z<1.0): {N_gal} galaxies, {N_rand} random
IDCM BAO = {bao_pred/h:.1f} h⁻¹ Mpc — {'WITHIN' if bao_pred/h < 250 else 'BEYOND'} data range

Harmonic matches:
  λ_sync/2 = {bao_pred*2/2/h:.1f} h⁻¹ Mpc → {'✅' if bao_pred*2/2/h < 250 else '❌'}
  λ_sync/3 = {bao_pred*2/3/h:.1f} h⁻¹ Mpc → {'✅' if bao_pred*2/3/h < 250 else '❌'}
  λ_sync/4 = {bao_pred*2/4/h:.1f} h⁻¹ Mpc
  λ_sync/5 = {bao_pred*2/5/h:.1f} h⁻¹ Mpc
  λ_sync/6 = {bao_pred*2/6/h:.1f} h⁻¹ Mpc
""")