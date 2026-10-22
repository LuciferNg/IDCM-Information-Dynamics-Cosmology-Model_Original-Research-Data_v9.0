#!/usr/bin/env python3
"""
70_hz_rederivation.py — H(z) 完整結構推導
========================================
Q(ell) = (1+z) * [1 + phi^-3 * exp(-(ell-ell_0)^2 / (2*sigma_phi^2))]
ell_0 = log_4(2) = 0.5, sigma_phi = 0.5*log_4(phi), phi^-3 = 0.236068

DM(ell) = (44-44/4^ell) x (R_H/44) x (1 + 2*phi^-1*ell)
DH(z) = R_H x (1 + delta_k0(ell)) / (1+z)

Zero free parameters. All from phi algebra.
"""
import math, json

PHI = (1 + 5**0.5)/2
PHI_INV = PHI - 1
PHI_INV_3 = PHI_INV ** 3
H0 = 72.59
C = 299792.458
R_H = C / H0
BAO_RD = 147.44
ELL_0 = math.log(2) / math.log(4)       # 0.5
SIGMA = 0.5 * math.log(PHI) / math.log(4)  # 0.17356

def ell(z): return math.log(1+z) / math.log(4)

def delta_k0(ell_val):
    d = ell_val - ELL_0
    return PHI_INV_3 * math.exp(-d**2 / (2 * SIGMA**2))

def D_app(z):
    l = ell(z); P = 1 + 2*PHI_INV*l; n = 44*(1-4**(-l))
    return n * (R_H/44) * P

def DH_full(z):
    return R_H * (1 + delta_k0(ell(z))) / (1+z)

def H_eff(z):
    return C / DH_full(z)

# DESI DR1
desi = [(0.510, 13.62, 0.25, 20.98, 0.61),
        (0.706, 16.85, 0.32, 20.08, 0.60),
        (0.930, 21.71, 0.28, 17.88, 0.35),
        (1.317, 27.79, 0.69, 13.82, 0.42),
        (2.330, 39.71, 0.94, 8.52, 0.17)]

if __name__ == '__main__':
    print("="*70)
    print("  IDCM Cosmology — Complete Structural Formula")
    print("  Zero free parameters")
    print("="*70)
    print(f"  H0 = {H0}, R_H = {R_H:.2f} Mpc, rd = {BAO_RD} Mpc")
    print(f"  ell_0 = {ELL_0:.6f}, sigma = {SIGMA:.6f}, phi^-3 = {PHI_INV_3:.6f}")
    
    chi2_dm, chi2_dh = 0, 0
    print(f"\n  {'z':>8s} {'DM/rd':>10s} {'DESI_DM':>10s} {'DH/rd':>10s} {'DESI_DH':>10s}")
    for z, dm_rd, edm, dh_rd, edh in desi:
        dm = D_app(z)/BAO_RD; dh = DH_full(z)/BAO_RD
        chi2_dm += ((dm-dm_rd)/edm)**2; chi2_dh += ((dh-dh_rd)/edh)**2
        print(f"  {z:>8.4f} {dm:>10.4f} {dm_rd:>10.4f} {dh:>10.4f} {dh_rd:>10.4f}")
    
    print(f"\n  DM/rd chi2 = {chi2_dm:.1f} (5 dof)")
    print(f"  DH/rd chi2 = {chi2_dh:.1f} (5 dof)")
    print(f"  Joint chi2 = {chi2_dm+chi2_dh:.1f} (10 dof)")
    print(f"  chi2/dof = {(chi2_dm+chi2_dh)/10:.2f}")
    
    # Save
    result = {'dm_chi2': chi2_dm, 'dh_chi2': chi2_dh, 'joint_chi2': chi2_dm+chi2_dh,
              'dof': 10, 'H0': H0, 'ell_0': ELL_0, 'sigma': SIGMA, 'phi_3': PHI_INV_3}
    with open('70_hz_results.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n  結果: 70_hz_results.json")