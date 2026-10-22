#!/usr/bin/env python3
"""
71_derived_quantities.py — 從結構公式推導衍生宇宙學量
======================================================
基於零自由參數結構公式：
  DM(ℓ) = (44-44/4^ℓ) × (R_H/44) × (1+2φ⁻¹×ℓ)
  DH(z) = R_H × (1 + δ_k0(ℓ)) / (1+z)

推導：H_eff(z), D_A(z), D_L(z), μ(z), w_eff(z), Ω_m(z)
"""
import math
import json

# ═══════════════════════════════════════════════════════════════
# 1. 結構常數（全部來自 φ 代數，零自由參數）
# ═══════════════════════════════════════════════════════════════
PHI = (1 + 5**0.5) / 2
PHI_INV = PHI - 1
PHI_3 = PHI_INV ** 3       # φ⁻³ = √5-2 = 0.236068
H0 = 72.59                  # km/s/Mpc
C = 299792.458              # km/s
R_H = C / H0                # 4129.94 Mpc
BAO_RD = 147.44             # λ_sync/2 Mpc
ELL_0 = math.log(2) / math.log(4)              # 0.5
SIGMA = 0.5 * math.log(PHI) / math.log(4)      # 0.173560

SEP = "─" * 75

# ═══════════════════════════════════════════════════════════════
# 2. 核心函數
# ═══════════════════════════════════════════════════════════════
def ell(z):
    """ℓ = log₄(1+z) — 結構座標"""
    if z < 0: return 0
    return math.log(1+z) / math.log(4)

def delta_k0(l):
    """DOS 共振包絡"""
    d = l - ELL_0
    return PHI_3 * math.exp(-d**2 / (2 * SIGMA**2))

def DM(z):
    """橫向距離（Formula 60）"""
    l = ell(z)
    P = 1 + 2 * PHI_INV * l
    n = 44 * (1 - 4**(-l))
    return n * (R_H / 44) * P

def DH(z):
    """徑向距離（新結構公式）"""
    return R_H * (1 + delta_k0(ell(z))) / (1+z)

# ═══════════════════════════════════════════════════════════════
# 3. 衍生量
# ═══════════════════════════════════════════════════════════════
def H_eff(z):
    """有效膨脹率 H_eff(z) = c/DH(z)"""
    return C / DH(z)

def D_A(z):
    """Angular diameter distance: D_A = DM/(1+z)"""
    return DM(z) / (1+z)

def D_L(z):
    """Luminosity distance: D_L = DM×(1+z)"""
    return DM(z) * (1+z)

def mu(z):
    """Distance modulus: μ = 5log₁₀(D_L/10pc)"""
    DL_mpc = D_L(z)
    DL_pc = DL_mpc * 1e6
    return 5 * math.log10(DL_pc / 10)

def w_eff(z):
    """有效暗能量狀態方程 (從 H(z) 定義)"""
    l = ell(z)
    dk = delta_k0(l)
    dk_prime = -dk * (l - ELL_0) / SIGMA**2  # dδ_k0/dℓ
    dldz = 1 / ((1+z) * math.log(4))          # dℓ/dz
    dk_dz = dk_prime * dldz                   # dδ_k0/dz
    
    # w_eff = -1/3 - (2/3)(1+z)·δ_k0'/(1+δ_k0)
    we = -1/3 - (2/3) * (1+z) * dk_dz / (1+dk)
    return we

def omega_m_eff(z):
    """有效物質密度參數 (從 H(z) 定義)"""
    OMEGA_M0 = 0.316718  # IDCM 結構值
    return OMEGA_M0 * (1+z)**3 * (H0 / H_eff(z))**2

# ═══════════════════════════════════════════════════════════════
# 4. 輸出表格
# ═══════════════════════════════════════════════════════════════
print("=" * 75)
print("  71: Derived Cosmological Quantities from IDCM Structural Formulas")
print("  Zero free parameters — all from φ algebra")
print("=" * 75)

print(f"\n  H₀ = {H0} km/s/Mpc, R_H = {R_H:.2f} Mpc, rd = {BAO_RD} Mpc")
print(f"  ℓ₀ = {ELL_0:.6f}, σ_φ = {SIGMA:.6f}, φ⁻³ = {PHI_3:.6f}")
print(f"\n  {SEP}")

# ── 4a. H_eff(z) 表 ──
print(f"\n  {SEP}")
print("  Table 1: H_eff(z) and derived quantities")
print(f"  {SEP}")
print(f"  {'z':>5s} {'ℓ':>7s} {'H_eff':>8s} {'D_A':>8s} {'D_L':>8s} {'μ':>7s} {'w_eff':>8s} {'Ω_m_eff':>8s}")
print(f"  {'':>5s} {'':>7s} {'(km/s)':>8s} {'(Mpc)':>8s} {'(Mpc)':>8s} {'(mag)':>8s} {'':>8s} {'':>8s}")
print(f"  {'─'*58}")

# ΛCDM 參考值（flat ΛCDM, H₀=67.4, Ω_m=0.315）
def h_lcdm(z):
    return 67.4 * math.sqrt(0.315*(1+z)**3 + 0.685)

for z in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.93, 1.0, 1.3, 1.5, 2.0, 2.33, 3.0, 5.0]:
    if z == 0: z = 1e-6
    he = H_eff(z)
    da = D_A(z)
    dl = D_L(z)
    mu_z = mu(z)
    we = w_eff(z)
    ome = omega_m_eff(z)
    print(f"  {z:>5.3f} {ell(z):>7.4f} {he:>8.2f} {da:>8.0f} {dl:>8.0f} {mu_z:>7.2f} {we:>+8.4f} {ome:>8.4f}")

# ── 4b. DESI 對比 ──
print(f"\n  {SEP}")
print("  Table 2: DESI DR1 BAO Comparison (DM/rd, DH/rd)")
print(f"  {SEP}")
desi_data = [
    (0.510, 13.62, 0.25, 20.98, 0.61),
    (0.706, 16.85, 0.32, 20.08, 0.60),
    (0.930, 21.71, 0.28, 17.88, 0.35),
    (1.317, 27.79, 0.69, 13.82, 0.42),
    (2.330, 39.71, 0.94, 8.52, 0.17),
]
print(f"  {'z':>5s} {'DM/rd':>7s} {'DESI_DM':>8s} {'Δ/σ':>6s} {'DH/rd':>7s} {'DESI_DH':>8s} {'Δ/σ':>6s}")
print(f"  {'─'*47}")
chi2_dm, chi2_dh = 0, 0
for z, dm_rd, edm, dh_rd, edh in desi_data:
    dm_idcm = DM(z) / BAO_RD
    dh_idcm = DH(z) / BAO_RD
    chi2_dm += ((dm_idcm - dm_rd) / edm)**2
    chi2_dh += ((dh_idcm - dh_rd) / edh)**2
    print(f"  {z:>5.3f} {dm_idcm:>7.4f} {dm_rd:>8.2f} {(dm_idcm-dm_rd)/edm:+>+5.2f} {dh_idcm:>7.4f} {dh_rd:>8.2f} {(dh_idcm-dh_rd)/edh:+>+5.2f}")
print(f"\n  DM/rd χ² = {chi2_dm:.1f} (5 dof)")
print(f"  DH/rd χ² = {chi2_dh:.1f} (5 dof)")
print(f"  Joint χ² = {chi2_dm+chi2_dh:.1f} (10 dof)")

# ── 4c. w_eff(z) 行為 ──
print(f"\n  {SEP}")
print("  Table 3: w_eff(z) — effective dark energy equation of state")
print(f"  {SEP}")
print(f"  {'z':>5s} {'ℓ':>7s} {'δ_k0':>8s} {'δ_k0_p':>8s} {'w_eff':>8s} {'H_eff':>8s} {'H_LCDM':>8s}")
print(f"  {'─'*52}")
for z in [0.0, 0.1, 0.3, 0.5, 0.7, 0.93, 1.0, 1.3, 1.5, 2.0, 2.33, 3.0, 5.0, 10.0]:
    if z == 0: z = 1e-6
    l = ell(z)
    dk = delta_k0(l)
    dk_prime = -dk * (l - ELL_0) / SIGMA**2
    we = w_eff(z)
    he = H_eff(z)
    hl = h_lcdm(z)
    print(f"  {z:>5.3f} {l:>7.4f} {dk:>8.6f} {dk_prime:>+8.6f} {we:>+8.4f} {he:>8.2f} {hl:>8.2f}")

# ── 4d. 距離模數（Pantheon+ 預測） ──
print(f"\n  {SEP}")
print("  Table 4: Distance modulus μ(z) for SNe Ia comparison")
print(f"  {SEP}")
print(f"  {'z':>5s} {'D_A':>10s} {'D_L':>10s} {'μ':>8s}")
print(f"  {'─'*33}")
for z in [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.3, 1.5, 2.0, 2.33]:
    da = D_A(z); dl = D_L(z); mu_z = mu(z)
    print(f"  {z:>5.3f} {da:>10.1f} {dl:>10.1f} {mu_z:>8.3f}")

# ═══════════════════════════════════════════════════════════════
# 5. 儲存結果
# ═══════════════════════════════════════════════════════════════
results = {
    'constants': {
        'H0': H0, 'R_H': R_H, 'BAO_RD': BAO_RD,
        'ell_0': ELL_0, 'sigma': SIGMA, 'phi_3': PHI_3
    },
    'desi_chi2': {
        'dm': chi2_dm, 'dh': chi2_dh, 'joint': chi2_dm+chi2_dh, 'dof': 10
    }
}
with open('71_derived_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n  {SEP}")
print(f"  Results saved: 71_derived_results.json")
print(f"  {SEP}")