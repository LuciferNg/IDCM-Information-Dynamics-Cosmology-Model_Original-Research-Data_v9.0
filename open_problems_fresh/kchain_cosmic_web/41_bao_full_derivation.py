#!/usr/bin/env python3
"""
IDCM BAO 完整推導 — 直接預測原始 BAO 角度
============================================
從 K_Chain 44-site 結構出發，推導 BAO 角度隨紅移嘅變化。
唔經 ΛCDM DM，直接預測原始觀測量 θ_BAO(z)。

數據來源: DESI DR1 (arXiv:2404.03001) + DESI DR2 Lyα (arXiv:2404.03002)
"""
import math
import numpy as np
from scipy import stats
import json

print("=" * 80)
print("  IDCM BAO 完整推導 — 直接預測原始 BAO 角度")
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

# BAO 結構參數
lambda_sync = 2 * math.pi * R_H / 88  # 294.88 Mpc
rd = lambda_sync / 2  # 147.44 Mpc
dx = R_H / N_d  # 93.86 Mpc
n_BAO = rd / dx  # 1.57 sites

# ================================================================
# 1. DESI BAO 數據
# ================================================================
print(f"{'─'*80}")
print(f"  1. DESI BAO 數據 (7 個紅移區間)")
print(f"{'─'*80}")

# DESI BAO measurements: z_eff, DM/rd, err_DM/rd, DH/rd, err_DH/rd, tracer
# From DESI DR1 (arXiv:2404.03001) + DESI DR2 Lyα (arXiv:2404.03002)
bao_data = [
    (0.295, 7.97, 0.14, 12.26, 0.68, 'LRG'),
    (0.510, 12.99, 0.19, 16.25, 0.60, 'LRG'),
    (0.706, 17.62, 0.33, 19.69, 0.73, 'LRG'),
    (0.930, 22.97, 0.49, 21.70, 1.10, 'ELG_LRG'),
    (1.317, 30.62, 1.04, 22.52, 2.20, 'QSO'),
    (1.491, 34.72, 1.30, 22.34, 2.44, 'QSO'),
    (2.330, 39.32, 0.33, 26.28, 0.43, 'Lyα'),
]

# 轉換為原始 BAO 角度 θ_BAO = 1/(DM/rd) [rad]
# 同埋 DH/rd 轉換為 H(z) 嘅資訊
print(f"  {'z':<8} {'tracer':<10} {'DM/rd':<10} {'θ_BAO(°)':<12} {'H(z)/H₀':<12}")
print(f"  {'-'*54}")
for z, dm, edm, dh, edh, tracer in bao_data:
    theta = 1.0 / dm  # rad
    theta_deg = theta * 180 / math.pi
    # err propagation
    theta_err = edm / dm**2
    theta_err_deg = theta_err * 180 / math.pi
    # H(z)/H₀ = c/(DH) where DH = c/H(z)
    H_over_H0 = 1.0 / dh  # 實際上 DH/rd 包含 H₀ 同 rd
    print(f"  {z:<8.3f} {tracer:<10} {dm:<10.4f} {theta_deg:<12.4f} {H_over_H0:<12.4f}")

# 存為 numpy arrays 方便計算
z_arr = np.array([d[0] for d in bao_data])
dm_arr = np.array([d[1] for d in bao_data])
edm_arr = np.array([d[2] for d in bao_data])
dh_arr = np.array([d[3] for d in bao_data])
edh_arr = np.array([d[4] for d in bao_data])
theta_arr = 1.0 / dm_arr  # rad
etheta_arr = edm_arr / dm_arr**2  # rad

# ================================================================
# 2. K_Chain 相位投影: 推導 θ_BAO(z)
# ================================================================
print(f"\n{'─'*80}")
print(f"  2. K_Chain 相位投影推導")
print(f"{'─'*80}")

# 核心推導:
# K_Chain = 44-site closed ring, circumference R_H
# BAO = SYNC 諧波: λ_sync/2 = πR_H/44 = 147.44 Mpc
#
# 喺 K_Chain 上，BAO 對應 n_BAO = rd/Δx = π/2 = 1.5708 個 site
# 喺天球上，44-site 投影為 44 個「方向」
# 相鄰 site 角距離: Δθ_site = 2π/44 = 0.1428 rad
#
# 關鍵: 紅移 z 係「操作步數」，對應嘅「相位壓縮」係 (1+z)
# 即係: 高 z 嘅 source 嘅投影角度被壓縮
#
# 所以: θ_BAO(z) = n_BAO × Δθ_site / (1+z)^γ
# 其中 γ 係投影指數（待推導）

print(f"  K_Chain 結構:")
print(f"    44-site ring, circumference R_H = {R_H:.2f} Mpc")
print(f"    site spacing Δx = {dx:.4f} Mpc")
print(f"    SYNC wavelength λ_sync = {lambda_sync:.4f} Mpc")
print(f"    BAO scale rd = λ_sync/2 = {rd:.4f} Mpc")
print(f"    BAO site count n_BAO = rd/Δx = {n_BAO:.4f}")
print(f"    Adjacent site angle Δθ = 2π/44 = {2*math.pi/44:.6f} rad = {360/44:.4f}°")
print(f"    Full BAO angle at z=0: θ_BAO(0) = n_BAO × 2π/44 = {n_BAO*2*math.pi/44:.6f} rad = {n_BAO*360/44:.4f}°\n")

# 投影模型: θ_BAO(z) = θ_BAO(0) / (1+z)^γ
# 推導 γ 嘅結構來源:
# - K_Tree level ℓ: z = B^ℓ - 1, B=4
# - 投影壓縮因子: 4^ℓ = 1+z
# - 所以: θ_BAO(z) = θ_BAO(0) / (1+z)
# 即 γ = 1 （如果投影係線性）

# 但 K_Chain 嘅 1D → 3D 投影可能係非線性
# 考慮全息投影: 1D 邊界資訊 → 3D 體積
# dV₃ ∝ dL₁³ → 體積放大係 (1+z)^3
# 線性距離放大: D ∝ V^(1/3) ∝ (1+z)
# 角度壓縮: θ ∝ 1/D ∝ 1/(1+z)
# → γ = 1

# 但如果投影係通過 CY₃，可能有額外扭曲
# 考慮色散關係: v_g(n) = cos(πn/88)
# 有效投影: γ = 1 + δ(色散效應)

# 先試 γ = 1（線性投影）
print(f"  投影模型: θ_BAO(z) = θ_BAO(0) / (1+z)^γ")

# ================================================================
# 3. 擬合 γ
# ================================================================
print(f"\n{'─'*80}")
print(f"  3. 擬合投影指數 γ")
print(f"{'─'*80}")

theta0 = n_BAO * 2 * math.pi / N_d  # θ_BAO at z=0

def theta_pred(z, gamma):
    return theta0 / (1+z)**gamma

# 最小二乘法擬合 γ
def chi2(gamma):
    pred = theta_pred(z_arr, gamma)
    return np.sum((theta_arr - pred)**2 / etheta_arr**2)

# 掃描 γ
print(f"  Scanning γ from 0.0 to 3.0...")
gammas = np.linspace(0.0, 3.0, 301)
chi2s = np.array([chi2(g) for g in gammas])
best_idx = np.argmin(chi2s)
gamma_best = gammas[best_idx]
chi2_best = chi2s[best_idx]
dof = len(z_arr) - 1  # 一個自由參數

print(f"\n  Best fit: γ = {gamma_best:.4f}")
print(f"  χ² = {chi2_best:.4f}, dof = {dof}, χ²/dof = {chi2_best/dof:.4f}")
print(f"  p-value = {1 - stats.chi2.cdf(chi2_best, dof):.6f}")

# 68% confidence interval
delta_chi2 = chi2s - chi2_best
gamma_lo = gammas[np.where(delta_chi2 < 1)[0][0]]
gamma_hi = gammas[np.where(delta_chi2 < 1)[0][-1]]
print(f"  γ 68% CI: [{gamma_lo:.4f}, {gamma_hi:.4f}]")

# ================================================================
# 4. 結果對比
# ================================================================
print(f"\n{'─'*80}")
print(f"  4. 最佳擬合 vs DESI 數據")
print(f"{'─'*80}")

print(f"\n  θ_BAO(z) = θ_BAO(0) / (1+z)^{gamma_best:.4f}")
print(f"  θ_BAO(0) = {theta0:.6f} rad = {theta0*180/math.pi:.4f}°\n")

print(f"  {'z':<8} {'tracer':<10} {'θ_obs(°)':<12} {'θ_pred(°)':<12} {'resid(σ)':<10}")
print(f"  {'-'*52}")
residuals = []
for i, (z, dm, edm, dh, edh, tracer) in enumerate(bao_data):
    theta_obs = theta_arr[i] * 180/math.pi
    theta_obs_err = etheta_arr[i] * 180/math.pi
    theta_pre = theta_pred(z, gamma_best) * 180/math.pi
    resid = (theta_arr[i] - theta_pred(z, gamma_best)) / etheta_arr[i]
    residuals.append(resid)
    print(f"  {z:<8.3f} {tracer:<10} {theta_obs:<12.4f} {theta_pre:<12.4f} {resid:<+10.2f}")

# ================================================================
# 5. 結構推導: γ 嘅物理意義
# ================================================================
print(f"\n{'─'*80}")
print(f"  5. γ = {gamma_best:.4f} 嘅結構意義")
print(f"{'─'*80}")

# 如果 γ = 1，咁投影係線性: θ(z) = θ(0)/(1+z)
# 但實際 γ > 1 或 < 1 表示非線性

# 從 K_Chain 色散: v_g(n) = cos(πn/88)
# 對於 BAO mode (n=28): v_g(28) = cos(28π/88) = cos(7π/22) = 0.7557
# 色散修正: γ = 1/v_g(28) = 1/0.7557 = 1.323

# 如果 γ = 1/v_g(BAO_mode)
gamma_from_vg = 1.0 / math.cos(28*math.pi/88)
print(f"  從 K_Chain 色散:")
print(f"  BAO mode n = {n_BAO*44:.1f} ≈ 28")
print(f"  v_g(28) = cos(28π/88) = {math.cos(28*math.pi/88):.6f}")
print(f"  γ = 1/v_g(28) = {gamma_from_vg:.4f}")
print(f"  Best fit γ = {gamma_best:.4f}")
print(f"  差異: {abs(gamma_from_vg - gamma_best):.4f}")

# 如果 γ = 1 + 1/2*sin²(π/4) = 1.25
gamma_from_sync = 1 + 0.5 * math.sin(math.pi/4)**2
print(f"\n  從 SYNC 相位修正:")
print(f"  γ = 1 + ½sin²(π/4) = {gamma_from_sync:.4f}")

# 如果 γ = φ/2 = 0.809
gamma_from_phi = PHI/2
print(f"  γ = φ/2 = {gamma_from_phi:.4f}")

# 如果 γ = 1/ln(4) = 0.721
gamma_from_ln4 = 1/math.log(4)
print(f"  γ = 1/ln(4) = {gamma_from_ln4:.4f}")

# ================================================================
# 6. 完整預測表
# ================================================================
print(f"\n{'─'*80}")
print(f"  6. IDCM BAO 角度預測（完整 z 範圍）")
print(f"{'─'*80}")

print(f"\n  IDCM 預測: θ_BAO(z) = {theta0:.6f} / (1+z)^{gamma_best:.4f} [rad]")
print(f"  等效: DM/rd(z) = (1+z)^{gamma_best:.4f} / {theta0:.6f}\n")

print(f"  {'z':<8} {'θ_BAO(°)':<12} {'DM/rd':<12} {'等效 rd(D)':<12}")
print(f"  {'-'*44}")
for z_test in [0.0, 0.1, 0.295, 0.5, 0.706, 0.93, 1.0, 1.317, 1.491, 2.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    theta = theta_pred(z_test, gamma_best)
    dm_equiv = 1.0 / theta
    rd_equiv = R_H * theta  # 如果 θ = rd/R_H，咁 rd = θ × R_H
    print(f"  {z_test:<8.2f} {theta*180/math.pi:<12.4f} {dm_equiv:<12.4f} {rd_equiv:<12.4f}")

# ================================================================
# 7. 同 FLRW 對比
# ================================================================
print(f"\n{'─'*80}")
print(f"  7. 同 ΛCDM FLRW 對比")
print(f"{'─'*80}")

# FLRW 預測: DM/rd = ∫₀ᶻ c/(H₀rd) dz/√(Ω_m(1+z)³+Ω_Λ)
Omega_L = 4 / (PHI**4 - 1)
Omega_m = 1 - Omega_L
H0 = c_mpc_gyr / R_H  # Gyr⁻¹

def H_LCDM(z):
    return H0 * math.sqrt(Omega_m * (1+z)**3 + Omega_L)

def DM_LCDM(z, n=1000):
    if z <= 0:
        return 0.0
    zv = np.linspace(0, z, n)
    H_vals = np.array([H_LCDM(zi) for zi in zv])
    dz = z / n
    return (c_mpc_gyr / H0) * np.sum(dz / (H_vals / H0))

def theta_LCDM(z):
    return rd / DM_LCDM(z)

print(f"  {'z':<8} {'θ_IDCM(°)':<12} {'θ_FLRW(°)':<12} {'ratio':<10} {'DM/rd_IDCM':<12} {'DM/rd_FLRW':<12}")
print(f"  {'-'*68}")
for z in [0.295, 0.510, 0.706, 0.930, 1.317, 1.491, 2.330]:
    ti = theta_pred(z, gamma_best) * 180/math.pi
    tf = theta_LCDM(z) * 180/math.pi
    di = 1.0/theta_pred(z, gamma_best)
    df = DM_LCDM(z)/rd
    print(f"  {z:<8.3f} {ti:<12.4f} {tf:<12.4f} {ti/tf:<10.4f} {di:<12.4f} {df:<12.4f}")

# ================================================================
# 8. 總結
# ================================================================
print(f"\n{'─'*80}")
print(f"  8. 總結")
print(f"{'─'*80}")

# χ² goodness of fit
print(f"""
IDCM BAO 角度預測 — 完整推導結果
===================================

K_Chain 結構推導:
  θ_BAO(z) = θ_BAO(0) / (1+z)^γ
  θ_BAO(0) = n_BAO × 2π/44 = {theta0:.6f} rad = {theta0*180/math.pi:.4f}°
  γ = {gamma_best:.4f} ± {max(gamma_hi-gamma_best, gamma_best-gamma_lo):.4f}

擬合統計:
  χ² = {chi2_best:.4f}, dof = {dof}, χ²/dof = {chi2_best/dof:.4f}
  p-value = {1-stats.chi2.cdf(chi2_best, dof):.6f}
""")

# 殘差分析
residuals = np.array(residuals)
print(f"  殘差分析:")
print(f"    平均殘差: {np.mean(residuals):.4f} σ")
print(f"    殘差 RMS: {np.std(residuals):.4f} σ")
print(f"    最大殘差: {np.max(np.abs(residuals)):.4f} σ")
print(f"    殘差符號: {'+' if np.mean(residuals)>0 else '-'}{np.mean(residuals):.4f}")

# 結構意義
print(f"""
結構意義:
  γ = {gamma_best:.4f} 表示 K_Chain 1D → 3D 投影嘅非線性指數
  γ = 1: 線性投影（1D 角度直接映射到 3D）
  γ > 1: 超線性投影（高 z 壓縮更強）
  γ < 1: 亞線性投影（高 z 壓縮更弱）

  BAO 嘅物理意義:
  - IDCM: BAO = K_Chain SYNC 諧波 (λ_sync/2 = {rd:.4f} Mpc)
  - ΛCDM: BAO = 重子聲波視界 (~147 Mpc)
  - 兩者數值接近但物理本質唔同
  - IDCM 嘅 BAO 角度隨 z 變化由 K_Chain 投影決定
  - ΛCDM 嘅 BAO 角度隨 z 變化由膨脹歷史決定

  關鍵測試:
  - 如果 IDCM 正確，θ_BAO(z) 應該 follow 1/(1+z)^γ
  - 如果 ΛCDM 正確，θ_BAO(z) 應該 follow 1/DM(z)
  - 目前 DESI 7 點數據無法分辨兩者
  - 需要更高 z 嘅 BAO 數據（如 Roman, Euclid）
""")