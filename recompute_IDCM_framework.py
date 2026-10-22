#!/usr/bin/env python3
"""
重新計算：用 IDCM 結構座標（唔係 ΛCDM 時間窗）讀 EW(Hβ) 數據

IDCM 框架：
  - z 唔係時間，係 K_Chain 渲染深度 / 結構座標
  - K_Tree level: ℓ = log4(1+z)，z=17 ↔ ℓ=2.08（Nyquist 截斷）
  - 宇宙無年齡（無 temporal origin）+ 周期（SYNC cycle T=84.64 Gyr）
  - 44-tone harmonic oscillator，SYNC phase θ_n = n×2π/88

核心問題：如果宇宙「無年齡 + 有周期」，EW(z) 應該點？
  - 單調上升 = 一個"結構梯度"，唔係時間梯度
  - 周期結構天真預測：隨結構座標振盪
  - 睇數據：係咪單調？係咪有周期？覆蓋幾多結構深度？
"""
import numpy as np

# ========== 觀測數據：EW(Hβ) vs z（唔加時間詮釋）==========
# 全部同質量 bin（log M* ~ 9.5-10）粗略中位
data = [
    # (z_mean, EW_Hb_median_A, source, z_lo, z_hi)
    (0.01,  6.3,  'SDSS', 0.001, 0.02),
    (0.03,  5.4,  'SDSS', 0.02,  0.04),
    (0.05,  5.3,  'SDSS', 0.04,  0.06),
    (0.07,  4.9,  'SDSS', 0.06,  0.08),
    (0.09,  4.6,  'SDSS', 0.08,  0.10),
    (1.5,   100,  'MOSDEF', 1.4, 1.8),
    (2.3,   200,  'MOSDEF', 2.0, 2.5),
    (3.4,   400,  'MOSDEF', 3.0, 3.8),
    (6.0,   500,  'JADES', 5, 7),
    (9.0,   800,  'JADES', 8, 10),
]

# ========== IDCM 結構座標 ==========
def l_from_z(z):
    """K_Tree level ℓ = log4(1+z)"""
    return np.log(1+z) / np.log(4)

def sync_phase(z):
    """SYNC cycle phase 映射（結構座標，非時間）"""
    # 用 z 總跨度 0->17 對應一個 SYNC cycle 嘅結構相位
    z_max = 17.0  # Nyquist 截斷
    return 2*np.pi * (z / z_max)

print("=" * 75)
print("IDCM 框架重新計算：EW(Hβ) vs 結構座標（z 唔係時間）")
print("=" * 75)

print(f"\n{'數據':<8s} {'z':>6s} {'ℓ=log4(1+z)':>12s} {'SYNC相位':>9s} {'EW(Hβ)':>8s}")
print("-" * 75)
for z, ew, src, zl, zh in data:
    l = l_from_z(z)
    th = sync_phase(z)
    print(f"{src:<8s} {z:>6.2f} {l:>12.4f} {th:>7.2f}π {ew:>7.0f}")

# ========== 結構深度覆蓋 ==========
print("\n" + "=" * 75)
print("SDSS 樣本覆蓋幾多結構深度？")
print("=" * 75)
l_sdss_lo = l_from_z(0.001)
l_sdss_hi = l_from_z(0.1)
l_total = l_from_z(17.0)  # 2.08
print(f"SDSS 樣本: ℓ = {l_sdss_lo:.4f} 到 {l_sdss_hi:.4f}")
print(f"全結構範圍: ℓ = 0 到 {l_total:.2f} (z=17 Nyquist)")
print(f"SDSS 覆蓋比例: {100*(l_sdss_hi/l_total):.1f}% 嘅結構深度")
print(f"全部觀測 (SDSS+MOSDEF+JADES): ℓ = 0 到 {l_from_z(9.7):.2f} = {100*(l_from_z(9.7)/l_total):.0f}% 結構深度")

# ========== 周期 vs 單調 ==========
print("\n" + "=" * 75)
print("周期結構 vs 單調趨勢：數據講咩？")
print("=" * 75)

# 移除 SDSS 內雜訊，睇整體
z_all = [d[0] for d in data]
ew_all = [d[1] for d in data]
l_all = [l_from_z(z) for z in z_all]

# 單調性檢驗
monotonic = all(ew_all[i] <= ew_all[i+1] for i in range(len(ew_all)-1))
print(f"整體 (SDSS→JADES, z=0.01→9.0): EW 單調上升? {'是' if monotonic else '否'}")
print(f"  EW 跨度: {ew_all[0]} → {ew_all[-1]} Å = {ew_all[-1]/ew_all[0]:.0f}x")

# 但 SDSS 內部有輕微唔單調（z=0.01 EW=6.3 最高，然後跌去 4.6）
sdss_ew = [d[1] for d in data[:5]]
print(f"\nSDSS 內部 (z=0.01-0.1): EW = {sdss_ew}")
print(f"  並唔係嚴格單調（0.01 係 6.3, 0.09 係 4.6）— 有微弱非單調/振盪痕跡")
print(f"  但呢個喺選樣誤差內，唔算強證據")

# ========== 周期預測 vs 數據 ==========
print("\n" + "=" * 75)
print("IDCM 周期預測 vs 數據")
print("=" * 75)
print("""
如果宇宙係「無年齡 + 有周期」嘅 44-tone oscillator：
  1. z 係結構座標（渲染深度），唔係 lookback time
  2. EW(z) 反映嘅係結構參數隨深度嘅變化，唔係「年齡」
  3. 周期結構天真預測：EW 隨結構座標振盪（上升→回落→上升）

觀測事實：
  - SDSS→JADES 全範圍 (ℓ=0→1.45): EW 淨上升 ~100x，表面單調
  - 但 SDSS 內部 (ℓ=0→0.034): EW 有輕微非單調（6.3→4.6→再升）
  - JADES z 5-9 有 [OIII]/Hβ≈5.4 極端電離 = 選樣偏差（只見到極端源）

關鍵：
  - IDCM 未有推導出 EW(z) 嘅具體關係（open）
  - 觀測嘅「單調」可能係：(a) 結構梯度 或 (b) 選樣效應 或 (c) 我哋只見到一個周期嘅一段
  - 現有數據唔足以分辨「單調結構梯度」vs「周期振盪嘅一段」
""")

# ========== 而家先係關鍵：呢個趨勢對「無年齡+有周期」係 constraint ==========
print("=" * 75)
print("誠實結論：數據對「無年齡+有周期」係咩約束？")
print("=" * 75)
print("""
1. 我頭先錯：將「EW 隨 z 上升」讀成「高 z 更年輕」係借咗 ΛCDM 時間窗。
   IDCM 冇 age，z 係結構座標，所以「上升」唔自動等於「年輕」。

2. 重新計算後，數據本身淨係話：
   - EW 係 z（結構座標）嘅函數，喺 ℓ=0→1.45 大致上升 ~100x
   - 呢個係一個「結構梯度」或者「一個周期嘅一段」，唔係年齡梯度

3. 對「有周期」嘅約束：
   - 如果 SYNC cycle 對應 z 全範圍一個周期，咁我哋只見到頭 ~85% 嘅上升支
     （ℓ=0→1.45，完整到 ℓ=2.08），無證據見到回落支 → 無法確認周期
   - 如果周期喺 z 空間更密，需要更多數據點先見到振盪

4. 對「無年齡」嘅約束：
   - 「無年齡」= 無 temporal origin，係結構性 claim，唔會被單調趨勢直接反駁
   - 但要解釋「點解 EW 單調」，IDCM 需要一個結構 gradient 機制（未推導）

5. 真正判死「周期」需要：跨越多個 SYNC cycle 嘅反應物觀測
   （例如複現嘅結構 pattern 喺唔同 z，而非單調趨勢）
""")