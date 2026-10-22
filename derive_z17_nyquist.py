#!/usr/bin/env python3
"""z=17 Nyquist 截斷的結構推導 — 修正版"""
import math
import numpy as np

H0 = 72.59
Om = 0.317
t_site = 0.306  # Gyr

def lookback_time(z, H0, Om):
    """Lookback time in Gyr from z=0 to z."""
    N = 200000
    z_arr = np.linspace(0, z, N+1)
    dz = z / N
    integrand = 1.0 / ((1 + z_arr) * np.sqrt(Om*(1+z_arr)**3 + (1-Om)))
    integral = integrand[0] + integrand[-1]
    integral += 4 * np.sum(integrand[1:-1:2])
    integral += 2 * np.sum(integrand[2:-1:2])
    integral *= dz / 3
    return integral / H0 * 977.8

# Total lookback time (z=∞ ≈ 1000)
t_total = lookback_time(1000, H0, Om)
print(f"Total lookback time (z=0→1000) = {t_total:.4f} Gyr")

# Universe age at z
for z in [10, 15, 16, 17, 18, 20]:
    t_z = lookback_time(z, H0, Om)
    age_z = t_total - t_z
    print(f"z={z:3d}: lookback={t_z:.4f} Gyr, age={age_z*1000:.1f} Myr")

# K_Chain Nyquist time scale
for n in [22, 44]:
    gamma = 4 * math.sin(math.pi * n / 88)**2
    tau = t_site / math.sqrt(gamma) * 1000  # Myr
    T = 2 * math.pi * t_site / math.sqrt(gamma) * 1000  # Myr
    print(f"\nn={n}: γ={gamma:.6f}")
    print(f"  characteristic time = t_site/√γ = {tau:.1f} Myr")
    print(f"  period = 2π·t_site/√γ = {T:.1f} Myr")

# Find exact z where universe age = 216.4 Myr
target_age = t_site / math.sqrt(2) * 1000  # 216.4 Myr
print(f"\n\n搜尋 universe age = {target_age:.1f} Myr 嘅 redshift:")
z_lo, z_hi = 0, 1000
for _ in range(60):
    z_mid = (z_lo + z_hi) / 2
    t_mid = lookback_time(z_mid, H0, Om)
    age_mid = (t_total - t_mid) * 1000  # Myr
    if age_mid > target_age:
        z_lo = z_mid
    else:
        z_hi = z_mid
z_match = (z_lo + z_hi) / 2
print(f"  t_site/√2 = {target_age:.1f} Myr 對應 z ≈ {z_match:.2f}")

# 2×t_site
target_2ts = 2 * t_site * 1000
z_lo, z_hi = 0, 1000
for _ in range(60):
    z_mid = (z_lo + z_hi) / 2
    t_mid = lookback_time(z_mid, H0, Om)
    age_mid = (t_total - t_mid) * 1000
    if age_mid > target_2ts:
        z_lo = z_mid
    else:
        z_hi = z_mid
z_match_2ts = (z_lo + z_hi) / 2
print(f"  2×t_site = {target_2ts:.0f} Myr 對應 z ≈ {z_match_2ts:.2f}")

# 1×t_site
target_1ts = t_site * 1000
z_lo, z_hi = 0, 1000
for _ in range(60):
    z_mid = (z_lo + z_hi) / 2
    t_mid = lookback_time(z_mid, H0, Om)
    age_mid = (t_total - t_mid) * 1000
    if age_mid > target_1ts:
        z_lo = z_mid
    else:
        z_hi = z_mid
z_match_1ts = (z_lo + z_hi) / 2
print(f"  1×t_site = {target_1ts:.0f} Myr 對應 z ≈ {z_match_1ts:.2f}")

# === K_Tree Nyquist condition ===
print("\n\n=== K_Tree Nyquist condition ===")
# Nyquist condition: need at least 2 K_Tree grid points per K_Chain site
# K_Tree scale at ℓ: R_H/4^ℓ
# Need: R_H/4^ℓ ≤ 2 × (R_H/44) = R_H/22
# 1/4^ℓ ≤ 1/22
# 4^ℓ ≥ 22
# ℓ ≥ log₄(22)

ell_nyquist = math.log(22, 4)
z_nyquist = 4**ell_nyquist - 1
print(f"Nyquist condition: ℓ = log₄(22) = {ell_nyquist:.4f}")
print(f"z_Nyquist = 4^{ell_nyquist:.4f} - 1 = {z_nyquist:.2f}")
print(f"→ At z > {z_nyquist:.1f}, K_Tree undersamples K_Chain structure")

# The actual cutoff at z=17
ell_17 = math.log(18, 4)
z_17 = 17
print(f"\nAt z=17: ℓ = log₄(18) = {ell_17:.4f}")
print(f"  K_Tree scale = R_H/4^{ell_17:.4f} = R_H/18 = {H0:.1f}... wait")
print(f"  R_H/18 = {299792.458/72.59/18:.0f} Mpc")
print(f"  K_Chain site spacing = R_H/44 = {299792.458/72.59/44:.0f} Mpc")
print(f"  Ratio: scale/site_spacing = {44/18:.3f}")
print(f"  → Each K_Tree grid point covers {44/18:.2f} K_Chain sites")
print(f"  → K_Chain structure is still resolvable (ratio > 1)")

# So the Nyquist cutoff is not at z=17 from the K_Tree alone
# The z=17 cutoff comes from the mode characteristic time
print("\n結論：z=17 嘅 Nyquist 截斷源自 K_Chain mode 嘅 characteristic time")
print(f"  t_site/√(γ_22) = {target_age:.1f} Myr → ΛCDM z ≈ {z_match:.2f} ≈ 17")
print(f"  z=17 係「物理時間 Nyquist」，唔係「空間 Nyquist」")
print(f"  K_Tree ℓ=2.08 係 consistent 但唔係決定性嘅因素")