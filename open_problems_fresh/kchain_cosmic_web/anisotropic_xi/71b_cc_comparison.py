#!/usr/bin/env python3
"""
71b_cc_comparison.py — H_eff(z) vs Cosmic Chronometer 數據
===========================================================
比較 IDCM 結構公式 H_eff(z) 同 CC H(z) 觀測數據。

CC H(z) 數據來源：Moresco (2016), Moresco et al. (2012),
Zhang et al. (2014), Stern et al. (2010), Ratsimbazafy et al. (2017)
"""
import math
import json

# ═══════════════════════════════════════════════════════════════
# 1. IDCM 結構公式
# ═══════════════════════════════════════════════════════════════
PHI = (1 + 5**0.5) / 2
PHI_INV = PHI - 1
PHI_3 = PHI_INV ** 3
H0 = 72.59
C = 299792.458
R_H = C / H0
ELL_0 = math.log(2) / math.log(4)
SIGMA = 0.5 * math.log(PHI) / math.log(4)

def ell(z): return math.log(1+z) / math.log(4)
def delta_k0(l): d=l-ELL_0; return PHI_3*math.exp(-d**2/(2*SIGMA**2))
def DH(z): return R_H * (1+delta_k0(ell(z))) / (1+z)
def H_eff(z): return C / DH(z)

# ═══════════════════════════════════════════════════════════════
# 2. CC H(z) 數據（Moresco 2016 compilation + 補充）
# ═══════════════════════════════════════════════════════════════
# 格式：(z, H, σ_H, ref)
cc_data = [
    # Moresco et al. (2012) — 11 points
    (0.090, 69.0, 12.0, "M12"),
    (0.170, 83.0, 8.0, "M12"),
    (0.270, 77.0, 14.0, "M12"),
    (0.280, 88.8, 36.6, "M12"),
    (0.400, 95.0, 17.0, "M12"),
    (0.480, 97.0, 62.0, "M12"),
    (0.570, 92.0, 23.0, "M12"),
    (0.593, 104.0, 13.0, "M12"),
    (0.680, 92.0, 8.0, "M12"),
    (0.730, 97.0, 12.0, "M12"),
    (0.781, 105.0, 12.0, "M12"),
    (0.875, 125.0, 17.0, "M12"),
    # Stern et al. (2010)
    (0.880, 90.0, 40.0, "S10"),
    # Zhang et al. (2014) — 10 points
    (0.179, 75.0, 4.0, "Z14"),
    (0.199, 75.0, 5.0, "Z14"),
    (0.352, 83.0, 14.0, "Z14"),
    (0.592, 104.0, 13.0, "Z14"),
    (0.680, 92.0, 8.0, "Z14"),
    (0.875, 125.0, 17.0, "Z14"),
    (1.037, 154.0, 20.0, "Z14"),
    (1.363, 160.0, 33.6, "Z14"),
    (1.965, 186.5, 50.4, "Z14"),
    # Moresco (2015) — 5 points
    (1.530, 140.0, 14.0, "M15"),
    (1.750, 202.0, 40.0, "M15"),
    (1.965, 186.5, 50.4, "M15"),
    # Ratsimbazafy et al. (2017)
    (0.470, 89.0, 34.0, "R17"),
    # Moresco (2016) — additional
    (0.070, 69.0, 19.6, "M16"),
    (0.120, 68.6, 26.2, "M16"),
    (0.200, 72.9, 29.6, "M16"),
    (0.900, 117.0, 23.0, "M16"),
    (1.260, 134.0, 17.0, "M16"),
    (1.480, 159.0, 24.0, "M16"),
    (1.430, 177.0, 18.0, "M16"),
    (1.530, 140.0, 14.0, "M16"),
    (1.750, 202.0, 40.0, "M16"),
    # Anderson et al. (2014) — BAO-derived H(z)
    (0.320, 79.2, 2.3, "A14"),
    (0.570, 92.4, 4.5, "A14"),
    (0.600, 87.1, 6.4, "A14"),
    (0.730, 80.3, 4.9, "A14"),
    (2.340, 222.0, 7.0, "A14"),
]

# 去重：保留每個 z 的最後一個點
seen = {}
for z, h, sig, ref in cc_data:
    seen[z] = (z, h, sig, ref)
cc_unique = sorted(seen.values(), key=lambda x: x[0])

# ═══════════════════════════════════════════════════════════════
# 3. 比較
# ═══════════════════════════════════════════════════════════════
print("=" * 75)
print("  71b: H_eff(z) vs Cosmic Chronometer Data")
print("=" * 75)

chi2, n = 0, 0
print(f"\n  {'z':>5s} {'H_obs':>7s} {'σ':>6s} {'H_IDCM':>8s} {'Δ/σ':>6s} {'ref':>5s}")
print(f"  {'─'*37}")
for z, h_obs, sig, ref in cc_unique:
    h_idcm = H_eff(z)
    if sig > 0:
        d_sig = (h_idcm - h_obs) / sig
        chi2 += d_sig**2
        n += 1
    else:
        d_sig = 0
    print(f"  {z:>5.3f} {h_obs:>7.1f} {sig:>6.1f} {h_idcm:>8.2f} {d_sig:>+6.2f} {ref:>5s}")

print(f"\n  χ² = {chi2:.1f} ({n} dof)")
print(f"  χ²/dof = {chi2/max(n-1,1):.2f}")

# 按紅移分段
print(f"\n  ─── 分段分析 ───")
for zmin, zmax, label in [(0, 0.5, "z<0.5"), (0.5, 1.0, "0.5<z<1.0"), (1.0, 2.0, "1.0<z<2.0"), (2.0, 10, "z>2.0")]:
    chi2_seg, n_seg = 0, 0
    for z, h_obs, sig, ref in cc_unique:
        if zmin <= z < zmax and sig > 0:
            d_sig = (H_eff(z) - h_obs) / sig
            chi2_seg += d_sig**2
            n_seg += 1
    if n_seg > 0:
        print(f"  {label}: χ²={chi2_seg:.1f} ({n_seg} pts)")

# ═══════════════════════════════════════════════════════════════
# 4. 儲存
# ═══════════════════════════════════════════════════════════════
results = {'chi2_cc': chi2, 'n_cc': n, 'chi2dof': chi2/max(n-1, 1)}
with open('71b_cc_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved: 71b_cc_results.json")