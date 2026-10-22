#!/usr/bin/env python3
"""CY₃ 拓撲算子驗證 — D_lattice 一階 + 二階 (1+ε)
===============================================
One-to-many test: m_b AND m_s simultaneously.
"""
import math, sys

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI
L = [round(PHI**n + (-1)**n * PHI**(-n)) for n in range(15)]
EPS = PHI_INV / 4
KAPPA = 1 / 16
CY3 = 134; h11, h21 = 36, 98; M = 33

# D_lattice operators
D_lep = 1.0
D1 = 1 + h11/h21 * EPS               # 一階
D2 = 1 + h11/h21 * EPS * (1 + EPS)   # 二階 (自能級數)

# VEV and scale
VEV_nat = math.sqrt(EPS / (2 * KAPPA))
V_EW = PHI**8 * (PHI**3 + 1)
SCALE = V_EW / VEV_nat

k_u = M * PHI_INV / 2
k_d = (M - L[4]) * PHI_INV / 2 - PHI_INV ** 4
k_l = (M - 2 * L[4]) * PHI_INV / 2

m_t_nat = VEV_nat / math.sqrt(2)
m_t = m_t_nat * SCALE
delta = PHI**88 / 2.435e18 - 1
m_tau_nat = m_t_nat * delta
m_tau = m_tau_nat * SCALE
m_b_bare = m_t_nat * PHI_INV ** k_d * SCALE

PDG = {"top":172.76,"charm":1.27,"up":0.00216,
       "bottom":4.18,"strange":0.093,"down":0.00467,
       "tau":1.77686,"muon":0.10566,"electron":0.000511}

passing, failing = 0, 0
def check(name, val, pdg_val, tol_pct, note=""):
    global passing, failing
    err = abs(val/pdg_val - 1)*100
    ok = err < tol_pct
    if ok: passing += 1
    else: failing += 1
    mark = "✅" if ok else "❌"
    print(f"  {mark} {name}: {val:.6f} (PDG {pdg_val}, {err:.2f}%) {note}")
    return ok

print("=" * 60)
print("CY₃ 拓撲算子 D_lattice 驗證")
print(f"D1 = 1 + 36/98 × ε        = {D1:.8f}")
print(f"D2 = 1 + 36/98 × ε × (1+ε)= {D2:.8f}")
print("=" * 60)

print(f"\n--- 一階測試 (D1) ---")
m_b_1 = m_b_bare * D1
m_s_1 = m_b_bare * PHI_INV ** k_d * D1
check("m_b (D1)", m_b_1, PDG["bottom"], 5, f"→ {m_b_1:.4f}")
check("m_s (D1)", m_s_1, PDG["strange"], 5, f"→ {m_s_1:.4f}")

print(f"\n--- 二階測試 (D2 = D1 × (1+ε)) ---")
m_b_2 = m_b_bare * D2
m_s_2 = m_b_bare * PHI_INV ** k_d * D2
check("m_b (D2)", m_b_2, PDG["bottom"], 5, f"→ {m_b_2:.4f}")
check("m_s (D2)", m_s_2, PDG["strange"], 5, f"→ {m_s_2:.4f}")

print(f"\n--- One-to-Many ---")
for name, D, bare_err_b, corr_err_b, bare_err_s, corr_err_s in [
    ("D1", D1, 6.54, abs(m_b_1/PDG["bottom"]-1)*100, 5.69, abs(m_s_1/PDG["strange"]-1)*100),
    ("D2", D2, 6.54, abs(m_b_2/PDG["bottom"]-1)*100, 5.69, abs(m_s_2/PDG["strange"]-1)*100),
]:
    ok = corr_err_b < bare_err_b and corr_err_s < bare_err_s
    if ok: passing += 1
    else: failing += 1
    print(f"  {'✅' if ok else '❌'} {name}: m_b {bare_err_b:.1f}%→{corr_err_b:.1f}%, "
          f"m_s {bare_err_s:.1f}%→{corr_err_s:.1f}%")

print(f"\n{'=' * 60}")
print(f"結果: {passing}/{passing+failing} ✅" if failing == 0 else
      f"結果: {passing}/{passing+failing} ({failing} failure{'s' if failing > 1 else ''})")
print(f"{'=' * 60}")
sys.exit(0 if failing == 0 else 1)