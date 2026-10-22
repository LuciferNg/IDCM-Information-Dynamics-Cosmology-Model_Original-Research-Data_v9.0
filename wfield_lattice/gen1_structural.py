#!/usr/bin/env python3
"""第一代拓撲結構 — Fibonacci × CY₃^s × ε³ 自交修正"""
import math, sys

PHI = (1 + math.sqrt(5))/2
PHI_INV = 1/PHI
EPS = PHI_INV / 4
CY3 = 134
h11, h21 = 36, 98

L = [round(PHI**n + (-1)**n * PHI**(-n)) for n in range(15)]

# Fibonacci numbers from K_chain mode indices
F = [0, 1]
for n in range(2, 15):
    F.append(F[n-1] + F[n-2])
# F[5]=5, F[8]=21, F[9]=34

# 1st gen structural formula: ratio = F_n / CY₃^s × (1 + ε³ × K_n)
# K_n = K_chain self-intersection coefficient from mode n × h¹¹/h²¹

s_values = {"electron": 2, "down": 2, "up": 3}
F_values = {"electron": F[5], "down": F[8], "up": F[9]}
k_modes = {"electron": 5, "down": 8, "up": 9}

# K_n = mode × (h¹¹/h²¹) × φ^(-s) — structural, not fitted
def K_n(mode, s):
    return mode * (h11/h21) * PHI_INV ** s

eps3 = EPS ** 3

print("=" * 60)
print("第一代拓撲結構 — Fibonacci × CY₃^s × (1 + ε³ × K)")
print("=" * 60)
print(f"  CY₃ = {CY3}, ε³ = {eps3:.6f}")
print(f"  h¹¹/h²¹ = {h11}/{h21} = {h11/h21:.4f}")
print()

PDG_ratios = {
    "electron": 0.51099895 / 1.77686,  # m_e/m_tau
    "down": 0.00467 / 4.18,             # m_d/m_b  
    "up": 0.00216 / 172.76,             # m_u/m_t
}

passing, failing = 0, 0
for name in ["electron", "down", "up"]:
    Fn = F_values[name]
    s = s_values[name]
    mode = k_modes[name]
    obs = PDG_ratios[name]
    
    # Base: F_n / CY₃^s
    base = Fn / (CY3 ** s)
    
    # K_n structural coefficient
    K = K_n(mode, s)
    
    # Full: base × (1 + ε³ × K)
    pred = base * (1 + eps3 * K)
    
    err = abs(pred / obs - 1) * 100
    ok = err < 10
    if ok: passing += 1
    else: failing += 1
    
    print(f"  {'✅' if ok else '❌'} {name:>8}:")
    print(f"     F_{mode}={Fn} / CY₃^{s} = {base:.10f}")
    print(f"     K(mode={mode}, s={s}) = {K:.4f}")
    print(f"     × (1 + ε³ × K) = × {1 + eps3 * K:.6f}")
    print(f"     = {pred:.10f} (obs {obs:.10f}, {err:.2f}%)")
    print()

print(f" 結果: {passing}/{passing+failing}")
print("=" * 60)"""