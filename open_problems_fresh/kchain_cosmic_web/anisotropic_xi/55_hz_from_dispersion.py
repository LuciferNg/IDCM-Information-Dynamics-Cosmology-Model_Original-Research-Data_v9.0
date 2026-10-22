#!/usr/bin/env python3
"""
55_hz_from_dispersion.py — 重新推導：從 K_Chain 44-mode 色散直接建構 H(z)
============================================================================
矛盾：舊結構 H(z) = H_base(z)/ζ(z) 有兩層 —
  baseline 內嵌 Ω_L=0.683（B=4 運行成本）
  ζ(z) 又做「低 z 壓低、高 z 提高」（本身係暗能量效應）
  → double counting，兩個 fit 機制做同一個物理。

重新推導原則（41 號文件核心 insight）：
  1. 紅移 z = 操作步數（結構座標），唔係時間
  2. K_Chain 44-mode: γ_n = 4sin²(πn/88), v_g(n) = cos(πn/88)
  3. 宇宙 = 44-tone harmonic oscillator = 條弦自身嘅域內共振
  4. H(z) 應該直接由 44-mode 色散決定，唔需要 Ω_L，唔需要 ζ

物理動機：
  紅移 z 反映觀測深度 → 有效模式 n_eff(z)（高 z 睇到更多高頻模式）
  每個 mode 有群速度 v_g(n) → 訊號傳播慢度 = 1/v_g(n)
  有效慢度 = 44 個 mode 嘅加權平均（權重 = mode 能量 γ_n）
  加權係「共振權重」：觀測深度 z 決定邊啲 mode 被激發

推導：
  1/v_eff(z) = Σ_n γ_n · w_n(z) / v_g(n)   （慢度 = 能量加權群速度倒數）
  H(z) = H₀ · (1+z)^α_eff(z)
  其中 α_eff(z) 由色散直接得出
"""
import math
import numpy as np
from scipy import optimize
import json

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
H0_IDCM = 72.59
C_LIGHT = 299792.458
N_D = 44
BAO = 147.44

print("=" * 80)
print("  重新推導 — H(z) from K_Chain 44-mode dispersion")
print("=" * 80)

# ================================================================
# 1. K_Chain 色散結構
# ================================================================
print(f"\n{'─'*80}")
print("  1. K_Chain 44-mode 色散")
print(f"{'─'*80}")

gamma_n = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_D)])
v_g_n = np.array([math.cos(math.pi * n / 88) for n in range(1, N_D)])
n_idx = np.arange(1, N_D)

# 驗證結構
print(f"\n  γ_n = 4sin²(πn/88), v_g(n) = cos(πn/88)")
print(f"  Σγ_n (n=1..43) = {gamma_n.sum():.4f} (全 88-site 係 176, 半個 ring 係 88)")
print(f"  γ_n + γ_(44-n) = 4 ✓（互補配對）")
print(f"  v_g(1) = {v_g_n[0]:.6f}, v_g(22) = {v_g_n[21]:.6f} (Nyquist), v_g(43) = {v_g_n[42]:.6f}")

# ================================================================
# 2. 有效群速度（色散加權）
# ================================================================
print(f"\n{'─'*80}")
print("  2. 有效慢度 = 能量加權群速度倒數")
print(f"{'─'*80}")

def n_eff(z, n_max=43):
    """
    有效模式數：觀測深度 z 決定邊啲 mode 被激發。
    z=0 → 最低頻 mode (n_eff→1)
    z→∞ → 全部 mode 被激發 (n_eff→43)
    
    映射：n_eff(z) = 1 + (n_max-1)·tanh(z/2)
    結構動機：tanh 係 41 號 baseline 已有嘅飽和函數（θ=tanh(z/2)），
    而 44 係 K_Chain 維度 — 觀測越深，共振覆蓋越多 mode
    """
    return 1.0 + (n_max - 1) * math.tanh(z / 2)

def v_eff(z):
    """有效群速度 = 加權平均（權重 = mode 能量 γ_n × 激發權重）"""
    ne = n_eff(z)
    # 激發權重：mode n 被 z 深度激發嘅程度（sigmoid 喺 n_eff 附近）
    # 權重 = γ_n × exp(-|n - n_eff|/σ)，σ 係共振寬度
    sigma = 8.0  # 共振寬度（半個 ring 嘅 ~1/5）
    w = gamma_n * np.exp(-np.abs(n_idx - ne) / sigma)
    w = w / w.sum()
    # 有效慢度 = Σ w_n / v_g(n)
    slow = np.sum(w / v_g_n)
    return 1.0 / slow

def alpha_eff(z):
    """
    有效色散指數：H(z) = H₀(1+z)^α_eff(z)
    慢度 vs 無色散 (v=1) 嘅比率決定 α 偏離 1 嘅程度
    """
    ve = v_eff(z)
    # α = 1 + log(v_eff)/log(1+z) 嘅連續形式
    # 直接: α_eff 反映群速度 < 1 → 訊號慢 → 距離遠 → H 增長慢
    return 1.0 / ve  # 慢度 = 指數（低 z 接近 1，高 z 接近 1/v_eff）

def hz_dispersion(z):
    """H(z) = H₀(1+z)^α_eff(z)"""
    return H0_IDCM * (1 + z) ** alpha_eff(z)

# 檢查形狀
print(f"\n  n_eff(z) = 1 + 42·tanh(z/2), σ = 8")
print(f"\n  {'z':<6} {'n_eff':<8} {'v_eff':<10} {'α_eff':<10} {'H(z)':<10}")
print(f"  {'─'*44}")
for zt in [0, 0.1, 0.3, 0.5, 1.0, 1.5, 2.0, 2.33, 5.0, 10.0]:
    ne = n_eff(zt)
    ve = v_eff(zt)
    ae = alpha_eff(zt)
    h = hz_dispersion(zt)
    print(f"  {zt:<6.1f} {ne:<8.2f} {ve:<10.4f} {ae:<10.4f} {h:<10.1f}")

# ================================================================
# 3. 對比 DESI（無任何 fit 參數！）
# ================================================================
print(f"\n{'─'*80}")
print("  3. 零參數預測 vs DESI DR2")
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

def integ_dm(z, N=300):
    zz = np.linspace(0, z, N)
    mid = (zz[1:] + zz[:-1]) / 2
    h = np.array([hz_dispersion(zm) for zm in mid])
    return np.sum((zz[1:] - zz[:-1]) / h)

def desi_predictions():
    model = []
    for i in range(len(desi_z)):
        z = desi_z[i]; qty = desi_qty[i]
        if qty == 'DM':
            pred = C_LIGHT * integ_dm(z) / BAO
        elif qty == 'DH':
            pred = C_LIGHT / hz_dispersion(z) / BAO
        elif qty == 'DV':
            dm = C_LIGHT * integ_dm(z) / BAO
            dh = C_LIGHT / hz_dispersion(z) / BAO
            pred = (z * dm**2 * dh) ** (1/3)
        model.append(pred)
    return np.array(model)

model = desi_predictions()
delta = np.array(desi_val) - model
chi2 = delta @ cov_desi_inv @ delta

print(f"\n  {'z':<8} {'量':<6} {'預測':<12} {'DESI':<12} {'Δ/σ':<8}")
print(f"  {'─'*46}")
for i in range(len(desi_z)):
    err = math.sqrt(cov_desi[i, i])
    print(f"  {desi_z[i]:<8.3f} {desi_qty[i]:<6} {model[i]:<12.4f} {desi_val[i]:<12.4f} "
          f"{(desi_val[i]-model[i])/err:<+8.2f}")

print(f"\n  χ²(DESI) = {chi2:.1f} (13 dof), χ²/dof = {chi2/13:.1f}")
print(f"  （零 fit 參數 — 純 K_Chain 結構預測）")

# ================================================================
# 4. 對比舊結構
# ================================================================
print(f"\n{'─'*80}")
print("  4. 對比：舊結構 (Ω_L baseline + ζ) vs 新結構 (純色散)")
print(f"{'─'*80}")

# 舊結構（_core.py 版本）
def hz_old(z):
    eps = PHI_INV / 4
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    h_base = H0_IDCM * (1 + z) ** alpha
    zeta = 1.0 + z * (1.0847 * math.exp(-z / 0.5114) - 0.4723 * (1 - math.exp(-z / 10.0)))
    return h_base / zeta

print(f"\n  {'z':<6} {'H_舊':<10} {'H_新':<10} {'H_ΛCDM':<10}")
print(f"  {'─'*36}")
for zt in [0, 0.3, 0.5, 1.0, 1.5, 2.0, 2.33]:
    h_old = hz_old(zt)
    h_new = hz_dispersion(zt)
    h_lcdm = 67.4 * math.sqrt(0.315 * (1+zt)**3 + 0.685)
    print(f"  {zt:<6.1f} {h_old:<10.1f} {h_new:<10.1f} {h_lcdm:<10.1f}")

# 儲存
output = {
    'structure': {
        'gamma_n': '4sin²(πn/88)',
        'v_g': 'cos(πn/88)',
        'n_eff': '1 + 42·tanh(z/2)',
        'sigma': 8.0,
        'alpha_eff': '1/v_eff(z)'
    },
    'chi2_desi_zero_param': float(chi2),
    'dof': 13,
    'predictions': [float(x) for x in model]
}
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/55_dispersion_hz_results.json', 'w') as f:
    json.dump(output, f, indent=2)
print(f"\n  結果: 55_dispersion_hz_results.json")
print(f"{'='*80}")