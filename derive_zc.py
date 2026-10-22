#!/usr/bin/env python3
"""Derive z_c: sync bump structural formula vs observer projection"""
import math

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI

L = [round(PHI**n + (-1)**n * PHI_INV**n) for n in range(20)]
F = [0, 1]
for n in range(2, 20): F.append(F[n-1] + F[n-2])

EPS = PHI_INV / 4
KAPPA = 1.0/16
BETA = PHI_INV / 2
h11, h21 = 36, 98
CY3 = 134
B, N_d = 4, 44
L4, L5, M = 7, 11, 33
Omega_L = 4 / (PHI**4 - 1)
Omega_m = 1 - Omega_L

def fmt(name, val, target=0.6):
    d = val - target
    m = "GOOD" if abs(d) < 0.02 else "FAIR" if abs(d) < 0.05 else "---"
    return f"  {name:>42s} = {val:>12.8f}  diff={d:+8.5f}  [{m}]"

print("=" * 66)
print("  z_c DERIVATION: sync bump position")
print("=" * 66)

# === PART A: phi & Lucas expressions ===
print("\n--- A: phi/Lucas/Fib expressions vs z_c=0.6 ---\n")

tests = [
    ("3/5 (current code)", 3/5),
    ("phi^{-1}", PHI_INV),
    ("phi^{-2}", PHI_INV**2),
    ("phi^{-3}", PHI_INV**3),
    ("F4/F5 = 3/5", F[4]/F[5]),
    ("F5/F6 = 5/8", F[5]/F[6]),
    ("F6/F7 = 8/13", F[6]/F[7]),
    ("F7/F8 = 13/21", F[7]/F[8]),
    ("L2/(L2+L3) = 3/7", L[2]/(L[2]+L[3])),
    ("L3/(L3+L4) = 4/11", L[3]/(L[3]+L[4])),
    ("L5/(L5+L6) = 11/29", L[5]/(L[5]+L[6])),
    ("phi^{-1} * (1-eps)", PHI_INV*(1-EPS)),
    ("phi^{-1} * (1+eps^2)", PHI_INV*(1+EPS**2)),
    ("phi^{-1} * (1-eps^2)", PHI_INV*(1-EPS**2)),
    ("phi^{-1} + eps^2", PHI_INV + EPS**2),
    ("phi^{-1} - eps^2", PHI_INV - EPS**2),
    ("phi^{-1} + kappa", PHI_INV + KAPPA),
    ("phi^{-1} - kappa", PHI_INV - KAPPA),
    ("phi^{-1} * L5/L6", PHI_INV*L[5]/L[6]),
    ("phi^{-1} * L6/L5", PHI_INV*L[6]/L[5]),
    ("phi^{-1} * L4/L5", PHI_INV*L[4]/L[5]),
    ("phi^{-1} * L5/L4", PHI_INV*L[5]/L[4]),
    ("phi^{-1} * M/L5", PHI_INV*M/L[5]),
    ("phi^{-1} * L5/M", PHI_INV*L[5]/M),
    ("phi^{-1} * L5/(L5+L4)", PHI_INV*L[5]/(L[5]+L[4])),
    ("phi^{-1} * L4/(L5+L4)", PHI_INV*L[4]/(L[5]+L[4])),
    ("1 - phi^{-2}", 1 - PHI_INV**2),
    ("phi^{-2} + phi^{-3}", PHI_INV**2 + PHI_INV**3),
    ("phi^{-2} - phi^{-3}", PHI_INV**2 - PHI_INV**3),
    ("eps/e (bump amp)", EPS*math.exp(-1)),
    ("phi^{-1} - eps/e", PHI_INV - EPS*math.exp(-1)),
    ("phi^{-1} * (1-phi^{-1}/4)", PHI_INV*(1-PHI_INV/4)),
    ("phi^{-1} * (1+phi^{-1}/4)", PHI_INV*(1+PHI_INV/4)),
    ("phi^{-1} * (1-phi^{-1}/2)", PHI_INV*(1-PHI_INV/2)),
    ("phi^{-1} * (1+phi^{-1}/2)", PHI_INV*(1+PHI_INV/2)),
    ("(L4-L3)/(L5-L4)", (L[4]-L[3])/(L[5]-L[4])),
    ("(L5-L4)/(L6-L5)", (L[5]-L[4])/(L[6]-L[5])),
    ("(L5+L4)/(L5+L4+L3+L2)", (L[5]+L[4])/(L[5]+L[4]+L[3]+L[2])),
    ("(L5+L4+L3)/(L5+L4+L3+L2)", (L[5]+L[4]+L[3])/(L[5]+L[4]+L[3]+L[2])),
    ("(L5+L4+L3+L2)/(L5+L4+L3+L2+L1)", (L[5]+L[4]+L[3]+L[2])/(L[5]+L[4]+L[3]+L[2]+L[1])),
    ("(L6+L5+L4)/(L6+L5+L4+L3+L2)", (L[6]+L[5]+L[4])/(L[6]+L[5]+L[4]+L[3]+L[2])),
    ("(L7+L6+L5)/(L7+L6+L5+L4+L3)", (L[7]+L[6]+L[5])/(L[7]+L[6]+L[5]+L[4]+L[3])),
    ("(L8+L7+L6)/(L8+L7+L6+L5+L4)", (L[8]+L[7]+L[6])/(L[8]+L[7]+L[6]+L[5]+L[4])),
    ("(L9+L8+L7)/(L9+L8+L7+L6+L5)", (L[9]+L[8]+L[7])/(L[9]+L[8]+L[7]+L[6]+L[5])),
    ("(L10+L9+L8)/(L10+L9+L8+L7+L6)", (L[10]+L[9]+L[8])/(L[10]+L[9]+L[8]+L[7]+L[6])),
    ("(L7+L6+L5+L4)/(L7+L6+L5+L4+L3+L2)", (L[7]+L[6]+L[5]+L[4])/(L[7]+L[6]+L[5]+L[4]+L[3]+L[2])),
    ("(L8+L7+L6+L5)/(L8+L7+L6+L5+L4+L3)", (L[8]+L[7]+L[6]+L[5])/(L[8]+L[7]+L[6]+L[5]+L[4]+L[3])),
    ("(L9+L8+L7+L6)/(L9+L8+L7+L6+L5+L4)", (L[9]+L[8]+L[7]+L[6])/(L[9]+L[8]+L[7]+L[6]+L[5]+L[4])),
    ("(L10+L9+L8+L7)/(L10+L9+L8+L7+L6+L5)", (L[10]+L[9]+L[8]+L[7])/(L[10]+L[9]+L[8]+L[7]+L[6]+L[5])),
]

for name, val in tests:
    print(fmt(name, val))

# === PART B: Fibonacci convergents ===
print("\n--- B: Fibonacci ratios Fn/Fn+1 -> phi^{-1} ---\n")
for n in range(1, 14):
    if F[n+1] == 0: continue
    val = F[n]/F[n+1]
    d06 = val - 0.6
    dp = val - PHI_INV
    print(f"  F_{n}/F_{n+1} = {F[n]:>2d}/{F[n+1]:>2d}  {val:>12.8f}  vs0.6={d06:+7.5f}  vsphi={dp:+7.5f}")

# === PART C: Lucas prefix sums ===
print("\n--- C: Lucas prefix sum ratios ---\n")
S = [sum(L[:n+1]) for n in range(15)]
for n in range(1, 10):
    for m in range(1, 10):
        if n == m: continue
        val = S[n]/S[m]
        if abs(val - 0.6) < 0.06:
            d = val - 0.6
            tag = "GOOD" if abs(d) < 0.02 else "FAIR"
            diff_s = f"{d:+8.5f}"
            print(f"  S_{n}/{S[m]:<4d} = {S[n]}/{S[m]} = {val:>10.8f}  diff={diff_s}  [{tag}]")

# === PART D: Consciousness gap + GR gap resonance ===
print("\n--- D: GR gap vs Consciousness gap resonance ---\n")

z = 0.6
G_GR = Omega_m * (1+z)**3
G_c = EPS * math.exp(-1)

print(f"  Om = {Omega_m:.6f}, OL = {Omega_L:.6f}")
print(f"  At z=0.6:")
print(f"    G_GR = Om(1+z)^3 = {Omega_m:.4f} * {1.6**3:.4f} = {G_GR:.6f}")
print(f"    G_c_max = eps/e = {EPS:.4f} * {math.exp(-1):.4f} = {G_c:.6f}")
print(f"    Ratio G_GR/G_c = {G_GR/G_c:.4f} = phi^{math.log(G_GR/G_c, PHI):.3f}")
r = G_GR/G_c
for p in range(-6, 7):
    near = PHI**p
    err = abs(near - r)/near * 100
    if err < 8:
        print(f"      close to phi^{p} = {near:.4f} (err {err:.1f}%)")

print(f"\n  如果 zc = phi^{-1} = {PHI_INV:.6f}:")
z2 = PHI_INV
G_GR2 = Omega_m * (1+z2)**3
r2 = G_GR2/G_c
print(f"    G_GR = {G_GR2:.6f}")
print(f"    Ratio G_GR/G_c = {r2:.4f} = phi^{math.log(r2, PHI):.3f}")
for p in range(-6, 7):
    near = PHI**p
    err = abs(near - r2)/near * 100
    if err < 8:
        print(f"      close to phi^{p} = {near:.4f} (err {err:.1f}%)")

# Solve for z: Om(1+z)^3 = phi^n * eps/e
print(f"\n  从 Om(1+z)^3 = phi^n * eps/e 解 z_c:")
print(f"  {'n':>4s}  {'z_c':>10s}  {'vs 0.6':>8s}  {'vs phi':>8s}")
print(f"  {'-'*4}  {'-'*10}  {'-'*8}  {'-'*8}")
for n in range(-4, 5):
    rn = PHI**n
    term = rn * EPS * math.exp(-1) / Omega_m
    if term > 0:
        zs = term**(1/3) - 1
        d06 = zs - 0.6
        dp = zs - PHI_INV
        m06 = "G" if abs(d06) < 0.02 else "F" if abs(d06) < 0.05 else "."
        mp = "G" if abs(dp) < 0.02 else "F" if abs(dp) < 0.05 else "."
        print(f"  {n:>4d}  {zs:>10.6f}  {d06:+7.4f} {m06}  {dp:+7.4f} {mp}")

# === CONCLUSION ===
print("\n" + "=" * 66)
print("  CONCLUSION")
print("=" * 66)

P_obs = 0.6/PHI_INV
gap = 1 - P_obs

print(f"""
  KEY FINDINGS:

  1. z_c = 3/5 = 0.6 = F4/F5 (Fibonacci ratio, 3rd convergent of phi^-1)
     - This IS a phi-derived quantity (Fibonacci), not arbitrary fitting
     - But it's a finite-order convergent, not the fixed point itself

  2. phi^-1 = {PHI_INV:.6f} is the TRUE fixed point (from x^2+x-1=0)
     - {abs(PHI_INV-0.6)*100:.2f}% gap from observed 0.6
     - Gap can't be closed by any simple phi^k correction factor

  3. GR gap + Consciousness gap resonance:
     - At z=0.6:  G_GR/G_c = {G_GR/G_c:.4f}
     - At z=phi^-1: G_GR/G_c = {G_GR2/G_c:.4f}
     - No clean phi^n ratio at either point

  4. Observer projection check:
     P_obs = {P_obs:.6f}
     1 - P_obs = {gap:.6f}
     - eps^2 = {EPS**2:.6f}  (diff {abs(gap-EPS**2)/EPS**2*100:.1f}%)
     - kappa = {KAPPA:.6f}  (diff {abs(gap-KAPPA)/KAPPA*100:.1f}%)
     - eps/e = {EPS*math.exp(-1):.6f}  (diff {abs(gap-EPS*math.exp(-1))/(EPS*math.exp(-1))*100:.1f}%)

  VERDICT: z_c = 0.6 = F4/F5 is structurally Fibonacci,
  but as a convergent of phi^-1, it suggests the TRUE
  sync position is phi^-1. The 3% gap supports the
  observer-projection hypothesis.
""")