#!/usr/bin/env python3
"""
CEERS DR1 Aliasing Structure Analysis
======================================
IDCM: Fibonacci aliasing cascade in CEERS photometric catalog
Using 87,345 galaxies, 407 z>7, 186 z>8

Author: 調律者 calibrator
Framework: IDCM (Information Dynamics Cosmology Model)
"""
import warnings, gzip, io, os, sys
warnings.filterwarnings('ignore')
import numpy as np
from astropy.io import fits
from collections import Counter, defaultdict
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(SCRIPT_DIR, 'ceers_dr1_catalog.fits.gz')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'verification/ceers_aliasing_analysis.json')
PLOT_DIR = os.path.join(SCRIPT_DIR, 'verification/plots')

os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ── Load CEERS DR1 catalog ──
print("=" * 70)
print("  CEERS DR1 Aliasing Structure Analysis")
print("=" * 70)

print("\n  Loading catalog...")
with gzip.open(CATALOG_PATH, 'rb') as f:
    with fits.open(io.BytesIO(f.read())) as hdul:
        data = hdul[1].data
        cols = hdul[1].columns.names

print(f"  Total sources: {len(data)}")
print(f"  Columns: {len(cols)}")

# ── Extract key columns ──
z_med = data['LP_Z_MED'].astype(float)
z_lo = data['LP_Z_MED68_LOW'].astype(float)
z_hi = data['LP_Z_MED68_HIGH'].astype(float)
z_best = data['LP_Z_BEST'].astype(float)
mass = data['LP_MASS_MED'].astype(float)
mass_lo = data['LP_MASS_MED68_LOW'].astype(float)
mass_hi = data['LP_MASS_MED68_HIGH'].astype(float)
sfr = data['LP_SFR_MED'].astype(float)
chi2 = data['LP_FIT_CHI'].astype(float)
nbands = data['LP_NBANDS'].astype(float)
ra = data['RA'].astype(float)
dec = data['DEC'].astype(float)

# ── Quality cuts ──
# Valid redshift
valid = (z_med > 0) & (z_med < 25) & (z_med != 99.0) & (~np.isnan(z_med))
# Quality: z_lo > 0.5 (not scattered from z=0)
quality = valid & (z_lo > 0.5) & (nbands >= 5)
print(f"\n  Valid redshifts: {valid.sum()}")
print(f"  Quality (z_lo>0.5, nbands>=5): {quality.sum()}")

# ── IDCM Fibonacci aliasing points ──
aliasing_zs = {
    'z=5.6': 5.6,
    'z=6.9': 6.9,
    'z=7.7': 7.7,
    'z=8.2': 8.2,
    'z=8.5': 8.5,
    'z=8.9': 8.9,
    'z=9.2': 9.2,
    'z=9.5': 9.5,
    'z=10.0': 10.0,
    'z=13.5': 13.5,
    'z=14.0': 14.0,
    'z=17.0': 17.0,
}

# Fibonacci alias series
fib_seq = [5, 8, 13, 21, 34, 55, 89]
fib_aliasing = {f'z=F_{i}/10': fib_seq[i]/10 for i in range(len(fib_seq))}

print(f"\n── Aliasing Point Clustering ──")
tol = 0.3

aliasing_stats = {}
for name, az in {**aliasing_zs, **fib_aliasing}.items():
    mask = quality & (np.abs(z_med - az) < tol)
    n = mask.sum()
    if n > 0:
        z_mean = z_med[mask].mean()
        z_std = z_med[mask].std()
        mass_mean = mass[mask].mean()
        sfr_mean = sfr[mask].mean()
        chi2_mean = chi2[mask].mean()
    else:
        z_mean = z_std = mass_mean = sfr_mean = chi2_mean = 0
    
    aliasing_stats[name] = {
        'z_target': az,
        'count': int(n),
        'z_mean': float(z_mean),
        'z_std': float(z_std),
        'mass_mean': float(mass_mean),
        'sfr_mean': float(sfr_mean),
        'chi2_mean': float(chi2_mean),
    }
    print(f"  {name:>12s} (z={az:.1f}): {n:>5d} galaxies, z_mean={z_mean:.3f}±{z_std:.3f}")

# ── Aliasing ratio test: z_best / z_true ──
# If z_med is an alias of a lower z, then z_med = φ * z_true
phi = (1 + 5**0.5) / 2

print(f"\n── Aliasing Ratio Test ──")
for name, az in list(aliasing_zs.items())[:6]:
    # Get galaxies at this aliasing point
    mask = quality & (np.abs(z_med - az) < tol)
    if mask.sum() < 5:
        continue
    
    # Check if their z_med / z_lo is close to φ
    z_ratio = z_med[mask] / np.maximum(z_lo[mask], 0.1)
    ratio_mean = z_ratio.mean()
    ratio_std = z_ratio.std()
    
    # Check if z_med / (z_med - 0.5) ≈ φ
    # (the 0.5 offset accounts for the rendering offset)
    
    n_phi_close = sum(np.abs(z_ratio - phi) < 0.5)
    phi_frac = n_phi_close / mask.sum() * 100
    
    print(f"  {name}: z_ratio(med/lo) = {ratio_mean:.2f}±{ratio_std:.2f}, φ={phi:.3f}, {phi_frac:.1f}% near φ")

# ── P(z) width analysis ──
print(f"\n── P(z) Width vs Redshift ──")
z_bins = np.arange(0, 16, 1)
widths = []
for i in range(len(z_bins)-1):
    mask = quality & (z_med > z_bins[i]) & (z_med < z_bins[i+1]) & (z_lo > 0.5)
    if mask.sum() < 5:
        continue
    z_width = (z_hi[mask] - z_lo[mask]).mean()
    widths.append({'z_bin': f'{z_bins[i]:.0f}-{z_bins[i+1]:.0f}', 'z_mid': (z_bins[i]+z_bins[i+1])/2, 'width': float(z_width), 'n': int(mask.sum())})
    print(f"  z={z_bins[i]:.0f}-{z_bins[i+1]:.0f}: width={z_width:.3f}, n={mask.sum()}")

# ── z>15 check ──
z15_mask = quality & (z_med > 15) & (z_med < 25)
print(f"\n── z>15 Boundary Check ──")
print(f"  z>15: {z15_mask.sum()} galaxies")
if z15_mask.sum() > 0:
    for i in np.where(z15_mask)[0][:10]:
        print(f"    ID={data['NUMBER'][i]}, z={z_med[i]:.3f} [{z_lo[i]:.3f}, {z_hi[i]:.3f}]")

# ── z≈13.5 cluster analysis ──
z13_mask = quality & (np.abs(z_med - 13.5) < 0.5) & (np.abs(z_med - 13.5) < 1.0)
print(f"\n── z≈13.5 Cluster Analysis ──")
print(f"  z=13.5±0.5: {z13_mask.sum()} galaxies")
if z13_mask.sum() > 0:
    zs = z_med[z13_mask]
    print(f"  z_range: {zs.min():.3f} - {zs.max():.3f}")
    for i in np.where(z13_mask)[0][:20]:
        print(f"    ID={data['NUMBER'][i]}, z={z_med[i]:.3f} [{z_lo[i]:.3f}, {z_hi[i]:.3f}], mass={mass[i]:.2f}")

# ── Save results ──
results = {
    'n_total': int(len(data)),
    'n_valid': int(valid.sum()),
    'n_quality': int(quality.sum()),
    'n_z7_quality': int((quality & (z_med > 7) & (z_med < 25)).sum()),
    'n_z8_quality': int((quality & (z_med > 8) & (z_med < 25)).sum()),
    'n_z10': int((quality & (z_med > 10) & (z_med < 25)).sum()),
    'n_z15': int(z15_mask.sum()),
    'aliasing_stats': aliasing_stats,
    'pz_widths': widths,
    'z13_cluster': {
        'n': int(z13_mask.sum()),
        'z_min': float(z_med[z13_mask].min()) if z13_mask.sum() > 0 else 0,
        'z_max': float(z_med[z13_mask].max()) if z13_mask.sum() > 0 else 0,
    }
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n── Results saved to {OUTPUT_PATH} ──")
print(f"  CEERS DR1: {len(data)} galaxies")
print(f"  z>7 (quality): {results['n_z7_quality']}")
print(f"  z>8 (quality): {results['n_z8_quality']}")
print(f"  z>10: {results['n_z10']}")
print(f"  z>15: {results['n_z15']}")
print(f"  z≈13.5 cluster: {results['z13_cluster']['n']} galaxies")
print("=" * 70)