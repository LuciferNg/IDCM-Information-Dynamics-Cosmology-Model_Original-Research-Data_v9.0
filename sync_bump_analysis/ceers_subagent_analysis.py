#!/usr/bin/env python3
"""Investigate P(z) width anomaly at z=13.5 in CEERS DR1 catalog."""

from astropy.io import fits
import numpy as np
import json

# ============================================================
# 1. LOAD CEERS DR1 CATALOG
# ============================================================
with fits.open('ceers_dr1_catalog.fits.gz') as hdul:
    data = hdul[1].data
    print(f"Total CEERS galaxies: {len(data)}")

    # Extract key columns
    z_med = data['LP_Z_MED']
    z_hi = data['LP_Z_MED68_HIGH']
    z_lo = data['LP_Z_MED68_LOW']
    ra = data['RA']
    dec = data['DEC']
    number = data['NUMBER']
    mass_med = data['LP_MASS_MED']
    mass_lo = data['LP_MASS_MED68_LOW']
    mass_hi = data['LP_MASS_MED68_HIGH']

    # Calculate P(z) width
    pz_width = z_hi - z_lo
    valid = (z_hi > 0) & (z_lo > 0) & (z_hi > z_lo) & np.isfinite(pz_width)

    print(f"Valid P(z) measurements: {np.sum(valid)}")

    # ============================================================
    # 2. P(Z) WIDTH IN REDSHIFT BINS
    # ============================================================
    print("\n=== P(z) Width by Redshift Bin ===")
    bins = [0, 2, 4, 6, 8, 10, 11, 12, 13, 14, 15, 20, 30]
    for i in range(len(bins)-1):
        lo, hi = bins[i], bins[i+1]
        mask = valid & (z_med >= lo) & (z_med < hi)
        n = np.sum(mask)
        if n > 0:
            w = pz_width[mask]
            print(f"  z={lo}-{hi}: N={n:5d}, mean_width={np.mean(w):.3f}, median_width={np.median(w):.3f}, "
                  f"std={np.std(w):.3f}, min={np.min(w):.3f}, max={np.max(w):.3f}")

    # ============================================================
    # 3. FINER BINNING AROUND Z=13.5
    # ============================================================
    print("\n=== Finer Binning around z=13.5 ===")
    fine_bins = [12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0]
    for i in range(len(fine_bins)-1):
        lo, hi = fine_bins[i], fine_bins[i+1]
        mask = valid & (z_med >= lo) & (z_med < hi)
        n = np.sum(mask)
        if n > 0:
            w = pz_width[mask]
            print(f"  z={lo}-{hi}: N={n:4d}, mean_width={np.mean(w):.3f}, median_width={np.median(w):.3f}, "
                  f"std={np.std(w):.3f}, min={np.min(w):.3f}, max={np.max(w):.3f}")

    # ============================================================
    # 4. EXTRACT Z=13-14 CLUSTER - DETAILED ANALYSIS
    # ============================================================
    print("\n=== Z=13-14 Cluster: Detailed Analysis ===")
    z13_mask = valid & (z_med >= 13.0) & (z_med < 14.0)
    z13_idx = np.where(z13_mask)[0]
    n_z13 = len(z13_idx)
    print(f"Total galaxies in z=13-14: {n_z13}")

    # Sort by NUMBER
    z13_sorted = sorted(z13_idx, key=lambda i: number[i])
    print(f"\n{n_z13} galaxies (sorted by NUMBER):")
    for i in z13_sorted:
        print(f"  NUMBER={number[i]:6d}  z_med={z_med[i]:.4f}  z_lo={z_lo[i]:.4f}  z_hi={z_hi[i]:.4f}  "
              f"width={pz_width[i]:.3f}  RA={ra[i]:.5f}  DEC={dec[i]:.5f}  "
              f"mass={mass_med[i]:.2e}  mass_lo={mass_lo[i]:.2e}  mass_hi={mass_hi[i]:.2e}")

    # ============================================================
    # 5. SPATIAL ANALYSIS
    # ============================================================
    print(f"\n=== Spatial clustering of z=13-14 cluster ===")
    ra_z13 = ra[z13_mask]
    dec_z13 = dec[z13_mask]
    z_z13 = z_med[z13_mask]
    w_z13 = pz_width[z13_mask]

    print(f"RA range: {np.min(ra_z13):.4f} to {np.max(ra_z13):.4f}  (span: {np.max(ra_z13)-np.min(ra_z13):.4f} deg)")
    print(f"DEC range: {np.min(dec_z13):.4f} to {np.max(dec_z13):.4f}  (span: {np.max(dec_z13)-np.min(dec_z13):.4f} deg)")

    # Check if there are spatial sub-clusters
    # Group by ~0.1 deg bins
    ra_bins = np.arange(214, 217, 0.1)
    dec_bins = np.arange(52, 54, 0.1)
    print(f"\nSpatial distribution (RA-DEC grid):")
    for ri in range(len(ra_bins)-1):
        for di in range(len(dec_bins)-1):
            mask2 = (ra_z13 >= ra_bins[ri]) & (ra_z13 < ra_bins[ri+1]) & \
                    (dec_z13 >= dec_bins[di]) & (dec_z13 < dec_bins[di+1])
            n = np.sum(mask2)
            if n > 0:
                print(f"  RA=[{ra_bins[ri]:.1f},{ra_bins[ri+1]:.1f}) DEC=[{dec_bins[di]:.1f},{dec_bins[di+1]:.1f}): N={n}")

    # ============================================================
    # 6. MASS DISTRIBUTION
    # ============================================================
    print(f"\n=== Mass distribution of z=13-14 cluster ===")
    m_z13 = mass_med[z13_mask]
    print(f"Mass range: {np.min(m_z13):.2e} to {np.max(m_z13):.2e}")
    print(f"Mean mass: {np.mean(m_z13):.2e}, Median mass: {np.median(m_z13):.2e}")
    print(f"log10(M/Msun) range: {np.min(np.log10(m_z13)):.2f} to {np.max(np.log10(m_z13)):.2f}")
    by_mass = sorted(z13_idx, key=lambda i: mass_med[i], reverse=True)
    for i in by_mass[:10]:
        print(f"  NUMBER={number[i]:6d}  mass={mass_med[i]:.2e}  [{mass_lo[i]:.2e}, {mass_hi[i]:.2e}]  z={z_med[i]:.4f}")

    # ============================================================
    # 7. GALAXIES AT Z>14.5
    # ============================================================
    print(f"\n=== Galaxies at z>14.5 ===")
    z_high_mask = valid & (z_med > 14.5)
    z_high_idx = np.where(z_high_mask)[0]
    n_high = len(z_high_idx)
    print(f"Total galaxies with z_med > 14.5: {n_high}")
    if n_high > 0:
        z_high_sorted = sorted(z_high_idx, key=lambda i: z_med[i], reverse=True)
        for i in z_high_sorted:
            print(f"  NUMBER={number[i]:6d}  z_med={z_med[i]:.4f}  z_lo={z_lo[i]:.4f}  z_hi={z_hi[i]:.4f}  "
                  f"width={pz_width[i]:.3f}  RA={ra[i]:.5f}  DEC={dec[i]:.5f}  mass={mass_med[i]:.2e}")

    # ============================================================
    # 8. COMPARE WITH OTHER Z RANGES FOR CONTEXT
    # ============================================================
    print(f"\n=== Comparison: P(z) width in z=11-15 for context ===")
    for zlo, zhi in [(11, 12), (12, 13), (13, 14), (14, 15)]:
        mask = valid & (z_med >= zlo) & (z_med < zhi)
        n = np.sum(mask)
        if n > 0:
            print(f"  z={zlo}-{zhi}: N={n:4d}, "
                  f"width mean={np.mean(pz_width[mask]):.3f} median={np.median(pz_width[mask]):.3f} "
                  f"std={np.std(pz_width[mask]):.3f}")

    # ============================================================
    # 9. SAVE RESULTS TO JSON
    # ============================================================
    results = {
        'total_galaxies': int(len(data)),
        'z13_14_cluster': {
            'n_galaxies': int(n_z13),
            'width_mean': float(np.mean(w_z13)),
            'width_median': float(np.median(w_z13)),
            'width_std': float(np.std(w_z13)),
            'width_min': float(np.min(w_z13)),
            'width_max': float(np.max(w_z13)),
            'ra_span': float(np.max(ra_z13) - np.min(ra_z13)),
            'dec_span': float(np.max(dec_z13) - np.min(dec_z13)),
            'mass_min': float(np.min(m_z13)),
            'mass_max': float(np.max(m_z13)),
            'mass_mean': float(np.mean(m_z13)),
            'mass_median': float(np.median(m_z13)),
        },
        'z_high_14_5': {
            'n_galaxies': int(n_high),
            'galaxies': [{'number': int(number[i]), 'z_med': float(z_med[i]), 
                          'z_lo': float(z_lo[i]), 'z_hi': float(z_hi[i]),
                          'width': float(pz_width[i]), 
                          'ra': float(ra[i]), 'dec': float(dec[i]),
                          'mass': float(mass_med[i])} for i in z_high_sorted]
        } if n_high > 0 else {'n_galaxies': 0, 'galaxies': []}
    }

    with open('ceers_pz_analysis_subagent.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to ceers_pz_analysis_subagent.json")