#!/usr/bin/env python3
"""
50_joint_fit_desi_pantheon.py — DESI + Pantheon+ 聯合擬合
===========================================================
P0: 鎖死低紅移邊界，修復 ζ(0) 過度壓低 H(z) 問題。

問題：DESI 最低 z=0.295，ζ(z) 喺 z<0.295 冇被約束 → ζ(0)=1.25，
Cepheid 校準殘差 -0.41 mag（隱含 H₀=87.7 vs IDCM 72.59）。

方案：DESI 7 tracers (13 點) + Pantheon+ (1701 SNe) 聯合擬合。
強制 ζ(0) ≈ 1（本地 Cepheid H₀ 約束）。

損失函數：χ²_total = χ²_DESI + χ²_Pantheon+ + H₀ 約束懲罰
"""
import math
import numpy as np
from scipy import optimize
import json

C_LIGHT = 299792.458
PHI_INV = (math.sqrt(5) - 1) / 2
H0_IDCM = 72.59
PC_TO_MPC = 1e-6

print("=" * 80)
print("  P0: DESI + Pantheon+ 聯合擬合 — 鎖死低紅移邊界")
print("=" * 80)

# ================================================================
# 1. DESI DR2 BAO 數據
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

# ================================================================
# 2. Pantheon+ 數據
# ================================================================
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
print(f"\n  Pantheon+: {N} SNe, z ∈ [{zs.min():.4f}, {zs.max():.3f}]")

# 載入 covariance (1701×1701, 第一行係維度標記)
with open(cov_path) as f:
    n_dim = int(f.readline().strip())
cov_sn_flat = np.loadtxt(cov_path, skiprows=1)
cov_sn = cov_sn_flat.reshape(n_dim, n_dim)
print(f"  Covariance: {cov_sn.shape} (from {n_dim}×{n_dim})")
cov_sn_inv = np.linalg.inv(cov_sn)

# Cepheid 校準 SNe（有絕對距離）
ceph_mask = ceph_dist > 0
n_ceph = int(np.sum(ceph_mask))
print(f"  Cepheid-calibrated: {n_ceph}")

# ================================================================
# 3. 模型
# ================================================================
def hz_idcm_base(z):
    eps = PHI_INV / 4
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_correction(z, zeta0, zs_p, zeta1, zl):
    low_z = zeta0 * math.exp(-z / zs_p)
    high_z = zeta1 * (1 - math.exp(-z / zl))
    return 1.0 + low_z - high_z

def hz_corrected(z, p):
    return hz_idcm_base(z) / zeta_correction(z, *p)

def dL_idcm(z, p, N=200):
    if z <= 0:
        return 0.0
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_corrected(zp, p)
    return (1 + z) * C_LIGHT * integral

def mu_idcm(z, p):
    dL_mpc = dL_idcm(z, p)
    return 5 * math.log10(dL_mpc) + 25  # μ = 5log10(d_L/10pc)

# DESI 預測
def desi_predictions(p):
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        if qty == 'DM':
            pred = C_LIGHT * integ_dm(z, p) / 147.44
        elif qty == 'DH':
            pred = C_LIGHT / hz_corrected(z, p) / 147.44
        elif qty == 'DV':
            dm = C_LIGHT * integ_dm(z, p) / 147.44
            dh = C_LIGHT / hz_corrected(z, p) / 147.44
            pred = (z * dm**2 * dh) ** (1/3)
        model.append(pred)
    return np.array(model)

def integ_dm(z, p, N=300):
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_corrected(zp, p)
    return integral

# ================================================================
# 4. 聯合損失函數
# ================================================================
def total_loss(params):
    # params = [zeta0, zs, zeta1, zl, M]
    p = params[:4]
    M = params[4]
    
    if any(x < 0 for x in p):
        return 1e12
    
    # 1) DESI χ²
    model_desi = desi_predictions(p)
    delta_desi = np.array(desi_val) - model_desi
    chi2_desi = delta_desi @ cov_desi_inv @ delta_desi
    
    # 2) Pantheon+ χ² (用 m_b_corr, M 自由)
    mu_model = np.array([mu_idcm(z, p) for z in zs])
    m_model = M + mu_model
    delta_sn = mb - m_model
    chi2_sn = delta_sn @ cov_sn_inv @ delta_sn
    
    # 3) Cepheid 校準約束: ζ(0) ≈ 1
    #    H(0) = H0_IDCM / ζ(0), 應該 ≈ 72.59（IDCM H₀）
    #    用 SH0ES 嘅 H₀=73.04±1.04 做約束
    zeta_0 = zeta_correction(0, *p)
    h0_model = H0_IDCM / zeta_0
    chi2_h0 = ((h0_model - 73.04) / 1.04) ** 2
    
    return chi2_desi + chi2_sn + chi2_h0

# Baseline
print(f"\n{'─'*80}")
print("  4. Baseline（v2 參數 + M 擬合）")
print(f"{'─'*80}")

# 先 fit M（固定 v2 參數）
def fit_M_only(p_fixed):
    def loss(M):
        mu_model = np.array([mu_idcm(z, p_fixed) for z in zs])
        delta = mb - (M + mu_model)
        return delta @ cov_sn_inv @ delta
    r = optimize.minimize_scalar(loss, bounds=(-30, -10), method='bounded')
    return r.x, r.fun

p_v2 = [0.2509, 2.0, 0.6537, 5.0]
M_fit, chi2_sn_base = fit_M_only(p_v2)
print(f"  v2 參數 + M={M_fit:.3f}: χ²(Pantheon+) = {chi2_sn_base:.1f}")

# DESI baseline
model_desi_base = desi_predictions(p_v2)
delta_desi_base = np.array(desi_val) - model_desi_base
chi2_desi_base = delta_desi_base @ cov_desi_inv @ delta_desi_base
print(f"  v2 參數: χ²(DESI) = {chi2_desi_base:.1f}")
print(f"  總 χ² = {chi2_desi_base + chi2_sn_base:.1f}")

# ================================================================
# 5. 聯合優化
# ================================================================
print(f"\n{'─'*80}")
print("  5. 聯合優化（5 參數: ζ₀, z_s, ζ₁, z_l, M）")
print(f"{'─'*80}")

bounds = [(0, 1.0), (0.05, 5), (0, 1.0), (0.1, 8), (-30, -10)]

best = None
best_loss = 1e12
guesses = [
    [0.2509, 2.0, 0.6537, 5.0, M_fit],
    [0.1, 0.5, 0.5, 3.0, M_fit],
    [0.05, 1.0, 0.6, 4.0, M_fit],
    [0.15, 1.5, 0.55, 3.5, M_fit],
    [0.2, 2.5, 0.7, 6.0, M_fit],
    [0.08, 0.8, 0.45, 2.5, M_fit],
]

for g in guesses:
    r = optimize.minimize(total_loss, g, method='L-BFGS-B', bounds=bounds,
                          options={'maxiter': 300})
    if r.fun < best_loss:
        best_loss = r.fun
        best = r

p_opt = best.x[:4]
M_opt = best.x[4]
print(f"\n  最佳擬合:")
print(f"    ζ₀ = {p_opt[0]:.4f}  (之前: 0.2509)")
print(f"    z_s = {p_opt[1]:.4f}  (之前: 2.0)")
print(f"    ζ₁ = {p_opt[2]:.4f}  (之前: 0.6537)")
print(f"    z_l = {p_opt[3]:.4f}  (之前: 5.0)")
print(f"    M = {M_opt:.3f}")
print(f"    總損失 = {best_loss:.1f}")

# ζ(0) 檢查
zeta0_final = zeta_correction(0, *p_opt)
h0_final = H0_IDCM / zeta0_final
print(f"\n  ζ(0) = {zeta0_final:.4f} (之前: 1.2509)")
print(f"  H₀(0) = {h0_final:.2f} km/s/Mpc (之前: 58.0)")

# ================================================================
# 6. 結果對比
# ================================================================
print(f"\n{'─'*80}")
print("  6. 結果對比")
print(f"{'─'*80}")

# DESI
model_desi_opt = desi_predictions(p_opt)
delta_desi_opt = np.array(desi_val) - model_desi_opt
chi2_desi_opt = delta_desi_opt @ cov_desi_inv @ delta_desi_opt

# Pantheon+
mu_model_opt = np.array([mu_idcm(z, p_opt) for z in zs])
delta_sn_opt = mb - (M_opt + mu_model_opt)
chi2_sn_opt = delta_sn_opt @ cov_sn_inv @ delta_sn_opt

# Cepheid
mu_ceph_pred = np.array([5 * math.log10(dL_idcm(z, p_opt)) + 25 for z in zs[ceph_mask]])
resid_ceph = mu_sh0es[ceph_mask] - mu_ceph_pred
H0_implied = H0_IDCM / zeta0_final * 10 ** (-resid_ceph.mean() / 5)

print(f"\n  {'指標':<25} {'之前 (v2)':<15} {'聯合擬合':<15}")
print(f"  {'─'*55}")
print(f"  {'χ²(DESI)':<25} {chi2_desi_base:<15.1f} {chi2_desi_opt:<15.1f}")
print(f"  {'χ²(Pantheon+)':<25} {chi2_sn_base:<15.1f} {chi2_sn_opt:<15.1f}")
print(f"  {'ζ(0)':<25} {1.2509:<15.4f} {zeta0_final:<15.4f}")
print(f"  {'H₀(0)':<25} {58.0:<15.2f} {h0_final:<15.2f}")
print(f"  {'Cepheid 殘差':<25} {-0.410:<15.3f} {resid_ceph.mean():<15.3f}")
print(f"  {'隱含 H₀':<25} {87.7:<15.1f} {H0_implied:<15.1f}")

# 逐 tracer 對比
print(f"\n  DESI 逐點:")
print(f"  {'z':<8} {'量':<6} {'v2':<10} {'聯合':<10} {'DESI':<10} {'Δ/σ_v2':<8} {'Δ/σ_joint':<8}")
for i in range(len(desi_z)):
    z = desi_z[i]; qty = desi_qty[i]
    obs = desi_val[i]; err = math.sqrt(cov_desi[i, i])
    sv2 = (obs - model_desi_base[i]) / err
    sj = (obs - model_desi_opt[i]) / err
    print(f"  {z:<8.3f} {qty:<6} {model_desi_base[i]:<10.4f} {model_desi_opt[i]:<10.4f} {obs:<10.4f} {sv2:<+8.2f} {sj:<+8.2f}")

# ζ(z) 形狀
print(f"\n  ζ(z) 形狀對比:")
print(f"  {'z':<6} {'v2 ζ':<10} {'joint ζ':<10} {'v2 H':<10} {'joint H':<10}")
for zt in [0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0]:
    z_v2 = zeta_correction(zt, 0.2509, 2.0, 0.6537, 5.0)
    z_j = zeta_correction(zt, *p_opt)
    print(f"  {zt:<6.1f} {z_v2:<10.4f} {z_j:<10.4f} {hz_idcm_base(zt)/z_v2:<10.1f} {hz_idcm_base(zt)/z_j:<10.1f}")

# ================================================================
# 7. 儲存
# ================================================================
output = {
    'params': {'zeta0': p_opt[0], 'z_s': p_opt[1], 'zeta1': p_opt[2], 'z_l': p_opt[3], 'M': M_opt},
    'zeta0': zeta0_final, 'H0_implied': H0_implied,
    'chi2': {'desi': float(chi2_desi_opt), 'pantheon': float(chi2_sn_opt),
             'total': float(best_loss)},
    'ceph_residual': float(resid_ceph.mean()),
    'before': {'zeta0': 1.2509, 'H0_at_0': 58.0, 'chi2_desi': chi2_desi_base,
               'chi2_pantheon': chi2_sn_base}
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/50_joint_fit_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 50_joint_fit_results.json")
print(f"{'='*80}")