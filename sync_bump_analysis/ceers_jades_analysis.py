#!/usr/bin/env python3
"""
Comprehensive analysis of CEERS z=13.5 cluster spatial properties and comparison
with JADES DR4 spectroscopic redshifts.

Checks:
1. JADES DR4 internal: compare z_PRISM (spectroscopic) with z_phot (photometric)
2. Δz/(1+z) distribution for systematic offsets at aliasing points
3. CEERS z=13.5 narrow-P(z) cluster spatial properties
4. 2D spatial clustering vs random sample
5. 11800-series sources deblending artifact check
"""

import numpy as np
import json
import gzip
import io
import os
from collections import OrderedDict
from astropy.io import fits
from scipy.spatial import KDTree
from scipy.stats import binned_statistic

# ============================================================
# 1. LOAD DATA
# ============================================================
print("=" * 70)
print("LOADING DATA")
print("=" * 70)

# CEERS
print("Loading CEERS DR1 catalog...")
with gzip.open('ceers_dr1_catalog.fits.gz', 'rb') as f:
    with fits.open(io.BytesIO(f.read())) as hdul:
        ceers = hdul[1].data
print(f"  CEERS rows: {len(ceers)}")

# JADES DR4
print("Loading JADES DR4 spectroscopic catalog...")
with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    jades_obs = hdul[1].data   # Obs_info (z_phot, z_PRISM, etc.)
    jades_r100 = hdul[2].data  # R100_5pix (z_PRISM, Z_FLAG, etc.)
print(f"  JADES Obs_info rows: {len(jades_obs)}")
print(f"  JADES R100_5pix rows: {len(jades_r100)}")

results = {}

# ============================================================
# 2. JADES DR4 INTERNAL: z_PRISM vs z_phot
# ============================================================
print("\n" + "=" * 70)
print("JADES DR4 INTERNAL: z_PRISM (spectroscopic) vs z_phot (photometric)")
print("=" * 70)

# z_PRISM is in HDU 2 (R100_5pix), z_phot is in HDU 1 (Obs_info)
# Match by Unique_ID or NIRCam_DR5_ID
# Build lookup from Obs_info by Unique_ID
obs_by_uid = {}
for row in jades_obs:
    obs_by_uid[row['Unique_ID'].strip()] = row

# Match R100_5pix to Obs_info
z_prism_vals = []
z_phot_vals = []
z_prism_err_low = []
z_prism_err_high = []
z_flag_vals = []
matched_ids = []
match_quality = []

for i, row in enumerate(jades_r100):
    uid = row['Unique_ID'].strip()
    z_prism = row['z_PRISM']
    z_flag = row['Z_FLAG']
    
    if uid in obs_by_uid:
        z_phot = obs_by_uid[uid]['z_phot']
        # Skip if either is NaN
        if np.isfinite(z_prism) and np.isfinite(z_phot):
            z_prism_vals.append(z_prism)
            z_phot_vals.append(z_phot)
            z_flag_vals.append(z_flag)
            matched_ids.append(uid)
            match_quality.append('both')

print(f"  Matched sources with valid z_PRISM and z_phot: {len(z_prism_vals)}")
print(f"  z_PRISM range: [{min(z_prism_vals):.3f}, {max(z_prism_vals):.3f}]")
print(f"  z_phot range: [{min(z_phot_vals):.3f}, {max(z_phot_vals):.3f}]")

z_prism_arr = np.array(z_prism_vals)
z_phot_arr = np.array(z_phot_vals)
z_flag_arr = np.array(z_flag_vals)

# Δz/(1+z)
dz_over_1pz = (z_prism_arr - z_phot_arr) / (1.0 + z_phot_arr)

# Stats
dz_mean = np.nanmean(dz_over_1pz)
dz_median = np.nanmedian(dz_over_1pz)
dz_std = np.nanstd(dz_over_1pz)
dz_mad = np.nanmedian(np.abs(dz_over_1pz - dz_median))

print(f"\n  Δz/(1+z) statistics:")
print(f"    Mean: {dz_mean:.6f}")
print(f"    Median: {dz_median:.6f}")
print(f"    Std: {dz_std:.6f}")
print(f"    MAD: {dz_mad:.6f}")

# Check for catastrophic outliers
cat_outliers = np.abs(dz_over_1pz) > 0.15
print(f"  Catastrophic outliers (|Δz/(1+z)| > 0.15): {np.sum(cat_outliers)} / {len(dz_over_1pz)} ({100*np.sum(cat_outliers)/len(dz_over_1pz):.1f}%)")

# Check for aliasing points: systematic offsets
# Common aliasing points: z ~ 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 13.5
aliasing_points = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 13.5]
aliasing_analysis = {}

print("\n  Aliasing point analysis:")
for zp in aliasing_points:
    # Sources within ±0.5 of the aliasing point
    mask = (z_phot_arr > zp - 0.5) & (z_phot_arr < zp + 0.5)
    if np.sum(mask) > 0:
        dz_subset = dz_over_1pz[mask]
        mean_offset = np.nanmean(dz_subset)
        std_offset = np.nanstd(dz_subset)
        n_src = np.sum(mask)
        aliasing_analysis[f"z~{zp}"] = {
            "n_sources": int(n_src),
            "mean_dz/(1+z)": float(mean_offset),
            "std_dz/(1+z)": float(std_offset),
            "median_dz/(1+z)": float(np.nanmedian(dz_subset))
        }
        print(f"    z~{zp:.1f}: n={n_src:4d}, mean Δz/(1+z)={mean_offset:+.6f}, std={std_offset:.6f}")

results["jades_dr4_internal"] = {
    "n_matched": len(z_prism_vals),
    "dz_over_1pz_mean": float(dz_mean),
    "dz_over_1pz_median": float(dz_median),
    "dz_over_1pz_std": float(dz_std),
    "dz_over_1pz_mad": float(dz_mad),
    "catastrophic_outlier_count": int(np.sum(cat_outliers)),
    "catastrophic_outlier_frac": float(np.sum(cat_outliers) / len(dz_over_1pz)),
    "aliasing_point_analysis": aliasing_analysis
}

# ============================================================
# 3. CEERS z=13.5 CLUSTER ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("CEERS z=13.5 NARROW-P(z) CLUSTER")
print("=" * 70)

# Target IDs
target_ids = [6357, 8282, 10243, 10835, 
              11802, 11803, 11804, 11805, 11806, 11807, 11808, 11809, 11810,
              14168, 14563, 22460, 24128, 25927, 26909, 28776, 29746, 
              35640, 35735, 36179]

print(f"  Target IDs ({len(target_ids)}): {target_ids}")

# Find sources in CEERS by NUMBER
target_sources = []
target_indices = []
number_to_idx = {}
for i, num in enumerate(ceers['NUMBER']):
    number_to_idx[num] = i

found_ids = []
missing_ids = []
for tid in target_ids:
    if tid in number_to_idx:
        idx = number_to_idx[tid]
        found_ids.append(tid)
        target_sources.append(ceers[idx])
        target_indices.append(idx)
    else:
        missing_ids.append(tid)

print(f"  Found in CEERS: {len(found_ids)}")
print(f"  Missing from CEERS: {missing_ids}")

if len(target_sources) > 0:
    # Extract properties
    z_med = np.array([s['LP_Z_MED'] for s in target_sources])
    z_best = np.array([s['LP_Z_BEST'] for s in target_sources])
    z_low = np.array([s['LP_Z_MED68_LOW'] for s in target_sources])
    z_high = np.array([s['LP_Z_MED68_HIGH'] for s in target_sources])
    ra = np.array([s['RA'] for s in target_sources])
    dec = np.array([s['DEC'] for s in target_sources])
    mass = np.array([s['LP_MASS_MED'] for s in target_sources])
    sfr = np.array([s['LP_SFR_MED'] for s in target_sources])
    chi2 = np.array([s['LP_FIT_CHI'] for s in target_sources])
    nbands = np.array([s['LP_NBANDS'] for s in target_sources])
    numbers = np.array([s['NUMBER'] for s in target_sources])
    
    # Also get morphological params
    x_image = np.array([s['X_IMAGE'] for s in target_sources])
    y_image = np.array([s['Y_IMAGE'] for s in target_sources])
    a_image = np.array([s['A_IMAGE'] for s in target_sources])
    b_image = np.array([s['B_IMAGE'] for s in target_sources])
    theta_image = np.array([s['THETA_IMAGE'] for s in target_sources])
    ellipticity = np.array([s['ELLIPTICITY'] for s in target_sources])
    kron_radius = np.array([s['KRON_RADIUS'] for s in target_sources])
    star_flag = np.array([s['STAR_FLAG'] for s in target_sources])
    
    # Print each source
    print("\n  Individual source properties:")
    print(f"  {'ID':>6} {'RA':>10} {'DEC':>10} {'z_med':>7} {'z_best':>7} {'z68_low':>7} {'z68_high':>7} {'mass':>8} {'SFR':>8} {'chi2':>7} {'nband':>5} {'A':>7} {'B':>7} {'ellip':>6} {'star':>4}")
    print("  " + "-" * 110)
    
    for i in range(len(target_sources)):
        print(f"  {numbers[i]:>6} {ra[i]:>10.5f} {dec[i]:>10.5f} {z_med[i]:>7.3f} {z_best[i]:>7.3f} {z_low[i]:>7.3f} {z_high[i]:>7.3f} {mass[i]:>8.2f} {sfr[i]:>8.2f} {chi2[i]:>7.1f} {nbands[i]:>5.0f} {a_image[i]:>7.2f} {b_image[i]:>7.2f} {ellipticity[i]:>6.3f} {star_flag[i]:>4.0f}")
    
    # Compute spatial extent
    ra_center = np.mean(ra)
    dec_center = np.mean(dec)
    ra_std = np.std(ra)
    dec_std = np.std(dec)
    
    # Convert RA, Dec offsets to arcsec
    # 1 degree ~ 3600 arcsec, at Dec~52.9 deg, cos(dec) ~ 0.603
    cos_dec = np.cos(np.radians(np.mean(dec)))
    ra_arcsec = ra_std * 3600 * cos_dec
    dec_arcsec = dec_std * 3600
    
    # Compute pairwise distances
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(ra1, dec1, ra2, dec2):
        """Great-circle distance in degrees"""
        r1 = np.radians(ra1)
        d1 = np.radians(dec1)
        r2 = np.radians(ra2)
        d2 = np.radians(dec2)
        dlat = d2 - d1
        dlon = r2 - r1
        a = sin(dlat/2)**2 + cos(d1) * cos(d2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return np.degrees(c) * 3600  # arcsec
    
    # Pairwise distances
    n_src = len(ra)
    pair_dists = []
    for i in range(n_src):
        for j in range(i+1, n_src):
            d = haversine(ra[i], dec[i], ra[j], dec[j])
            pair_dists.append(d)
    
    pair_dists = np.array(pair_dists)
    print(f"\n  Spatial properties:")
    print(f"    RA center: {ra_center:.5f} ± {ra_std:.5f} deg ({ra_arcsec:.2f} arcsec)")
    print(f"    Dec center: {dec_center:.5f} ± {dec_std:.5f} deg ({dec_arcsec:.2f} arcsec)")
    print(f"    Mean pairwise distance: {np.mean(pair_dists):.2f} arcsec")
    print(f"    Median pairwise distance: {np.median(pair_dists):.2f} arcsec")
    print(f"    Min pairwise distance: {np.min(pair_dists):.2f} arcsec")
    print(f"    Max pairwise distance: {np.max(pair_dists):.2f} arcsec")
    
    # Check if sources are clustered or spread out
    # For NIRCam, typical FOV is ~2.2 arcmin = 132 arcsec
    print(f"    Relative to NIRCam FOV (~132 arcsec):")
    print(f"      Cluster spans {ra_arcsec*2:.1f} x {dec_arcsec*2:.1f} arcsec")
    
    # Summary of z distribution
    print(f"\n  Redshift summary:")
    print(f"    z_med: {np.min(z_med):.3f} - {np.max(z_med):.3f}, mean={np.mean(z_med):.3f}")
    print(f"    z_best: {np.min(z_best):.3f} - {np.max(z_best):.3f}, mean={np.mean(z_best):.3f}")
    
    # Cluster properties
    cluster_props = {
        "n_sources_found": len(target_sources),
        "n_sources_targeted": len(target_ids),
        "missing_ids": missing_ids,
        "source_details": [],
        "ra_mean": float(ra_center),
        "dec_mean": float(dec_center),
        "ra_std_deg": float(ra_std),
        "dec_std_deg": float(dec_std),
        "ra_std_arcsec": float(ra_arcsec),
        "dec_std_arcsec": float(dec_arcsec),
        "mean_pairwise_dist_arcsec": float(np.mean(pair_dists)),
        "median_pairwise_dist_arcsec": float(np.median(pair_dists)),
        "min_pairwise_dist_arcsec": float(np.min(pair_dists)),
        "max_pairwise_dist_arcsec": float(np.max(pair_dists)),
        "z_med_min": float(np.min(z_med)),
        "z_med_max": float(np.max(z_med)),
        "z_med_mean": float(np.mean(z_med)),
        "z_best_min": float(np.min(z_best)),
        "z_best_max": float(np.max(z_best)),
        "z_best_mean": float(np.mean(z_best)),
    }
    
    for i in range(len(target_sources)):
        cluster_props["source_details"].append({
            "number": int(numbers[i]),
            "ra": float(ra[i]),
            "dec": float(dec[i]),
            "z_med": float(z_med[i]),
            "z_best": float(z_best[i]),
            "z_68_low": float(z_low[i]),
            "z_68_high": float(z_high[i]),
            "mass": float(mass[i]),
            "sfr": float(sfr[i]),
            "chi2": float(chi2[i]),
            "nbands": int(nbands[i]),
            "x_image": float(x_image[i]),
            "y_image": float(y_image[i]),
            "a_image": float(a_image[i]),
            "b_image": float(b_image[i]),
            "theta_image": float(theta_image[i]),
            "ellipticity": float(ellipticity[i]),
            "kron_radius": float(kron_radius[i]),
            "star_flag": int(star_flag[i])
        })
    
    results["ceers_z13p5_cluster"] = cluster_props

# ============================================================
# 4. 2D SPATIAL CLUSTERING vs RANDOM SAMPLE
# ============================================================
print("\n" + "=" * 70)
print("2D SPATIAL CLUSTERING: z=13.5 CLUSTER vs RANDOM SAMPLE")
print("=" * 70)

if len(target_sources) >= 3:
    # Define the spatial region of the targets
    ra_min, ra_max = ra.min(), ra.max()
    dec_min, dec_max = dec.min(), dec.max()
    # Add margin
    margin = 0.01  # ~0.6 arcmin margin
    ra_min_m = ra_min - margin
    ra_max_m = ra_max + margin
    dec_min_m = dec_min - margin
    dec_max_m = dec_max + margin
    
    print(f"  Target region: RA=[{ra_min:.4f}, {ra_max:.4f}], Dec=[{dec_min:.4f}, {dec_max:.4f}]")
    print(f"  With margin: RA=[{ra_min_m:.4f}, {ra_max_m:.4f}], Dec=[{dec_min_m:.4f}, {dec_max_m:.4f}]")
    
    # Find all CEERS sources in the same region
    in_region = ((ceers['RA'] >= ra_min_m) & (ceers['RA'] <= ra_max_m) &
                 (ceers['DEC'] >= dec_min_m) & (ceers['DEC'] <= dec_max_m))
    region_sources = ceers[in_region]
    n_region = np.sum(in_region)
    print(f"  Total sources in region: {n_region}")
    
    if n_region > 0:
        region_ra = np.array(region_sources['RA'])
        region_dec = np.array(region_sources['DEC'])
        region_z = np.array(region_sources['LP_Z_MED'])
        
        # What fraction of region sources are at z~13.5?
        z_high_mask = region_z > 10.0
        n_high_z = np.sum(z_high_mask)
        print(f"  Sources at z>10 in region: {n_high_z}")
        
        # Build KD-tree for all sources in region
        # Convert RA, Dec to radians for proper distance
        region_ra_rad = np.radians(region_ra)
        region_dec_rad = np.radians(region_dec)
        # Convert to Cartesian for KD-tree
        x = np.cos(region_dec_rad) * np.cos(region_ra_rad)
        y = np.cos(region_dec_rad) * np.sin(region_ra_rad)
        z = np.sin(region_dec_rad)
        region_xyz = np.column_stack([x, y, z])
        
        # Target sources in Cartesian
        target_ra_rad = np.radians(ra)
        target_dec_rad = np.radians(dec)
        tx = np.cos(target_dec_rad) * np.cos(target_ra_rad)
        ty = np.cos(target_dec_rad) * np.sin(target_ra_rad)
        tz = np.sin(target_dec_rad)
        target_xyz = np.column_stack([tx, ty, tz])
        
        # Build tree
        tree = KDTree(region_xyz)
        
        # Compute NN distances for target sources
        target_nn_dists, _ = tree.query(target_xyz, k=2)  # k=2 because first is self
        target_nn_dist = target_nn_dists[:, 1]  # Second nearest neighbor
        target_nn_arcsec = np.degrees(np.arccos(1.0 - target_nn_dist**2 / 2.0)) * 3600
        
        print(f"\n  Nearest neighbor distances for z=13.5 sources:")
        for i, (nid, nn) in enumerate(zip(numbers, target_nn_arcsec)):
            print(f"    ID {nid:>6}: NN distance = {nn:.2f} arcsec")
        
        # Random sampling for comparison: draw n_src random sources from region
        # and compute their NN distances, repeat 1000 times
        n_random_samples = min(1000, 200000)
        n_target = len(target_sources)
        random_nn_means = []
        
        np.random.seed(42)
        for _ in range(n_random_samples):
            rand_idx = np.random.choice(n_region, n_target, replace=False)
            rand_xyz = region_xyz[rand_idx]
            rand_nn_dists, _ = tree.query(rand_xyz, k=2)
            rand_nn = rand_nn_dists[:, 1]
            rand_nn_mean = np.mean(np.degrees(np.arccos(1.0 - rand_nn**2 / 2.0)) * 3600)
            random_nn_means.append(rand_nn_mean)
        
        random_nn_means = np.array(random_nn_means)
        target_mean_nn = np.mean(target_nn_arcsec)
        
        # Percentile of target mean NN in random distribution
        percentile = np.sum(random_nn_means <= target_mean_nn) / n_random_samples * 100
        
        print(f"\n  NN clustering analysis:")
        print(f"    Target mean NN distance: {target_mean_nn:.2f} arcsec")
        print(f"    Random mean NN distance: {np.mean(random_nn_means):.2f} arcsec ± {np.std(random_nn_means):.2f}")
        print(f"    Target NN percentile in random distribution: {percentile:.1f}%")
        
        if percentile < 5.0:
            print(f"    *** SIGNIFICANT CLUSTERING: z=13.5 sources are more clustered than {100-percentile:.1f}% of random samples")
        elif percentile < 16.0:
            print(f"    * MODERATE CLUSTERING: z=13.5 sources are somewhat clustered")
        elif percentile > 95.0:
            print(f"    *** ANTI-CLUSTERED: z=13.5 sources are more spread out than expected")
        else:
            print(f"    No significant spatial clustering detected")
        
        # Also compute 2D histogram of region sources
        ra_bins = np.linspace(ra_min_m, ra_max_m, 20)
        dec_bins = np.linspace(dec_min_m, dec_max_m, 20)
        H, _, _ = np.histogram2d(region_ra, region_dec, bins=[ra_bins, dec_bins])
        
        target_H, _, _ = np.histogram2d(ra, dec, bins=[ra_bins, dec_bins])
        
        print(f"\n  2D density analysis:")
        print(f"    Mean density in region: {n_region / (len(ra_bins)-1) / (len(dec_bins)-1):.1f} sources/bin")
        print(f"    Max density: {H.max()} sources/bin")
        print(f"    Target source max per bin: {target_H.max()}")
        
        # Summary
        clustering_results = {
            "n_target_sources": n_target,
            "n_region_sources": int(n_region),
            "region_ra_range": [float(ra_min_m), float(ra_max_m)],
            "region_dec_range": [float(dec_min_m), float(dec_max_m)],
            "target_mean_nn_arcsec": float(target_mean_nn),
            "random_mean_nn_arcsec_mean": float(np.mean(random_nn_means)),
            "random_mean_nn_arcsec_std": float(np.std(random_nn_means)),
            "target_nn_percentile": float(percentile),
            "is_significantly_clustered": bool(percentile < 5.0),
            "target_nn_distances": [float(d) for d in target_nn_arcsec],
            "n_high_z_in_region": int(n_high_z)
        }
        results["spatial_clustering"] = clustering_results
    
    # ============================================================
    # 5. 11800-SERIES SOURCES DEBLENDING CHECK
    # ============================================================
    print("\n" + "=" * 70)
    print("11800-SERIES SOURCES: DEBLENDING ARTIFACT CHECK")
    print("=" * 70)
    
    # IDs near 11800
    series_11800_ids = [11802, 11803, 11804, 11805, 11806, 11807, 11808, 11809, 11810]
    series_11800_sources = []
    series_11800_indices = []
    
    for sid in series_11800_ids:
        if sid in number_to_idx:
            idx = number_to_idx[sid]
            series_11800_sources.append(ceers[idx])
            series_11800_indices.append(idx)
    
    print(f"  Found 11800-series sources in CEERS: {len(series_11800_sources)} / {len(series_11800_ids)}")
    
    if len(series_11800_sources) >= 2:
        s_x = np.array([s['X_IMAGE'] for s in series_11800_sources])
        s_y = np.array([s['Y_IMAGE'] for s in series_11800_sources])
        s_a = np.array([s['A_IMAGE'] for s in series_11800_sources])
        s_b = np.array([s['B_IMAGE'] for s in series_11800_sources])
        s_theta = np.array([s['THETA_IMAGE'] for s in series_11800_sources])
        s_ra = np.array([s['RA'] for s in series_11800_sources])
        s_dec = np.array([s['DEC'] for s in series_11800_sources])
        s_ellip = np.array([s['ELLIPTICITY'] for s in series_11800_sources])
        s_kron = np.array([s['KRON_RADIUS'] for s in series_11800_sources])
        s_iso = np.array([s['ISO_AREA'] for s in series_11800_sources])
        s_star = np.array([s['STAR_FLAG'] for s in series_11800_sources])
        s_z = np.array([s['LP_Z_MED'] for s in series_11800_sources])
        s_z_best = np.array([s['LP_Z_BEST'] for s in series_11800_sources])
        s_chi2 = np.array([s['LP_FIT_CHI'] for s in series_11800_sources])
        s_nbands = np.array([s['LP_NBANDS'] for s in series_11800_sources])
        s_mass = np.array([s['LP_MASS_MED'] for s in series_11800_sources])
        s_sfr = np.array([s['LP_SFR_MED'] for s in series_11800_sources])
        s_numbers = np.array([s['NUMBER'] for s in series_11800_sources])
        
        print(f"\n  11800-series source properties:")
        print(f"  {'ID':>6} {'RA':>10} {'DEC':>10} {'X':>7} {'Y':>7} {'A':>7} {'B':>7} {'theta':>6} {'ellip':>6} {'kron':>6} {'iso':>5} {'z_med':>7} {'chi2':>7} {'nband':>5}")
        print("  " + "-" * 105)
        
        for i in range(len(series_11800_sources)):
            print(f"  {s_numbers[i]:>6} {s_ra[i]:>10.5f} {s_dec[i]:>10.5f} {s_x[i]:>7.1f} {s_y[i]:>7.1f} {s_a[i]:>7.2f} {s_b[i]:>7.2f} {s_theta[i]:>6.1f} {s_ellip[i]:>6.3f} {s_kron[i]:>6.2f} {s_iso[i]:>5.0f} {s_z[i]:>7.3f} {s_chi2[i]:>7.1f} {s_nbands[i]:>5.0f}")
        
        # Check for deblending signatures:
        # 1. Proximity in pixel space - are they near each other?
        pixel_dists = []
        for i in range(len(s_x)):
            for j in range(i+1, len(s_x)):
                dist = np.sqrt((s_x[i] - s_x[j])**2 + (s_y[i] - s_y[j])**2)
                pixel_dists.append(dist)
        
        pixel_dists = np.array(pixel_dists)
        print(f"\n  Deblending checks:")
        print(f"  Pixel position ranges: X={s_x.min():.1f}-{s_x.max():.1f}, Y={s_y.min():.1f}-{s_y.max():.1f}")
        print(f"  Pixel span: {s_x.max()-s_x.min():.1f} x {s_y.max()-s_y.min():.1f}")
        print(f"  Min pixel separation: {pixel_dists.min():.1f} px" if len(pixel_dists) > 0 else "  Only one source")
        print(f"  Mean pixel separation: {pixel_dists.mean():.1f} px" if len(pixel_dists) > 0 else "")
        
        # Check if sources are very close (within a few pixels of each other)
        close_pairs = pixel_dists[pixel_dists < 10.0] if len(pixel_dists) > 0 else []
        print(f"  Pairs with <10 px separation: {len(close_pairs)} / {len(pixel_dists)}")
        
        # Check for highly elongated or small sources
        print(f"  A_IMAGE range: {s_a.min():.2f} - {s_a.max():.2f} (mean: {s_a.mean():.2f})")
        print(f"  B_IMAGE range: {s_b.min():.2f} - {s_b.max():.2f} (mean: {s_b.mean():.2f})")
        print(f"  Ellipticity range: {s_ellip.min():.3f} - {s_ellip.max():.3f}")
        
        very_small = s_a[s_a < 2.0]
        print(f"  Very small (A_IMAGE < 2 px): {len(very_small)} / {len(s_a)}")
        
        # Check for similar theta angles (aligned sources might be deblending artifacts)
        theta_diff = []
        for i in range(len(s_theta)):
            for j in range(i+1, len(s_theta)):
                diff = np.abs(s_theta[i] - s_theta[j])
                diff = min(diff, 180 - diff)  # Handle 180 deg wrap
                theta_diff.append(diff)
        theta_diff = np.array(theta_diff)
        if len(theta_diff) > 0:
            print(f"  Theta angle differences: min={theta_diff.min():.1f}°, max={theta_diff.max():.1f}°, mean={theta_diff.mean():.1f}°")
            aligned_pairs = theta_diff[theta_diff < 10.0]
            print(f"  Aligned pairs (θ diff < 10°): {len(aligned_pairs)} / {len(theta_diff)}")
        
        # Check if all sources are in the same NIRCam pointing (same X/Y region)
        # For typical NIRCam, images are ~2048 x 2048 pixels
        print(f"\n  NIRCam detector context:")
        print(f"    X range: {s_x.min():.1f} - {s_x.max():.1f} (span: {s_x.max()-s_x.min():.1f})")
        print(f"    Y range: {s_y.min():.1f} - {s_y.max():.1f} (span: {s_y.max()-s_y.min():.1f})")
        print(f"    All in same detector region: {s_x.max()-s_x.min() < 100 and s_y.max()-s_y.min() < 100}")
        
        # Check F277W flux as a sanity check
        # The 11800-series should have measurable flux in NIRCam bands
        # Let's check a few bands
        f277w_flux = np.array([s['F277W_FLUX'] for s in series_11800_sources])
        f356w_flux = np.array([s['F356W_FLUX'] for s in series_11800_sources])
        f444w_flux = np.array([s['F444W_FLUX'] for s in series_11800_sources])
        f200w_flux = np.array([s['F200W_FLUX'] for s in series_11800_sources])
        
        print(f"\n  Photometric fluxes:")
        print(f"  {'ID':>6} {'F200W':>10} {'F277W':>10} {'F356W':>10} {'F444W':>10}")
        for i in range(len(s_numbers)):
            print(f"  {s_numbers[i]:>6} {f200w_flux[i]:>10.2f} {f277w_flux[i]:>10.2f} {f356w_flux[i]:>10.2f} {f444w_flux[i]:>10.2f}")
        
        # Check for negative fluxes (artifact indicator)
        negative_flux = (f277w_flux < 0) | (f356w_flux < 0) | (f444w_flux < 0)
        print(f"  Sources with negative flux in any NIRCam band: {np.sum(negative_flux)} / {len(s_numbers)}")
        
        deblending_results = {
            "n_sources_found": len(series_11800_sources),
            "source_details": [],
            "pixel_x_range": [float(s_x.min()), float(s_x.max())],
            "pixel_y_range": [float(s_y.min()), float(s_y.max())],
            "pixel_span_x": float(s_x.max() - s_x.min()),
            "pixel_span_y": float(s_y.max() - s_y.min()),
            "min_pixel_separation": float(pixel_dists.min()) if len(pixel_dists) > 0 else None,
            "mean_pixel_separation": float(pixel_dists.mean()) if len(pixel_dists) > 0 else None,
            "close_pairs_lt10px": int(len(close_pairs)),
            "a_image_range": [float(s_a.min()), float(s_a.max())],
            "b_image_range": [float(s_b.min()), float(s_b.max())],
            "ellipticity_range": [float(s_ellip.min()), float(s_ellip.max())],
            "very_small_sources_a_lt_2": int(len(very_small)),
            "theta_aligned_pairs_lt10deg": int(len(aligned_pairs)) if len(theta_diff) > 0 else None,
            "sources_with_negative_flux": int(np.sum(negative_flux)),
            "all_same_detector_region": bool(s_x.max() - s_x.min() < 100 and s_y.max() - s_y.min() < 100)
        }
        
        for i in range(len(series_11800_sources)):
            deblending_results["source_details"].append({
                "number": int(s_numbers[i]),
                "ra": float(s_ra[i]),
                "dec": float(s_dec[i]),
                "x_image": float(s_x[i]),
                "y_image": float(s_y[i]),
                "a_image": float(s_a[i]),
                "b_image": float(s_b[i]),
                "theta_image": float(s_theta[i]),
                "ellipticity": float(s_ellip[i]),
                "kron_radius": float(s_kron[i]),
                "iso_area": int(s_iso[i]),
                "star_flag": int(s_star[i]),
                "z_med": float(s_z[i]),
                "z_best": float(s_z_best[i]),
                "chi2": float(s_chi2[i]),
                "nbands": int(s_nbands[i]),
                "mass": float(s_mass[i]),
                "sfr": float(s_sfr[i]),
                "f277w_flux": float(f277w_flux[i]),
                "f356w_flux": float(f356w_flux[i]),
                "f444w_flux": float(f444w_flux[i]),
                "f200w_flux": float(f200w_flux[i])
            })
        
        # Deblending assessment
        deblending_indicators = []
        
        # Check 1: Very close pixel proximity
        if len(pixel_dists) > 0 and pixel_dists.min() < 5.0:
            deblending_indicators.append("VERY_CLOSE_PIXELS: sources separated by <5 pixels")
        if len(pixel_dists) > 0 and pixel_dists.min() < 10.0:
            deblending_indicators.append("CLOSE_PIXELS: sources separated by <10 pixels")
        
        # Check 2: Very small sources
        if len(very_small) > 0:
            deblending_indicators.append(f"SMALL_SOURCES: {len(very_small)} sources have A_IMAGE < 2 px")
        
        # Check 3: Aligned theta angles
        if len(theta_diff) > 0 and len(aligned_pairs) >= len(theta_diff) * 0.5:
            deblending_indicators.append(f"ALIGNED_THETA: {len(aligned_pairs)}/{len(theta_diff)} pairs have aligned position angles")
        
        # Check 4: Negative flux
        if np.sum(negative_flux) > 0:
            deblending_indicators.append(f"NEGATIVE_FLUX: {int(np.sum(negative_flux))} sources have negative NIRCam flux")
        
        # Check 5: Low NBANDS
        low_nbands = s_nbands[s_nbands < 5]
        if len(low_nbands) > 0:
            deblending_indicators.append(f"LOW_NBANDS: {len(low_nbands)} sources have <5 bands used in fitting")
        
        # Check 6: High chi2
        high_chi2 = s_chi2[s_chi2 > 5.0]
        if len(high_chi2) > 0:
            deblending_indicators.append(f"HIGH_CHI2: {len(high_chi2)} sources have chi2 > 5.0")
        
        # Check 7: All sources in same compact detector region
        if s_x.max() - s_x.min() < 50 and s_y.max() - s_y.min() < 50:
            deblending_indicators.append("COMPACT_REGION: all sources within 50x50 pixel region")
        
        # Overall assessment
        n_indicators = len(deblending_indicators)
        if n_indicators >= 4:
            deblending_verdict = "LIKELY_DEBLENDING_ARTIFACTS"
        elif n_indicators >= 2:
            deblending_verdict = "POSSIBLE_DEBLENDING_ARTIFACTS"
        else:
            deblending_verdict = "UNLIKELY_DEBLENDING_ARTIFACTS"
        
        deblending_results["deblending_indicators"] = deblending_indicators
        deblending_results["deblending_verdict"] = deblending_verdict
        deblending_results["n_deblending_indicators"] = n_indicators
        
        print(f"\n  Deblending indicators found:")
        for ind in deblending_indicators:
            print(f"    - {ind}")
        print(f"  Total indicators: {n_indicators}/7")
        print(f"  VERDICT: {deblending_verdict}")
        
        results["deblending_11800_series"] = deblending_results

# ============================================================
# 6. SAVE RESULTS
# ============================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

output_path = 'ceers_jades_analysis_results.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"  Saved to {output_path}")
print(f"  File size: {os.path.getsize(output_path)} bytes")

# Print summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# JADES comparison
jr = results.get("jades_dr4_internal", {})
print(f"\nJADES DR4 z_PRISM vs z_phot:")
print(f"  N={jr.get('n_matched', 'N/A')}")
print(f"  Δz/(1+z): mean={jr.get('dz_over_1pz_mean', 'N/A'):+.6f}, median={jr.get('dz_over_1pz_median', 'N/A'):+.6f}, std={jr.get('dz_over_1pz_std', 'N/A'):.6f}")

# Cluster
cp = results.get("ceers_z13p5_cluster", {})
print(f"\nCEERS z=13.5 cluster:")
print(f"  Found {cp.get('n_sources_found', 'N/A')}/{cp.get('n_sources_targeted', 'N/A')} sources")
print(f"  Spatial extent: {cp.get('ra_std_arcsec', 'N/A'):.1f} x {cp.get('dec_std_arcsec', 'N/A'):.1f} arcsec")
print(f"  Mean pair distance: {cp.get('mean_pairwise_dist_arcsec', 'N/A'):.1f} arcsec")

# Clustering
sc = results.get("spatial_clustering", {})
if sc:
    print(f"\nSpatial clustering:")
    print(f"  Target mean NN: {sc.get('target_mean_nn_arcsec', 'N/A'):.1f} arcsec")
    print(f"  Random mean NN: {sc.get('random_mean_nn_arcsec_mean', 'N/A'):.1f} arcsec")
    print(f"  Percentile: {sc.get('target_nn_percentile', 'N/A'):.1f}%")
    print(f"  Significantly clustered: {sc.get('is_significantly_clustered', 'N/A')}")

# Deblending
db = results.get("deblending_11800_series", {})
if db:
    print(f"\n11800-series deblending check:")
    print(f"  Found {db.get('n_sources_found', 'N/A')} sources")
    print(f"  Indicators: {db.get('n_deblending_indicators', 'N/A')}/7")
    print(f"  Verdict: {db.get('deblending_verdict', 'N/A')}")

print("\nDone!")