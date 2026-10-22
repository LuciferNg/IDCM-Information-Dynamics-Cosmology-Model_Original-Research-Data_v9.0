#!/usr/bin/env python3
"""
50b_pantheon_only_fit.py — Pantheon+ 獨立擬合（唔混 DESI）
===========================================================
問題：聯合擬合時 DESI tight covariance 主導，犧牲 SNe。
先睇 SNe 獨立想要嘅 ζ(z) 形狀。

方法：
1. 固定 M，掃描 (ζ₀, z_s, ζ₁, z_l) 網格 → 搵 SNe 最優
2. 比較 SNe-only 同 DESI-only 嘅最優形狀
3. 睇兩者係咪有交集（一致嘅 ζ(z)）
"""
import math
import numpy as np
from scipy import optimize
from scipy.interpolate import interp1d
import json

C_LIGHT = 299792.458
PHI_INV = (math.sqrt(5) - 1) / 2
H0_IDCM = 72.59
BAO = 147.44

print("=" * 80)
print("  Pantheon+ 獨立擬合 — SNe 想要嘅 ζ(z) 形狀")
print("=" * 80)

# 載入數據
data_path = '/tmp/pantheon_extract/DataRelease-main/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat'
cov_path = '/tmp/pantheon_extract/DataRelease-main/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov'

with open(data_path) as f:
    header = f.readline().split()
col = {name: i for i, name in enumerate(header)}

zs, mb, mu_sh0es, ceph_dist = [], [], [], []
with open(data_path) as f:
    f.readline()
    for line in f:
        parts = line.split()
        if len(parts) < len(header):
            continue
        zs.append(float(parts[col['zCMB']]))
        mb.append(float(parts[col['m_b_corr']]))
        mu_sh0es.append(float(parts[col['MU_SH0ES']]))
        ceph_dist.append(float(parts[col['CEPH_DIST']]))

zs = np.array(zs); mb = np.array(mb)
mu_sh0es = np.array(mu_sh0es); ceph_dist = np.array(ceph_dist)
N = len(zs)

with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov_sn = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_sn_inv = np.linalg.inv(cov_sn)
ceph_mask = ceph_dist > 0

# 模型
def hz_idcm_base_vec(z):
    eps = PHI_INV / 4
    theta = np.tanh(z / 2)
    alpha = 1 + np.log(1 - 2 * eps * theta) / np.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_correction(z, zeta0, zs_p, zeta1, zl):
    return 1.0 + zeta0 * np.exp(-z / zs_p) - zeta1 * (1 - np.exp(-z / zl))

def compute_mu(z, p):
    n = 200
    zz = np.linspace(0, z, n)
    h = hz_idcm_base_vec((zz[1:] + zz[:-1]) / 2) / zeta_correction((zz[1:] + zz[:-1]) / 2, *p)
    dc = C_LIGHT * np.sum((zz[1:] - zz[:-1]) / h)
    dL = (1 + z) * dc
    return 5 * np.log10(dL * 1e6) - 5

# 網格插值
z_grid = np.linspace(0.001, 2.5, 300)
def make_mu_interp(p):
    mu_vals = np.array([compute_mu(zg, p) for zg in z_grid])
    return interp1d(z_grid, mu_vals, kind='cubic', bounds_error=False, fill_value='extrapolate')

# ================================================================
# 1. 固定 v2 形狀，fit M → baseline χ²
# ================================================================
p_v2 = [0.2509, 2.0, 0.6537, 5.0]
mu_interp_v2 = make_mu_interp(p_v2)
mu_v2 = mu_interp_v2(zs)

def loss_M(M):
    delta = mb - (M + mu_v2)
    return delta @ cov_sn_inv @ delta

r = optimize.minimize_scalar(loss_M, bounds=(-30, -10), method='bounded')
M_v2, chi2_v2 = r.x, r.fun
print(f"\n  v2 形狀: M={M_v2:.3f}, χ²(SN)={chi2_v2:.1f}")

# ================================================================
# 2. Pantheon-only 優化（5 參數）
# ================================================================
print(f"\n{'─'*80}")
print("  2. Pantheon-only 優化")
print(f"{'─'*80}")

def total_loss_sn(params):
    p = params[:4]; M = params[4]
    if any(x < 0 for x in p) or p[1] < 0.02 or p[3] < 0.1:
        return 1e12
    mu_interp = make_mu_interp(p)
    mu_model = mu_interp(zs)
    delta = mb - (M + mu_model)
    return delta @ cov_sn_inv @ delta

bounds = [(0, 1.5), (0.05, 8), (0, 1.5), (0.1, 10), (-30, -10)]
guesses = [
    [0.2509, 2.0, 0.6537, 5.0, M_v2],
    [0.1, 1.0, 0.5, 3.0, M_v2],
    [0.3, 3.0, 0.8, 6.0, M_v2],
    [0.05, 0.5, 0.3, 2.0, M_v2],
    [0.5, 4.0, 1.0, 8.0, M_v2],
    [0.0, 1.0, 0.0, 1.0, M_v2],
    [0.2, 2.0, 0.4, 4.0, M_v2],
]

best = None; best_loss = 1e12
for g in guesses:
    r = optimize.minimize(total_loss_sn, g, method='L-BFGS-B', bounds=bounds,
                          options={'maxiter': 200})
    if r.fun < best_loss:
        best_loss = r.fun; best = r

p_sn = best.x[:4]; M_sn = best.x[4]
print(f"\n  SNe-only 最優:")
print(f"    ζ₀={p_sn[0]:.4f} z_s={p_sn[1]:.4f} ζ₁={p_sn[2]:.4f} z_l={p_sn[3]:.4f} M={M_sn:.3f}")
print(f"    χ²(SN)={best_loss:.1f}")

# ================================================================
# 3. DESI-only 優化（4 參數）
# ================================================================
print(f"\n{'─'*80}")
print("  3. DESI-only 優化")
print(f"{'─'*80}")

desi_z = [0.295, 0.510, 0.510, 0.706, 0.706, 
          0.934, 0.934, 1.321, 1.321, 1.484, 1.484, 2.33, 2.33]
desi_qty = ['DV', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DM', 'DH', 'DH', 'DM']
desi_val = [7.94167639, 13.58758434, 21.86294686, 17.35069094, 19.45534918,
            21.57563956, 17.64149464, 27.60085612, 14.17602155, 30.51190063,
            12.81699964, 8.63154567, 38.98897396]
cov_desi = np.array([
    [5.78998687e-03, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2.83473742e-02, -3.26062007e-02, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, -3.26062007e-02, 1.83928040e-01, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 3.23752442e-02, -2.37445646e-02, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -2.37445646e-02, 1.11469198e-01, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 2.61732816e-02, -1.12938006e-02, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1.12938006e-02, 4.04183878e-02, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1.05336516e-01, -2.90308418e-02, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, -2.90308418e-02, 5.04233092e-02, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 5.83020277e-01, -1.95215562e-01, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -1.95215562e-01, 2.68336193e-01, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.02136194e-02, -2.31395216e-02],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2.31395216e-02, 2.82685779e-01],
])
cov_desi_inv = np.linalg.inv(cov_desi)

def integ_dm(z, p, N=200):
    zz = np.linspace(0, z, N)
    h = hz_idcm_base_vec((zz[1:] + zz[:-1]) / 2) / zeta_correction((zz[1:] + zz[:-1]) / 2, *p)
    return np.sum((zz[1:] - zz[:-1]) / h)

def desi_predictions(p):
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        if qty == 'DM':
            pred = C_LIGHT * integ_dm(z, p) / BAO
        elif qty == 'DH':
            pred = C_LIGHT / (hz_idcm_base_vec(z) / zeta_correction(z, *p)) / BAO
        elif qty == 'DV':
            dm = C_LIGHT * integ_dm(z, p) / BAO
            dh = C_LIGHT / (hz_idcm_base_vec(z) / zeta_correction(z, *p)) / BAO
            pred = (z * dm**2 * dh) ** (1/3)
        model.append(pred)
    return np.array(model)

def total_loss_desi(p):
    if any(x < 0 for x in p) or p[1] < 0.02:
        return 1e12
    model = desi_predictions(p)
    delta = np.array(desi_val) - model
    return delta @ cov_desi_inv @ delta

bounds_d = [(0, 1.5), (0.05, 8), (0, 1.5), (0.1, 10)]
best_d = None; best_d_loss = 1e12
for g in [[0.2509, 2.0, 0.6537, 5.0], [0.1, 1.0, 0.5, 3.0], [0.3, 3.0, 0.8, 6.0],
          [0.5, 4.0, 1.0, 8.0], [0.05, 0.5, 0.3, 2.0]]:
    r = optimize.minimize(total_loss_desi, g, method='L-BFGS-B', bounds=bounds_d,
                          options={'maxiter': 200})
    if r.fun < best_d_loss:
        best_d_loss = r.fun; best_d = r

p_desi = best_d.x
print(f"\n  DESI-only 最優:")
print(f"    ζ₀={p_desi[0]:.4f} z_s={p_desi[1]:.4f} ζ₁={p_desi[2]:.4f} z_l={p_desi[3]:.4f}")
print(f"    χ²(DESI)={best_d_loss:.1f}")

# ================================================================
# 4. 兩者交叉驗證
# ================================================================
print(f"\n{'─'*80}")
print("  4. 交叉驗證（SNe-only 形狀跑 DESI，DESI-only 形狀跑 SNe）")
print(f"{'─'*80}")

# SNe-only 形狀 → DESI χ²
chi2_desi_from_sn = total_loss_desi(p_sn)
# DESI-only 形狀 → SNe χ²（fit M）
mu_interp_d = make_mu_interp(p_desi)
mu_d = mu_interp_d(zs)
def loss_M_d(M):
    delta = mb - (M + mu_d)
    return delta @ cov_sn_inv @ delta
r = optimize.minimize_scalar(loss_M_d, bounds=(-30, -10), method='bounded')
chi2_sn_from_desi = r.fun

print(f"\n  {'形狀':<20} {'χ²(DESI)':<12} {'χ²(SN)':<12} {'總':<12}")
print(f"  {'─'*56}")
print(f"  {'v2 (0.2509,2,0.65,5)':<20} {141.3:<12.1f} {chi2_v2:<12.1f} {141.3+chi2_v2:<12.1f}")
print(f"  {'SNe-only':<20} {chi2_desi_from_sn:<12.1f} {best_loss:<12.1f} {chi2_desi_from_sn+best_loss:<12.1f}")
print(f"  {'DESI-only':<20} {best_d_loss:<12.1f} {chi2_sn_from_desi:<12.1f} {best_d_loss+chi2_sn_from_desi:<12.1f}")

# ζ(0) 同 H₀ 檢查
print(f"\n  ζ(0) 同 H₀:")
for name, p in [('v2', p_v2), ('SNe-only', p_sn), ('DESI-only', p_desi)]:
    z0 = zeta_correction(0, *p)
    print(f"    {name:<12} ζ(0)={z0:.4f}  H₀(0)={H0_IDCM/z0:.1f}")

# ζ(z) 形狀對比
print(f"\n  ζ(z) 形狀:")
print(f"  {'z':<6} {'v2':<10} {'SNe-only':<10} {'DESI-only':<10}")
for zt in [0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 2.33]:
    print(f"  {zt:<6.1f} {zeta_correction(zt, *p_v2):<10.4f} {zeta_correction(zt, *p_sn):<10.4f} {zeta_correction(zt, *p_desi):<10.4f}")

# ================================================================
# 5. 儲存
# ================================================================
output = {
    'pantheon_only': {'params': list(p_sn), 'chi2': float(best_loss), 'M': M_sn},
    'desi_only': {'params': list(p_desi), 'chi2': float(best_d_loss)},
    'v2': {'params': p_v2, 'chi2_desi': 141.3, 'chi2_sn': float(chi2_v2)},
    'cross': {
        'sn_shape_on_desi': float(chi2_desi_from_sn),
        'desi_shape_on_sn': float(chi2_sn_from_desi)
    }
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/50b_pantheon_only_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 50b_pantheon_only_results.json")
print(f"{'='*80}")