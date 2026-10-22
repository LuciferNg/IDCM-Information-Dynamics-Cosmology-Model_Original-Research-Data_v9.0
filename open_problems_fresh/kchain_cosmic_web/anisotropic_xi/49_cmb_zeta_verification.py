#!/usr/bin/env python3
"""
49_cmb_zeta_verification.py — Planck CMB 角功率譜 vs IDCM 44-mode 結構
======================================================================
終極試煉：IDCM 嘅離散晶格頻譜（λ_sync=294.88, BAO=147.44 Mpc）如果真實，
必須喺 CMB 聲學峰中展現對應相位。

測試：
1. IDCM H(z)（含 ζ(z)）預測 D_A(z*) → 聲學尺度 θ_s → 峰間距 Δℓ
2. Planck 峰位置比：ℓ₁:ℓ₂:ℓ₃ — 係咪諧波結構？
3. 峰位置對應嘅實體尺度 — 同 λ_sync/n 系列比較
"""
import math
import numpy as np

C_LIGHT = 299792.458
PHI_INV = (math.sqrt(5) - 1) / 2
H0_IDCM = 72.59
LAMBDA_SYNC = 294.88
BAO_SCALE = LAMBDA_SYNC / 2  # 147.44 Mpc

print("=" * 80)
print("  Planck CMB vs IDCM 44-mode 結構 — 終極試煉")
print("=" * 80)

# ================================================================
# 1. IDCM H(z)（含 ζ(z) 修正）→ D_A(z*)
# ================================================================
def hz_idcm_base(z):
    eps = PHI_INV / 4
    theta = math.tanh(z / 2)
    alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
    return H0_IDCM * (1 + z) ** alpha

def zeta_correction(z, zeta0=0.2509, zs=2.0, zeta1=0.6537, zl=5.0):
    low_z = zeta0 * math.exp(-z / zs)
    high_z = zeta1 * (1 - math.exp(-z / zl))
    return 1.0 + low_z - high_z

def hz_corrected(z):
    return hz_idcm_base(z) / zeta_correction(z)

def comoving_distance(z, N=5000):
    """D_C(z) = c·∫₀ᶻ dz'/H(z')  (Mpc)"""
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_corrected(zp)
    return C_LIGHT * integral

# ΛCDM 對比
def hz_lcdm(z, H0=67.4, Om=0.315):
    OL = 1 - Om
    return H0 * math.sqrt(Om * (1+z)**3 + OL)

def comoving_distance_lcdm(z, N=5000):
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / hz_lcdm(zp)
    return C_LIGHT * integral

# Recombination redshift (ΛCDM 值, 作為輸入)
Z_STAR = 1090.0

print(f"\n  重組紅移 z* = {Z_STAR}")

# IDCM D_A(z*)
DC_idcm = comoving_distance(Z_STAR)
DA_idcm = DC_idcm / (1 + Z_STAR)  # angular diameter distance
print(f"\n  IDCM: D_C(z*) = {DC_idcm:.0f} Mpc, D_A(z*) = {DA_idcm:.0f} Mpc")

# ΛCDM D_A(z*)
DC_lcdm = comoving_distance_lcdm(Z_STAR)
DA_lcdm = DC_lcdm / (1 + Z_STAR)
print(f"  ΛCDM: D_C(z*) = {DC_lcdm:.0f} Mpc, D_A(z*) = {DA_lcdm:.0f} Mpc")

# ================================================================
# 2. 聲學尺度 θ_s 同峰間距
# ================================================================
print(f"\n{'─'*80}")
print("  2. 聲學尺度預測")
print(f"{'─'*80}")

# IDCM 用 BAO scale 作為聲學尺度
theta_s_idcm = BAO_SCALE / DA_idcm  # radians
ell_A_idcm = math.pi / theta_s_idcm  # acoustic scale (peak spacing)
print(f"\n  IDCM: θ_s = {theta_s_idcm:.6f} rad = {math.degrees(theta_s_idcm):.3f}°")
print(f"  IDCM: ℓ_A = π/θ_s = {ell_A_idcm:.1f} (預測峰間距 Δℓ)")

# ΛCDM 用 r_d ≈ 147.09 Mpc
rd_lcdm = 147.09
theta_s_lcdm = rd_lcdm / DA_lcdm
ell_A_lcdm = math.pi / theta_s_lcdm
print(f"\n  ΛCDM: θ_s = {theta_s_lcdm:.6f} rad = {math.degrees(theta_s_lcdm):.3f}°")
print(f"  ΛCDM: ℓ_A = π/θ_s = {ell_A_lcdm:.1f} (預測峰間距 Δℓ)")

# 峰位置預測
print(f"\n  峰位置預測（n×ℓ_A + 相位偏移）:")
for n in [1, 2, 3, 4]:
    print(f"    Peak {n}: ℓ ≈ {n * ell_A_idcm:.0f} (IDCM) | {n * ell_A_lcdm:.0f} (ΛCDM)")

# ================================================================
# 3. 載入 Planck 數據，找峰位置
# ================================================================
print(f"\n{'─'*80}")
print("  3. Planck 實際峰位置")
print(f"{'─'*80}")

# Load Planck TT
data = []
with open('/home/wsl/IDCM/data/planck/COM_PowerSpect_CMB-TT-full_R3.01.txt') as f:
    for line in f:
        if line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            data.append((float(parts[0]), float(parts[1])))
data = np.array(data)
ell = data[:, 0]
Dl = data[:, 1]
print(f"  載入 {len(ell)} 個數據點, ℓ ∈ [{ell.min():.0f}, {ell.max():.0f}]")

# 找峰（平滑後局部最大）
from scipy.ndimage import gaussian_filter1d
Dl_smooth = gaussian_filter1d(Dl, sigma=15)

# 喺 ℓ > 100 找峰（跳過低 ℓ 背景）
mask = ell > 100
peaks = []
for i in range(5, len(ell) - 5):
    if not mask[i]:
        continue
    if Dl_smooth[i] > Dl_smooth[i-1] and Dl_smooth[i] > Dl_smooth[i+1]:
        # 檢查係咪顯著峰
        local_min = min(Dl_smooth[max(0,i-50):i+51])
        if Dl_smooth[i] - local_min > 100:
            peaks.append((ell[i], Dl_smooth[i]))

# 去重：保留最高峰
unique_peaks = []
for p in peaks:
    if not unique_peaks or p[0] - unique_peaks[-1][0] > 80:
        unique_peaks.append(p)
    else:
        if p[1] > unique_peaks[-1][1]:
            unique_peaks[-1] = p

print(f"\n  偵測到嘅聲學峰:")
peak_ells = []
for p in unique_peaks[:6]:
    peak_ells.append(p[0])
    print(f"    ℓ = {p[0]:.0f} (D_ℓ = {p[1]:.0f} μK²)")

# 峰間距
print(f"\n  峰間距:")
for i in range(len(peak_ells) - 1):
    print(f"    Δℓ({i+1}→{i+2}) = {peak_ells[i+1] - peak_ells[i]:.0f}")

# ================================================================
# 4. 峰位置比 — 諧波結構測試
# ================================================================
print(f"\n{'─'*80}")
print("  4. 諧波結構測試")
print(f"{'─'*80}")

if len(peak_ells) >= 3:
    ratios = [peak_ells[i] / peak_ells[0] for i in range(len(peak_ells))]
    print(f"\n  峰位置比（相對第一峰）:")
    for i, r in enumerate(ratios):
        print(f"    ℓ_{i+1}/ℓ₁ = {r:.3f}")
    print(f"\n  諧波系列 (1:2:3:4) 對比:")
    for i in range(len(peak_ells)):
        print(f"    ℓ_{i+1} = {peak_ells[i]:.0f} | 諧波 n={i+1}: {peak_ells[0]*(i+1):.0f} | 偏差 {(peak_ells[i] - peak_ells[0]*(i+1))/peak_ells[0]*(i+1)*100:+.1f}%")

# ================================================================
# 5. 峰位置 ↔ λ_sync 系列映射
# ================================================================
print(f"\n{'─'*80}")
print("  5. 峰位置 ↔ IDCM 尺度映射")
print(f"{'─'*80}")

# 每個峰嘅實體尺度: λ = 2π·D_A/ℓ
print(f"\n  每個峰對應嘅實體尺度（用 IDCM D_A）:")
for i, lp in enumerate(peak_ells):
    lam = 2 * math.pi * DA_idcm / lp
    lam_mpc = lam
    # 同 λ_sync/n 比較
    lam_n = LAMBDA_SYNC / (i + 1)
    ratio = lam_mpc / lam_n
    print(f"    Peak {i+1} (ℓ={lp:.0f}): λ = {lam_mpc:.1f} Mpc | λ_sync/{i+1} = {lam_n:.1f} | 比 = {ratio:.3f}")

# 對比 ΛCDM
print(f"\n  （用 ΛCDM D_A 做對比）:")
for i, lp in enumerate(peak_ells):
    lam = 2 * math.pi * DA_lcdm / lp
    print(f"    Peak {i+1} (ℓ={lp:.0f}): λ = {lam:.1f} Mpc")

# ================================================================
# 6. 總結
# ================================================================
print(f"\n{'─'*80}")
print("  6. 總結")
print(f"{'─'*80}")
print(f"""
  IDCM 聲學尺度預測: ℓ_A = {ell_A_idcm:.0f}
  ΛCDM 聲學尺度預測: ℓ_A = {ell_A_lcdm:.0f}
  Planck 實測峰間距: Δℓ ≈ {peak_ells[1]-peak_ells[0] if len(peak_ells)>1 else 'N/A'}
  
  IDCM 預測 vs Planck:
  - 峰間距（如果 ℓ_A 匹配）→ 結構驗證
  - 峰位置比（諧波 vs 非諧波）→ 結構辨識
  - 峰對應實體尺度 → λ_sync 系列對比
""")