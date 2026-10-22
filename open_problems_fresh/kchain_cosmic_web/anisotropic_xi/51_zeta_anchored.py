#!/usr/bin/env python3
"""
51_zeta_anchored.py — 落錨 ζ(0)≡1 算子 + 敏感度檢驗 + 方案A/B 對照
====================================================================
P0 最終版：

1. 誠實檢驗：SNe 對 ζ(0) 有幾敏感？（掃描 ζ(0)，睇 χ²(SN) 曲線）
2. 方案 A：ζ(z) = 1 + z·[A·e^(-z/z₁) - B·(1-e^(-z/z₂))]，ζ(0)≡1 硬編碼
3. 方案 B：Cubic Spline 節點（z=0 固定 1.0）
4. 對照：χ²(DESI), χ²(SN), 參數有冇撞邊界
"""
import math
import numpy as np
from scipy import optimize
from scipy.interpolate import interp1d, CubicSpline
import json

C_LIGHT = 299792.458
PHI_INV = (math.sqrt(5) - 1) / 2
H0_IDCM = 72.59
BAO = 147.44

print("=" * 80)
print("  ζ(0)≡1 落錨算子 — 方案 A vs B + 敏感度檢驗")
print("=" * 80)

# ================================================================
# 數據載入（DESI + Pantheon+）
# ================================================================
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
with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov_sn = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_sn_inv = np.linalg.inv(cov_sn)
ceph_mask = ceph_dist > 0
print(f"  Pantheon+: {len(zs)} SNe, Cepheid: {int(ceph_mask.sum())}")

# ================================================================
# 基礎模型
# ================================================================
def hz_idcm_base_vec(z):
    eps = PHI_INV / 4
    theta = np.tanh(z / 2)
    alpha = 1 + np.log(1 - 2 * eps * theta) / np.log(4)
    return H0_IDCM * (1 + z) ** alpha

def compute_mu(z, zeta_fn):
    n = 200
    zz = np.linspace(0, z, n)
    mid = (zz[1:] + zz[:-1]) / 2
    h = hz_idcm_base_vec(mid) / zeta_fn(mid)
    dc = C_LIGHT * np.sum((zz[1:] - zz[:-1]) / h)
    dL = (1 + z) * dc
    return 5 * np.log10(dL * 1e6) - 5

def integ_dm(z, zeta_fn, N=200):
    zz = np.linspace(0, z, N)
    mid = (zz[1:] + zz[:-1]) / 2
    h = hz_idcm_base_vec(mid) / zeta_fn(mid)
    return np.sum((zz[1:] - zz[:-1]) / h)

def desi_predictions(zeta_fn):
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        if qty == 'DM':
            pred = C_LIGHT * integ_dm(z, zeta_fn) / BAO
        elif qty == 'DH':
            pred = C_LIGHT / (hz_idcm_base_vec(z) / zeta_fn(z)) / BAO
        elif qty == 'DV':
            dm = C_LIGHT * integ_dm(z, zeta_fn) / BAO
            dh = C_LIGHT / (hz_idcm_base_vec(z) / zeta_fn(z)) / BAO
            pred = (z * dm**2 * dh) ** (1/3)
        model.append(pred)
    return np.array(model)

def chi2_desi_model(zeta_fn):
    model = desi_predictions(zeta_fn)
    delta = np.array(desi_val) - model
    return delta @ cov_desi_inv @ delta

def chi2_sn_model(zeta_fn, M):
    mu_vals = np.array([compute_mu(z, zeta_fn) for z in zs])
    delta = mb - (M + mu_vals)
    return delta @ cov_sn_inv @ delta

def fit_M_sn(zeta_fn):
    mu_vals = np.array([compute_mu(z, zeta_fn) for z in zs])
    def loss(M):
        delta = mb - (M + mu_vals)
        return delta @ cov_sn_inv @ delta
    r = optimize.minimize_scalar(loss, bounds=(-30, -10), method='bounded')
    return r.x, r.fun

# ================================================================
# 1. 敏感度檢驗：SNe 對 ζ(0) 有幾敏感？
# ================================================================
print(f"\n{'─'*80}")
print("  1. 敏感度檢驗：χ²(SN) vs ζ(0)")
print(f"{'─'*80}")

# 用 v2 形狀，但掃描 ζ₀（z=0 截距）
def zeta_scan(zeta0):
    def fn(z):
        return 1.0 + zeta0 * np.exp(-z / 2.0) - 0.6537 * (1 - np.exp(-z / 5.0))
    return fn

print(f"\n  {'ζ(0)':<10} {'H₀(0)':<10} {'χ²(SN)':<12} {'Δχ²':<8}")
print(f"  {'─'*40}")
scan_results = []
for zeta0 in [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]:
    fn = zeta_scan(zeta0)
    M, c2 = fit_M_sn(fn)
    scan_results.append((zeta0, c2))
    print(f"  {zeta0:<10.2f} {H0_IDCM/(1+zeta0):<10.1f} {c2:<12.1f} {c2 - scan_results[0][1]:<+8.1f}")

# ================================================================
# 2. 方案 A：解析落錨 ζ(z) = 1 + z·[A·e^(-z/z₁) - B·(1-e^(-z/z₂))]
# ================================================================
print(f"\n{'─'*80}")
print("  2. 方案 A：解析落錨算子")
print(f"{'─'*80}")

def make_zeta_A(params):
    A, z1, B, z2 = params
    def fn(z):
        z = np.asarray(z, dtype=float)
        return 1.0 + z * (A * np.exp(-z / z1) - B * (1 - np.exp(-z / z2)))
    return fn

def loss_A_desi(params):
    if any(p <= 0 for p in params):
        return 1e12
    return chi2_desi_model(make_zeta_A(params))

bounds_A = [(0, 5), (0.05, 10), (0, 5), (0.05, 10)]
best_A = None; best_A_loss = 1e12
for g in [[0.5, 1.0, 0.5, 2.0], [0.3, 2.0, 0.3, 3.0], [1.0, 0.5, 1.0, 1.0],
          [0.2, 3.0, 0.2, 5.0], [0.8, 0.3, 0.8, 0.5], [0.1, 5.0, 0.1, 8.0]]:
    r = optimize.minimize(loss_A_desi, g, method='L-BFGS-B', bounds=bounds_A,
                          options={'maxiter': 300})
    if r.fun < best_A_loss:
        best_A_loss = r.fun; best_A = r

pA = best_A.x
zeta_A = make_zeta_A(pA)
chi2_A_desi = best_A_loss
M_A, chi2_A_sn = fit_M_sn(zeta_A)
print(f"\n  方案 A 最優 (DESI-only):")
print(f"    A={pA[0]:.4f} z₁={pA[1]:.4f} B={pA[2]:.4f} z₂={pA[3]:.4f}")
print(f"    χ²(DESI)={chi2_A_desi:.1f} (之前 DESI-only: 102.4, v2: 141.3)")
print(f"    χ²(SN)={chi2_A_sn:.1f} (M={M_A:.3f})")
print(f"    ζ(0)={zeta_A(0):.4f} (硬編碼 ≡1)")
print(f"    收斂: {best_A.success}, 撞邊界: {any(abs(x) > 0.99*b for x, b in zip(pA, [5,10,5,10]))}")

# ================================================================
# 3. 方案 B：Cubic Spline 節點
# ================================================================
print(f"\n{'─'*80}")
print("  3. 方案 B：Cubic Spline 節點")
print(f"{'─'*80}")

# 節點: z=[0, 0.3, 0.8, 1.5, 2.3], ζ(0)=1 固定
knots = [0.0, 0.3, 0.8, 1.5, 2.3]
# 可變: ζ(0.3), ζ(0.8), ζ(1.5), ζ(2.3)
# 漸近: ζ(2.3) 之後用最後斜率外推, 或者 clamp
def make_zeta_B(vals):
    z1v, z2v, z3v, z4v = vals
    y = np.array([1.0, z1v, z2v, z3v, z4v])
    cs = CubicSpline(knots, y, bc_type='natural')
    def fn(z):
        z = np.asarray(z, dtype=float)
        # clamp at z>=2.3 to avoid runaway extrapolation
        return np.where(z <= 2.3, cs(z), z4v)
    return fn

def loss_B_desi(params):
    if any(p < 0.5 or p > 1.5 for p in params):
        return 1e12
    return chi2_desi_model(make_zeta_B(params))

bounds_B = [(0.5, 1.5)] * 4
best_B = None; best_B_loss = 1e12
for g in [[1.2, 1.1, 1.0, 0.9], [1.1, 1.05, 1.0, 0.95], [1.3, 1.2, 1.1, 1.0],
          [1.15, 1.1, 1.05, 1.0], [1.25, 1.15, 1.05, 0.95], [1.0, 1.0, 1.0, 1.0]]:
    r = optimize.minimize(loss_B_desi, g, method='L-BFGS-B', bounds=bounds_B,
                          options={'maxiter': 300})
    if r.fun < best_B_loss:
        best_B_loss = r.fun; best_B = r

pB = best_B.x
zeta_B = make_zeta_B(pB)
chi2_B_desi = best_B_loss
M_B, chi2_B_sn = fit_M_sn(zeta_B)
print(f"\n  方案 B 最優 (DESI-only):")
print(f"    ζ(0.3)={pB[0]:.4f} ζ(0.8)={pB[1]:.4f} ζ(1.5)={pB[2]:.4f} ζ(2.3)={pB[3]:.4f}")
print(f"    χ²(DESI)={chi2_B_desi:.1f}")
print(f"    χ²(SN)={chi2_B_sn:.1f} (M={M_B:.3f})")
print(f"    ζ(0)={zeta_B(0):.4f} (固定 ≡1)")
print(f"    收斂: {best_B.success}")

# ================================================================
# 4. 對照表
# ================================================================
print(f"\n{'─'*80}")
print("  4. 對照表")
print(f"{'─'*80}")

print(f"\n  {'模型':<22} {'χ²(DESI)':<10} {'χ²(SN)':<10} {'總':<10} {'ζ(0)':<8}")
print(f"  {'─'*60}")
models = [
    ('v2 (0.25,2,0.65,5)', 141.3, 2663.1, 1.2509),
    ('DESI-only (舊形式)', 102.4, 2629.4, 1.2335),
    ('SNe-only (ζ≡1)', 2055.2, 2526.6, 1.0000),
    ('方案A 落錨', chi2_A_desi, chi2_A_sn, zeta_A(0)),
    ('方案B Spline', chi2_B_desi, chi2_B_sn, zeta_B(0)),
]
for name, cd, csn, z0 in models:
    print(f"  {name:<22} {cd:<10.1f} {csn:<10.1f} {cd+csn:<10.1f} {z0:<8.4f}")

# ζ(z) 形狀
print(f"\n  ζ(z) 形狀對比:")
print(f"  {'z':<6} {'方案A':<10} {'方案B':<10} {'v2':<10}")
for zt in [0, 0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 2.3]:
    print(f"  {zt:<6.2f} {zeta_A(zt):<10.4f} {zeta_B(zt):<10.4f} "
          f"{1+0.2509*np.exp(-zt/2)-0.6537*(1-np.exp(-zt/5)):<10.4f}")

# 儲存
output = {
    'sensitivity': {'zeta0_scan': [[float(a), float(b)] for a, b in scan_results]},
    'plan_A': {'params': [float(x) for x in pA], 'chi2_desi': float(chi2_A_desi), 'chi2_sn': float(chi2_A_sn), 'M': float(M_A)},
    'plan_B': {'params': [float(x) for x in pB], 'chi2_desi': float(chi2_B_desi), 'chi2_sn': float(chi2_B_sn), 'M': float(M_B)},
    'comparison': [[str(m[0]), float(m[1]), float(m[2]), float(m[3])] for m in models]
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/51_zeta_anchored_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 51_zeta_anchored_results.json")
print(f"{'='*80}")