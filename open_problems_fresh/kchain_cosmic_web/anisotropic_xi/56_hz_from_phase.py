#!/usr/bin/env python3
"""
56_hz_from_phase.py — 重新推導 v2：由色散相位累積直接建構 H(z)
=================================================================
v1 教訓（55）：能量加權全部 44 mode 錯 — v_g(43)≈0 令慢度爆炸。

v2 正確方向（41 號 insight）：
  1. BAO 係 K_Chain 第 28 諧波，實體波長 λ_BAO = 147.44 Mpc
  2. 紅移 z = 操作步數（結構座標）— 觀測深度
  3. 訊號以群速度 v_g(n) = cos(πn/88) 傳播
  4. 有效模式數隨 z 演化：n_eff(z) = 28/(1+z)（紅移壓縮 mode 數）
  5. 相位累積 Φ(z) = ∫₀ᶻ dz'/(1+z')/v_g(n_eff(z'))
  6. θ(z) = θ₀·exp(-Φ(z)) — 色散令 BAO 角度壓縮
  7. θ(z) = λ_BAO/D_A(z) → D_A(z) → D_C(z) → H(z)

關鍵：呢條鏈完全冇 Ω_L，冇 ζ — 只有 K_Chain 結構。
θ₀ 由「第 28 諧波繞一圈」決定：θ₀ = 2π/28（一個波峰嘅角尺度）
"""
import math
import numpy as np
from scipy import optimize
import json

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
H0_IDCM = 72.59
C_LIGHT = 299792.458
BAO = 147.44
N_BAO = 28

print("=" * 80)
print("  重新推導 v2 — H(z) from phase accumulation")
print("=" * 80)

# ================================================================
# 1. 色散相位累積
# ================================================================
def n_eff(z):
    """有效模式數：z=0 → 28, z→∞ → 0（紅移壓縮）"""
    ne = N_BAO / (1 + z)
    return max(min(ne, 43), 1)  # clamp

def v_g(n):
    """群速度"""
    return math.cos(math.pi * n / 88)

def phase_accumulate(z, N=400):
    """Φ(z) = ∫₀ᶻ dz'/(1+z')/v_g(n_eff(z'))"""
    zz = np.linspace(0, z, N)
    dz = z / N
    phi = 0.0
    for zi in zz:
        ne = n_eff(zi)
        vg = v_g(ne)
        if vg < 0.1:
            vg = 0.1
        phi += dz / (1 + zi) / vg
    return phi

def theta_idcm(z):
    """θ(z) = θ₀·exp(-Φ(z))，θ₀ = 2π/28"""
    theta0 = 2 * math.pi / N_BAO  # 0.2244 rad
    return theta0 * math.exp(-phase_accumulate(z))

def DA_from_theta(z):
    """D_A(z) = λ_BAO/θ(z)"""
    return BAO / theta_idcm(z)

def H_from_phase(z, N=200):
    """
    由 D_A(z) 反推 H(z)：
    D_C(z) = (1+z)·D_A(z)
    H(z) = c / (dD_C/dz)
    數值微分
    """
    dz = z / N
    z1, z2 = z - dz, z + dz
    if z1 < 0: z1 = 0
    DC1 = (1 + z1) * DA_from_theta(z1)
    DC2 = (1 + z2) * DA_from_theta(z2)
    dDC = (DC2 - DC1) / (z2 - z1)
    return C_LIGHT / dDC if dDC > 0 else float('inf')

print(f"\n  n_eff(z) = 28/(1+z), v_g = cos(πn/88)")
print(f"  θ₀ = 2π/28 = {2*math.pi/28:.6f} rad = {360/28:.2f}°")

# 形狀檢查
print(f"\n  {'z':<6} {'n_eff':<8} {'v_g':<10} {'Φ':<10} {'θ(°)':<10} {'D_A(Mpc)':<12}")
print(f"  {'─'*56}")
for zt in [0.01, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 2.33]:
    ne = n_eff(zt)
    vg = v_g(ne)
    phi = phase_accumulate(zt)
    th = theta_idcm(zt) * 180 / math.pi
    da = DA_from_theta(zt)
    print(f"  {zt:<6.2f} {ne:<8.2f} {vg:<10.4f} {phi:<10.4f} {th:<10.4f} {da:<12.1f}")

# ================================================================
# 2. 對比 DESI（零參數）
# ================================================================
print(f"\n{'─'*80}")
print("  2. 零參數預測 vs DESI DR2")
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

def DM_pred(z):
    """DM/rd = D_C(z)/λ_BAO = (1+z)·D_A(z)/λ_BAO"""
    return (1 + z) * DA_from_theta(z) / BAO

def DH_pred(z):
    """DH/rd = c/(H(z)·λ_BAO)"""
    H_z = H_from_phase(z)
    return C_LIGHT / H_z / BAO if H_z != float('inf') else float('nan')

print(f"\n  {'z':<8} {'量':<6} {'預測':<12} {'DESI':<12} {'Δ/σ':<8}")
print(f"  {'─'*46}")
chi2 = 0.0
for i in range(len(desi_z)):
    z = desi_z[i]; qty = desi_qty[i]
    if qty == 'DM':
        pred = DM_pred(z)
    elif qty == 'DH':
        pred = DH_pred(z)
    elif qty == 'DV':
        dm = DM_pred(z)
        dh = DH_pred(z)
        pred = (z * dm**2 * dh) ** (1/3)
    err = math.sqrt(cov_desi[i, i])
    sig = (desi_val[i] - pred) / err
    chi2 += sig**2
    print(f"  {z:<8.3f} {qty:<6} {pred:<12.4f} {desi_val[i]:<12.4f} {sig:<+8.2f}")

print(f"\n  χ²(DESI) = {chi2:.1f} (13 dof), χ²/dof = {chi2/13:.1f}")
print(f"  （零 fit 參數 — 純 K_Chain 色散相位累積）")

# ================================================================
# 3. H(z) 形狀對比
# ================================================================
print(f"\n{'─'*80}")
print("  3. H(z) 形狀對比")
print(f"{'─'*80}")

print(f"\n  {'z':<6} {'H_色散':<12} {'H_舊(Ω_L+ζ)':<14} {'H_ΛCDM':<12}")
print(f"  {'─'*44}")
for zt in [0.05, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0]:
    h_new = H_from_phase(zt)
    eps = PHI_INV / 4
    theta = math.tanh(zt / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    h_base = H0_IDCM * (1 + zt) ** alpha
    zeta = 1.0 + zt * (1.0847 * math.exp(-zt / 0.5114) - 0.4723 * (1 - math.exp(-zt / 10.0)))
    h_old = h_base / zeta
    h_lcdm = 67.4 * math.sqrt(0.315 * (1+zt)**3 + 0.685)
    print(f"  {zt:<6.2f} {h_new:<12.1f} {h_old:<14.1f} {h_lcdm:<12.1f}")

output = {
    'method': 'phase accumulation: θ(z)=θ₀exp(-Φ(z)), Φ=∫dz/(1+z)/v_g(28/(1+z))',
    'chi2_desi': float(chi2),
    'dof': 13,
    'theta0': 2*math.pi/N_BAO
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/56_phase_hz_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 56_phase_hz_results.json")
print(f"{'='*80}")