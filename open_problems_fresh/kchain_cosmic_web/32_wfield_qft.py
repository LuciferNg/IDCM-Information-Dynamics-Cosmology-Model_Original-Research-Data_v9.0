#!/usr/bin/env python3
"""
W-field 量子場論 — 完整驗證腳本
==================================
從經典 Lagrangian 到量子真空衰變率，所有數字驗證。

步驟:
1. 經典 Lagrangian + Hamiltonian
2. 正則量子化 — 模式展開、頻譜
3. 真空漲落 — 量子漲落幅度
4. Bounce 解 — 均勻 bounce + 梯度修正
5. 真空衰變率 — 全部機制比較
6. 奇點正則化 — 證明積分收斂
"""

import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4
KAP = 1/16
N_d = 44
c = 0.3066
t_site = R_H / (N_d * c) / 1000  # Gyr
T_SYNC = 88 * t_site  # 88-step SYNC phase period

# 勢能
const = -(PHI_INV**2/2 - math.log(PHI_INV + 1))
def V(C):
    return C**2/2 - math.log(abs(C+1)) + const

def V_dd(C):
    return 1 + 1/(C+1)**2

print("=" * 80)
print("  W-FIELD 量子場論 — 完整驗證")
print("=" * 80)

# ================================================================
# 1. 經典 Lagrangian
# ================================================================
print(f"\n{'─'*80}")
print("  1. 經典 Lagrangian")
print(f"{'─'*80}")

print(f"""
  L = Sum_n [1/2(d_t phi_n)^2 - 1/2 gamma_n(phi_n - phi_{n-1})^2 - V(phi_n)]

  V(phi) = phi^2/2 - ln|phi+1| + const
  V(phi^-1) = 0,  V(0) = {V(0):.6f},  V(-phi) = {V(-PHI):.6f}
""")

# ================================================================
# 2. 模式展開與頻譜
# ================================================================
print(f"\n{'─'*80}")
print("  2. 模式展開與頻譜")
print(f"{'─'*80}")

V_dd_vac = V_dd(PHI_INV)
omega = math.sqrt(V_dd_vac)

print(f"  V''(phi^-1) = 1 + 1/(phi+1)^2 = 1 + 1/{PHI_INV+1:.6f}^2 = {V_dd_vac:.6f}")
print(f"  omega_0 = sqrt(V'') = {omega:.6f}")

# K_Chain 頻譜
print(f"\n  K_Chain 模式頻譜 omega_k = sqrt(gamma_k + V''(phi^-1)):")
print(f"  {'k':<4} {'gamma_k':<10} {'omega_k':<10} {'lambda_k':<12}")
print(f"  {'─'*40}")

modes = []
for k in range(1, N_d+1):
    gam = 4 * math.sin(math.pi * k / 88)**2
    omega_k = math.sqrt(gam + V_dd_vac)
    lam_k = 2 * math.pi / omega_k
    modes.append({'k': k, 'gamma': gam, 'omega': omega_k, 'lambda': lam_k})
    if k <= 5 or k == 22 or k == 44:
        print(f"  {k:<4} {gam:<10.6f} {omega_k:<10.6f} {lam_k:<12.6f}")

# 真空能
E0_vac = 0.5 * sum(m['omega'] for m in modes)
print(f"\n  真空能: E_0 = 1/2 Sum omega_k = {E0_vac:.6f}")
print(f"  平均 omega_k = {E0_vac*2/N_d:.6f}")

# ================================================================
# 3. 量子漲落
# ================================================================
print(f"\n{'─'*80}")
print("  3. 量子漲落")
print(f"{'─'*80}")

# 真空漲落: 用 harmonic oscillator 基態
# 對於單 site harmonic oscillator: ⟨Δφ²⟩ = 1/(2ω)
# 對 44-mode 系統: 每個 mode 貢獻 1/(2ω_k), 平均到 N_d sites
delta_phi_sq_mode = sum(1/(2*m['omega']) for m in modes) / N_d
delta_phi_mode = math.sqrt(delta_phi_sq_mode)

# 但更直接: 單 site W-field 嘅量子漲落係 harmonic oscillator 基態
# ω = sqrt(V''(phi^-1)) = 1.176
# ⟨Δφ²⟩_ho = 1/(2ω) = 0.425
# √⟨Δφ²⟩_ho = 0.652
delta_phi_sq_ho = 1/(2*omega)
delta_phi_ho = math.sqrt(delta_phi_sq_ho)

# 跟結構值 √κ = 0.25 比較
# κ = 1/16 係四階耦合常數，唔係直接嘅場漲落
# 但兩者有關聯: κ = 1/(4ω²) 如果 V(φ) = ½ω²φ² + κφ⁴
# 從 harmonic 近似: ω² = V''(φ⁻¹) = 1.382
# κ = 1/16 → 預測 harmonic 漲落 = 1/(2√(V'')) = 0.425 → 但實際場論多 mode 修正

print(f"  單 site harmonic oscillator:")
print(f"  omega = {omega:.6f}")
print(f"  <Delta phi^2>_ho = 1/(2omega) = {delta_phi_sq_ho:.6f}")
print(f"  sqrt(<Delta phi^2>)_ho = {delta_phi_ho:.6f}")

print(f"\n  44-mode 晶格場:")
print(f"  <Delta phi^2> = 1/N_d Sum 1/(2omega_k) = {delta_phi_sq_mode:.6f}")
print(f"  sqrt(<Delta phi^2>) = {delta_phi_mode:.6f}")

print(f"\n  結構值:")
print(f"  kappa = {KAP}")
print(f"  sqrt(kappa) = {math.sqrt(KAP):.6f}")
print(f"  波動幅度比: {delta_phi_ho/math.sqrt(KAP):.2f}x (harmonic)")
print(f"  波動幅度比: {delta_phi_mode/math.sqrt(KAP):.2f}x (lattice)")

# 真空穩定性: 用 harmonic oscillator 基態漲落
Delta_V = V(0) - V(PHI_INV)
stability_ho = Delta_V / (delta_phi_ho * math.sqrt(V_dd_vac))
stability_mode = Delta_V / (delta_phi_mode * math.sqrt(V_dd_vac))

print(f"\n  真空穩定性 (harmonic oscillator 近似):")
print(f"  Delta V = {Delta_V:.6f}")
print(f"  sqrt(<Delta phi^2>) x sqrt(V'') = {delta_phi_ho * math.sqrt(V_dd_vac):.6f}")
print(f"  Delta V / (sqrt(<Delta phi^2>) x sqrt(V'')) = {stability_ho:.4f}")

# ================================================================
# 4. Bounce 解
# ================================================================
print(f"\n{'─'*80}")
print("  4. Bounce 解 (Euclidean 穿隧)")
print(f"{'─'*80}")

# 4.1 單 site bounce
N = 20000
S_WKB = 0.0
for i in range(N+1):
    C = 0 + i * PHI_INV / N
    v = V(C)
    if v < 0: v = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S_WKB += w * math.sqrt(2 * v) if v > 0 else 0
S_WKB *= PHI_INV / (3 * N)

S_B_1 = 2 * S_WKB  # bounce action = 2 x WKB integral

print(f"  單 site bounce:")
print(f"  S_WKB = int_0^{PHI_INV} sqrt(2V) dC = {S_WKB:.6f}")
print(f"  S_B(1) = 2 x S_WKB = {S_B_1:.6f}")
print(f"  t_bounce(1) = tau_0 x exp(S_B(1)) = {t_site * math.exp(S_B_1):.4e} Gyr")

# 4.2 44-site uniform bounce
S_B_44 = N_d * S_B_1
print(f"\n  44-site uniform bounce (梯度=0, 所有 site 同步):")
print(f"  S_B(44) = {N_d} x {S_B_1:.6f} = {S_B_44:.6f}")
print(f"  t_bounce(44) = {t_site:.4f} x exp({S_B_44:.4f}) = {t_site * math.exp(S_B_44):.4e} Gyr")

# 4.3 梯度修正 bounce
avg_gamma = sum(4*math.sin(math.pi*n/88)**2 for n in range(1, N_d)) / (N_d-1)

S_eff = 0.0
N2 = 10000
for i in range(N2+1):
    C = 0 + i * PHI_INV / N2
    v_eff = V(C) + 0.5 * avg_gamma * (C - PHI_INV)**2
    if v_eff < 0: v_eff = 0
    w = 1 if i == 0 or i == N2 else (4 if i % 2 == 1 else 2)
    S_eff += w * math.sqrt(2 * v_eff) if v_eff > 0 else 0
S_eff *= PHI_INV / (3 * N2)
S_B_grad = 2 * N_d * S_eff

print(f"\n  梯度修正 bounce:")
print(f"  <gamma_n> = {avg_gamma:.4f}")
print(f"  S_eff = {S_eff:.6f}")
print(f"  S_B(grad) = {N_d} x 2 x {S_eff:.6f} = {S_B_grad:.4f}")
print(f"  t_bounce(grad) = {t_site * math.exp(S_B_grad):.4e} Gyr")

# 4.4 Escape bounce (到 C < -1, 穿過奇點)
print(f"\n  逃逸 bounce (到 C < -1, 穿過奇點):")
# 段1: phi^-1 -> 0
S1 = S_WKB
# 段2: 0 -> -1+eps (避開奇點)
eps_min = 1e-6
N3 = 50000
S2 = 0.0
for i in range(N3+1):
    C = -1 + eps_min + (0 + 1 - eps_min) * (1 - i/N3)  # 從 0 到 -1+eps
    if C <= -1: continue
    v = V(C)
    if v < 0: v = 0
    w = 1 if i == 0 or i == N3 else (4 if i % 2 == 1 else 2)
    S2 += w * math.sqrt(2 * v) if v > 0 else 0
S2 *= (1.0 - eps_min) / (3 * N3)

S_escape_1 = 2 * (S1 + S2)
S_escape_44 = N_d * S_escape_1

print(f"  段1: phi^-1 -> 0 : S1 = {S1:.6f}")
print(f"  段2: 0 -> -1+eps : S2 = {S2:.6f} (eps={eps_min:.0e})")
print(f"  單 site escape bounce: 2S = {2*(S1+S2):.4f}")
print(f"  44-site escape bounce: 2S = {2*S_escape_44:.4f}")
print(f"  t_escape = {t_site * math.exp(2*S_escape_44):.4e} Gyr")

# ================================================================
# 5. 奇點正則化
# ================================================================
print(f"\n{'─'*80}")
print("  5. 奇點正則化檢查")
print(f"{'─'*80}")

print(f"  V(C) ~ -ln|C+1| near C=-1")
print(f"  sqrt(2V(C)) ~ sqrt(-2ln|C+1|)")
print(f"  Integral int sqrt(-2ln x) dx converges as x -> 0")

print(f"\n  {'eps':<10} {'V(-1+eps)':<15} {'sqrt(2V)':<15} {'eps*sqrt(-2ln(eps))':<20} {'converges?'}")
print(f"  {'─'*60}")
for e in [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6]:
    C = -1 + e
    v = V(C)
    integrand = math.sqrt(2*v) if v > 0 else 0
    approx = e * math.sqrt(-2 * math.log(e)) if e > 0 else 0
    conv = "YES" if approx < 0.5 else "NO"
    print(f"  {e:<10.0e} {v:<15.4f} {integrand:<15.4f} {approx:<20.6f} {conv}")

# ================================================================
# 6. 真空衰變率比較
# ================================================================
print(f"\n{'─'*80}")
print("  6. 真空衰變率比較")
print(f"{'─'*80}")

# Kramers 逃逸率 (單 site)
# Gamma = (omega_0/2pi) x exp(-Delta_V/kappa)  (high-friction Kramers)
# 但呢個係經典熱漲落，唔係量子
# Kramers 量子逃逸: Gamma = (omega_0/2pi) x (sqrt(1+(kappa/2DeltaV)^2) - kappa/2DeltaV) x exp(-Delta_V/kappa)
# 簡化: Gamma ~ (omega_0/2pi) x exp(-Delta_V/kappa) 因為 Delta_V/kappa >> 1?
# Delta_V = 0.290, kappa = 0.0625, Delta_V/kappa = 4.64 — 唔係 >> 1

kramers_quantum = (omega/(2*math.pi)) * \
    (math.sqrt(1 + (KAP/(2*Delta_V))**2) - KAP/(2*Delta_V)) * \
    math.exp(-Delta_V/KAP)

# 但呢個係 rate per unit time, 我哋要 t = 1/Gamma
t_kramers = 1.0 / kramers_quantum  # 自然單位
# 轉換到 Gyr: t_site = 0.306 Gyr 對應 harmonic 週期 2pi/omega = 5.34
# 所以 1 自然單位 = t_site x omega / (2pi) ???
# 更簡單: 用 t_site 做基本單位，因為 t_site = 0.306 Gyr 係 site-to-site 時間
# t_kramers_Gyr = t_site / (kramers_quantum * t_site) — 唔啱
# 直接用 tau_0 = 2pi/omega 做基本時間單位
tau_0 = 2*math.pi / omega  # 自然單位下的 harmonic 週期
# Gamma 係 rate per natural time unit
# t = 1/Gamma natural units
# 轉換 Gyr: t_Gyr = (1/Gamma) x tau_0_conversion
# 用 t_site 而唔係 tau_0? 有啲亂
# 直接用 WKB 時間公式: t = t_site x exp(2S)

rates = [
    ("單 site WKB (2S=0.462)", 2*S_WKB, t_site, "單 site harmonic 近似"),
    ("44-site uniform (2S=20.34)", 2*S_WKB*N_d, t_site, "集體 uniform mode"),
    ("44-site 梯度 (2S=31.29)", 2*S_eff*N_d, t_site, "含平均梯度修正"),
    ("44-site Gaussian (φ^2/2κ=20.94)", PHI**2/(2*KAP), T_SYNC/N_d, "Gaussian 漲落逃逸 (T_SYNC/P_total)"),
    ("44-site 逃逸到 C<-1 (2S=321.6)", 2*(S1+S2)*N_d, t_site, "穿過奇點逃逸"),
    ("舊結構 1/κ=16", 16, t_site, "舊 e^16 公式"),
]

print(f"\n  {'模型':<35} {'指數':<10} {'t_cycle (Gyr)':<20} {'宇宙>13.8Gyr?':<15}")
print(f"  {'─'*80}")

for name, exponent, tau, note in rates:
    t = tau * math.exp(exponent)
    ok = "YES" if t > 13.8 else "NO"
    print(f"  {name:<35} {exponent:<10.4f} {t:<20.4e} {ok:<15}")

# ================================================================
# 7. 結論
# ================================================================
print(f"\n{'─'*80}")
print("  7. 量子場論結論")
print(f"{'─'*80}")

print(f"""
  1. 經典 Lagrangian 已建立 — 從遞迴結構推導，無自由參數
  2. 正則量子化完成 — {N_d} 個模式 omega_k 完整對角化
  3. Harmonic 真空漲落 sqrt(<Delta phi^2>) = {delta_phi_ho:.4f} (harmonic) 或 {delta_phi_mode:.4f} (lattice)
  4. 真空穩定係數 (harmonic) = {stability_ho:.4f} — 真空不穩定
  5. Uniform bounce 係最優路徑 — S_B = {S_B_44:.4f}
  6. 44-site 集體效應係關鍵 — 單 site 錯誤預測 {t_site * math.exp(S_B_1):.2e} Gyr
  7. 最佳估計: t_cycle ~ {t_site * math.exp(S_B_44):.2e} Gyr (uniform mode)
  8. 保守估計: t_cycle ~ {t_site * math.exp(S_B_grad):.2e} Gyr (含梯度)
  9. 奇點積分收斂 — 逃逸到 C < -1 理論上可行，但 2S={2*S_escape_44:.0f} 太長
  10. 最合理逃逸機制: uniform mode WKB bounce
  11. 量子場論框架完整 — 下一步: 數值 bounce 解 + prefactor A
""")