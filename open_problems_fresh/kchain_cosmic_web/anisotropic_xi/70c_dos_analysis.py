#!/usr/bin/env python3
"""70c_dos_analysis.py — delta_44(ell) normalisation analysis"""
import math

PHI = (1 + 5**0.5)/2
PHI_INV = PHI - 1
N_D = 44
H0 = 72.59
C = 299792.458
R_H = C / H0
BAO_RD = 147.44

ELL_N = [math.log(1 + n * PHI_INV) / math.log(4) for n in range(1, N_D + 1)]
WEIGHT_N = [PHI_INV ** n for n in range(1, N_D + 1)]
SUM_W = sum(WEIGHT_N)

def ell(z): return math.log(1+z) / math.log(4)
desi = [(0.510, 20.98, 0.61), (0.706, 20.08, 0.60), (0.930, 17.88, 0.35),
        (1.317, 13.82, 0.42), (2.330, 8.52, 0.17)]

def delta_44(ell_val, sigma, norm):
    total = 0.0
    for i in range(N_D):
        g = math.exp(-(ell_val - ELL_N[i])**2 / (2 * sigma**2))
        total += WEIGHT_N[i] * g
    if norm == 'sum_w': return total / SUM_W
    elif norm == '1_44': return total / 44
    else: return total

def DH_full(z, sigma, norm):
    l = ell(z)
    d = delta_44(l, sigma, norm)
    return R_H * (1 + d) / (1 + z)

print("="*70)
print("  delta_44(ell) normalisation analysis")
print("="*70)
print("")
print("  phi^(-n) weight sum = %.6f" % SUM_W)
print("  ell range: %.4f -> %.4f" % (ELL_N[0], ELL_N[-1]))
print("  mean spacing: %.4f" % ((ELL_N[-1]-ELL_N[0])/43))

# Compare normalisations
for norm_name, norm_mode in [('sum_w norm', 'sum_w'), 
                              ('1/44 fixed', '1_44'),
                              ('no norm', 'none')]:
    print("")
    print("  --- %s ---" % norm_name)
    for sigma_name, sigma in [('sigma=phi^-1=0.618', PHI_INV),
                              ('sigma=eps=0.1545', PHI_INV/4),
                              ('sigma=0.05', 0.05),
                              ('sigma=0.1', 0.1)]:
        print("")
        print("  %s:" % sigma_name)
        print("  %8s %8s %10s %10s %10s %10s" % ('z','ell','1+delta','DH/rd','DESI','Delta/sig'))
        chi2 = 0
        for z, dh_rd, edh in desi:
            l = ell(z)
            dh = DH_full(z, sigma, norm_mode)
            pred = dh / BAO_RD
            sig = (pred - dh_rd) / edh
            chi2 += sig**2
            d = delta_44(l, sigma, norm_mode)
            print("  %8.4f %8.4f %10.6f %10.4f %10.4f %+10.2f" % (z, l, 1+d, pred, dh_rd, sig))
        print("  chi2 = %.1f" % chi2)

# Best sigma scan (sum_w norm)
print("")
print("  --- best sigma scan (sum_w norm) ---")
print("  %10s %10s" % ('sigma','chi2'))
for sigma in [0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.5, 0.618]:
    chi2 = 0
    for z, dh_rd, edh in desi:
        dh = DH_full(z, sigma, 'sum_w')
        pred = dh / BAO_RD
        sig = (pred - dh_rd) / edh
        chi2 += sig**2
    print("  %10.4f %10.1f" % (sigma, chi2))

chi2_bare = 0
for z, dh_rd, edh in desi:
    dh_bare = R_H / (1+z)
    pred = dh_bare / BAO_RD
    sig = (pred - dh_rd) / edh
    chi2_bare += sig**2
print("  %10s %10.1f" % ('bare', chi2_bare))