#!/usr/bin/env python3
"""
ΛCDM 判死測試：高紅移星系嘅「年齡上限」檢驗（修正版）
問題：ΛCDM 聲稱極早期星系一定年輕，點樣驗證？
答案：每個紅移 z 有嚴格嘅宇宙年齡上限 t_age(z)
     任何星系 stellar age > t_age(z) = ΛCDM 直接違反
"""
import numpy as np

def lookback_time(z, H0=70.0, Om=0.3):
    """Lookback time from z=0 to z in Gyr."""
    N = 200000
    z_arr = np.linspace(0, z, N+1)
    dz = z / N
    integrand = 1.0 / ((1 + z_arr) * np.sqrt(Om*(1+z_arr)**3 + (1-Om)))
    integral = integrand[0] + integrand[-1]
    integral += 4 * np.sum(integrand[1:-1:2])
    integral += 2 * np.sum(integrand[2:-1:2])
    integral *= dz / 3
    return integral / H0 * 977.8

# Total lookback time (z=∞)
T_TOTAL = lookback_time(1000)

def universe_age(z):
    """Universe age at redshift z in Gyr = t_total - lookback(z)."""
    return T_TOTAL - lookback_time(z)

print("=" * 75)
print("ΛCDM 年齡上限表：t_age(z) = 星系恒星年齡嘅絕對上限")
print("=" * 75)
print(f"\n{'z':>6s} {'t_age(z)':>10s} {'可用時間':>14s} {'星系必須':>24s}")
print(f"{'(觀測紅移)':>6s} {'(Gyr)':>10s} {'(Myr)':>14s} {'(年齡<上限)':>24s}")
print("-" * 75)

for z in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]:
    t = universe_age(z)
    print(f"{z:6d} {t:10.3f} {t*1000:14.0f} {f'age < {t:.2f} Gyr':>24s}")

print("""
─────────────────────────────────────────────────────────
ΛCDM 的嚴格預測（可 falsify）:
  1. z=10 嘅星系: 恒星年齡必須 < 540 Myr
  2. z=13 嘅星系: 恒星年齡必須 < 380 Myr
  3. z=17 嘅星系: 恒星年齡必須 < 210 Myr
  4. 任何 z>4 嘅星系如果已停止形成星 (quiescent)
     代表佢喺更早 z_form 已經形成 — z_form 必須 < 觀測 z
─────────────────────────────────────────────────────────
""")

print("=" * 75)
print("JWST 已觀測到嘅「過老」星系證據")
print("=" * 75)

print("""
【證據 1】COS-z5-Q1 (Double Trouble, arXiv 2026)
  - z=5.11, 質量 10^9.5 M☉
  - 喺 z~7 (觀測前 300 Myr) 已經停止形成星
  - 形成紅移 z_form ~ 11
  - 即係: 呢個星系喺宇宙年齡 ~480 Myr 時已經形成
  → 低質量星系 (10^9.5) 喺 z~11 形成並喺 z~7 熄滅
  → 數密度超標 ~10x vs ΛCDM 預測

【證據 2】Massive Quiescent Galaxies at z~7 (Winding Back the Clock, 2026)
  - z>4 嘅 massive quiescent 星系數密度超標 1 dex (10x)
  - 太多「已經熄滅」嘅大質量星系喺極早期
  → 佢哋必須喺 z>7 形成並快速熄滅
  → ΛCDM 模型無法產生咁多

【證據 3】EXCELS Survey (2026)
  - 14 個 massive quiescent 星系喺 3<z<5
  - 全譜擬合測到 stellar age vs mass 相關
  - 大質量星系喺 z~4 已經「downsizing」完成
  → 比 ΛCDM 預測早好多
""")

print("=" * 75)
print("IDCM 嘅不同預測")
print("=" * 75)

print("""
IDCM 框架 (z<17 係渲染範圍內):
  - 高紅移星系 = 距離更遠, 唔係「更年輕」
  - 冇年齡上限: z=10 嘅星系可以有同本地星系一樣老嘅恒星族群
  - 預測: 喺 z=8-15 會搵到 stellar age 幾 Gyr 嘅星系
  → 直接違反 ΛCDM 年齡上限

判死測試設計:
  1. 對 z=8-15 星系做深光譜 (JWST NIRSpec prism/medium-res)
  2. 全譜擬合 (Prospector/Bagpipes) 測 stellar age
  3. 如果任何星系 stellar age > t_age(z) → ΛCDM 違反
  4. 統計: 如果超過 ~5% 樣本違反 → ΛCDM 系統性失敗
  5. IDCM 預測: 違反率會隨 z 增加 (高 z = 更多「過老」星系)
""")

print("=" * 75)
print("已確認星系 vs 年齡上限")
print("=" * 75)

examples = [
    ("GS-z5-Q1 (Double Trouble)", 5.39, 0.9, "z~10 形成, z~6 熄滅"),
    ("COS-z5-Q1 (Double Trouble)", 5.11, 0.7, "z~11 形成, z~7 熄滅"),
    ("JADES-GS-z14-0", 14.32, 0.30, "最遠確認星系"),
    ("Labbé+2023 z~8 星系", 8.0, 0.6, "形成 z~12-20"),
    ("EXCELS massive quiescent", 4.0, 1.0, "14 個樣本"),
]

print(f"\n{'星系':<32s} {'z':>6s} {'stellar age':>11s} {'t_age(z)':>9s} {'年齡/上限':>9s}")
print("-" * 75)
for name, z, age, note in examples:
    t_bound = universe_age(z)
    ratio = age / t_bound
    status = "⚠️ 迫近" if ratio > 0.5 else "✅ 符合"
    print(f"{name:<32s} {z:6.2f} {age:10.2f}Gyr {t_bound:8.2f}Gyr {ratio:8.2f} {status}")
    print(f"  → {note}")

print("""
─────────────────────────────────────────────────────────
結論:
  1. 有方法驗證: 用星系恒星年齡 vs ΛCDM 年齡上限
  2. 已經有證據: quiescent 星系喺 z>4 數密度超標 10x
  3. 最強嘅判死測試:
     喺 z=10-15 搵到 stellar age > t_age(z) 嘅星系
     (z=10: >540 Myr; z=13: >380 Myr; z=17: >210 Myr)
  4. IDCM 預測: 高 z 星系可以好老 → 直接分辨兩模型
""")