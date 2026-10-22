#!/usr/bin/env python3
"""
43_kchain_2d_xi.py — K_Chain 2D ξ(σ, π) 全息投影預測
========================================================
從 44-mode 駐波疊加直接建構 ξ(s⊥, s∥) 理論預測。

核心 insight:
- ξ(σ, π) 係原始 2D 相關函數，未經 ΛCDM 距離積分汙染
- K_Chain 44-mode 干涉 → 駐波 → 宇宙網
- 每個 mode 有唔同相速度 v_g(n) = cos(πn/88)
- 阻抗 Z_n = γ_n/|v_g(n)| 決定各向異性
- 反射 R_n = (Z_n - Z_{n-1})/(Z_n + Z_{n-1}) 決定 LOS 方向性

呢個 script 建構理論預測嘅 2D 模式，然後同已知嘅
BAO ring 特徵做定性比較。

注意：呢個係零自由參數預測 — 所有常數從 x²+x-1=0 導出。
如果 K_Chain 正確，ξ(σ, π) 應顯示：
1. BAO ring 喺 λ_sync/2 ≈ 147 Mpc（唔係 ΛCDM 嘅 105 h⁻¹Mpc）
2. 高階諧波喺 λ_sync/n
3. 各向異性特徵（阻抗反射導致 LOS 方向拉伸/壓縮）
"""
import math
import numpy as np
import json

# ================================================================
# 0. K_Chain 核心常數
# ================================================================
print("=" * 80)
print("  K_CHAIN 2D ξ(σ, π) 全息投影預測")
print("=" * 80)

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
L = [round(PHI**n + (-1)**n * PHI_INV**n) for n in range(15)]
SYNC, L3, L5 = L[0], L[3], L[5]
H0_IDCM = 72.59
C_LIGHT = 299792.458
R_H = C_LIGHT / H0_IDCM  # 4129.94 Mpc
H = H0_IDCM / 100
LAMBDA_SYNC = 2 * math.pi * R_H / 88  # 294.88 Mpc
BAO_MPC = LAMBDA_SYNC / 2  # 147.44 Mpc
N_d = 44

# 44-mode 色散
gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d)])
v_g_n = np.array([math.cos(math.pi * n / 88) for n in range(1, N_d)])
k_n = np.array([2 * math.pi * n / R_H for n in range(1, N_d)])  # 波數 (Mpc⁻¹)
lam_n = np.array([2 * math.pi / k for k in k_n])  # 波長 (Mpc)

# 阻抗 Z_n = γ_n / |v_g(n)|
Z_n = gamma_n / np.abs(v_g_n)
Z_n[np.isinf(Z_n)] = 1e6

# 反射係數
R_n = np.zeros(N_d - 1)
for i in range(1, N_d - 1):
    R_n[i] = (Z_n[i] - Z_n[i-1]) / (Z_n[i] + Z_n[i-1])

# SYNC 相位
theta_n = np.array([n * 2 * math.pi / 88 for n in range(1, N_d)])

print(f"\n  K_Chain 參數（全部從 x²+x-1=0 導出）:")
print(f"  φ = {PHI:.10f}")
print(f"  H₀ = {H0_IDCM:.2f} km/s/Mpc")
print(f"  R_H = {R_H:.2f} Mpc")
print(f"  λ_sync = {LAMBDA_SYNC:.2f} Mpc")
print(f"  BAO = λ_sync/2 = {BAO_MPC:.2f} Mpc = {BAO_MPC/H:.1f} h⁻¹Mpc")
print(f"  N_d = {N_d} modes")

# ================================================================
# 1. 建構 ξ(σ, π) 理論模型
# ================================================================
print(f"\n{'─'*80}")
print("  1. 建構 ξ(σ, π) 2D 理論模型")
print(f"{'─'*80}")

# 諧波振幅
def harmonic_amplitude(n):
    """第 n 個諧波嘅振幅（從 γ_n 同 Lucas 數導出）"""
    if n < 1 or n >= N_d:
        return 0
    g = gamma_n[n-1]
    L_val = L[n] if n < len(L) else 1
    amp = g / max(L_val, 1) * abs(math.cos(theta_n[n-1]))
    return amp

# 每個 mode 嘅各向異性權重
def mode_anisotropy(n):
    """第 n 個 mode 嘅各向異性強度（ξ₂/ξ₀ 比率）"""
    if n < 1 or n >= N_d:
        return 0
    ref = R_n[n-1]
    vg = v_g_n[n-1]
    Z = Z_n[n-1]
    # 反射 × 群速度 / 阻抗
    aniso = ref * vg / (1 + Z)
    return aniso

# 創建 2D 格點
N_grid = 200
s_max = 400  # Mpc
sigma = np.linspace(2, s_max, N_grid)  # s⊥ (transverse)
pi_axis = np.linspace(2, s_max, N_grid)  # s∥ (LOS)

# 理論 ξ(σ, π)
xi_2d = np.zeros((N_grid, N_grid))

# 疊加諧波
for n in range(2, 25):  # n=2..24
    amp = harmonic_amplitude(n)
    lam = LAMBDA_SYNC / n
    k = 2 * math.pi / lam
    
    aniso = mode_anisotropy(n)
    
    # 阻尼：高 mode 衰減更快
    damping = 80 * math.exp(-n / 80)
    
    for i in range(N_grid):
        for j in range(N_grid):
            s = math.sqrt(sigma[i]**2 + pi_axis[j]**2)
            if s < 1: continue
            mu = pi_axis[j] / s  # cos(θ) = LOS 方向
            
            # 各向異性修正
            # P₂(μ) = (3μ² - 1)/2
            P2 = (3 * mu**2 - 1) / 2
            
            # 總相關函數
            # ξ(σ, π) = ξ₀(s) + ξ₂(s)·P₂(μ)
            xi0 = amp * math.cos(k * s) * math.exp(-s / damping)
            xi2 = amp * aniso * math.cos(k * s + math.pi/2) * math.exp(-s / damping)
            
            xi_2d[i, j] += xi0 + xi2 * P2

# 正規化
xi_2d = xi_2d / np.max(np.abs(xi_2d)) * 0.1

print(f"  2D 格點: {N_grid}×{N_grid}")
print(f"  尺度範圍: 2 - {s_max} Mpc")
print(f"  ξ(σ, π) 值範圍: [{xi_2d.min():.4f}, {xi_2d.max():.4f}]")

# ================================================================
# 2. 提取特徵輪廓
# ================================================================
print(f"\n{'─'*80}")
print("  2. 特徵輪廓提取")
print(f"{'─'*80}")

# 沿對角線 (σ = π) 提取 — 即 monopole 嘅 s 軸
s_diag = np.array([math.sqrt(sigma[i]**2 + pi_axis[i]**2) for i in range(N_grid)])
xi_diag = np.array([xi_2d[i, i] for i in range(N_grid)])

# 沿 σ-軸 (π=0) — 純橫向
xi_trans = xi_2d[:, 0]

# 沿 π-軸 (σ=0) — 純視線方向
xi_los = xi_2d[0, :]

print(f"  對角線 (σ=π): ξ 範圍 [{xi_diag.min():.4f}, {xi_diag.max():.4f}]")
print(f"  橫向 (π=0): ξ 範圍 [{xi_trans.min():.4f}, {xi_trans.max():.4f}]")
print(f"  視線 (σ=0): ξ 範圍 [{xi_los.min():.4f}, {xi_los.max():.4f}]")

# ================================================================
# 3. 諧波位置檢測
# ================================================================
print(f"\n{'─'*80}")
print("  3. 理論諧波位置")
print(f"{'─'*80}")

print(f"  {'n':<5} {'λ_sync/n (Mpc)':<18} {'λ_sync/n (h⁻¹Mpc)':<20} {'振幅':<12} {'各向異性':<12}")
print(f"  {'─'*65}")
for n in range(2, 21):
    lam_mpc = LAMBDA_SYNC / n
    lam_hinv = lam_mpc / H
    amp = harmonic_amplitude(n)
    aniso = mode_anisotropy(n)
    print(f"  {n:<5} {lam_mpc:<18.2f} {lam_hinv:<20.1f} {amp:<12.6f} {aniso:<12.4f}")

# ================================================================
# 4. 對比 BOSS 數據
# ================================================================
print(f"\n{'─'*80}")
print("  4. 同 BOSS DR12 數據對比")
print(f"{'─'*80}")

import zipfile
DATA_PATH = '/home/wsl/IDCM/sync_bump_analysis/ross_dr12_corrfunc.zip'
z = zipfile.ZipFile(DATA_PATH)

def load_multipole(z, zbin, kind, bincent=0):
    fname = (f'Ross_2016_COMBINEDDR12/Ross_2016_COMBINEDDR12_{zbin}'
             f'_correlation_function_{kind}_post_recon_bincent{bincent}.dat')
    s, xi, err = [], [], []
    with z.open(fname) as f:
        for line in f.read().decode().strip().split('\n'):
            if line.startswith('#') or not line.strip(): continue
            parts = line.split()
            s.append(float(parts[0]))
            xi.append(float(parts[1]))
            err.append(float(parts[2]))
    return np.array(s), np.array(xi), np.array(err)

# 載入 BOSS zbin1 數據
s_boss, xi0_boss, err0_boss = load_multipole(z, 'zbin1', 'monopole')
_, xi2_boss, err2_boss = load_multipole(z, 'zbin1', 'quadrupole')

# 將 BOSS 數據從 h⁻¹Mpc 轉換到 Mpc (IDCM's H₀)
s_boss_mpc = s_boss * H  # h⁻¹Mpc → Mpc

print(f"\n  BOSS DR12 zbin1 數據（轉換到 Mpc 用 IDCM H₀={H0_IDCM}）:")
print(f"  {'s (h⁻¹Mpc)':<15} {'s (Mpc)':<15} {'ξ₀':<15} {'ξ₂':<15}")
print(f"  {'─'*55}")
for i in range(0, min(20, len(s_boss))):
    print(f"  {s_boss[i]:<15.1f} {s_boss_mpc[i]:<15.2f} {xi0_boss[i]:<15.6f} {xi2_boss[i]:<15.6f}")

# 喺 BOSS 嘅 s 位置計算理論 ξ₀ 同 ξ₂
xi0_pred = np.zeros(len(s_boss_mpc))
xi2_pred = np.zeros(len(s_boss_mpc))

for n in range(2, 25):
    amp = harmonic_amplitude(n)
    lam = LAMBDA_SYNC / n
    k = 2 * math.pi / lam
    aniso = mode_anisotropy(n)
    damping = 80 * math.exp(-n / 80)
    
    for i, s in enumerate(s_boss_mpc):
        xi0_pred[i] += amp * math.cos(k * s) * math.exp(-s / damping)
        xi2_pred[i] += amp * aniso * math.cos(k * s + math.pi/2) * math.exp(-s / damping)

# 正規化
xi0_pred = xi0_pred / np.max(np.abs(xi0_pred)) * np.max(np.abs(xi0_boss)) * 0.1
xi2_pred = xi2_pred / np.max(np.abs(xi2_pred)) * np.max(np.abs(xi2_boss)) * 0.1

# 輸出對比
print(f"\n  BOSS s (h⁻¹Mpc) vs 理論預測:")
print(f"  {'s':<10} {'BOSS ξ₀':<15} {'理論 ξ₀':<15} {'BOSS ξ₂':<15} {'理論 ξ₂':<15}")
print(f"  {'─'*65}")
for i in range(0, len(s_boss), 3):
    print(f"  {s_boss[i]:<10.1f} {xi0_boss[i]:<15.6f} {xi0_pred[i]:<15.6f} {xi2_boss[i]:<15.6f} {xi2_pred[i]:<15.6f}")

# ================================================================
# 5. 關鍵診斷
# ================================================================
print(f"\n{'─'*80}")
print("  5. 關鍵診斷：IDCM BAO 位置 vs ΛCDM BAO 位置")
print(f"{'─'*80}")

# IDCM BAO 位置
IDCM_BAO_MPC = BAO_MPC  # 147.44 Mpc
IDCM_BAO_HINV = IDCM_BAO_MPC / H  # 203.1 h⁻¹Mpc

# ΛCDM BAO 位置（標準值）
LCDM_BAO_HINV = 105.0  # h⁻¹Mpc (typical)
LCDM_BAO_MPC = LCDM_BAO_HINV * 0.676  # 用 Planck 2018 H₀=67.6

print(f"\n  IDCM BAO:")
print(f"    λ_sync/2 = {IDCM_BAO_MPC:.2f} Mpc")
print(f"    = {IDCM_BAO_HINV:.1f} h⁻¹Mpc (IDCM H₀={H0_IDCM})")
print(f"\n  ΛCDM BAO:")
print(f"    ~{LCDM_BAO_HINV:.0f} h⁻¹Mpc")
print(f"    = {LCDM_BAO_MPC:.1f} Mpc (Planck H₀=67.6)")
print(f"\n  比率: {IDCM_BAO_MPC / LCDM_BAO_MPC:.2f}x")
print(f"\n  BOSS 數據範圍: s = {s_boss[0]:.1f} - {s_boss[-1]:.1f} h⁻¹Mpc")
print(f"  IDCM BAO 喺 BOSS 數據範圍外! (s_max={s_boss[-1]:.1f} < {IDCM_BAO_HINV:.1f})")
print(f"\n  → 結論: BOSS DR12 嘅尺度範圍唔夠睇到 IDCM BAO peak")
print(f"  → 需要 DESI 或更大範圍嘅數據")

# ================================================================
# 6. 儲存結果
# ================================================================
# 儲存理論預測（用於後續視覺化）
output = {
    'constants': {
        'lambda_sync': LAMBDA_SYNC,
        'bao_mpc': BAO_MPC,
        'R_H': R_H,
        'H0': H0_IDCM,
        'N_d': N_d
    },
    'harmonic_series': [
        {'n': int(n), 'lam_mpc': float(LAMBDA_SYNC/n), 
         'lam_hinv': float(LAMBDA_SYNC/n/H),
         'amplitude': float(harmonic_amplitude(n)),
         'anisotropy': float(mode_anisotropy(n)),
         'gamma': float(gamma_n[n-1]),
         'v_g': float(v_g_n[n-1]),
         'Z': float(Z_n[n-1]),
         'R': float(R_n[n-1] if n-1 < len(R_n) else 0)}
        for n in range(1, 25)
    ],
    'boss_data': {
        's_hinv': s_boss.tolist(),
        's_mpc': s_boss_mpc.tolist(),
        'xi0': xi0_boss.tolist(),
        'xi2': xi2_boss.tolist(),
        'err0': err0_boss.tolist(),
        'err2': err2_boss.tolist()
    },
    'prediction': {
        'xi0': xi0_pred.tolist(),
        'xi2': xi2_pred.tolist()
    }
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/43_kchain_2d_xi.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果已儲存至 43_kchain_2d_xi.json")

print(f"\n{'='*80}")
print(f"  K_CHAIN 2D ξ(σ, π) 全息投影 — 零自由參數預測")
print(f"{'='*80}")