#!/usr/bin/env python3
"""
53_gw_standard_siren.py — P2: GW Standard Siren 純時空驗證
============================================================
用引力波標準燭光（GW170817 及已知事件）測試落錨 ζ(z) 算子。

引力波直接喺時空晶格傳遞（strain），無電磁波污染
（無 IGM 吸收、無重子阻抗、無連續譜擬合）。

測試：
1. GW170817: z=0.0099, D_L=43.8±2.9 Mpc
   IDCM 預測 D_L(z) 用落錨 ζ(z) H(z)
2. H₀ 一致性: GW 測量 70.3±5.3 vs IDCM 72.59
3. 對比 baseline (無 ζ) vs 落錨 ζ
"""
import math
import numpy as np
import sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import H_z, hz_zeta, H0_IDCM

C_LIGHT = 299792.458  # km/s
print("=" * 80)
print("  P2: GW Standard Siren — 引力波純時空驗證")
print("=" * 80)

# ================================================================
# 1. 已知 GW 事件（Bright Sirens / 有紅移）
# ================================================================
# GW170817: BNS, host NGC 4993, z=0.0099
# D_L = 43.8 ± 2.9 Mpc (Abbott et al. 2017)
# H₀ from GW170817 = 70.0 +12.0/-8.0 (initial) → 70.3 ± 5.3 (Hotokezaka 2019)
gw_events = [
    {
        'name': 'GW170817',
        'z': 0.0099,
        'DL': 43.8,
        'DL_err': 2.9,
        'type': 'BNS + EM counterpart',
        'H0_meas': 70.3,
        'H0_err': 5.3,
        'note': '唯一有電磁對應體嘅 bright siren'
    },
]

print(f"\n  載入 {len(gw_events)} 個 GW 事件")

# ================================================================
# 2. IDCM 預測 D_L(z)
# ================================================================
def dL_idcm(z):
    """Luminosity distance from IDCM H(z) with anchored ζ(z)"""
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / H_z(zp)
    Dc = C_LIGHT * integral  # comoving distance Mpc
    return (1 + z) * Dc  # luminosity distance

def dL_baseline(z):
    """Baseline: IDCM H(z) WITHOUT ζ correction"""
    eps = (math.sqrt(5) - 1) / 2 / 4
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        theta = math.tanh(zp / 2)
        alpha = 1 + math.log(1 - 2 * eps * theta) / math.log(4)
        h = H0_IDCM * (1 + zp) ** alpha
        integral += dz / h
    return (1 + z) * C_LIGHT * integral

# 對比 ΛCDM
def dL_lcdm(z, H0=67.4, Om=0.315):
    N = 500
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        h = H0 * math.sqrt(Om * (1+zp)**3 + (1-Om))
        integral += dz / h
    return (1 + z) * C_LIGHT * integral

print(f"\n{'─'*80}")
print("  2. D_L(z) 預測對比")
print(f"{'─'*80}")

for ev in gw_events:
    z = ev['z']
    dl_idcm = dL_idcm(z)
    dl_base = dL_baseline(z)
    dl_lcdm = dL_lcdm(z)
    dl_obs = ev['DL']
    dl_err = ev['DL_err']
    
    sigma_idcm = (dl_obs - dl_idcm) / dl_err
    sigma_base = (dl_obs - dl_base) / dl_err
    sigma_lcdm = (dl_obs - dl_lcdm) / dl_err
    
    print(f"\n  {ev['name']} ({ev['type']})")
    print(f"    z = {z:.4f}")
    print(f"    觀測 D_L = {dl_obs:.1f} ± {dl_err:.1f} Mpc")
    print(f"    IDCM(ζ)  D_L = {dl_idcm:.1f} Mpc  Δ/σ = {sigma_idcm:+.2f}")
    print(f"    IDCM(base) D_L = {dl_base:.1f} Mpc  Δ/σ = {sigma_base:+.2f}")
    print(f"    ΛCDM     D_L = {dl_lcdm:.1f} Mpc  Δ/σ = {sigma_lcdm:+.2f}")

# ================================================================
# 3. H₀ 一致性
# ================================================================
print(f"\n{'─'*80}")
print("  3. H₀ 一致性")
print(f"{'─'*80}")

for ev in gw_events:
    z = ev['z']
    # 低 z 近似: D_L ≈ c·z/H₀ → H₀ ≈ c·z/D_L
    # 用 IDCM D_L 反推 H₀
    dl_idcm = dL_idcm(z)
    H0_from_DL = C_LIGHT * z / dl_idcm  # 近似
    # 精確: D_L = (1+z)·c·∫dz/H → 喺低 z, H₀ ≈ c·z·(1+z)/D_L
    H0_exact = C_LIGHT * z * (1 + z) / dl_idcm
    
    print(f"\n  {ev['name']}:")
    print(f"    GW 測量 H₀ = {ev['H0_meas']} ± {ev['H0_err']}")
    print(f"    IDCM H₀(結構) = {H0_IDCM:.2f}")
    print(f"    從 IDCM D_L 反推 H₀ ≈ {H0_exact:.1f}")
    print(f"    IDCM vs GW: Δ/σ = {(ev['H0_meas'] - H0_IDCM) / ev['H0_err']:.2f}")
    print(f"    一致性: {'✅ 1σ 內' if abs(ev['H0_meas'] - H0_IDCM) < ev['H0_err'] else '⚠️ 超出 1σ'}")

# ================================================================
# 4. 未來預測（2026+ 事件）
# ================================================================
print(f"\n{'─'*80}")
print("  4. 未來 bright siren 預測")
print(f"{'─'*80}")

print(f"\n  IDCM D_L(z) 預測表（用嚟預測未來 GW 事件）:")
print(f"  {'z':<8} {'D_L (Mpc)':<12} {'μ (mag)':<12}")
for z in [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
    dl = dL_idcm(z)
    mu = 5 * math.log10(dl * 1e6) - 5
    print(f"  {z:<8.3f} {dl:<12.1f} {mu:<12.3f}")

# ================================================================
# 5. 儲存
# ================================================================
results = []
for ev in gw_events:
    z = ev['z']
    results.append({
        'name': ev['name'],
        'z': z,
        'DL_obs': ev['DL'], 'DL_err': ev['DL_err'],
        'DL_idcm': dL_idcm(z),
        'DL_baseline': dL_baseline(z),
        'DL_lcdm': dL_lcdm(z),
        'sigma_idcm': (ev['DL'] - dL_idcm(z)) / ev['DL_err'],
        'H0_idcm': H0_IDCM,
        'H0_gw': ev['H0_meas'], 'H0_gw_err': ev['H0_err'],
    })

import json
with open('/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web/anisotropic_xi/53_gw_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  結果: 53_gw_results.json")
print(f"{'='*80}")