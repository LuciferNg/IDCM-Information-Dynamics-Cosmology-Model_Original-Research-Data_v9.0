#!/usr/bin/env python3
"""
全面驗證 — 本 session 所有推導的數值正確性
"""
import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
N_d = 44
c = 0.3066
t_site = R_H / (N_d * c) / 1000
const = 0.290229

def V(C):
    return C**2/2 - math.log(abs(C+1)) + const

def S_WKB():
    N = 20000
    S = 0.0
    for i in range(N+1):
        C = 0 + i * PHI_INV / N
        v = V(C)
        if v < 0: v = 0
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S += w * math.sqrt(2 * v) if v > 0 else 0
    return S * PHI_INV / (3 * N)

errors = []

def check(name, val, expected, tol=0.05):
    if expected == 0:
        if abs(val) < tol:
            print(f"  ✅ {name}: {val:.6e} ≈ 0")
            return True
        else:
            errors.append(f"❌ {name}: {val:.6e} ≠ 0")
            return False
    elif abs(val/expected - 1) > tol:
        errors.append(f"❌ {name}: {val:.6e} ≠ {expected:.6e} (diff {abs(val/expected-1)*100:.1f}%)")
        return False
    else:
        print(f"  ✅ {name}: {val:.6e} = {expected:.6e}")
        return True

print("=" * 80)
print("  全面數值驗證")
print("=" * 80)

# 1. 基本常數
print(f"\n  ── 1. 基本常數 ──")
check("φ", PHI, 1.6180339887)
check("φ⁻¹", PHI_INV, 0.6180339887)
check("ε", PHI_INV/4, 0.1545084972)
check("κ", 1/16, 0.0625)
check("N_d", N_d, 44)
check("R_H", R_H, 4129.94)
check("λ_sync", LAMBDA_SYNC, 294.88)

# 2. 時間尺度
print(f"\n  ── 2. 時間尺度 ──")
check("t_site = R_H/(44c)", t_site, 0.3061)
t_round = N_d * t_site
check("t_round = 44×t_site", t_round, 13.47)
T_SYNC = 88 * t_site
check("T_SYNC = 88×t_site", T_SYNC, 26.94)
T_1 = LAMBDA_SYNC / c / 1000
check("T_1 = λ_sync/c", T_1, 0.962)

# 3. K_Chain 本徵值
print(f"\n  ── 3. K_Chain 本徵值 ──")
total_energy = sum(4*math.sin(math.pi*n/88)**2 for n in range(1,44))
check("Σ γ_n = 86", total_energy, 86, 0.01)
check("γ_1 = 4 sin²(π/88)", 4*math.sin(math.pi/88)**2, 0.005096, 0.01)
check("γ_22 = 2", 4*math.sin(math.pi*22/88)**2, 2.0, 0.01)
check("γ_44 = 4", 4*math.sin(math.pi*44/88)**2, 4.0, 0.01)

# 4. WKB 穿隧
print(f"\n  ── 4. WKB 穿隧 ──")
S = S_WKB()
check("S_single = ∫√(2V)dC", S, 0.2312, 0.01)
check("2S_single", 2*S, 0.4624, 0.01)

# 5. 44-site 模型
print(f"\n  ── 5. 44-site 模型 ──")
check("44-site uniform: 2S", 44*2*S, 20.34, 0.01)
t_uniform = t_site * math.exp(44 * 2 * S)
check("44-site uniform: t_cycle", t_uniform, 2.09e8, 0.1)

# 平均梯度
avg_gam = sum(4*math.sin(math.pi*n/88)**2 for n in range(1,44)) / 43
check("⟨γ⟩ = 2.0", avg_gam, 2.0, 0.01)

S_avg = 0.0
N = 10000
for i in range(N+1):
    C = 0 + i * PHI_INV / N
    v_eff = V(C) + 0.5 * avg_gam * (C - PHI_INV)**2
    if v_eff < 0: v_eff = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S_avg += w * math.sqrt(2 * v_eff) if v_eff > 0 else 0
S_avg *= PHI_INV / (3 * N)

check("S_avg (平均梯度)", S_avg, 0.3555, 0.01)
check("44×2S_avg", 44*2*S_avg, 31.29, 0.01)
t_avg = t_site * math.exp(44 * 2 * S_avg)
check("t_cycle (avg gradient)", t_avg, 1.18e13, 0.1)

# 6. 勢能
print(f"\n  ── 6. 勢能 V(C) ──")
check("V(φ⁻¹) = 0", V(PHI_INV), 0, 0.01)
check("V(0) = 0.290", V(0), 0.2902, 0.01)
check("V(-φ) = 2.080", V(-PHI), 2.0805, 0.01)

# 7. Gaussian fluctuation
print(f"\n  ── 7. Gaussian fluctuation ──")
P_single = math.exp(-1.618**2 / (2 * 1/16))
check("P_single = exp(-20.94)", P_single, 8.2e-10, 0.1)
P_44 = 44 * P_single
t_gauss = 26.94 / P_44
check("t_gauss = 7.5e8 Gyr", t_gauss, 7.5e8, 0.2)

# 8. 44 × 4^ℓ × t_site
print(f"\n  ── 8. 44 × 4^ℓ × t_site ──")
for ell, expected in [(22, 2.37e14), (23, 9.48e14), (24, 3.79e15)]:
    t = N_d * (4**ell) * t_site
    check(f"ℓ={ell}: 44×4^{ell}×t_site", t, expected, 0.1)

# 9. 總結
print(f"\n{'─'*80}")
if errors:
    print(f"\n  ❌ 發現 {len(errors)} 個錯誤:")
    for e in errors:
        print(f"  {e}")
else:
    print(f"\n  ✅ 所有數值驗證通過，無幻覺")
print(f"")