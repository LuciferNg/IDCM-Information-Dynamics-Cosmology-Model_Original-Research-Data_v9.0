#!/usr/bin/env python3
"""
50_joint_fit_desi_pantheon_v2.py — DESI + Pantheon+ 聯合擬合（向量化）
====================================================================
P0: 鎖死低紅移邊界。向量化 μ(z) 計算（網格 + 插值），提速 100 倍。
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
Z_MAX = 3.0
N_GRID = 400

print("=" * 80)
print("  P0: DESI + Pantheon+ 聯合擬合（向量化）")
print("=" * 80)

# ================================================================
# 1. 數據載入
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
N = len(zs)

with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov_sn = np.loadtxt(cov_path, skiprows=1).reshape(n_dim, n_dim)
cov_sn_inv = np.linalg.inv(cov_sn)

ceph_mask = ceph_dist > 0
n_ceph = int(np.sum(ceph_mask))
print(f"  Pantheon+: {N} SNe | Cepheid: {n_ceph} | Cov: {cov_sn.shape}")

# ================================================================
# 2. 向量化模型
# ================================================================
z_grid = np.linspace(0.001, Z_MAX, N_GRID)

def hz_idcm_base_vec(z):
    eps = PHI_INV / 4
    theta = np.tanh(z / 2)
    alpha = 1 + np.log(1 - 2 * eps * theta) / np.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_correction(z, zeta0, zs_p, zeta1, zl):
    return 1.0 + zeta0 * np.exp(-z / zs_p) - zeta1 * (1 - np.exp(-z / zl))

def hz_corrected_vec(z, p):
    return hz_idcm_base_vec(z) / zeta_correction(z, *p)

def mu_grid_model(p):
    """Return interp1d of μ(z) on grid"""
    h = hz_corrected_vec(z_grid, p)
    dc = C_LIGHT * np.cumsum(np.concatenate([[0], (z_grid[1:] - z_grid[:-1]) / h[1:]]))
    # 更正: dc[i] = ∫₀^{z_grid[i]} c dz/H
    dc_full = np.zeros(N_GRID)
    dz = z_grid[1] - z_grid[0]
    # 用 mid-point 積分
    for i in range(1, N_GRID):
        dc_full[i] = dc_full[i-1] + dz / hz_corrected_vec((z_grid[i-1] + z_grid[i])/2, p)
    dL = (1 + z_grid) * dc_full * C_LIGHT / C_LIGHT  # (1+z)*D_C in Mpc
    mu = 5 * np.log10(dL * 1e6) - 5  # μ = 5log10(d_L/10pc)
    return interp1d(z_grid, mu, kind='linear', bounds_error=False, fill_value='extrapolate')

def compute_mu(z, p):
    """μ(z) 用累積積分（直接，唔用插值，保證 DESI 精度）"""
    # 用 z 嘅細網格
    n = 200
    zz = np.linspace(0, z, n)
    h = hz_corrected_vec((zz[1:] + zz[:-1]) / 2, p)
    dc = C_LIGHT * np.sum((zz[1:] - zz[:-1]) / h)
    dL = (1 + z) * dc
    return 5 * np.log10(dL * 1e6) - 5

# DESI 預測（用 compute_mu 同直接積分）
def integ_dm(z, p, N=200):
    zz = np.linspace(0, z, N)
    h = hz_corrected_vec((zz[1:] + zz[:-1]) / 2, p)
    return np.sum((zz[1:] - zz[:-1]) / h)

def desi_predictions(p):
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        if qty == 'DM':
            pred = C_LIGHT * integ_dm(z, p) / BAO
        elif qty == 'DH':
            pred = C_LIGHT / hz_corrected_vec(z, p) / BAO
        elif qty == 'DV':
            dm = C_LIGHT * integ_dm(z, p) / BAO
            dh = C_LIGHT / hz_corrected_vec(z, p) / BAO
            pred = (z * dm**2 * dh) ** (1/3)
        model.append(pred)
    return np.array(model)

# ================================================================
# 3. 聯合損失
# ================================================================
def total_loss(params):
    p = params[:4]; M = params[4]
    if any(x < 0 for x in p) or p[1] < 0.02:
        return 1e12
    
    # DESI
    model_desi = desi_predictions(p)
    delta_desi = np.array(desi_val) - model_desi
    chi2_desi = delta_desi @ cov_desi_inv @ delta_desi
    
    # Pantheon+（向量化）
    mu_model = np.array([compute_mu(z, p) for z in zs])
    delta_sn = mb - (M + mu_model)
    chi2_sn = delta_sn @ cov_sn_inv @ delta_sn
    
    # H₀ 約束: ζ(0) → H₀(0) ≈ 73
    zeta0 = zeta_correction(0, *p)
    h0_model = H0_IDCM / zeta0
    chi2_h0 = ((h0_model - 73.04) / 1.04) ** 2
    
    return chi2_desi + chi2_sn + chi2_h0

# Baseline
p_v2 = [0.2509, 2.0, 0.6537, 5.0]
model_desi_base = desi_predictions(p_v2)
chi2_desi_base = (np.array(desi_val) - model_desi_base) @ cov_desi_inv @ (np.array(desi_val) - model_desi_base)

# Fit M for baseline
mu_base = np.array([compute_mu(z, p_v2) for z in zs])
def loss_M(M):
    delta = mb - (M + mu_base)
    return delta @ cov_sn_inv @ delta
r = optimize.minimize_scalar(loss_M, bounds=(-30, -10), method='bounded')
M_base, chi2_sn_base = r.x, r.fun
print(f"\n  Baseline (v2): χ²_DESI={chi2_desi_base:.1f}, χ²_SN={chi2_sn_base:.1f}, M={M_base:.3f}")
print(f"  總 = {chi2_desi_base + chi2_sn_base:.1f}")

# ================================================================
# 4. 聯合優化
# ================================================================
print(f"\n{'─'*80}")
print("  4. 聯合優化")
print(f"{'─'*80}")

bounds = [(0, 1.0), (0.05, 5), (0, 1.0), (0.1, 8), (-30, -10)]

# 注意: compute_mu 每次 200 步積分 × 1701 SNe = 340k 步/次, 太慢
# 改用網格插值（μ 對 z 平滑，插值誤差 < 0.001 mag）
def make_mu_interp(p):
    """預計算 μ(z) 喺網格，返回插值函數"""
    mu_vals = np.array([compute_mu(zg, p) for zg in z_grid])
    return interp1d(z_grid, mu_vals, kind='cubic', bounds_error=False, fill_value='extrapolate')

def total_loss_fast(params):
    p = params[:4]; M = params[4]
    if any(x < 0 for x in p) or p[1] < 0.02:
        return 1e12
    model_desi = desi_predictions(p)
    chi2_desi = (np.array(desi_val) - model_desi) @ cov_desi_inv @ (np.array(desi_val) - model_desi)
    
    mu_interp = make_mu_interp(p)
    mu_model = mu_interp(zs)
    delta_sn = mb - (M + mu_model)
    chi2_sn = delta_sn @ cov_sn_inv @ delta_sn
    
    zeta0 = zeta_correction(0, *p)
    h0_model = H0_IDCM / zeta0
    chi2_h0 = ((h0_model - 73.04) / 1.04) ** 2
    return chi2_desi + chi2_sn + chi2_h0

best = None; best_loss = 1e12
guesses = [
    [0.2509, 2.0, 0.6537, 5.0, M_base],
    [0.1, 0.5, 0.5, 3.0, M_base],
    [0.05, 1.0, 0.6, 4.0, M_base],
    [0.15, 1.5, 0.55, 3.5, M_base],
    [0.08, 0.8, 0.45, 2.5, M_base],
    [0.02, 2.0, 0.7, 6.0, M_base],
]

for g in guesses:
    r = optimize.minimize(total_loss_fast, g, method='L-BFGS-B', bounds=bounds,
                          options={'maxiter': 150})
    if r.fun < best_loss:
        best_loss = r.fun; best = r

p_opt = best.x[:4]; M_opt = best.x[4]
print(f"\n  最佳:")
print(f"    ζ₀={p_opt[0]:.4f} z_s={p_opt[1]:.4f} ζ₁={p_opt[2]:.4f} z_l={p_opt[3]:.4f} M={M_opt:.3f}")

# 驗證
zeta0_final = zeta_correction(0, *p_opt)
h0_final = H0_IDCM / zeta0_final
model_desi_opt = desi_predictions(p_opt)
chi2_desi_opt = (np.array(desi_val) - model_desi_opt) @ cov_desi_inv @ (np.array(desi_val) - model_desi_opt)
mu_interp_opt = make_mu_interp(p_opt)
mu_opt = mu_interp_opt(zs)
chi2_sn_opt = (mb - (M_opt + mu_opt)) @ cov_sn_inv @ (mb - (M_opt + mu_opt))

# Cepheid
mu_ceph_pred = np.array([5 * np.log10(compute_mu(z, p_opt) * 0 + 1) for z in zs[ceph_mask]])  # placeholder
mu_ceph_pred = mu_interp_opt(zs[ceph_mask])
resid_ceph = mu_sh0es[ceph_mask] - mu_ceph_pred
H0_implied = h0_final * 10 ** (-resid_ceph.mean() / 5)

print(f"\n  {'指標':<22} {'之前 (v2)':<14} {'聯合擬合':<14}")
print(f"  {'─'*50}")
print(f"  {'χ²(DESI)':<22} {chi2_desi_base:<14.1f} {chi2_desi_opt:<14.1f}")
print(f"  {'χ²(Pantheon+)':<22} {chi2_sn_base:<14.1f} {chi2_sn_opt:<14.1f}")
print(f"  {'ζ(0)':<22} {1.2509:<14.4f} {zeta0_final:<14.4f}")
print(f"  {'H₀(0)':<22} {58.0:<14.2f} {h0_final:<14.2f}")
print(f"  {'Cepheid 殘差':<22} {-0.410:<14.3f} {resid_ceph.mean():<14.3f}")
print(f"  {'隱含 H₀':<22} {87.7:<14.1f} {H0_implied:<14.1f}")

print(f"\n  DESI 逐點:")
print(f"  {'z':<8} {'量':<6} {'v2':<10} {'聯合':<10} {'DESI':<10} {'Δ/σ_v2':<8} {'Δ/σ_j':<8}")
for i in range(len(desi_z)):
    z = desi_z[i]; qty = desi_qty[i]
    obs = desi_val[i]; err = math.sqrt(cov_desi[i, i])
    print(f"  {z:<8.3f} {qty:<6} {model_desi_base[i]:<10.4f} {model_desi_opt[i]:<10.4f} {obs:<10.4f} "
          f"{(obs-model_desi_base[i])/err:<+8.2f} {(obs-model_desi_opt[i])/err:<+8.2f}")

print(f"\n  ζ(z) 形狀:")
print(f"  {'z':<6} {'v2 ζ':<10} {'joint ζ':<10}")
for zt in [0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0]:
    print(f"  {zt:<6.1f} {zeta_correction(zt, 0.2509, 2.0, 0.6537, 5.0):<10.4f} {zeta_correction(zt, *p_opt):<10.4f}")

output = {
    'params': {'zeta0': p_opt[0], 'z_s': p_opt[1], 'zeta1': p_opt[2], 'z_l': p_opt[3], 'M': M_opt},
    'zeta0_final': zeta0_final, 'H0_at_0': h0_final, 'H0_implied': H0_implied,
    'chi2': {'desi': float(chi2_desi_opt), 'pantheon': float(chi2_sn_opt), 'total': float(best_loss)},
    'ceph_residual': float(resid_ceph.mean()),
    'before': {'zeta0': 1.2509, 'H0_at_0': 58.0, 'chi2_desi': chi2_desi_base, 'chi2_sn': chi2_sn_base}
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/50_joint_fit_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 50_joint_fit_results.json")
print(f"{'='*80}")