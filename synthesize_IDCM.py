#!/usr/bin/env python3
"""
整合結論：用 IDCM 結構座標完整重算 EW(z)，分離選樣效應
數據：SDSS (原始) + MOSDEF + CEERS EELG (mean EW=1400Å, n=181)
"""
import numpy as np

# ========== 觀測數據 ==========
# (z, EW_Hb_mean_A, source, 選樣)
data = [
    (0.01, 6.3,  'SDSS all-SF',   'mass-complete'),
    (0.03, 5.4,  'SDSS all-SF',   'mass-complete'),
    (0.05, 5.3,  'SDSS all-SF',   'mass-complete'),
    (0.07, 4.9,  'SDSS all-SF',   'mass-complete'),
    (0.09, 4.6,  'SDSS all-SF',   'mass-complete'),
    (1.5,  100,  'MOSDEF',        'mass-complete-ish'),
    (2.3,  200,  'MOSDEF',        'mass-complete-ish'),
    (3.4,  400,  'MOSDEF',        'mass-complete-ish'),
    (6.0,  1400, 'CEERS EELG',    'EXTREME tail, EW>5000A'),
    (9.0,  1400, 'CEERS EELG',    'EXTREME tail, EW>5000A'),
]

def l_from_z(z):
    return np.log(1+z)/np.log(4)

print("=" * 78)
print("關鍵：分離「固有結構趨勢」vs「選樣效應」")
print("=" * 78)

print(f"\n{'數據':<20s} {'z':>6s} {'ℓ':>7s} {'EW':>8s} {'選樣':>30s}")
print("-" * 78)
for z, ew, src, sel in data:
    print(f"{src:<20s} {z:>6.2f} {l_from_z(z):>7.2f} {ew:>6.0f} {sel:>30s}")

print("""
============================================================
核心論點：'單調上升'係咪真？定係選樣假象？
============================================================

1. SDSS（mass-complete, z=0.01-0.1）:
   EW 由 6.3 微跌到 4.6（喺 ℓ=0.007→0.062）
   → 本地質量完備樣本：EW 幾乎冇 z 趨勢，甚至略跌

2. MOSDEF（z=1.5-3.4）:
   EW ~100→400 Å，比 SDSS 高 20-80x
   但 MOSDEF 有固定質量下限，未真正 mass-complete

3. CEERS EELG（z=4-9, mean EW=1400Å）:
   → 呢個係「極端尾樣本」！選樣條件 EW_obs > 5000 Å
   → 只包含宇宙最極端嘅發射線星系
   → 1400 Å 係尾部分佈嘅 mean，唔係全部星系嘅 mean

============================================================
所以「EW 隨 z 上升 100x」其中幾多係真相，幾多係選樣？
============================================================

假設 IDCM 框架（z=結構座標，宇宙無年齡+有周期）：
  - 如果 EW 係結構 gradient，mass-complete 樣本應該全程平滑上升
  - 但 SDSS mass-complete 顯示：本地 EW 幾乎唔郁（6.3→4.6）
  - MOSDEF 冇真正 mass-complete（有質量下限偏見）
  - CEERS 係極端尾 (EW>5000Å)，肯定唔係 mass-complete

結論：
  「EW 隨 z 上升 100x」嘅主要driver = 高 z 只見到極端 EELG（選樣）
  + 恆星質量下限偏見（高 z 只見到光/重星系）
  ≠ 星系本身喺結構上更年輕

============================================================
對「無年齡+有周期」嘅真正檢驗
============================================================

要證明/否証「周期」+「無年齡」，需要：
  1. mass-complete 樣本（唔可以有 EW/質量下限偏見）
  2. 覆蓋多個 SYNC cycle 嘅反應物 pattern
  3. 睇有冇「回落」（周期）vs 一路升（單調 gradient）

現有數據：
  - SDSS 本地係 mass-complete，但只覆蓋 ℓ=0→0.062 (3%)
  - MOSDEF/CEERS 高 z 有選樣偏見，唔算 mass-complete
  → 冇任何樣本同時滿足 mass-complete + 跨周期

所以：現有數據唔足以判死「無年齡+有周期」。
唯一堅實結論 = SDSS 本地 mass-complete 顯示 EW 冇強 z 趨勢。
""")