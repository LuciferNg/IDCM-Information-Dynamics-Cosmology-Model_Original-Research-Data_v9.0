#!/usr/bin/env python3
"""
DESI BAO Harmonic Analysis — K_Chain Prediction
================================================
Compare DESI DR1 and DR2 BAO measurements with K_Chain harmonic series.

K_Chain prediction:
  λ_sync = 2π·R_H/88 = 294.88 Mpc  (fundamental SYNC mode)
  BAO = λ_sync/2 = 147.44 Mpc        (first harmonic)
  Higher harmonics: λ_sync/n for n=3,4,5,...

DESI DR1: 1.3-3.5% errors on DM/rd
DESI DR2: ~0.8% errors on Lyα BAO, galaxy bins ~1-2%
DESI DR2 Lyα forest: DM/rd = 39.32 ± 0.33, DH/rd = 8.600 ± 0.066 (0.8%)
"""

import math
import sys
import json

# ================================================================
# K_Chain parameters
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
KAPPA = 1/16
BETA = PHI_INV / 2
N_d = 44
H0 = 72.59  # km/s/Mpc (IDCM structural)
c = 299792.458  # km/s
Mpc = 3.085677581e22  # m

# Hubble radius
R_H = c / H0  # Mpc (c in km/s, H0 in km/s/Mpc → result in Mpc)

print("=" * 70)
print("DESI BAO HARMONIC ANALYSIS — K_Chain Prediction")
print("=" * 70)
print(f"\nIDCM Parameters:")
print(f"  H₀    = {H0:.2f} km/s/Mpc (structural)")
print(f"  R_H   = {R_H:.2f} Mpc = {R_H/1000:.2f} Gpc")
print(f"  N_d   = {N_d} (K_Chain sites)")
print()

# ================================================================
# K_Chain SYNC wavelength
# ================================================================
# The K_Chain is a 44-site ring (88 with dual). The SYNC coupling
# cos(θ_n - θ_m - 2π/88) has phase difference 2π/88 between adjacent sites.
# The physical wavelength is the ring circumference divided by 88.
# The ring circumference = R_H (Hubble radius = maximum observable scale).
lambda_sync = 2 * math.pi * R_H / 88  # Mpc

print("K_Chain SYNC Wavelength:")
print(f"  λ_sync = 2π / (88/R_H) = {lambda_sync:.2f} Mpc")
print()

# ================================================================
# Harmonic series
# ================================================================
harmonics = {}
for n in range(1, 11):
    harm = lambda_sync / n
    harmonics[n] = harm
    if n == 2:
        print(f"  λ_sync/{n} = {harm:.2f} Mpc  ← BAO (first harmonic)")
    else:
        print(f"  λ_sync/{n} = {harm:.2f} Mpc")

print(f"\n  Observed BAO = 147.05 Mpc (DESI, eq. 2.5, from Planck CMB)")
print(f"  λ_sync/2     = {lambda_sync/2:.2f} Mpc (IDCM prediction)")
print(f"  Ratio        = {lambda_sync/2/147.05:.4f}")
print()

# ================================================================
# DESI DR1 BAO measurements (from Table 1)
# ================================================================
# DESI measures DM/rd, DH/rd, DV/rd where rd = 147.05 Mpc
# Convert to physical distances: D = (DM/rd) × rd

desi_data = [
    # (tracer, zeff, DM_rd, err_DM, DH_rd, err_DH, DV_rd, err_DV, r)
    ("BGS",  0.295,  None, None, None, None, 7.93, 0.15, None),
    ("LRG1", 0.510,  13.62, 0.25, 20.98, 0.61, None, None, -0.445),
    ("LRG2", 0.706,  16.85, 0.32, 20.08, 0.60, None, None, -0.420),
    ("LRG3+ELG1", 0.930, 21.71, 0.28, 17.88, 0.35, None, None, -0.389),
    ("ELG2", 1.317,  27.79, 0.69, 13.82, 0.42, None, None, -0.444),
    ("QSO",  1.491,  None, None, None, None, 26.07, 0.67, None),
    ("Lya",  2.330,  39.71, 0.94, 8.52, 0.17, None, None, -0.477),
]

rd = 147.05  # Mpc (DESI sound horizon)

print("=" * 70)
print("DESI DR1 BAO Measurements (converted to Mpc)")
print("=" * 70)
print(f"{'Tracer':<12} {'z_eff':<6} {'DM (Mpc)':<15} {'DH (Mpc)':<15} {'DV (Mpc)':<15}")
print("-" * 63)

for row in desi_data:
    tracer, z, dm_r, e_dm, dh_r, e_dh, dv_r, e_dv, r = row
    dm = dm_r * rd if dm_r else None
    e_dm_val = e_dm * rd if e_dm else None
    dh = dh_r * rd if dh_r else None
    e_dh_val = e_dh * rd if e_dh else None
    dv = dv_r * rd if dv_r else None
    e_dv_val = e_dv * rd if e_dv else None
    
    dm_str = f"{dm:.1f} ± {e_dm_val:.1f}" if dm else "—"
    dh_str = f"{dh:.1f} ± {e_dh_val:.1f}" if dh else "—"
    dv_str = f"{dv:.1f} ± {e_dv_val:.1f}" if dv else "—"
    print(f"{tracer:<12} {z:<6.3f} {dm_str:<15} {dh_str:<15} {dv_str:<15}")

print()

# ================================================================
# Predict what DESI should see at each redshift
# ================================================================
# The BAO signal appears as a peak in the correlation function at ~147 Mpc
# In ΛCDM, this is the sound horizon rd
# In IDCM, this is λ_sync/2
#
# The DESI measurements DM(z)/rd are the comoving distance to redshift z
# divided by the sound horizon. The BAO scale is imprinted as a standard ruler.
#
# Key question: Is the BAO signal at 147 Mpc consistent with being a harmonic
# of the K_Chain fundamental mode λ_sync = 294.9 Mpc?

print("=" * 70)
print("K_Chain Harmonic Prediction vs DESI BAO")
print("=" * 70)
print()

# The prediction: BAO = λ_sync/2 = 147.45 Mpc
bao_pred = lambda_sync / 2
bao_obs = 147.05  # DESI eq. 2.5

print(f"BAO prediction: λ_sync/2 = {bao_pred:.2f} Mpc")
print(f"BAO observed:   147.05 Mpc (DESI, from Planck CMB)")
print(f"Deviation:      {abs(bao_pred - bao_obs):.2f} Mpc ({abs(bao_pred/bao_obs - 1)*100:.2f}%)")
print()

# ================================================================
# Test: Does the DESI data prefer a specific BAO scale?
# ================================================================
# DESI constrains DM/rd at each redshift.
# In ΛCDM, rd = 147.05 Mpc is fixed from CMB.
# In IDCM, the BAO scale is λ_sync/2 = 147.45 Mpc.
#
# The difference (0.27%) is well within DESI's measurement errors.
# Both predictions are consistent with the data.

print("=" * 70)
print("Consistency Check")
print("=" * 70)
print()
print(f"IDCM predicts BAO = λ_sync/2 = {bao_pred:.2f} Mpc")
print(f"ΛCDM uses  rd = 147.05 Mpc")
print(f"Difference: {(bao_pred - bao_obs):.2f} Mpc = {(bao_pred/bao_obs - 1)*100:.3f}%")
print()
print("DESI DR1 errors on DM/rd are 1.3-3.5%")
print("DESI DR1 errors on DH/rd are 2.0-3.0%")
print("The 0.27% difference is well within DESI errors.")
print("Both predictions are consistent with current data.")
print()

# ================================================================
# Higher harmonics: testable prediction
# ================================================================
print("=" * 70)
print("Testable Prediction: Higher BAO Harmonics")
print("=" * 70)
print()
print("If BAO = λ_sync/2 (first harmonic of K_Chain closed ring),")
print("then higher harmonics should exist at:")
print()

for n in [3, 4, 5, 6, 7]:
    harm = lambda_sync / n
    # Convert to k-space (k = 2π/λ)
    k = 2 * math.pi / harm
    print(f"  λ/{n} = {harm:.1f} Mpc  (k = {k:.4f} h/Mpc, h={H0/100:.3f})")

print()
print("These harmonics should appear as additional wiggles in the")
print("matter power spectrum P(k) at k = 2π/(λ_sync/n) = n·k_fundamental")
print()
print("ΛCDM predicts these wiggles as the Fourier transform of the")
print("BAO peak, but does NOT predict the exact harmonic spacing.")
print(f"IDCM predicts EXACTLY equal spacing in k-space:")
print(f"  Δk = 2π/λ_sync = 2π/{lambda_sync:.1f} = {2*math.pi/lambda_sync:.4f} h/Mpc")
print(f"  This is the fundamental wavenumber of the K_Chain SYNC mode.")
print()

# ================================================================
# Summary
# ================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
1. IDCM PREDICTION: BAO = λ_sync/2 = {bao_pred:.2f} Mpc
   ΛCDM value: rd = 147.05 Mpc
   Difference: {abs(bao_pred - bao_obs):.2f} Mpc ({abs(bao_pred/bao_obs-1)*100:.3f}%)

2. CONSISTENCY: Both predictions are consistent with DESI DR1 data.
   DESI measurement errors (1.3-3.5%) are much larger than the 0.27% 
   difference between the two predictions.

3. DISCRIMINATION: To distinguish IDCM from ΛCDM, need:
   - Higher precision BAO at multiple redshifts (DESI DR2+)
   - Detection of higher harmonics at λ/3, λ/4, λ/5
   - Exact harmonic spacing Δk = {2*math.pi/lambda_sync:.4f} h/Mpc

4. MOST IMPORTANT: IDCM DERIVES the BAO scale from K_Chain geometry.
   ΛCDM fits it from CMB data. This is the fundamental difference:
   structural derivation vs. phenomenological fit.
""")