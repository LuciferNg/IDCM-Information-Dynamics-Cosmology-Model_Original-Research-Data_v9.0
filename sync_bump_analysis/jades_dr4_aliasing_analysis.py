#!/usr/bin/env python3
"""
JADES DR4 Spectroscopic Catalog — Deep Aliasing Analysis
Checks if the φ-ratio pattern is real or a selection effect from
the luminosity function and spectroscopic targeting.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.signal import find_peaks
from scipy.special import gamma, gammaincc
from scipy.integrate import quad
import os

# ============================================================
# 1. Load data
# ============================================================
print("=" * 70)
print("JADES DR4 SPECTROSCOPIC CATALOG — DEEP ALIASING ANALYSIS")
print("=" * 70)

with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    data = hdul[2].data  # HDU 2 = R100_5pix

z = data['z_PRISM']
z_flag = data['Z_FLAG']
uid = data['Unique_ID']
nid = data['NIRCam_DR5_ID']

# Filter out NaN/bad z
mask = np.isfinite(z) & (z > 0) & (z < 15)
z = z[mask]
z_flag = z_flag[mask]
uid = uid[mask]
nid = nid[mask]

print(f"\nTotal sources: {len(z)} (after filtering NaN/out-of-range z)")

# ============================================================
# 2. z_PRISM distribution, bins of 0.1
# ============================================================
bins = np.arange(0, 15.1, 0.1)
bin_centers = (bins[:-1] + bins[1:]) / 2
counts, _ = np.histogram(z, bins=bins)

print(f"\n--- z_PRISM distribution (bin=0.1, z=0 to 15) ---")
print(f"Total in histogram: {counts.sum()}")
print(f"Max bin count: {counts.max()} at z~{bin_centers[counts.argmax()]:.2f}")

# Find all local maxima using scipy
peaks, properties = find_peaks(counts, prominence=1, width=1)
peak_zs = bin_centers[peaks]
peak_counts = counts[peaks]
prominences = properties['prominences']

print(f"\nLocal maxima found: {len(peaks)}")
print(f"{'z':>8s} {'count':>8s} {'prominence':>12s}")
print("-" * 30)
for pz, pc, pp in sorted(zip(peak_zs, peak_counts, prominences), key=lambda x: -x[1]):
    print(f"{pz:>8.2f} {pc:>8d} {pp:>12.2f}")

# ============================================================
# 3. Check Fibonacci aliasing points
# ============================================================
fib_points = [5.6, 6.9, 7.7, 8.2, 8.5, 8.9, 9.2, 9.5, 10.0, 13.5, 14.0]
print(f"\n{'='*70}")
print(f"3. FIBONACCI ALIASING POINT CHECK")
print(f"{'='*70}")

def find_nearest_peak(z_target, peaks_z, peaks_counts, bins):
    """Find the nearest local maximum to a target redshift."""
    idx = np.argmin(np.abs(peaks_z - z_target))
    return peaks_z[idx], peaks_counts[idx], abs(peaks_z[idx] - z_target)

# Also check the bin counts directly
def bin_idx_for_z(z_target):
    return int(np.searchsorted(bins, z_target) - 1)

print(f"{'Target z':>10s} {'Nearest peak':>13s} {'Count':>8s} {'Delta':>8s} {'Bin count':>10s}")
print("-" * 55)
for fz in fib_points:
    nz, nc, nd = find_nearest_peak(fz, peak_zs, peak_counts, bins)
    bi = bin_idx_for_z(fz)
    bc = counts[bi] if 0 <= bi < len(counts) else 0
    flag = " <<< MATCH" if nd < 0.15 else ""
    print(f"{fz:>10.2f} {nz:>13.2f} {nc:>8d} {nd:>8.3f} {bc:>10d}{flag}")

# ============================================================
# 4. Z_FLAG quality comparison
# ============================================================
print(f"\n{'='*70}")
print(f"4. Z_FLAG QUALITY COMPARISON")
print(f"{'='*70}")

# Z_FLAG is a set-notation string like '{4, 5, 6, 7}' or '{6, 7}'
# Parse: check if '4' is in the set (low quality), vs '6' or '7' (high quality)
def parse_zflag(zf_str):
    """Parse Z_FLAG string like '{6, 7}' into a set of integers."""
    try:
        s = str(zf_str).strip()
        if s.startswith('{') and s.endswith('}'):
            inner = s[1:-1].strip()
            if inner:
                return set(int(x.strip()) for x in inner.split(','))
        return set()
    except (ValueError, AttributeError):
        return set()

zflag_sets = np.array([parse_zflag(f) for f in z_flag])

# Low quality: Z_FLAG includes 4 (and is not empty)
low_qual = np.array([4 in s for s in zflag_sets])
# High quality: includes 6 or 7, but NOT 4
high_qual = np.array([(6 in s or 7 in s) and 4 not in s for s in zflag_sets])

print(f"\nLow quality (Z_FLAG=4): {low_qual.sum()} sources")
print(f"High quality (Z_FLAG=6,7): {high_qual.sum()} sources")

counts_low, _ = np.histogram(z[low_qual], bins=bins)
counts_high, _ = np.histogram(z[high_qual], bins=bins)

# Find peaks in each
peaks_low, _ = find_peaks(counts_low, prominence=1, width=1)
peaks_high, _ = find_peaks(counts_high, prominence=1, width=1)

print(f"\nLow-quality peaks: {len(peaks_low)}")
print(f"High-quality peaks: {len(peaks_high)}")

print(f"\nLow-quality peaks at z:")
for pz in sorted(bin_centers[peaks_low]):
    pi = np.where(bin_centers == pz)[0][0]
    print(f"  z={pz:.2f} (count={counts_low[pi]})")

print(f"\nHigh-quality peaks at z:")
for pz in sorted(bin_centers[peaks_high]):
    pi = np.where(bin_centers == pz)[0][0]
    print(f"  z={pz:.2f} (count={counts_high[pi]})")

# Check if fib points appear more strongly in low-quality
print(f"\nFibonacci aliasing points by Z_FLAG quality:")
for fz in fib_points:
    bi = bin_idx_for_z(fz)
    if 0 <= bi < len(counts):
        cl = counts_low[bi]
        ch = counts_high[bi]
        ratio_low = cl / counts_low.sum() * 100
        ratio_high = ch / counts_high.sum() * 100
        print(f"  z={fz:>5.2f}: low={cl:>4d} ({ratio_low:.2f}%), high={ch:>4d} ({ratio_high:.2f}%)")

# ============================================================
# 5. GOODS-S vs GOODS-N
# ============================================================
print(f"\n{'='*70}")
print(f"5. GOODS-S vs GOODS-N FIELD COMPARISON")
print(f"{'='*70}")

uid_str = np.array([str(u).lower() for u in uid])
goods_s = np.array(['goods-s' in u for u in uid_str])
goods_n = np.array(['goods-n' in u for u in uid_str])

print(f"\nGOODS-S: {goods_s.sum()} sources")
print(f"GOODS-N: {goods_n.sum()} sources")
print(f"Other: {(~goods_s & ~goods_n).sum()} sources")

counts_s, _ = np.histogram(z[goods_s], bins=bins)
counts_n, _ = np.histogram(z[goods_n], bins=bins)

peaks_s, _ = find_peaks(counts_s, prominence=1, width=1)
peaks_n, _ = find_peaks(counts_n, prominence=1, width=1)

print(f"\nGOODS-S peaks: {len(peaks_s)}")
print(f"GOODS-N peaks: {len(peaks_n)}")

print(f"\nGOODS-S peaks at z:")
for pz in sorted(bin_centers[peaks_s]):
    pi = np.where(bin_centers == pz)[0][0]
    print(f"  z={pz:.2f} (count={counts_s[pi]})")

print(f"\nGOODS-N peaks at z:")
for pz in sorted(bin_centers[peaks_n]):
    pi = np.where(bin_centers == pz)[0][0]
    print(f"  z={pz:.2f} (count={counts_n[pi]})")

# Check fib points for each field
print(f"\nFibonacci aliasing points by field:")
for fz in fib_points:
    bi = bin_idx_for_z(fz)
    if 0 <= bi < len(counts):
        cs = counts_s[bi]
        cn = counts_n[bi]
        print(f"  z={fz:>5.2f}: GOODS-S={cs:>4d}, GOODS-N={cn:>4d}")

# ============================================================
# 6. PHI-RATIO AT 5.6→6.9
# ============================================================
print(f"\n{'='*70}")
print(f"6. PHI-RATIO ANALYSIS: z=5.6 vs z=6.9")
print(f"{'='*70}")

phi = 1.618033988749895
phi_ratio = 6.9 / 5.6
print(f"\nObserved ratio 6.9/5.6 = {phi_ratio:.6f}")
print(f"Golden ratio φ = {phi:.6f}")
print(f"Deviation from φ: {(phi_ratio - phi)/phi*100:.2f}%")

# Observed counts at these bins
bi_56 = bin_idx_for_z(5.6)
bi_69 = bin_idx_for_z(6.9)
print(f"\nz=5.6 bin [{bins[bi_56]:.1f}, {bins[bi_56+1]:.1f}): count = {counts[bi_56]}")
print(f"z=6.9 bin [{bins[bi_69]:.1f}, {bins[bi_69+1]:.1f}): count = {counts[bi_69]}")
print(f"Observed N(6.9)/N(5.6) = {counts[bi_69]/counts[bi_56]:.4f}")

# Also look at the full peak region
# Find the actual peak centers nearest to 5.6 and 6.9
peak_56 = peak_zs[np.argmin(np.abs(peak_zs - 5.6))]
peak_69 = peak_zs[np.argmin(np.abs(peak_zs - 6.9))]
count_56 = peak_counts[np.argmin(np.abs(peak_zs - 5.6))]
count_69 = peak_counts[np.argmin(np.abs(peak_zs - 6.9))]
print(f"\nNearest peak to 5.6: z={peak_56:.2f}, count={count_56}")
print(f"Nearest peak to 6.9: z={peak_69:.2f}, count={count_69}")
print(f"Peak ratio N(6.9)/N(5.6) = {count_69/count_56:.4f}")

# ============================================================
# 7. LUMINOSITY FUNCTION TEST
# ============================================================
print(f"\n{'='*70}")
print(f"7. LUMINOSITY FUNCTION SELECTION EFFECT TEST")
print(f"{'='*70}")

# Schechter luminosity function: phi(L) dL = phi* (L/L*)^alpha exp(-L/L*) d(L/L*)
# In magnitude terms: phi(M) dM = 0.4 ln(10) phi* 10^(0.4(alpha+1)(M*-M)) exp(-10^(0.4(M*-M))) dM
# The expected N(z) in a flux-limited sample goes as:
# N(z) ∝ dV/dz * integral of phi(M) over M < M_limit(z)
# where M_limit(z) = m_limit - 5*log10(d_L(z)/10pc) - K(z)

alpha = -1.7  # typical faint-end slope at z~5-7
M_star = -21.0  # characteristic magnitude at z~5-7

def schechter_mag(M, alpha, M_star):
    """Schechter function in magnitude units (unnormalized)."""
    x = 10**(0.4 * (M_star - M))
    return x**(alpha + 1) * np.exp(-x)

# Cosmological parameters
Omega_m = 0.315
Omega_L = 0.685
H0 = 67.4
c = 3e5  # km/s

def dL(z):
    """Luminosity distance in Mpc (flat LCDM)."""
    def E(zp):
        return 1.0 / np.sqrt(Omega_m * (1+zp)**3 + Omega_L)
    dc, _ = quad(lambda zp: c / (H0 * np.sqrt(Omega_m*(1+zp)**3 + Omega_L)), 0, z)
    return dc * (1 + z)

def dV_dz(z):
    """Comoving volume element per steradian per unit redshift."""
    dc, _ = quad(lambda zp: c / (H0 * np.sqrt(Omega_m*(1+zp)**3 + Omega_L)), 0, z)
    E_z = np.sqrt(Omega_m * (1+z)**3 + Omega_L)
    return c / H0 * dc**2 / E_z

z_vals = [5.6, 6.9]
m_lim = 28.5  # typical NIRSpec magnitude limit

print(f"\nUsing Schechter parameters: alpha={alpha}, M*={M_star}")
print(f"Assumed magnitude limit: m_lim={m_lim}")
print(f"\n{'z':>6s} {'dL(Mpc)':>12s} {'dV/dz':>12s} {'M_lim(z)':>10s} {'phi(M_lim)':>12s}")
print("-" * 50)

results = {}
for zv in z_vals:
    dl = dL(zv)
    vol = dV_dz(zv)
    # Typical K-correction for star-forming at z~6: ~1.5 mag
    K_corr = 1.5
    M_lim = m_lim - 5 * np.log10(dl / 10) - K_corr
    # Schechter at M_lim
    phi_at_lim = schechter_mag(M_lim, alpha, M_star)
    
    print(f"{zv:>6.1f} {dl:>12.1f} {vol:>12.2e} {M_lim:>10.2f} {phi_at_lim:>12.2e}")
    results[zv] = {'dl': dl, 'vol': vol, 'M_lim': M_lim, 'phi_lim': phi_at_lim}

ratio_vol = results[6.9]['vol'] / results[5.6]['vol']
ratio_phi = results[6.9]['phi_lim'] / results[5.6]['phi_lim']
ratio_expected = ratio_vol * ratio_phi

print(f"\nVolume ratio V(6.9)/V(5.6) = {ratio_vol:.4f}")
print(f"LF ratio phi(6.9)/phi(5.6) = {ratio_phi:.4f}")
print(f"Expected N(6.9)/N(5.6) (from LF selection) = {ratio_expected:.4f}")

# Also compute the integrated LF more carefully
def cumulative_schechter(M_lim, alpha, M_star):
    """
    Cumulative Schechter function: integral of phi(M) dM from -inf to M_lim.
    N(<M_lim) ∝ Gamma(alpha+2, x_lim) where x_lim = 10^(0.4*(M_star - M_lim))
    """
    x_lim = 10**(0.4 * (M_star - M_lim))
    return gamma(alpha + 2) * gammaincc(alpha + 2, x_lim)

print(f"\n--- Integrated Schechter function ---")
for zv in z_vals:
    cum = cumulative_schechter(results[zv]['M_lim'], alpha, M_star)
    print(f"z={zv:.1f}: N_cum(<M_lim) = {cum:.4f}")
    results[zv]['cum'] = cum

ratio_cum = results[6.9]['cum'] / results[5.6]['cum']
ratio_full = ratio_vol * ratio_cum

print(f"\nVolume ratio: {ratio_vol:.4f}")
print(f"Cumulative LF ratio: {ratio_cum:.4f}")
print(f"Expected N(6.9)/N(5.6) = {ratio_full:.4f}")
print(f"Observed N(6.9)/N(5.6) = {counts[bi_69]/counts[bi_56]:.4f}")
print(f"Observed peak ratio: {count_69/count_56:.4f}")

# Sensitivity to K-correction
print(f"\n--- Sensitivity to K-correction ---")
for K_corr in [0.5, 1.0, 1.5, 2.0, 2.5]:
    for zv in z_vals:
        dl = results[zv]['dl']
        M_lim = m_lim - 5 * np.log10(dl / 10) - K_corr
        results[zv]['M_lim_k'] = M_lim
        results[zv]['cum_k'] = cumulative_schechter(M_lim, alpha, M_star)
    
    r_vol = results[6.9]['vol'] / results[5.6]['vol']
    r_cum = results[6.9]['cum_k'] / results[5.6]['cum_k']
    r_total = r_vol * r_cum
    print(f"  K={K_corr:.1f}: M_lim(5.6)={results[5.6]['M_lim_k']:.2f}, M_lim(6.9)={results[6.9]['M_lim_k']:.2f}, "
          f"ratio={r_total:.4f}")

# Sensitivity to magnitude limit
print(f"\n--- Sensitivity to magnitude limit ---")
for m_lim_test in [27.0, 27.5, 28.0, 28.5, 29.0, 29.5]:
    K_corr = 1.5
    for zv in z_vals:
        dl = results[zv]['dl']
        M_lim = m_lim_test - 5 * np.log10(dl / 10) - K_corr
        results[zv]['M_lim_m'] = M_lim
        results[zv]['cum_m'] = cumulative_schechter(M_lim, alpha, M_star)
    
    r_vol = results[6.9]['vol'] / results[5.6]['vol']
    r_cum = results[6.9]['cum_m'] / results[5.6]['cum_m']
    r_total = r_vol * r_cum
    print(f"  m_lim={m_lim_test:.1f}: ratio={r_total:.4f}")

# Sensitivity to alpha
print(f"\n--- Sensitivity to faint-end slope alpha ---")
for alpha_test in [-2.0, -1.9, -1.8, -1.7, -1.6, -1.5]:
    m_lim_test = 28.5
    K_corr = 1.5
    for zv in z_vals:
        dl = results[zv]['dl']
        M_lim = m_lim_test - 5 * np.log10(dl / 10) - K_corr
        results[zv]['cum_a'] = cumulative_schechter(M_lim, alpha_test, M_star)
    
    r_vol = results[6.9]['vol'] / results[5.6]['vol']
    r_cum = results[6.9]['cum_a'] / results[5.6]['cum_a']
    r_total = r_vol * r_cum
    print(f"  alpha={alpha_test:.1f}: ratio={r_total:.4f}")

# ============================================================
# 8. SPECTROSCOPIC TARGETING SELECTION EFFECTS
# ============================================================
print(f"\n{'='*70}")
print(f"8. SPECTROSCOPIC TARGETING BIAS ANALYSIS")
print(f"{'='*70}")

print(f"\nEmission line positions in NIRCam filters:")
print(f"{'Line':>15s} {'z=5.6':>15s} {'z=6.9':>15s}")
print("-" * 45)
lines = [('Ly-alpha 1216A', 1216), ('CIV 1549A', 1549), ('CIII] 1907A', 1907),
         ('[OII] 3727A', 3727), ('[OIII] 5007A', 5007), ('H-alpha 6563A', 6563)]
for name, wave in lines:
    obs_56 = wave * (1 + 5.6)
    obs_69 = wave * (1 + 6.9)
    print(f"{name:>15s} {obs_56:>8.0f}A {obs_69:>8.0f}A")

# NIRCam filters
nircam_filters = {'F090W': 0.9, 'F115W': 1.15, 'F150W': 1.5, 'F200W': 2.0,
                  'F277W': 2.77, 'F356W': 3.56, 'F410M': 4.1, 'F444W': 4.44}
print(f"\nNIRCam filter coverage (um):")
for fname, fwave in nircam_filters.items():
    print(f"  {fname}: {fwave:.2f} um ({fwave*1e4:.0f} A)")

print(f"\nKey: At z=5.6, Ly-alpha falls at {1216*(1+5.6):.0f}A = {1216*(1+5.6)/1e4:.2f}um")
print(f"      At z=6.9, Ly-alpha falls at {1216*(1+6.9):.0f}A = {1216*(1+6.9)/1e4:.2f}um")

# ============================================================
# 9. Save plots
# ============================================================
print(f"\n{'='*70}")
print("9. GENERATING PLOTS")
print(f"{'='*70}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Full distribution
ax = axes[0, 0]
ax.bar(bin_centers, counts, width=0.08, alpha=0.7, color='steelblue', edgecolor='navy', linewidth=0.5)
ax.plot(bin_centers[peaks], counts[peaks], 'ro', markersize=5, label=f'Local maxima (n={len(peaks)})')
for fz in fib_points:
    ax.axvline(fz, color='red', alpha=0.3, linestyle=':', linewidth=0.8)
ax.set_xlabel('z_PRISM')
ax.set_ylabel('Number of sources')
ax.set_title('JADES DR4 Spectroscopic: z_PRISM Distribution\n(bin=0.1, red dashed=φ-aliasing points)')
ax.set_xlim(0, 15)
ax.legend(fontsize=8)

# Plot 2: Zoom z=4-11
ax = axes[0, 1]
ax.bar(bin_centers, counts, width=0.08, alpha=0.7, color='steelblue', edgecolor='navy', linewidth=0.5)
ax.plot(bin_centers[peaks], counts[peaks], 'ro', markersize=5)
for fz in fib_points:
    ax.axvline(fz, color='red', alpha=0.5, linestyle=':', linewidth=1.0)
    ax.text(fz, ax.get_ylim()[1]*0.95, f'{fz:.1f}', rotation=90, fontsize=7, color='red', alpha=0.7)
ax.set_xlabel('z_PRISM')
ax.set_ylabel('Number of sources')
ax.set_title('Zoom: z=4-11')
ax.set_xlim(4, 11)
ax.axvline(5.6, color='green', linestyle='--', alpha=0.5, label='φ-ratio pair')
ax.axvline(6.9, color='green', linestyle='--', alpha=0.5)
ax.legend(fontsize=8)

# Plot 3: Z_FLAG comparison
ax = axes[1, 0]
ax.bar(bin_centers - 0.02, counts_low, width=0.04, alpha=0.6, color='coral', label=f'Z_FLAG=4 (low qual, n={low_qual.sum()})')
ax.bar(bin_centers + 0.02, counts_high, width=0.04, alpha=0.6, color='seagreen', label=f'Z_FLAG=6,7 (high qual, n={high_qual.sum()})')
ax.set_xlabel('z_PRISM')
ax.set_ylabel('Number of sources')
ax.set_title('Z_FLAG Quality Comparison')
ax.set_xlim(4, 11)
ax.legend(fontsize=8)

# Plot 4: GOODS-S vs GOODS-N
ax = axes[1, 1]
ax.bar(bin_centers - 0.02, counts_s, width=0.04, alpha=0.6, color='goldenrod', label=f'GOODS-S (n={goods_s.sum()})')
ax.bar(bin_centers + 0.02, counts_n, width=0.04, alpha=0.6, color='purple', label=f'GOODS-N (n={goods_n.sum()})')
ax.set_xlabel('z_PRISM')
ax.set_ylabel('Number of sources')
ax.set_title('GOODS-S vs GOODS-N')
ax.set_xlim(4, 11)
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('jades_dr4_aliasing_analysis.png', dpi=150)
print("Saved: jades_dr4_aliasing_analysis.png")

# Additional plot: detailed phi-ratio region
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(bin_centers, counts, width=0.08, alpha=0.7, color='steelblue', edgecolor='navy', linewidth=0.5)
# Mark the phi-ratio pair
ax2.axvspan(5.55, 5.65, color='green', alpha=0.15, label='z=5.6 bin')
ax2.axvspan(6.85, 6.95, color='red', alpha=0.15, label='z=6.9 bin')
ax2.axvline(5.6, color='green', linestyle='--', linewidth=1.5)
ax2.axvline(6.9, color='red', linestyle='--', linewidth=1.5)
# Annotate
ax2.annotate(f'Count: {counts[bi_56]}', xy=(5.6, counts[bi_56]), xytext=(5.2, counts[bi_56]*1.3),
             arrowprops=dict(arrowstyle='->', color='green'), fontsize=10, color='green')
ax2.annotate(f'Count: {counts[bi_69]}', xy=(6.9, counts[bi_69]), xytext=(7.2, counts[bi_69]*1.3),
             arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')
ax2.set_xlabel('z_PRISM')
ax2.set_ylabel('Number of sources')
ax2.set_title(f'φ-ratio Pair: N(6.9)/N(5.6) = {counts[bi_69]/counts[bi_56]:.4f}  (φ = {phi:.4f})')
ax2.set_xlim(4.5, 8.5)
ax2.legend()
plt.tight_layout()
plt.savefig('jades_dr4_phi_ratio_detail.png', dpi=150)
print("Saved: jades_dr4_phi_ratio_detail.png")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)