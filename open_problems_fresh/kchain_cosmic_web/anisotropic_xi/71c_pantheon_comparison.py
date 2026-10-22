#!/usr/bin/env python3
"""
71c_pantheon_comparison.py — IDCM μ(z) vs Pantheon+ SNe Ia
=============================================================
比較新結構公式 μ(z) 同 Pantheon+ 1701 顆 SNe Ia 嘅光度距離。

IDCM 預測：μ(z) = 5·log₁₀(DM(ℓ)×(1+z)×10⁵)
DM(ℓ) = (44-44/4^ℓ)×(R_H/44)×(1+2φ⁻¹×ℓ)

唯一的自由參數：M（絕對星等），與 H₀ 退化
"""
import math
import numpy as np
import json

# ═══════════════════════════════════════════════════════════════
# 1. IDCM 結構公式
# ═══════════════════════════════════════════════════════════════
PHI = (1 + 5**0.5) / 2
PHI_INV = PHI - 1
PHI_3 = PHI_INV ** 3
H0 = 72.59
C = 299792.458
R_H = C / H0
ELL_0 = math.log(2) / math.log(4)
SIGMA = 0.5 * math.log(PHI) / math.log(4)

def ell(z): return math.log(1+z) / math.log(4)
def D_app(z):
    l = ell(z); P = 1+2*PHI_INV*l; n = 44*(1-4**(-l))
    return n*(R_H/44)*P
def D_L(z): return D_app(z) * (1+z)
def mu_idcm(z):
    """μ = 5·log₁₀(DL_Mpc) + 25 (standard distance modulus formula)"""
    DL_mpc = D_L(z)
    if DL_mpc <= 0: return 0
    return 5 * math.log10(DL_mpc) + 25

# ═══════════════════════════════════════════════════════════════
# 2. 載入 Pantheon+ 數據
# ═══════════════════════════════════════════════════════════════
data_path = '/tmp/Pantheon+SH0ES.dat'
print("=" * 75)
print("  71c: Pantheon+ SNe Ia vs IDCM μ(z)")
print("=" * 75)

# Read header
with open(data_path) as f:
    header = f.readline().split()

col = {name: i for i, name in enumerate(header)}
print(f"\n  數據列: zCMB={col['zCMB']}, m_b_corr={col['m_b_corr']}, "
      f"MU_SH0ES={col['MU_SH0ES']}, CEPH_DIST={col['CEPH_DIST']}")

# Read data
zs, mbs, mbs_err = [], [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header): continue
        z = float(parts[col['zCMB']])
        mb = float(parts[col['m_b_corr']])
        mb_err = float(parts[col['m_b_corr_err_RAW']])
        if z > 0.01 and mb_err > 0:  # 排除 z<0.01 近域
            zs.append(z)
            mbs.append(mb)
            mbs_err.append(mb_err)

zs = np.array(zs); mbs = np.array(mbs); mbs_err = np.array(mbs_err)
N = len(zs)
print(f"  載入 {N} 顆 SNe（z>0.01）")
print(f"  z 範圍: {zs.min():.4f} - {zs.max():.3f}")

# ═══════════════════════════════════════════════════════════════
# 3. 擬合絕對星等 M
# ═══════════════════════════════════════════════════════════════
# μ = m_b - M → M = m_b - μ
# χ²(M) = Σ[(m_b - M - μ_idcm) / σ_mb]²
# M 最優 = Σ[(m_b - μ_idcm)/σ²] / Σ[1/σ²]
mu_pred = np.array([mu_idcm(z) for z in zs])
w = 1 / mbs_err**2
M_best = np.sum(w * (mbs - mu_pred)) / np.sum(w)
chi2 = np.sum(w * (mbs - M_best - mu_pred)**2)

print(f"\n  ─── 擬合結果 ───")
print(f"  M_best = {M_best:.4f} mag")
print(f"  χ² = {chi2:.1f} ({N} dof)")
print(f"  χ²/dof = {chi2/max(N-1,1):.2f}")
print(f"  H₀ = {H0} km/s/Mpc (fixed, IDCM structural)")

# 計算有效 H₀ 從 M 校準
# 標準關係：5·log₁₀(H₀) = M_B + 19.26 (from SH0ES calibration)
# 但呢個係 ΛCDM 關係，IDCM 唔適用
# IDCM 嘅 H₀ 已由結構鎖死

# ═══════════════════════════════════════════════════════════════
# 4. 紅移分箱分析
# ═══════════════════════════════════════════════════════════════
print(f"\n  ─── 紅移分箱 ───")
bins = [(0.01, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.8), (0.8, 1.2), (1.2, 2.0)]
for zmin, zmax in bins:
    mask = (zs >= zmin) & (zs < zmax)
    nbin = np.sum(mask)
    if nbin < 3: continue
    residuals = (mbs - M_best - mu_pred)[mask]
    resid_mean = np.mean(residuals)
    resid_std = np.std(residuals) / np.sqrt(nbin)
    chi2_bin = np.sum((residuals / mbs_err[mask])**2) if nbin > 0 else 0
    print(f"  {zmin:.2f}<z<{zmax:.2f}: n={nbin:4d}, μ_resid={resid_mean:+.4f}±{resid_std:.4f}")

# ═══════════════════════════════════════════════════════════════
# 5. 對比舊 ζ(z) 結果
# ═══════════════════════════════════════════════════════════════
print(f"\n  ─── 歷史對比 ───")
print(f"  舊 ζ(z) approach: χ²(SN) = 2139 (1701 SNe, ζ(z) 4-param fit)")
print(f"  新結構公式:       χ²(SN) = {chi2:.1f} ({N} SNe, M only)")
print(f"  改善: {chi2 - 2139:+.1f} (正數=差, 負數=好)")

# ═══════════════════════════════════════════════════════════════
# 6. 儲存
# ═══════════════════════════════════════════════════════════════
results = {
    'M_best': M_best,
    'chi2_sn': chi2,
    'n_sn': N,
    'chi2dof': chi2/max(N-1,1),
    'H0': H0
}
with open('71c_pantheon_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved: 71c_pantheon_results.json")