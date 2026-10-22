# CEERS DR1 P(z) Width Anomaly Investigation — Final Summary

## 1. Initial Anomaly: P(z) Width Drop at z=13-14

| Redshift Bin | N    | Mean Width | Median Width | Std   |
|-------------|------|-----------|-------------|-------|
| 11-12       | 20   | 9.73      | 11.21       | 3.96  |
| 12-13       | 17   | 10.66     | 13.02       | 4.75  |
| **13-14**   | **65**| **3.35**  | **0.53**    | 4.92  |
| 14-15       | 18   | 1.23      | 0.78        | 2.03  |

The apparent drop is **misleading** — the z=13-14 bin is **bimodal**, not uniformly narrow.

## 2. The z=13-14 Cluster: Two Populations

### Narrow group (width < 1.0): 40 galaxies
- **Median width**: 0.21
- **Chi² range**: 18-4101 (mean: 363) — **VERY POOR FITS**
- 6/40 have STAR_FLAG=1 (stellar contamination)
- z_best disagrees with z_med for several (e.g., #47465: z_med=13.97, z_best=1.04)

### Wide group (width >= 1.0): 25 galaxies
- **Median width**: 10.45
- **Chi² range**: 2-78 (mean: 23) — **GOOD FITS**
- Only 2/25 have STAR_FLAG=1
- These are the physically plausible high-z candidates

## 3. Ultra-Narrow Sources (width < 0.1): Clear Artifacts

11 galaxies have P(z) widths of 0.017-0.099 — equivalent to dz/(1+z) ~ 0.001, which is **spectroscopic quality** and **unphysical for photometric redshifts**.

### The 11800-Series Cluster (5 sources)
- **11802** (width=0.057, chi²=254), **11804** (0.056, 284), **11807** (0.031, 261), **11809** (0.041, 493), **11810** (0.028, 126)
- **Spatially within 1-24 arcsec of each other** — clearly deblending artifacts of a single bright source
- 3/5 have STAR_FLAG=1
- Consecutive SExtractor IDs from the same detection tile

### Other Ultra-Narrow Artifacts
- **22460** (width=0.017, chi²=4101) — worst fit in entire catalog
- **85156** (width=0.019, chi²=1284, STAR_FLAG=1)
- **44979** (width=0.022, chi²=2582)
- **28776** (width=0.072, chi²=447)
- **36179** (width=0.066, chi²=251)
- **36328** (width=0.099, chi²=325)

## 4. Spatial Distribution

The z=13-14 galaxies are **widely scattered** across the CEERS field (RA 214.72-215.16, Dec 52.73-53.01), spanning ~0.45° × 0.28°. No single overdensity — the narrow-P(z) sources are scattered across the field, not physically clustered.

## 5. JADES DR4 Cross-Match

**Zero matches** between CEERS z=13-14 galaxies and JADES DR4 spectroscopic catalog. None of the 65 CEERS objects have spectroscopic confirmation in JADES.

JADES DR4 itself has 21 galaxies with z_PRISM > 10 (max z=14.5881), but these are in GOODS fields, not CEERS.

## 6. Galaxies at z > 14.5

**None found** in CEERS DR1 catalog.

## 7. Interpretation: The Narrow P(z) Cluster is an ARTIFACT

**Conclusion: The narrow P(z) cluster at z=13.5 is a systematic artifact, not a real physical overdensity.**

Evidence:
1. **Unphysical widths**: dz/(1+z) ~ 0.001 for photometric redshifts at z~13.5
2. **Catastrophic chi² values**: 4100, 2582, 1284 — orders of magnitude above the wide group (2-78)
3. **Stellar contamination**: 4/11 ultra-narrow sources have STAR_FLAG=1
4. **Deblending artifacts**: 5 consecutive SExtractor IDs within 1-24 arcsec
5. **z_best disagreement**: #47465 has z_med=13.97 but z_best=1.04 — a clear low-z interloper misclassified by the median
6. **No spectroscopic confirmation**: Zero matches in JADES DR4
7. **The SED fitting likely converged on a delta function** at the grid boundary for sources with insufficient photometric constraints, producing artificially narrow posteriors

The 25 wide-P(z) sources (width >= 1.0) with chi² < 80 are the **genuine high-z candidates** in CEERS DR1.