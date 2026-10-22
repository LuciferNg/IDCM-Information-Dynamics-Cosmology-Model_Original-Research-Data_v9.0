#!/usr/bin/env python3
"""
71d_pantheon_shape_test.py — IDCM μ(z) 形狀測試（放寬 H₀）
=============================================================
如果 IDCM 嘅距離-紅移關係形狀正確，放寬 H₀（或 M）應該
可以 fit 到 Pantheon+ 數據。如果形狀本身唔 match，則
χ² 會仍然好大。

測試策略：
1. 固定 H₀=72.59，只 fit M → χ²(SN)
2. 放寬 H₀，同時 fit H₀+M → 最低 χ²(SN)
3. 比較 χ² 改善，判斷形狀問題 vs 歸一化問題
"""
import math
import numpy as np
from scipy import optimize
import json

# ═══════════════════════════════════════════════════════════════
# 1. IDCM 結構（可選 H₀ 縮放）
# ═══════════════════════════════════════════════════════════════
PHI = (1 + 5**0.5) / 2
PHI_INV = PHI - 1
PHI_3 = PHI_INV ** 3
ELL_0 = math.log(2) / math.log(4)
SIGMA = 0.5 * math.log(PHI) / math.log(4)
C = 299792.458

def ell(z): return math.log(1+z) / math.log(4)
def DM_scaled(z, H0_val):
    """DM(ℓ) with variable H₀"""
    R_H = C / H0_val
    l = ell(z); P = 1+2*PHI_INV*l; n = 44*(1-4**(-l))
    return n*(R_H/44)*P
def mu_idcm(z, H0_val):
    DL_mpc = DM_scaled(z, H0_val) * (1+z)
    if DL_mpc <= 0: return 0
    return 5 * math.log10(DL_mpc) + 25

# ═══════════════════════════════════════════════════════════════
# 2. 載入數據
# ═══════════════════════════════════════════════════════════════
data_path = '/tmp/Pantheon+SH0ES.dat'
with open(data_path) as f:
    header = f.readline().split()
col = {name: i for i, name in enumerate(header)}

zs, mbs, mbs_err = [], [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header): continue
        z = float(parts[col['zCMB']])
        mb = float(parts[col['m_b_corr']])
        mb_err = float(parts[col['m_b_corr_err_RAW']])
        if z > 0.01 and mb_err > 0:
            zs.append(z); mbs.append(mb); mbs_err.append(mb_err)

zs = np.array(zs); mbs = np.array(mbs); mbs_err = np.array(mbs_err)
N = len(zs)
print(f"  Pantheon+ 載入: {N} SNe")

# ═══════════════════════════════════════════════════════════════
# 3. 測試 1: 固定 H₀=72.59，fit M
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("  測試 1: 固定 H₀=72.59, fit M only")
print(f"{'='*60}")

H0_fixed = 72.59
mu_pred = np.array([mu_idcm(z, H0_fixed) for z in zs])
w = 1/mbs_err**2
M_fixed = np.sum(w*(mbs - mu_pred)) / np.sum(w)
chi2_fixed = np.sum(w*(mbs - M_fixed - mu_pred)**2)
print(f"  M = {M_fixed:.4f}")
print(f"  χ² = {chi2_fixed:.1f} ({N} dof)")
print(f"  χ²/dof = {chi2_fixed/(N-1):.2f}")

# ═══════════════════════════════════════════════════════════════
# 4. 測試 2: Free H₀ + M
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("  測試 2: free H₀ + M (2 params)")
print(f"{'='*60}")

def chi2_2params(params):
    H0_val, M_val = params
    mu = np.array([mu_idcm(z, H0_val) for z in zs])
    return np.sum(w*(mbs - M_val - mu)**2)

result = optimize.minimize(
    chi2_2params, [72.59, -19.3],
    method='Nelder-Mead',
    options={'maxiter': 1000, 'xatol': 1e-6, 'fatol': 1e-3}
)
H0_best, M_best = result.x
chi2_free = result.fun

print(f"  H₀ = {H0_best:.2f} km/s/Mpc")
print(f"  M  = {M_best:.4f}")
print(f"  χ² = {chi2_free:.1f} ({N-2} dof)")
print(f"  χ²/dof = {chi2_free/(N-2):.2f}")
print(f"  Δχ² vs fixed = {chi2_free - chi2_fixed:+.1f}")

# ═══════════════════════════════════════════════════════════════
# 5. 測試 3: ΛCDM 參考（H₀+Ω_m+M，3 params）
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("  測試 3: ΛCDM 參考 (H₀+Ω_m+M, 3 params)")
print(f"{'='*60}")

def mu_lcdm(z, H0_val, Om):
    """Flat ΛCDM distance modulus"""
    def E(zp): return math.sqrt(Om*(1+zp)**3 + (1-Om))
    # Simpson integration
    n = 200
    dz = z/n; integral = 0
    for i in range(n):
        zp = (i+0.5)*dz
        integral += dz/E(zp)
    DC = C/H0_val * integral
    DL = (1+z)*DC
    if DL <= 0: return 0
    return 5*math.log10(DL*1e6/10)

def chi2_lcdm(params):
    H0_val, Om_val, M_val = params
    if Om_val <= 0 or Om_val >= 1: return 1e10
    chi2 = 0
    for i in range(N):
        mu = mu_lcdm(zs[i], H0_val, Om_val)
        chi2 += ((mbs[i] - M_val - mu) / mbs_err[i])**2
    return chi2

result_lcdm = optimize.minimize(
    chi2_lcdm, [67.4, 0.315, -19.3],
    method='Nelder-Mead',
    options={'maxiter': 2000, 'xatol': 1e-6, 'fatol': 1e-3}
)
H0_lcdm, Om_lcdm, M_lcdm = result_lcdm.x
chi2_lcdm = result_lcdm.fun

print(f"  H₀ = {H0_lcdm:.2f} km/s/Mpc")
print(f"  Ω_m = {Om_lcdm:.4f}")
print(f"  M  = {M_lcdm:.4f}")
print(f"  χ² = {chi2_lcdm:.1f} ({N-3} dof)")
print(f"  χ²/dof = {chi2_lcdm/(N-3):.2f}")

# ═══════════════════════════════════════════════════════════════
# 6. 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print("  總結")
print(f"{'='*60}")
print(f"  {'Model':<30s} {'χ²':>8s} {'dof':>5s} {'χ²/dof':>8s}")
print(f"  {'─'*51}")
print(f"  {'IDCM fixed H₀ (M only)':<30s} {chi2_fixed:>8.1f} {N-1:>5d} {chi2_fixed/(N-1):>8.2f}")
print(f"  {'IDCM free H₀+M':<30s} {chi2_free:>8.1f} {N-2:>5d} {chi2_free/(N-2):>8.2f}")
print(f"  {'ΛCDM H₀+Ω_m+M':<30s} {chi2_lcdm:>8.1f} {N-3:>5d} {chi2_lcdm/(N-3):>8.2f}")
print(f"  {'Flat ΛCDM (Planck prior)':<30s} {'~2600':>8s} {'~1585':>5s} {'~1.63':>8s}")

# ═══════════════════════════════════════════════════════════════
# 7. 儲存
# ═══════════════════════════════════════════════════════════════
results = {
    'fixed_H0': {'H0': H0_fixed, 'M': M_fixed, 'chi2': chi2_fixed, 'dof': N-1},
    'free_H0': {'H0': H0_best, 'M': M_best, 'chi2': chi2_free, 'dof': N-2},
    'lcdm': {'H0': H0_lcdm, 'Om': Om_lcdm, 'M': M_lcdm, 'chi2': chi2_lcdm, 'dof': N-3}
}
with open('71d_pantheon_shape_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved: 71d_pantheon_shape_results.json")