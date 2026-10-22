#!/usr/bin/env python3
"""
Generate NIRCam + HST filter transmission curves from known specifications
Bagpipes expects: wavelength (Angstrom), transmission (0-1)
"""
import numpy as np, os

filter_dir = os.path.expanduser("~/IDCM/sync_bump_analysis/filters")
os.makedirs(filter_dir, exist_ok=True)

# NIRCam filter specifications (from JWST documentation)
# pivot wavelength (um), bandwidth (um), shape
# Using Gaussian approximation for each filter
filters = {
    # HST ACS filters
    "F435W":  {"pivot": 0.433, "fwhm": 0.065, "type": "gaussian"},
    "F606W":  {"pivot": 0.592, "fwhm": 0.122, "type": "gaussian"},
    "F814W":  {"pivot": 0.806, "fwhm": 0.140, "type": "gaussian"},
    # JWST NIRCam filters
    "F115W":  {"pivot": 1.154, "fwhm": 0.125, "type": "gaussian"},
    "F150W":  {"pivot": 1.501, "fwhm": 0.163, "type": "gaussian"},
    "F200W":  {"pivot": 1.989, "fwhm": 0.216, "type": "gaussian"},
    "F277W":  {"pivot": 2.776, "fwhm": 0.305, "type": "gaussian"},
    "F356W":  {"pivot": 3.569, "fwhm": 0.395, "type": "gaussian"},
    "F410M":  {"pivot": 4.082, "fwhm": 0.297, "type": "gaussian"},
    "F444W":  {"pivot": 4.404, "fwhm": 0.483, "type": "gaussian"},
}

for fname, fp in filters.items():
    pivot_um = fp["pivot"]
    fwhm_um = fp["fwhm"]
    sigma_um = fwhm_um / 2.355  # Gaussian sigma
    
    # Generate wavelength range: ±3 sigma from pivot
    wav_min = max(0.1, pivot_um - 4 * sigma_um)
    wav_max = pivot_um + 4 * sigma_um
    
    # 200 points across the filter
    wav_um = np.linspace(wav_min, wav_max, 200)
    # Convert to Angstrom for Bagpipes
    wav_ang = wav_um * 1e4
    
    # Gaussian transmission
    transmission = np.exp(-0.5 * ((wav_um - pivot_um) / sigma_um)**2)
    # Normalize peak to 1
    transmission = transmission / transmission.max()
    
    # Write to file
    outpath = os.path.join(filter_dir, f"{fname}.dat")
    with open(outpath, "w") as f:
        f.write("# Wavelength(Angstrom) Transmission\n")
        for w, t in zip(wav_ang, transmission):
            f.write(f"{w:.1f} {t:.6f}\n")
    
    print(f"  {fname}: {len(wav_ang)} points, {wav_min:.3f}-{wav_max:.3f}um")

print(f"\nDone. Generated {len(filters)} filter files in {filter_dir}/")