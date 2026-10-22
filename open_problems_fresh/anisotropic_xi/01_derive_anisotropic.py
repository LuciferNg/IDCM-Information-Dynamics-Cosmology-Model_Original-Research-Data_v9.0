#!/usr/bin/env python3
"""
Anisotropic ξ(σ, π) — 2D Correlation Function from Multipoles
===============================================================
The K_Chain impedance/reflection model predicts anisotropic features
in the 2D correlation function ξ(σ, π).

σ = transverse separation (perpendicular to LOS)
π = line-of-sight separation (parallel to LOS)

The monopole ξ₀(s) is the angle-averaged ξ(σ, π).
The quadrupole ξ₂(s) measures the anisotropy.

We don't have the full 2D data, but we can derive the quadrupole
from the monopole using the K_Chain geometry prediction.
"""

import math
import numpy as np
from scipy.interpolate import interp1d
from scipy.special import legendre
import sys, os, zipfile
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

print("=" * 80)
print("  ANISOTROPIC ξ(σ, π) — K_CHAIN GOEMETRY PREDICTION")
print("=" * 80)

# ================================================================
# 1. K_Chain geometry in 2D
# ================================================================
print(f"\n{'─'*80}")
print("  1. K_CHAIN GEOMETRY IN (σ, π) SPACE")
print(f"{'─'*80}")

# The K_Chain is a 1D closed string. In 3D projection:
# - The harmonic interference pattern is ISOTROPIC in angle-average
# - The impedance/reflection creates ANISOTROPIC features
# 
# Reflection geometry:
# - Mode n reflects at impedance mismatch → creates a standing wave
# - The reflected wave has a preferred direction (LOS vs transverse)
#
# ξ(σ, π) = ξ₀(s) + ξ₂(s) · P₂(μ) + ξ₄(s) · P₄(μ) + ...
# where μ = π/s, s = √(σ² + π²)

print(f"  ξ(σ, π) = ξ₀(s) + ξ₂(s) · P₂(μ) + ξ₄(s) · P₄(μ) + ...")
print(f"  where μ = π/s, s = √(σ² + π²)")
print(f"")
print(f"  K_Chain prediction:")
print(f"  - Monopole ξ₀: harmonic series at λ_sync/n")
print(f"  - Quadrupole ξ₂: impedance reflection signature")
print(f"  - Reflection creates a preferred LOS direction")
print(f"")

# ================================================================
# 2. Load BOSS DR12 monopole data
# ================================================================
print(f"{'─'*80}")
print("  2. BOSS DR12 MONOPOLE → QUADRUPOLE PREDICTION")
print(f"{'─'*80}")

z = zipfile.ZipFile('/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip')
data_path = 'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_zbin1_correlation_function_monopole_post_recon_bincent0.dat'
s_b, xi_b, err_b = [], [], []
with z.open(data_path) as f:
    for line in f.read().decode().strip().split('\n'):
        if line.startswith('#') or not line.strip(): continue
        parts = line.split()
        s_b.append(float(parts[0])); xi_b.append(float(parts[1])); err_b.append(float(parts[2]))
s_b = np.array(s_b); xi_b = np.array(xi_b); err_b = np.array(err_b)

lam_sync_hinv = LAMBDA_SYNC / H

# The quadrupole from the K_Chain model:
# ξ₂(s) = β · dξ₀/ds · s  (Kaiser formula for RSD)
# where β = f/b (growth rate / bias)

# For IDCM, the growth rate f is related to the K_Tree branching:
# f(z) = dln D / dln a ≈ Ω_m(z)^0.55  (standard ΛCDM)
# But IDCM: f(z) = B_eff(z)^α  (from K_Tree projection)

# Simple model: ξ₂(s) = 0.4 · ξ₀(s)  (typical for LRGs at z=0.38)
beta = 0.4
xi_2_pred = beta * xi_b

print(f"  β = {beta} (Kaiser RSD factor for LRGs)")
print(f"  ξ₂(s) = β · ξ₀(s) = {beta} · ξ₀(s)")
print(f"")

# ================================================================
# 3. 2D ξ(σ, π) from K_Chain model
# ================================================================
print(f"{'─'*80}")
print("  3. 2D ξ(σ, π) GOEMETRY REFLECTION PREDICTION")
print(f"{'─'*80}")

# Create a 2D grid
sigma = np.linspace(10, 200, 40)
pi = np.linspace(10, 200, 40)
SIGMA, PI = np.meshgrid(sigma, pi)
S = np.sqrt(SIGMA**2 + PI**2)
MU = PI / S

# Monopole (interpolated from BOSS data)
xi_interp = interp1d(s_b, xi_b, kind='cubic', bounds_error=False, fill_value=0)
xi_0 = np.array([[float(xi_interp(s)) for s in row] for row in S])

# Quadrupole (K_Chain model)
P2 = 0.5 * (3 * MU**2 - 1)  # Legendre P₂
xi_2_model = beta * xi_0 * P2

# Full 2D model
xi_2d = xi_0 + xi_2_model

# Find reflection features in 2D
# The reflection at scale s_reflect creates a preferred direction
reflections = []
for n in range(2, 12):
    gam = 4 * math.sin(math.pi * n / 88)**2
    vg = math.cos(math.pi * n / 88)
    Z_curr = gam / abs(vg) if abs(vg) > 1e-10 else 1e10
    Z_prev = 4 * math.sin(math.pi * (n-1) / 88)**2 / abs(math.cos(math.pi * (n-1) / 88))
    R = (Z_curr - Z_prev) / (Z_curr + Z_prev) if (Z_curr > 0 and Z_prev > 0) else 0
    s_ref = lam_sync_hinv / (2 * n * abs(R)) if abs(R) > 1e-10 else 1e10
    reflections.append((n, R, s_ref))

print(f"  Reflection features in (σ, π) space:")
print(f"  {'n':<4} {'R':<12} {'s_ref (h⁻¹)':<15} {'σ_ref':<12} {'π_ref':<12}")
print(f"  {'─'*55}")

for n, R, s_ref in reflections:
    if s_ref < 10 or s_ref > 200: continue
    # Isotropic reflection: σ = π = s_ref/√2
    sigma_ref = s_ref / math.sqrt(2)
    pi_ref = s_ref / math.sqrt(2)
    print(f"  {n:<4} {R:<+12.4f} {s_ref:<15.1f} {sigma_ref:<12.1f} {pi_ref:<12.1f}")

# ================================================================
# 4. Check if we have quadrupole data
# ================================================================
print(f"\n{'─'*80}")
print("  4. QUADRUPOLE DATA AVAILABILITY")
print(f"{'─'*80}")

# Check eBOSS data for multipole files
e_files = ['/home/wsl/IDCM/sync_bump_analysis/eboss_dr16_lrg_xi.txt',
           '/home/wsl/IDCM/sync_bump_analysis/eboss_xi_full.txt']

print(f"  Available data files:")
for f in e_files:
    if os.path.exists(f):
        fsize = os.path.getsize(f)
        print(f"  ✅ {f} ({fsize} bytes)")
    else:
        print(f"  ❌ {f}")

# Check for multipole data in the tar.gz
print(f"")
print(f"  Current data: monopole ξ₀(s) only")
print(f"  Needed: ξ₂(s) quadrupole, ξ₄(s) hexadecapole")
print(f"  These are available in the BOSS/eBOSS publications")
print(f"  but require downloading additional data files")
print(f"")
print(f"  Without multipole data, the 2D analysis is limited to")
print(f"  the K_Chain geometry prediction shown above.")

# ================================================================
# 5. Summary
# ================================================================
print(f"\n{'─'*80}")
print("  5. SUMMARY")
print(f"{'─'*80}")

print(f"""
  Anisotropic ξ(σ, π) analysis:
  
  K_Chain prediction:
    ξ(σ, π) = ξ₀(s) + ξ₂(s) · P₂(μ) + ...
    where ξ₂(s) = β · ξ₀(s)  (Kaiser RSD)
    and β = {beta} (LRG at z=0.38)
  
  Reflection features in (σ, π):
    Isotropic reflection: σ = π = s_reflect/√2
    n=2: σ=π={reflections[0][2]/math.sqrt(2):.0f} h⁻¹ Mpc
    n=3: σ=π={reflections[1][2]/math.sqrt(2):.0f} h⁻¹ Mpc
  
  Data limitation:
    We only have monopole ξ₀(s) data.
    Quadrupole ξ₂(s) and hexadecapole ξ₄(s) required
    for full 2D analysis.
    
  Action: Download BOSS DR12/eBOSS DR16 multipole data
  from the SDSS data release server.
""")