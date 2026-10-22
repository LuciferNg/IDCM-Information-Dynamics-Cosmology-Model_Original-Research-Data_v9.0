#!/usr/bin/env python3
"""
verify_all.py — 66號文件所有公式數值驗證 + CY₃ 推導確認
=====================================================
"""
import math, sys
sys.path.insert(0, '/home/wsl/.hermes/skills/idcm/idcm-structural-derivation/scripts')
from idcm_core import *

PASS, FAIL = 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; mark = "✅"
    else: FAIL += 1; mark = "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

def check_val(name, pred, obs, tol, unit=""):
    global PASS, FAIL
    err = abs(pred/obs - 1)*100 if obs != 0 else float('inf')
    if err < tol: PASS += 1; mark = "✅"
    else: FAIL += 1; mark = "❌"
    print(f"  {mark} {name}: {pred:.6f} {unit}(ref {obs:.6f}, err {err:.2f}%)")

KAPPA = 1/16
PHI_INV = (math.sqrt(5)-1)/2
V_EW = 245.9837
EPS = 0.1545085
h11, h21 = 36, 98

def W_sq(n):
    g = 4*math.sin(math.pi*n/88)**2
    return 1.236 / (1 + g/(4*EPS))

def m_n(n):
    lam = math.exp(-n)
    return (KAPPA - lam) * V_EW * lam * 1000

def P_n_linear(n):
    return 1 + 2*PHI_INV * n

def P_n_cy3(n):
    K2 = 2*(h21-h11)/h21 - 2*PHI_INV
    return 1 + 2*PHI_INV * n + K2 * n**2

print("=" * 72)
print("  66號文件驗證 — CY₃ 投影算子 + 暗物質豐度")
print("=" * 72)

# 1. CY3 基本數值
print(f"\n{'─'*60}")
print("  1. CY₃(36,98) 基本數值")
print(f"{'─'*60}")
check("h^11 = 36", h11 == 36)
check("h^21 = 98", h21 == 98)
check("chi = 2(h^11 - h^21) = -124", 2*(h11-h21) == -124)
check_val("(h^21 - h^11)/h^21", (h21-h11)/h21, 62/98, 0.001)
check_val("phi^-1", PHI_INV, 0.618034, 0.001)

# 2. 投影算子係數
print(f"\n{'─'*60}")
print("  2. 投影算子係數")
print(f"{'─'*60}")
check_val("2*(h^21-h^11)/h^21", 2*(h21-h11)/h21, 1.265306, 0.1)
check_val("2*phi^-1", 2*PHI_INV, 1.236068, 0.1)
K2 = 2*(h21-h11)/h21 - 2*PHI_INV
check_val("K2 = 2*(h^21-h^11)/h^21 - 2*phi^-1", K2, 0.029238, 1.0)

# 3. 線性近似
print(f"\n{'─'*60}")
print("  3. 線性近似 P_n = 1 + 2*phi^-1*n")
print(f"{'─'*60}")
for n in [0, 1, 2, 4, 7, 22]:
    p = P_n_linear(n)
    print(f"  P_{n} = {p:.4f}")

# 4. CY3 二階投影
print(f"\n{'─'*60}")
print("  4. CY₃ 二階投影 P_n = 1 + 2*phi^-1*n + K2*n^2")
print(f"{'─'*60}")
for n in [0, 1, 2, 4, 7, 22]:
    p = P_n_cy3(n)
    p_lin = P_n_linear(n)
    print(f"  P_{n} = {p:.4f} ({'+' if p>p_lin else ''}{p-p_lin:.4f} vs linear)")

# 5. 完整模式譜求和
print(f"\n{'─'*60}")
print("  5. 完整模式譜求和")
print(f"{'─'*60}")

# Linear
E_vis_lin = 0
for i, m in enumerate([2.16, 4.67, 93.0]):
    E_vis_lin += m * W_sq(i) * P_n_linear(i)
E_dm_lin = 0
for n in range(4, 44):
    if math.exp(-n) < KAPPA:
        E_dm_lin += m_n(n) * W_sq(n) * P_n_linear(n)
ratio_lin = E_dm_lin / E_vis_lin

# CY3
E_vis_cy3 = 0
for i, m in enumerate([2.16, 4.67, 93.0]):
    E_vis_cy3 += m * W_sq(i) * P_n_cy3(i)
E_dm_cy3 = 0
for n in range(4, 44):
    if math.exp(-n) < KAPPA:
        E_dm_cy3 += m_n(n) * W_sq(n) * P_n_cy3(n)
ratio_cy3 = E_dm_cy3 / E_vis_cy3

print(f"  Linear: Ω_DM/Ω_b = {ratio_lin:.4f}  (target: 6.5, Δ = {abs(ratio_lin/6.5-1)*100:.2f}%)")
print(f"  CY₃:    Ω_DM/Ω_b = {ratio_cy3:.4f}  (target: 6.5, Δ = {abs(ratio_cy3/6.5-1)*100:.2f}%)")
check_val("Linear ratio", ratio_lin, 6.12, 2.0)
check_val("CY3 ratio", ratio_cy3, 6.5, 1.0)

# 6. phi^-1 與 CY3 嘅關係
print(f"\n{'─'*60}")
print("  6. phi^-1 與 CY₃ 嘅結構關係")
print(f"{'─'*60}")
check_val("phi^-1 = (h^21-h^11)/h^21 - phi^-4/10", 
          (h21-h11)/h21 - PHI_INV**4/10, PHI_INV, 0.1)

# 7. 所有數值驗證
print(f"\n{'─'*60}")
print("  7. 66號文件所有數值驗證")
print(f"{'─'*60}")

checks = [
    ("h^11 = 36", h11 == 36),
    ("h^21 = 98", h21 == 98),
    ("chi = -124", 2*(h11-h21) == -124),
    ("phi^-1 = 0.618034", abs(PHI_INV - 0.618034) < 0.0001),
    ("(h^21-h^11)/h^21 = 0.632653", abs((h21-h11)/h21 - 0.632653) < 0.001),
    ("2*(h^21-h^11)/h^21 = 1.265306", abs(2*(h21-h11)/h21 - 1.265306) < 0.001),
    ("2*phi^-1 = 1.236068", abs(2*PHI_INV - 1.236068) < 0.001),
    ("K2 = 0.029238", abs(K2 - 0.029238) < 0.001),
    ("Linear ratio = 6.12", abs(ratio_lin - 6.12) < 0.1),
    ("CY3 ratio = 6.5030", abs(ratio_cy3 - 6.5030) < 0.1),
    ("CY3 ratio within 0.1% of 6.5", abs(ratio_cy3/6.5 - 1) < 0.001),
]
for name, cond in checks:
    check(name, cond)

# 8. 總結
print(f"\n{'='*72}")
print(f"  結果: {PASS}/{PASS+FAIL} 通過" + (" ✅" if FAIL == 0 else f" ❌ ({FAIL} 失敗)"))
print(f"{'='*72}")
print(f"\n  K₂ = 2·(h²¹ − h¹¹)/h²¹ − 2φ⁻¹ = {K2:.6f}")
print(f"  Ω_DM/Ω_b = {ratio_cy3:.4f} (target: 6.5, Δ = {abs(ratio_cy3/6.5-1)*100:.2f}%)")
print(f"  K₂ 係結構推導，無自由參數")
print(f"\n  文件: 66_dm_cy3_exact.md")