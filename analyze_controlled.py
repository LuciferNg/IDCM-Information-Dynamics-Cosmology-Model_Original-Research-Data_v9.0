#!/usr/bin/env python3
"""
SDSS 控制變數測試結果分析：固定質量+金屬量後，EW(Hβ) vs z 斜率 vs ΛCDM sSFR 預測
"""
import json
import numpy as np

with open('/home/wsl/IDCM/sdss_controlled_results.json') as f:
    data = json.load(f)

results = data['results']
print(f"Total bins: {len(results)}")

# For each (mass, OH) pair with both z bins, compute the EW ratio
print("\n=== EW(Hβ) 高z/低z 比率（固定質量+金屬量）===")
print(f"{'質量':>8s} {'金屬量':>8s} {'n_low':>6s} {'n_high':>6s} {'EW_low':>8s} {'EW_high':>8s} {'比率':>6s}")
print("-" * 55)

ratios = []
for r in results:
    if r['z_lo'] < 0.01:  # low-z bin
        low = r
        # find matching high-z bin
        for r2 in results:
            if (r2['mass_lo'] == r['mass_lo'] and r2['mass_hi'] == r['mass_hi'] and
                r2['oh_lo'] == r['oh_lo'] and r2['oh_hi'] == r['oh_hi'] and
                r2['z_lo'] > 0.03):
                ratio = r2['ew_med'] / r['ew_med']
                ratios.append((r['mass_lo'], r['mass_hi'], r['oh_lo'], r['oh_hi'],
                               r['n'], r2['n'], r['ew_med'], r2['ew_med'], ratio))
                print(f"{r['mass_lo']:.1f}-{r['mass_hi']:.1f} {r['oh_lo']:.1f}-{r['oh_hi']:.1f} "
                      f"{r['n']:6d} {r2['n']:6d} {r['ew_med']:7.1f} {r2['ew_med']:7.1f} {ratio:5.2f}x")

if ratios:
    rs = [x[8] for x in ratios]
    print(f"\nMean ratio: {np.mean(rs):.2f}x ± {np.std(rs):.2f}")

# ΛCDM sSFR prediction: sSFR ∝ (1+z)^2.5 (Madau-Dickinson-like)
# z_low ~ 0.025, z_high ~ 0.075
z_low, z_high = 0.025, 0.075
ssfr_ratio = ((1 + z_high) / (1 + z_low)) ** 2.5
age_low = 13.35  # Gyr at z=0.025 (ΛCDM)
age_high = 12.85  # Gyr at z=0.075
print(f"\n=== ΛCDM 預測 ===")
print(f"sSFR ratio (z=0.075 vs z=0.025): {ssfr_ratio:.2f}x")
print(f"Age ratio: {age_high/age_low:.3f} (only {100*(1-age_high/age_low):.1f}% younger)")

print(f"""
=== 關鍵對比 ===
觀測到嘅 EW(Hβ) 平均比率: {np.mean(rs):.2f}x (固定質量+金屬量)
ΛCDM sSFR 預測比率:        {ssfr_ratio:.2f}x
ΛCDM 年齡比率:            {age_high/age_low:.2f}x

結論：
1. SDSS 本地 (z<0.1) 已經見到固定質量+金屬量下 EW 隨 z 上升
2. 觀測斜率 ({np.mean(rs):.2f}x) 比 ΛCDM sSFR 預測 ({ssfr_ratio:.2f}x) 更陡
3. 但要注意：SDSS 高 z bin 有選樣效應（更亮、更大質量嘅星系更容易被選入光譜樣本）
   → 呢個選樣偏差會人為增加高 z EW
4. 真正比較需要 MOSDEF (z=1.5-3.4) 同 JADES (z>5) 數據
""")