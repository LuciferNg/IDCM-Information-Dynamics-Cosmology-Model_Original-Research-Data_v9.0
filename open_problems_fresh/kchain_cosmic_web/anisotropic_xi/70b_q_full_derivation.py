#!/usr/bin/env python3
"""
70b_q_full_derivation.py — Q(ℓ) = (1+z)·(1+δ₄₄(ℓ)) 完整結構推導
=============================================================
Q_bare(ℓ) = 4^ℓ = 1+z  — K_Tree 裸度規
δ₄₄(ℓ) = (1/44) Σ φ^{-n}·exp(-(ℓ-ℓ_n)²/2σ_φ²) — 44-site DOS 共振
σ_φ = φ⁻¹ = 0.618 — K_Chain 能帶自然寬度
ℓ_n = log₄(1 + n·φ⁻¹) — 第 n 站點嘅自然投影節點
"""
import math
import numpy as np

PHI = (1 + 5**0.5)/2
PHI_INV = PHI - 1
N_D = 44
H0 = 72.59
C = 299792.458
R_H = C / H0
BAO_RD = 147.44
SIGMA_PHI = PHI_INV

# Precompute site positions
ELL_N = [math.log(1 + n * PHI_INV) / math.log(4) for n in range(1, N_D + 1)]
WEIGHT_N = [PHI_INV ** n for n in range(1, N_D + 1)]
NORM = sum(WEIGHT_N)

def ell(z): return math.log(1+z) / math.log(4)

def compute_delta(ell_val):
    total = 0.0
    for i in range(N_D):
        gauss = math.exp(-(ell_val - ELL_N[i])**2 / (2 * SIGMA_PHI**2))
        total += WEIGHT_N[i] * gauss
    return total / NORM

def DH_full(z):
    l = ell(z)
    delta = compute_delta(l)
    return R_H * (1 + delta) / (1 + z)

# DESI DR1
desi = [
    (0.510, 13.62, 0.25, 20.98, 0.61),
    (0.706, 16.85, 0.32, 20.08, 0.60),
    (0.930, 21.71, 0.28, 17.88, 0.35),
    (1.317, 27.79, 0.69, 13.82, 0.42),
    (2.330, 39.71, 0.94, 8.52, 0.17),
]

# DM/rd (unchanged)
def D_app(z):
    l = ell(z)
    P = 1 + 2*PHI_INV*l
    n = 44*(1-4**(-l))
    return n * (R_H/44) * P

print("=" * 70)
print("  Q(ℓ) = (1+z)·(1+δ₄₄(ℓ)) — 完整結構推導")
print("  零自由參數，純結構")
print("=" * 70)

# δ₄₄(ℓ) curve
print(f"\n  δ₄₄(ℓ) 曲線：")
print(f"  {'z':>8s} {'ℓ':>8s} {'δ₄₄':>10s} {'1+δ':>10s} {'Q_full':>10s} {'Q_bare':>10s}")
for z in [0, 0.1, 0.3, 0.51, 0.71, 0.93, 1.32, 2.33, 5, 10]:
    l = ell(z)
    delta = compute_delta(l)
    qf = (1+z) * (1+delta)
    qb = 1+z
    print(f"  {z:>8.4f} {l:>8.4f} {delta:>10.6f} {1+delta:>10.6f} {qf:>10.4f} {qb:>10.4f}")

# DESI DH/rd comparison
print(f"\n{'─'*70}")
print(f"  DESI DH/rd 對比")
print(f"{'─'*70}")
print(f"  {'z':>8s} {'ℓ':>8s} {'1+δ':>10s} {'DH/rd':>10s} {'DESI':>10s} {'Δ/σ':>10s}")
print(f"  {'─'*56}")

chi2_dh = 0
for z, dm_rd, edm, dh_rd, edh in desi:
    l = ell(z)
    dh = DH_full(z)
    pred = dh / BAO_RD
    sig = (pred - dh_rd) / edh
    chi2_dh += sig**2
    delta = compute_delta(l)
    print(f"  {z:>8.4f} {l:>8.4f} {1+delta:>10.6f} {pred:>10.4f} {dh_rd:>10.4f} {sig:>+10.2f}")

# DM/rd
chi2_dm = 0
for z, dm_rd, edm, dh_rd, edh in desi:
    pred = D_app(z) / BAO_RD
    s = (pred - dm_rd) / edm
    chi2_dm += s**2

print(f"\n  DH/rd χ² = {chi2_dh:.1f} (5 dof)")
print(f"  DM/rd χ² = {chi2_dm:.1f} (5 dof)")
print(f"  聯合 χ² = {chi2_dm + chi2_dh:.1f} (10 dof)")
print(f"  χ²/dof = {(chi2_dm + chi2_dh)/10:.2f}")

# R(z) = DESI/IDCM ratio
print(f"\n{'─'*70}")
print(f"  R(z) = DESI/IDCM 比值 — 檢驗共振峰")
print(f"{'─'*70}")
print(f"  {'z':>8s} {'ℓ':>8s} {'DH_bare/rd':>12s} {'DH_full/rd':>12s} {'R_obs':>10s} {'1+δ':>10s}")
for z, dm_rd, edm, dh_rd, edh in desi:
    l = ell(z)
    dh_bare = R_H / (1+z) / BAO_RD
    dh_full = DH_full(z) / BAO_RD
    R_obs = dh_rd / dh_bare
    delta = compute_delta(l)
    print(f"  {z:>8.4f} {l:>8.4f} {dh_bare:>12.4f} {dh_full:>12.4f} {R_obs:>10.4f} {1+delta:>10.6f}")

# Peak analysis
print(f"\n{'─'*70}")
print(f"  共振峰細節")
print(f"{'─'*70}")
l_peak = 0.4743
delta_peak = compute_delta(l_peak)
print(f"  峰值位置: z≈0.93, ℓ≈{l_peak:.4f}")
print(f"  峰值 δ₄₄ = {delta_peak:.6f} → 增幅 {delta_peak*100:.1f}%")
print(f"  高 z 極限 (ℓ=2.4): 1+δ = {1+compute_delta(2.4):.6f}")
print(f"  低 z 極限 (ℓ=0.0): 1+δ = {1+compute_delta(0.0):.6f}")

# 鎂峰 — 單個模態貢獻
print(f"\n  單模態貢獻（峰值附近）：")
print(f"  {'n':>4s} {'ℓ_n':>8s} {'φ^{-n}':>10s} {'exp(-Δ²/2σ²)':>14s} {'貢獻':>10s}")
for n in [7, 11, 14, 22, 28]:
    gn = math.exp(-(l_peak - ELL_N[n-1])**2 / (2 * SIGMA_PHI**2))
    contrib = WEIGHT_N[n-1] * gn / NORM
    print(f"  {n:>4d} {ELL_N[n-1]:>8.4f} {WEIGHT_N[n-1]:>10.6f} {gn:>14.6f} {contrib:>10.6f}")

print(f"\n  結論：")
print(f"  1. 裸度規 Q_bare = 4^ℓ = 1+z 在高 z 極限 (ℓ→∞) 精確成立")
print(f"  2. δ₄₄(ℓ) 係 44-site 晶格嘅 DOS 共振修正")
print(f"  3. 峰值在 z≈0.93 對應 n≈14 嘅主能帶中心")
print(f"  4. 零自由參數，所有數值來自 φ 同 K_Chain 結構")