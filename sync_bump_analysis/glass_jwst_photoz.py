#!/usr/bin/env python3
"""
GLASS-JWST Simple Photo-z Estimation
======================================
Lyman break method using 15-band photometry
Abell 2744 field — independent test of IDCM aliasing hypothesis

Author: 調律者 calibrator
"""
import warnings, numpy as np, json, os, sys
warnings.filterwarnings('ignore')
from astropy.io import fits

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(SCRIPT_DIR, 'glass_jwst_catalog.fits')
OUTPUT_PATH = os.path.join(SCRIPT_DIR, 'verification/glass_jwst_photoz_results.json')

# Filter pivot wavelengths (microns)
FILTERS = {
    'f435w': 0.435, 'f606w': 0.606, 'f775w': 0.775, 'f814w': 0.814,
    'f090w': 0.902, 'f115w': 1.154, 'f105w': 1.055, 'f125w': 1.248,
    'f140w': 1.392, 'f160w': 1.539, 'f150w': 1.501, 'f200w': 1.990,
    'f277w': 2.766, 'f356w': 3.568, 'f410m': 4.082, 'f444w': 4.402,
}

# Lyman break wavelength (rest-frame)
Lyman_alpha = 0.1216  # microns

def estimate_photoz(fluxes, names):
    """Estimate photo-z from the Lyman break position."""
    # Sort filters by wavelength
    sorted_filters = sorted([(FILTERS[n], n) for n in names if n in FILTERS])
    
    # For each pair of adjacent filters, check for a flux drop
    # The Lyman break causes a drop in flux when the break enters a filter
    best_z = -1
    best_drop = 0
    
    for i in range(1, len(sorted_filters)):
        wl1, name1 = sorted_filters[i-1]
        wl2, name2 = sorted_filters[i]
        
        f1 = fluxes[names.index(name1)] if name1 in names else 0
        f2 = fluxes[names.index(name2)] if name2 in names else 0
        
        if f1 > 0 and f2 > 0:
            # Flux drop ratio (f2/f1, should be >1 if break is between them)
            # Actually, if break is between wl1 and wl2, f1 should be depressed
            # and f2 should be unaffected
            ratio = f2 / f1 if f1 > 0 else 0
            
            # Redshift where Lyman break falls between wl1 and wl2
            z_break = (wl1 + wl2) / 2 / Lyman_alpha - 1
            
            # A strong drop (ratio > 1.5) indicates the break is between these filters
            if ratio > 1.5 and ratio > best_drop:
                best_drop = ratio
                best_z = z_break
    
    return best_z, best_drop

print("=" * 70)
print("  GLASS-JWST Photo-z Estimation")
print("=" * 70)

# Load catalog
print("\n  Loading GLASS-JWST catalog...")
hdul = fits.open(CATALOG_PATH, memmap=False)
data = hdul[1].data  # ISO aperture
cols = hdul[1].columns.names

# Get flux column names
flux_cols = [c for c in cols if c.startswith('f_') and not c.endswith('_e')]
err_cols = [c for c in cols if c.endswith('_e')]
print(f"  Flux columns: {flux_cols}")

# Filter names (remove 'f_' prefix)
filter_names = [c[2:] for c in flux_cols]

# Compute photo-z for each source
print("\n  Computing photo-z...")
n_sources = len(data)
photo_zs = np.full(n_sources, -1.0)
photo_z_drops = np.full(n_sources, 0.0)

for i in range(n_sources):
    fluxes = np.array([data[c][i] for c in flux_cols], dtype=float)
    # Skip flagged sources
    if np.any(np.isnan(fluxes)) or np.all(fluxes <= 0):
        continue
    z, drop = estimate_photoz(fluxes.tolist(), filter_names)
    photo_zs[i] = z
    photo_z_drops[i] = drop

# Results
valid = (photo_zs > 0) & (photo_zs < 25)
print(f"  Valid photo-z: {valid.sum()} / {n_sources}")

# z>7
z7 = valid & (photo_zs > 7) & (photo_zs < 25)
print(f"  z>7: {z7.sum()}")

# z>8
z8 = valid & (photo_zs > 8) & (photo_zs < 25)
print(f"  z>8: {z8.sum()}")

# z>10
z10 = valid & (photo_zs > 10) & (photo_zs < 25)
print(f"  z>10: {z10.sum()}")

# z>15
z15 = valid & (photo_zs > 15) & (photo_zs < 25)
print(f"  z>15: {z15.sum()}")

# Aliasing point counts
print(f"\n── Aliasing Point Counts ──")
for az in [5.6, 6.9, 7.7, 8.2, 8.5, 8.9, 9.2, 9.5, 10.0, 13.5, 14.0]:
    cnt = sum((abs(photo_zs - az) < 0.3) & valid)
    print(f"  z={az:.1f}: {cnt}")

# φ-ratio test
phi = (1 + 5**0.5) / 2
print(f"\n── φ-ratio Test ──")
aliasing_zs = [5.6, 6.9, 7.7, 8.2, 8.5, 8.9]
for i in range(len(aliasing_zs)-1):
    z1, z2 = aliasing_zs[i], aliasing_zs[i+1]
    n1 = sum((abs(photo_zs - z1) < 0.3) & valid)
    n2 = sum((abs(photo_zs - z2) < 0.3) & valid)
    if n2 > 0:
        ratio = n1 / n2
        dev = abs(ratio/phi - 1) * 100
        print(f"  {z1:.1f}→{z2:.1f}: {n1}/{n2} = {ratio:.3f} (dev={dev:.1f}%)")

# Save results
results = {
    'n_total': int(n_sources),
    'n_valid': int(valid.sum()),
    'n_z7': int(z7.sum()),
    'n_z8': int(z8.sum()),
    'n_z10': int(z10.sum()),
    'n_z15': int(z15.sum()),
    'method': 'Lyman_break',
    'aliasing_counts': {str(az): int(sum((abs(photo_zs - az) < 0.3) & valid)) for az in [5.6, 6.9, 7.7, 8.2, 8.5, 8.9, 9.2, 9.5, 10.0, 13.5, 14.0]},
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n── Results saved to {OUTPUT_PATH} ──")
print("=" * 70)

hdul.close()