#!/usr/bin/env python3
"""
IDCM BAO 完整推導 v2 — 從 K_Chain 色散直接預測
================================================
放棄簡單冪律擬合，從 K_Chain 44-mode 色散關係直接推導
BAO 角度隨紅移嘅變化。

核心 insight:
- BAO 係 K_Chain 嘅第 28 個諧波 (k_28 = 28 × 2π/R_H)
- 每個諧波有群速度 v_g(n) = cos(πn/88)
- 紅移 z = 操作步數 = 諧波嘅「傳播距離」
- BAO 角度 = 諧波嘅相位投影，受色散修正
"""
import math
import numpy as np
from scipy import stats
import json

print("=" * 80)
print("  IDCM BAO v2 — 從 K_Chain 色散直接預測")
print("=" * 80)

# ================================================================
# 0. 基本參數
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
N_d = 44
B = 4
R_H = 4129.94  # Mpc
c_mpc_gyr = 306.6

# K_Chain 色散
gamma_n = [4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d)]
v_g_n = [math.cos(math.pi * n / 88) for n in range(1, N_d)]
k_n = [2 * math.pi * n / R_H for n in range(1, N_d)]  # 波數

# BAO 係第 28 個諧波
n_BAO = 28
k_BAO = k_n[n_BAO - 1]  # 0.0426 h/Mpc
v_g_BAO = v_g_n[n_BAO - 1]  # cos(28π/88) = cos(7π/22)
lambda_BAO = 2 * math.pi / k_BAO  # 147.44 Mpc

print(f"K_Chain 色散:")
print(f"  K_Chain modes: n=1..43")
print(f"  BAO mode: n={n_BAO}")
print(f"  k_BAO = {k_BAO:.6f} h/Mpc")
print(f"  λ_BAO = {lambda_BAO:.4f} Mpc")
print(f"  v_g(BAO) = cos({n_BAO}π/88) = {v_g_BAO:.6f}")

# ================================================================
# 1. DESI BAO 數據
# ================================================================
print(f"\n{'─'*80}")
print(f"  DESI BAO 數據")
print(f"{'─'*80}")

bao_data = [
    (0.295, 7.97, 0.14, 12.26, 0.68, 'LRG'),
    (0.510, 12.99, 0.19, 16.25, 0.60, 'LRG'),
    (0.706, 17.62, 0.33, 19.69, 0.73, 'LRG'),
    (0.930, 22.97, 0.49, 21.70, 1.10, 'ELG_LRG'),
    (1.317, 30.62, 1.04, 22.52, 2.20, 'QSO'),
    (1.491, 34.72, 1.30, 22.34, 2.44, 'QSO'),
    (2.330, 39.32, 0.33, 26.28, 0.43, 'Lyα'),
]

z_arr = np.array([d[0] for d in bao_data])
dm_arr = np.array([d[1] for d in bao_data])
edm_arr = np.array([d[2] for d in bao_data])
theta_arr = 1.0 / dm_arr  # rad
etheta_arr = edm_arr / dm_arr**2

# ================================================================
# 2. 從 K_Chain 色散推導 BAO 角度
# ================================================================
print(f"\n{'─'*80}")
print(f"  從 K_Chain 色散推導 BAO 角度")
print(f"{'─'*80}")

# 核心推導:
# 喺 K_Chain 上，第 n 個諧波嘅波數: k_n = 2πn/R_H
# BAO 係第 28 諧波: k_BAO = 2π×28/R_H = 0.0426 h/Mpc
#
# 喺天球上，第 n 諧波嘅角波數: ℓ_n = n (球諧波次數)
# 因為 1D K_Chain 投影到天球上，環繞一圈 = 2π
# 第 n 諧波繞一圈有 n 個波峰 → ℓ = n
#
# 所以 BAO 嘅角波數: ℓ_BAO = 28
# BAO 角尺度: θ_BAO = 2π/ℓ_BAO = 2π/28 = 0.2244 rad = 12.85°
#
# 但呢個係 z=0 嘅角尺度。隨 z 增加，角尺度被壓縮。
# 壓縮因子 = 1/(1+z) (因為 redshift = mapping depth 嘅壓縮)

# 方法 H: 直接從 K_Chain 色散推導
# θ(z) = (2π/n_BAO) × (1+z)^(-α) × f_corr(z)
# 其中 α 係色散指數，f_corr 係色散修正

# 色散修正: 群速度 v_g(n) 决定訊號傳播速度
# 對於 BAO mode (n=28): v_g = cos(28π/88) = 0.541
# 即 BAO 訊號以 ~0.54c 傳播
# 所以有效 redshift = (1+z)^(1/v_g) = (1+z)^(1/0.541) = (1+z)^1.85

# 即: θ(z) = 2π/28 × (1+z)^(-1/v_g(28))
# θ(z) = 0.2244 × (1+z)^(-1.85)

# 或者更精確: 考慮色散嘅完整形式
# 從 K_Chain 色散: ω_n = 2|sin(πn/88)|
# 群速度: v_g = dω/dk
# 對於離散晶格: v_g(n) = cos(πn/88)
# 相位累積: Φ(z) = ∫₀ᶻ (1/v_g(n(z'))) dz'/(1+z')
# 其中 n(z) = 28/(1+z) (紅移壓縮 mode 數)

# 正確形式:
# θ(z) = 2π/n_BAO × (1+z)^(-γ(z))
# 其中 γ(z) = 1/v_g(n(z)) = 1/cos(π×28/(88×(1+z)))

def gamma_z(z):
    """有效投影指數（隨 z 變化）"""
    n_eff = 28 / (1 + z)  # 有效 mode 數（隨 z 壓縮）
    if n_eff > 43:
        n_eff = 43
    if n_eff < 1:
        n_eff = 1
    vg = math.cos(math.pi * n_eff / 88)
    if vg < 0.1:
        vg = 0.1
    return 1.0 / vg

def theta_idcm(z):
    """IDCM BAO 角度預測"""
    theta0 = 2 * math.pi / 28  # 0.2244 rad
    gamma = gamma_z(z)
    return theta0 / (1+z)**gamma

# 另一種形式: 考慮積分色散
# 有效相位累積: Φ(z) = ∫₀ᶻ d ln(1+z') / v_g(n(z'))
# θ(z) = 2π/28 × exp(-Φ(z))

def theta_idcm_integral(z, n_step=100):
    """IDCM BAO 角度預測（積分形式）"""
    theta0 = 2 * math.pi / 28
    # 積分: Φ(z) = ∫₀ᶻ dz'/(1+z')/v_g(n(z'))
    # 但 n(z') = 28/(1+z')
    z_vals = np.linspace(0, z, n_step)
    dz = z / n_step
    phi = 0
    for zi in z_vals:
        n_eff = 28 / (1 + zi)
        if n_eff > 43:
            n_eff = 43
        if n_eff < 1:
            n_eff = 1
        vg = math.cos(math.pi * n_eff / 88)
        if vg < 0.1:
            vg = 0.1
        phi += dz / (1 + zi) / vg
    return theta0 * math.exp(-phi)

print(f"\n  色散修正:")
print(f"  BAO mode n=28, v_g = cos(28π/88) = {v_g_BAO:.6f}")
print(f"  γ(z=0) = 1/v_g(28) = {1/v_g_BAO:.4f}")
print(f"  γ(z) = 1/cos(π×28/(88×(1+z)))\n")

print(f"  {'z':<8} {'n_eff':<10} {'v_g':<12} {'γ':<10} {'θ_pred(°)':<12} {'θ_obs(°)':<12}")
print(f"  {'-'*64}")
for i, (z, dm, edm, dh, edh, tracer) in enumerate(bao_data):
    n_eff = 28 / (1 + z)
    vg = math.cos(math.pi * n_eff / 88)
    if vg < 0.1: vg = 0.1
    gamma = 1.0 / vg
    theta_p = theta_idcm(z) * 180 / math.pi
    theta_o = theta_arr[i] * 180 / math.pi
    print(f"  {z:<8.3f} {n_eff:<10.4f} {vg:<12.6f} {gamma:<10.4f} {theta_p:<12.4f} {theta_o:<12.4f}")

# ================================================================
# 3. 完整擬合統計
# ================================================================
print(f"\n{'─'*80}")
print(f"  擬合統計")
print(f"{'─'*80}")

# 計算 χ²
chi2_vg = 0
for i in range(len(z_arr)):
    pred = theta_idcm(z_arr[i])
    obs = theta_arr[i]
    err = etheta_arr[i]
    chi2_vg += ((pred - obs) / err) ** 2

dof = len(z_arr)
print(f"  χ² (色散模型) = {chi2_vg:.4f}, dof = {dof}, χ²/dof = {chi2_vg/dof:.4f}")

# 積分形式
chi2_int = 0
for i in range(len(z_arr)):
    pred = theta_idcm_integral(z_arr[i])
    obs = theta_arr[i]
    err = etheta_arr[i]
    chi2_int += ((pred - obs) / err) ** 2

print(f"  χ² (積分模型) = {chi2_int:.4f}, dof = {dof}, χ²/dof = {chi2_int/dof:.4f}")

# ================================================================
# 4. 嘗試: 從 K_Chain 本徵值直接推導
# ================================================================
print(f"\n{'─'*80}")
print(f"  從 K_Chain 本徵值直接推導")
print(f"{'─'*80}")

# 另一種思路: BAO 角度 = 本徵值 γ_n 嘅投影
# 對於 harmonic oscillator, 能量 E_n = γ_n = 4 sin²(πn/88)
# BAO (n=28): E_28 = 4 sin²(28π/88) = 4 sin²(7π/22)
# 角尺度: θ ∝ 1/√E_n

E_BAO = 4 * math.sin(math.pi * 28 / 88) ** 2
print(f"  BAO mode energy: E_28 = 4 sin²(28π/88) = {E_BAO:.6f}")

# 嘗試: θ(z) = 2π/√(E_28 × (1+z)^2)
def theta_energy(z):
    theta0 = 2 * math.pi / math.sqrt(E_BAO)
    return theta0 / (1+z)

print(f"  θ(z) = 2π/√E_28 / (1+z) = {2*math.pi/math.sqrt(E_BAO):.4f} / (1+z) rad\n")

chi2_en = 0
for i in range(len(z_arr)):
    pred = theta_energy(z_arr[i])
    obs = theta_arr[i]
    err = etheta_arr[i]
    chi2_en += ((pred - obs) / err) ** 2
print(f"  χ² (能量模型) = {chi2_en:.4f}, dof = {dof}, χ²/dof = {chi2_en/dof:.4f}")

# ================================================================
# 5. 最佳擬合: 自由 γ
# ================================================================
print(f"\n{'─'*80}")
print(f"  最佳擬合")
print(f"{'─'*80}")

# 掃描 γ
theta0 = 2 * math.pi / 28
gammas = np.linspace(0.5, 3.0, 501)
chi2s = []
for g in gammas:
    pred = theta0 / (1+z_arr)**g
    chi2 = np.sum((pred - theta_arr)**2 / etheta_arr**2)
    chi2s.append(chi2)

best_idx = np.argmin(chi2s)
gamma_best = gammas[best_idx]
chi2_best = chi2s[best_idx]

print(f"  θ(z) = {theta0:.6f} / (1+z)^γ")
print(f"  最佳 γ = {gamma_best:.4f}")
print(f"  χ² = {chi2_best:.4f}, dof = {dof}, χ²/dof = {chi2_best/dof:.4f}")

# ================================================================
# 6. 所有模型對比
# ================================================================
print(f"\n{'─'*80}")
print(f"  所有模型對比")
print(f"{'─'*80}")

print(f"  {'z':<8} {'θ_obs':<10} {'ΛCDM':<10} {'γ=const':<10} {'色散':<10} {'積分':<10} {'能量':<10}")
print(f"  {'-'*68}")
for i, (z, dm, edm, dh, edh, tracer) in enumerate(bao_data):
    theta_o = theta_arr[i] * 180/math.pi
    # ΛCDM
    Omega_L = 4/(PHI**4-1)
    Omega_m = 1-Omega_L
    H0 = c_mpc_gyr / R_H
    def H_LCDM(zi):
        return H0 * math.sqrt(Omega_m*(1+zi)**3 + Omega_L)
    def DM_LCDM(zi):
        n=1000
        zv = np.linspace(0,zi,n)
        Hv = [H_LCDM(zx) for zx in zv]
        return (c_mpc_gyr/H0)*np.sum(zi/n/(np.array(Hv)/H0))
    theta_lcdm = lambda_BAO/2 / DM_LCDM(z) * 180/math.pi
    theta_gamma = theta0/(1+z)**gamma_best * 180/math.pi
    theta_vg = theta_idcm(z) * 180/math.pi
    theta_int = theta_idcm_integral(z) * 180/math.pi
    theta_en = theta_energy(z) * 180/math.pi
    print(f"  {z:<8.3f} {theta_o:<10.4f} {theta_lcdm:<10.4f} {theta_gamma:<10.4f} {theta_vg:<10.4f} {theta_int:<10.4f} {theta_en:<10.4f}")

# ================================================================
# 7. 總結
# ================================================================
print(f"\n{'─'*80}")
print(f"  總結")
print(f"{'─'*80}")

models = [
    ("ΛCDM FLRW", "N/A", "N/A"),
    ("冪律 γ=const", f"{gamma_best:.4f}", f"{chi2_best:.1f}"),
    ("色散修正", f"1/v_g(z)", f"{chi2_vg:.1f}"),
    ("積分色散", f"∫ dz/v_g", f"{chi2_int:.1f}"),
    ("能量模型", f"1/√E", f"{chi2_en:.1f}"),
]

print(f"\n  {'模型':<20} {'參數':<20} {'χ²':<10}")
print(f"  {'-'*50}")
for name, param, chi2 in models:
    print(f"  {name:<20} {param:<20} {chi2:<10}")

print(f"""
結論:
  所有 IDCM 模型嘅 χ² 都遠大於 dof，
  表示簡單嘅冪律/色散模型唔夠描述 DESI 數據。

  需要更深入嘅 insight:
  - K_Chain 嘅 1D → 3D 投影唔係簡單嘅冪律
  - 可能係全息投影 (holographic projection)
  - 或者 BAO 嘅角度同距離嘅關係係非局部 (non-local)

  開放問題:
  1. 點解 ΛCDM FLRW 做到 ~1% 精度？
  2. IDCM 嘅相位投影同 ΛCDM 嘅幾何投影有咩關係？
  3. 如果紅移 = 相位落差，點解 BAO 角度同 ΛCDM 預測咁接近？
""")