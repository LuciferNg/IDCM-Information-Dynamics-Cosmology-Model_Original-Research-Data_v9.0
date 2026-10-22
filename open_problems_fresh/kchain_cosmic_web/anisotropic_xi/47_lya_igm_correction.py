#!/usr/bin/env python3
"""
47_lya_igm_correction.py — Lyα 森林 IGM 阻抗修正
====================================================
Lyα DH (z=2.33) 殘留 -4.2σ，IDCM H(z) = 224.5 vs DESI 要求 235.5 km/s/Mpc。

IGM 修正項：ζ_IGM(z) = 1 + ζ_lyα · τ_eff(z)
其中 τ_eff(z) = 0.0023 × (1+z)^3.3 係 Lyα 有效光學深度

總修正：ζ_total(z) = ζ_galaxy(z) · ζ_IGM(z)
"""
import math
import numpy as np
from scipy import optimize
import json
import sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import H0_IDCM, BAO_MPC, C_LIGHT, PHI_INV, hz_zeta, H_z

BAO_SCALE = BAO_MPC

print("=" * 80)
print("  Lyα IGM 阻抗修正 — 高紅移殘差處理")
print("=" * 80)

# Lyα effective optical depth: τ_eff(z) = 0.0023 × (1+z)^3.3
def tau_eff(z):
    return 0.0023 * (1 + z) ** 3.3

def zeta_igm(z, zeta_lya=0.0):
    """IGM-specific impedance correction"""
    return 1.0 + zeta_lya * tau_eff(z)

def H_z_igm(z, zeta_lya=0.0):
    """H(z) with both galaxy and IGM correction"""
    return H_z(z) / zeta_igm(z, zeta_lya)  # H = H_gal / ζ_IGM

# 測試 τ_eff(z)
print(f"\n  Lyα 有效光學深度 τ_eff(z) = 0.0023 × (1+z)^3.3")
for zt in [0, 1, 2, 2.33, 3, 4]:
    print(f"  z={zt:.1f}: τ_eff={tau_eff(zt):.4f}")

# DESI Lyα 數據
lya_z = 2.33
lya_DH_obs = 8.63154567
lya_DH_err = math.sqrt(0.0102136194)
lya_DM_obs = 38.98897396
lya_DM_err = math.sqrt(0.282685779)

# Fit ζ_lyα to match Lyα DH
def fit_zeta_lya():
    target_H = C_LIGHT / (lya_DH_obs * BAO_SCALE)
    H_gal = H_z(lya_z)
    
    # Need ζ_IGM = H_gal / target_H
    zeta_needed = H_gal / target_H
    zeta_lya = (zeta_needed - 1) / tau_eff(lya_z)
    return zeta_lya, zeta_needed

zeta_lya_opt, zeta_needed = fit_zeta_lya()
print(f"\n  需要 ζ_IGM(z=2.33) = {zeta_needed:.4f}")
print(f"  對應 ζ_lyα = {zeta_lya_opt:.4f}")

# 用優化確認
def chi2_lya(params):
    zeta_lya = params[0]
    H = H_z_igm(lya_z, zeta_lya)
    DH = C_LIGHT / H / BAO_SCALE
    DM = compute_dm(lya_z, zeta_lya)
    chi2 = ((lya_DH_obs - DH)/lya_DH_err)**2 + ((lya_DM_obs - DM)/lya_DM_err)**2
    return chi2

def compute_dm(z, zeta_lya):
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / H_z_igm(zp, zeta_lya)
    return C_LIGHT * integral / BAO_SCALE

result = optimize.minimize(chi2_lya, [zeta_lya_opt], bounds=[(0, 2)])
zeta_lya_best = result.x[0]
print(f"\n  優化 ζ_lyα = {zeta_lya_best:.4f}")
print(f"  χ²(Lyα only) = {result.fun:.1f} (2 dof)")

# 最終結果
H_final = H_z_igm(lya_z, zeta_lya_best)
DH_final = C_LIGHT / H_final / BAO_SCALE
DM_final = compute_dm(lya_z, zeta_lya_best)
print(f"\n  最終 H(z=2.33) = {H_final:.1f} km/s/Mpc")
print(f"  DH/rd = {DH_final:.4f} (DESI: {lya_DH_obs:.4f})")
print(f"  DM/rd = {DM_final:.4f} (DESI: {lya_DM_obs:.4f})")
print(f"  DH Δ/σ = {(lya_DH_obs - DH_final)/lya_DH_err:.2f}")
print(f"  DM Δ/σ = {(lya_DM_obs - DM_final)/lya_DM_err:.2f}")

# 全 tracer 重新計算
print(f"\n{'─'*80}")
print("  全 tracer 驗證（星系 + IGM 修正）")
print(f"{'─'*80}")

desi_data = [
    (0.295, 7.94167639, 'DV'), (0.510, 13.58758434, 'DM'), (0.510, 21.86294686, 'DH'),
    (0.706, 17.35069094, 'DM'), (0.706, 19.45534918, 'DH'), (0.934, 21.57563956, 'DM'),
    (0.934, 17.64149464, 'DH'), (1.321, 27.60085612, 'DM'), (1.321, 14.17602155, 'DH'),
    (1.484, 30.51190063, 'DM'), (1.484, 12.81699964, 'DH'), (2.33, 8.63154567, 'DH'),
    (2.33, 38.98897396, 'DM'),
]
cov = np.array([
    [5.79e-3,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,2.83e-2,-3.26e-2,0,0,0,0,0,0,0,0,0,0],
    [0,-3.26e-2,1.84e-1,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,3.24e-2,-2.37e-2,0,0,0,0,0,0,0,0],
    [0,0,0,-2.37e-2,1.11e-1,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,2.62e-2,-1.13e-2,0,0,0,0,0,0],
    [0,0,0,0,0,-1.13e-2,4.04e-2,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1.05e-1,-2.90e-2,0,0,0,0],
    [0,0,0,0,0,0,0,-2.90e-2,5.04e-2,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,5.83e-1,-1.95e-1,0,0],
    [0,0,0,0,0,0,0,0,0,-1.95e-1,2.68e-1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,1.02e-2,-2.31e-2],
    [0,0,0,0,0,0,0,0,0,0,0,-2.31e-2,2.83e-1],
])
cov_inv = np.linalg.inv(cov)

model = []
for z, val, qty in desi_data:
    if qty == 'DM': pred = compute_dm(z, zeta_lya_best)
    elif qty == 'DH': pred = C_LIGHT / H_z_igm(z, zeta_lya_best) / BAO_SCALE
    elif qty == 'DV':
        dm = compute_dm(z, zeta_lya_best)
        dh = C_LIGHT / H_z_igm(z, zeta_lya_best) / BAO_SCALE
        pred = (z * dm**2 * dh) ** (1/3)
    model.append(pred)

delta = np.array([d[1] for d in desi_data]) - np.array(model)
chi2 = delta @ cov_inv @ delta
print(f"\n  總 χ² = {chi2:.1f} (9 dof)")
print(f"  χ²/dof = {chi2/9:.1f}")

result = {
    'zeta_lya': zeta_lya_best,
    'tau_eff_at_2.33': tau_eff(2.33),
    'H_at_2.33': H_final,
    'DH_sigma': (lya_DH_obs - DH_final)/lya_DH_err,
    'DM_sigma': (lya_DM_obs - DM_final)/lya_DM_err,
    'chi2_total': chi2
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/47_lya_igm_results.json', 'w') as f:
    json.dump(result, f, indent=2)
print(f"\n  結果: 47_lya_igm_results.json")
print(f"{'='*80}")