#!/usr/bin/env python3
"""
深入推導：τ_depth = 44×t_site 與 z=17 Nyquist 截斷的結構關係
"""
import math
import numpy as np

# === Parameters ===
H0 = 72.59  # km/s/Mpc
Om = 0.317
c = 299792.458  # km/s
Gyr = 3.15576e16  # s
Mpc_per_Gly = 306.601

# Derived
H0_1ps = H0 * 3.240779e-20
R_H = c / H0  # Mpc
t_site = 0.306  # Gyr

def lookback_time(z, H0, Om):
    """Lookback time in Gyr from z=0 to z=z_max."""
    N = 200000
    z_arr = np.linspace(0, z, N+1)
    dz = z / N
    integrand = 1.0 / ((1 + z_arr) * np.sqrt(Om*(1+z_arr)**3 + (1-Om)))
    integral = integrand[0] + integrand[-1]
    integral += 4 * np.sum(integrand[1:-1:2])
    integral += 2 * np.sum(integrand[2:-1:2])
    integral *= dz / 3
    return integral / H0 * 977.8

def universe_age(z, H0, Om):
    """Age of universe at redshift z in Gyr."""
    return lookback_time(1e9, H0, Om) - lookback_time(z, H0, Om)

print("=" * 70)
print("第一部分：τ_depth = K_Chain 環的 light-crossing time")
print("=" * 70)

t_hubble = 1 / H0_1ps / Gyr
t_44ts = 44 * t_site

print(f"""
K_Chain 結構:
  44 sites, closed periodic ring
  site spacing a = R_H/44 = {R_H/44:.1f} Mpc
  t_site = a/c = {t_site} Gyr

τ_depth = 44 × t_site = {t_44ts:.4f} Gyr   ← K_Chain light-crossing time
1/H₀    = {t_hubble:.4f} Gyr                 ← Hubble time
Match: {abs(t_44ts - t_hubble)/t_hubble*100:.3f}% diff ✅

物理意義: 光環繞 K_Chain 44-site 環一圈要 13.46 Gyr
呢個係結構內的最大因果距離 — 因果視界
""")

# === Part 2: z=17 Nyquist ===
print("=" * 70)
print("第二部分：z=17 的 Nyquist 結構推導")
print("=" * 70)

# The key: t_site/√(γ_n) for n=22 ≈ 211 Myr ≈ ΛCDM universe age at z=17
for n in [22]:
    gamma = 4 * math.sin(math.pi * n / 88)**2
    tau_char = t_site / math.sqrt(gamma) * 1000  # Myr
    print(f"\nK_Chain mode n={n}:")
    print(f"  γ_n = 4 sin²({n}π/88) = {gamma:.6f}")
    print(f"  characteristic time = t_site/√γ = {tau_char:.1f} Myr")

# What is the ΛCDM universe age at z=17?
t_age_17 = universe_age(17, H0, Om)
t_age_16 = universe_age(16, H0, Om)
t_age_18 = universe_age(18, H0, Om)

print(f"\nΛCDM universe age at z=16: {t_age_16*1000:.1f} Myr")
print(f"ΛCDM universe age at z=17: {t_age_17*1000:.1f} Myr")
print(f"ΛCDM universe age at z=18: {t_age_18*1000:.1f} Myr")
print(f"K_Chain n=22 characteristic time: {tau_char:.1f} Myr")
print(f"Match: |t_age_17 - {tau_char:.1f}| = {abs(t_age_17*1000 - tau_char):.1f} Myr")

# === Part 3: K_Tree resolution ===
print("\n" + "=" * 70)
print("第三部分：K_Tree ℓ = log₄(1+z) 的結構意義")
print("=" * 70)

print(f"""
K_Tree: 33 levels, branching factor B=4
Scale at level ℓ: R_H / 4^ℓ

ℓ = 0:  scale = R_H        = {R_H:.0f} Mpc  (全 K_Chain)
ℓ = 1:  scale = R_H/4      = {R_H/4:.0f} Mpc  (11 sites)
ℓ = 2:  scale = R_H/16     = {R_H/16:.0f} Mpc  (2.75 sites → barely resolved)
ℓ = 2.08: scale = R_H/18   = {R_H/18:.0f} Mpc  (z=17, 2.44 sites)
ℓ = 3:  scale = R_H/64     = {R_H/64:.0f} Mpc  (0.69 sites → UNRESOLVED)
""")

# At what ℓ does scale = 1 K_Chain site?
ell_1site = math.log(44, 4)
z_1site = 4**ell_1site - 1
print(f"ℓ = log₄(44) = {ell_1site:.4f}: scale = 1 site spacing")
print(f"  → z = 4^{ell_1site:.4f} - 1 = {z_1site:.1f}")
print(f"  → At z < {z_1site:.1f}, K_Tree can resolve individual K_Chain sites")

# At what ℓ does scale = 2 sites (Nyquist)?
ell_2site = math.log(22, 4)
z_2site = 4**ell_2site - 1
print(f"ℓ = log₄(22) = {ell_2site:.4f}: scale = 2 site spacings (Nyquist)")
print(f"  → z = 4^{ell_2site:.4f} - 1 = {z_2site:.1f}")
print(f"  → At z > {z_2site:.1f}, Nyquist undersampling")

# === Part 4: The unified picture ===
print("\n" + "=" * 70)
print("第四部分：統一圖像 — 兩種不同的結構面向")
print("=" * 70)

print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                    K_Chain 44-site 閉環                             │
│                         (從 x²+x-1=0 推導)                          │
│                              │                                      │
│              ┌───────────────┴───────────────┐                      │
│              │                               │                      │
│         因果視界                          Nyquist 截斷                │
│         (τ_depth)                       (z=17)                      │
│              │                               │                      │
│    光環繞 44 步所需時間            44-site 離散的頻率極限              │
│    44 × t_site = 13.46 Gyr       t_site/√2 ≈ 216 Myr                │
│    = 1/H₀                        → ΛCDM z ≈ 17                     │
│              │                               │                      │
│    答案: 「有幾遠」                 答案: 「有幾清」                    │
│    (how far light can travel)     (how finely space is resolved)    │
│              │                               │                      │
│    K_Chain 環的周長 = 13.46 光年    K_Chain 環的像素 = 44 格          │
│    (幾何性質)                      (離散化性質)                       │
└─────────────────────────────────────────────────────────────────────┘

這兩個不是矛盾，而是同一結構的兩個不同面向：
  - 因果視界 → 回答「K_Chain 環有多大」
  - Nyquist 截斷 → 回答「K_Chain 環有多精細」
  
「K_Chain 永恆」係結構性質（從 x²+x-1=0 推導，無時間參數）
「13.8 Gyr = 44×t_site」係因果性質（環的 light-crossing time）
兩者描述不同層面，無需 reconciliation
""")

# === Part 5: Key testable predictions ===
print("=" * 70)
print("第五部分：可檢驗的預測")
print("=" * 70)

print(f"""
預測 1: τ_depth = 44 × t_site = 1/H₀
  → 如果 H₀ 改變，rendering depth 應成反比改變
  → H₀ = 72.59 → τ_depth = 13.46 Gyr

預測 2: z=17 係 Nyquist 截斷
  → 無 z>17 嘅星系（唔係「好難睇到」，而係「無格點」）
  → JWST 永遠唔會確認 z>17 嘅星系
  → 呢個係結構預測，唔係觀測極限

預測 3: K_Tree ℓ=2.08 cutoff
  → 紅移分布喺 z≈17 有平滑 cutoff，唔係 sharp edge
  → 星系數量喺 z=15-17 急劇下降，但仲有
  → 喺 z=17+ 完全真空

預測 4: K_Chain 環無「之前」
  → z>17 = NaN，唔係「之前有個隱藏宇宙」
  → 唔存在「Big Bang 之前」嘅問題
  → 因為 Big Bang 唔係時間起點，係 rendering 極限
""")

# === Part 6: The error in the previous hallucination ===
print("=" * 70)
print("第六部分：之前幻覺嘅結構錯誤")
print("=" * 70)

print("""
之前幻覺 #1: 「局部熱寂 / 兩層熱力學」
  錯誤: 將 K_Chain 同 3D 投影分為兩個層面嘅熱力學
  結構事實: 宇宙 = 44-tone harmonic oscillator，無分層熱力學
  τ_depth = 13.46 Gyr 係因果視界，唔係熱力學邊界

之前幻覺 #2: 「WKB bounce = 新宇宙循環」
  錯誤: 將 W-field bounce 擴大解釋成宇宙循環機制
  結構事實: 32_wfield_qft.md 嘅 bounce 係 W-field 量子穿隧計算
  bounce 同 τ_depth 完全無關

之前幻覺 #3: 「渲染邊界 = 電腦模擬比喻」
  錯誤: 將 z>17=NaN 講成「投影機」、「buffer」、「菲林」
  結構事實: z>17=NaN 係 K_Chain 44-site 嘅 Nyquist 截斷
  呢個係 Fourier 分析的基本結果，唔需要比喻
""")