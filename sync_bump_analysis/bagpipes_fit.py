#!/usr/bin/env python3
"""
Bagpipes SED fitting for CEERS z≈8.2 galaxies
=============================================
Check if P(z) posterior has secondary peak at z=6.9 (Fibonacci aliasing)

Targets: Galaxy 2859 (z=8.106) and Galaxy 13050 (z=8.137)
"""
import numpy as np
import bagpipes as pipes
import json, os, warnings, sys
warnings.filterwarnings("ignore")

print("=" * 72)
print("  Bagpipes SED Fitting — CEERS z≈8.2 Aliasing Test")
print("=" * 72)

# ══════════════════════════════════════════════════════════════════
# Filter paths
# ══════════════════════════════════════════════════════════════════
filter_dir = os.path.expanduser("~/IDCM/sync_bump_analysis/filters")
filt_list = [
    os.path.join(filter_dir, "F435W.dat"),
    os.path.join(filter_dir, "F606W.dat"),
    os.path.join(filter_dir, "F814W.dat"),
    os.path.join(filter_dir, "F115W.dat"),
    os.path.join(filter_dir, "F150W.dat"),
    os.path.join(filter_dir, "F200W.dat"),
    os.path.join(filter_dir, "F277W.dat"),
    os.path.join(filter_dir, "F356W.dat"),
    os.path.join(filter_dir, "F410M.dat"),
    os.path.join(filter_dir, "F444W.dat"),
]

# ══════════════════════════════════════════════════════════════════
# Define photometry (in nJy → Bagpipes uses uJy = ×0.001)
# ══════════════════════════════════════════════════════════════════
def make_photometry(flux_njy, err_njy):
    """Convert nJy to uJy. Returns 2D array [n_filters, 3]"""
    phot = np.zeros((len(flux_njy), 3))
    for i, (f, e) in enumerate(zip(flux_njy, err_njy)):
        phot[i, 0] = max(f * 0.001, 0.001)  # flux in uJy
        phot[i, 1] = e * 0.001               # error in uJy
    return phot

# Galaxy 2859: z=8.106
phot_2859 = make_photometry(
    [2.58, -1.52, 3.88, 10.02, 15.37, 11.85, 14.94, 52.42, 63.28, 124.94],
    [3.73, 4.19, 4.78, 2.85, 3.80, 3.60, 2.79, 2.24, 6.01, 3.50]
)

# Galaxy 13050: z=8.137
phot_13050 = make_photometry(
    [5.08, -1.79, 7.12, 9.91, 12.86, 11.56, 22.50, 64.61, 81.98, 147.83],
    [7.56, 4.11, 6.83, 3.42, 4.66, 4.09, 2.59, 2.16, 6.07, 3.66]
)

# ══════════════════════════════════════════════════════════════════
# Define model components (Bagpipes format)
# ══════════════════════════════════════════════════════════════════
# delayed-tau SFH + nebular emission + dust attenuation
fit_instructions = {
    "redshift": (5.0, 10.0),
    "delayed": {
        "age": (0.01, 1.0),       # age of stellar pop in Gyr
        "tau": (0.1, 5.0),         # e-folding time in Gyr
        "massformed": (7.0, 12.0),  # log10(M*/M☉)
        "metallicity": (0.01, 2.5),  # Z/Z☉
    },
    "dust": {"Av": (0.0, 2.0), "type": "Calzetti"},
    "nebular": {"logU": -3.0},
}

# ══════════════════════════════════════════════════════════════════
# Helper function
# ══════════════════════════════════════════════════════════════════
def load_galaxy_data(phot_array):
    def loader(ID):
        return phot_array
    return loader

# ══════════════════════════════════════════════════════════════════
# Run fitting for Galaxy 2859
# ══════════════════════════════════════════════════════════════════
print("\n  ── Galaxy 2859 (z=8.106) ──")

try:
    g2859 = pipes.galaxy("2859", load_galaxy_data(phot_2859), 
                          phot_units="mujy", spectrum_exists=False, 
                          photometry_exists=True, filt_list=filt_list)
    print(f"  Galaxy created: {len(g2859.photometry)} photometric points")
    
    print("  Running Nautilus MCMC fit (may take 5-15 min)...")
    sys.stdout.flush()
    
    f2859 = pipes.fit(g2859, fit_instructions, run="2859_fit", n_posterior=500)
    f2859.fit(verbose=True, n_live=400)
    
    print("  Fit completed!")
    print(f"  Posterior samples shape: {f2859.posterior.samples.shape}")
    
    z_samples = f2859.posterior.samples["redshift"]
    print(f"  z posterior: min={z_samples.min():.3f}, max={z_samples.max():.3f}, "
          f"mean={z_samples.mean():.3f}, median={np.median(z_samples):.3f}")
    
    for az in [5.6, 6.9, 7.7, 8.2]:
        frac = np.sum(np.abs(z_samples - az) < 0.2) / len(z_samples)
        peak_flag = " ⬆ SPIKE" if frac > 0.15 else " (bump)" if frac > 0.05 else ""
        print(f"    z={az}: {frac:.1%} samples{peak_flag}")
    
    np.savetxt("2859_z_posterior.txt", z_samples)
    print("  z posterior saved to 2859_z_posterior.txt")
    
    # Check for bimodality
    z_hist, z_edges = np.histogram(z_samples, bins=50, range=(5, 10))
    peak_z = z_edges[:-1][z_hist == z_hist.max()]
    n_peaks = np.sum(z_hist > z_hist.max() * 0.5)
    print(f"  P(z) peaks at z={peak_z}")
    print(f"  Number of significant peaks: {n_peaks}")
    if n_peaks >= 2:
        print("  ✅ BIMODAL P(z) DETECTED!")
    
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

# ══════════════════════════════════════════════════════════════════
# Run fitting for Galaxy 13050
# ══════════════════════════════════════════════════════════════════
print("\n  ── Galaxy 13050 (z=8.137) ──")

try:
    g13050 = pipes.galaxy("13050", load_galaxy_data(phot_13050),
                           phot_units="mujy", spectrum_exists=False,
                           photometry_exists=True, filt_list=filt_list)
    print(f"  Galaxy created: {len(g13050.photometry)} photometric points")
    
    print("  Running Nautilus MCMC fit (may take 5-15 min)...")
    sys.stdout.flush()
    
    f13050 = pipes.fit(g13050, fit_instructions, run="13050_fit", n_posterior=500)
    f13050.fit(verbose=True, n_live=400)
    
    print("  Fit completed!")
    print(f"  Posterior samples shape: {f13050.posterior.samples.shape}")
    
    z_samples = f13050.posterior.samples["redshift"]
    print(f"  z posterior: min={z_samples.min():.3f}, max={z_samples.max():.3f}, "
          f"mean={z_samples.mean():.3f}, median={np.median(z_samples):.3f}")
    
    for az in [5.6, 6.9, 7.7, 8.2]:
        frac = np.sum(np.abs(z_samples - az) < 0.2) / len(z_samples)
        peak_flag = " ⬆ SPIKE" if frac > 0.15 else " (bump)" if frac > 0.05 else ""
        print(f"    z={az}: {frac:.1%} samples{peak_flag}")
    
    np.savetxt("13050_z_posterior.txt", z_samples)
    print("  z posterior saved to 13050_z_posterior.txt")
    
    z_hist, z_edges = np.histogram(z_samples, bins=50, range=(5, 10))
    peak_z = z_edges[:-1][z_hist == z_hist.max()]
    n_peaks = np.sum(z_hist > z_hist.max() * 0.5)
    print(f"  P(z) peaks at z={peak_z}")
    print(f"  Number of significant peaks: {n_peaks}")
    if n_peaks >= 2:
        print("  ✅ BIMODAL P(z) DETECTED!")
    
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

# ══════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  Done")
print("=" * 72)