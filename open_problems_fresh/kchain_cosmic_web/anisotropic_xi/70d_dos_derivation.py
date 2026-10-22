#!/usr/bin/env python3
"""
70d_dos_derivation.py — 從 K_Chain 44-site 本徵值譜直接推導 DOS
===============================================================
唔用高斯假定。從 Hamiltonian H = H_KTree ⊗ 1_44 + 1_Tree ⊗ H_KChain
計算自然態密度 DOS(ell)，然後睇佢自然湧現出咩形狀。
"""
import math
import numpy as np

PHI = (1 + 5**0.5)/2
PHI_INV = PHI - 1
N_D = 44
H0 = 72.59
C = 299792.458
R_H = C / H0
BAO_RD = 147.44

# ================================================================
# 1. K_Chain 本徵值譜
# ================================================================
gamma = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_D + 1)]

# ================================================================
# 2. K_Tree 本徵值譜
# ================================================================
L = 53/8  # K_Tree depth
M = 33    # K_Tree levels
mu = [PHI ** (L - m) for m in range(M + 1)]

# ================================================================
# 3. 自然投影節點 ell_n (從 phi^k 冪次)
# ================================================================
# 每個 K_Chain 模式 n 對應一個 phi^k 投影節點
# k 從 0 開始，n=1 對應 k=0, n=2 對應 k=-1, n=3 對應 k=-2, ...
# 或者：k = 1-n，即 n=1->k=0, n=2->k=-1, n=3->k=-2, ...
# 1+z_k = 1 + phi^k

def ell_from_k(k):
    """ell_k = log_4(1 + phi^k)"""
    return math.log(1 + PHI**k) / math.log(4) if k >= 0 else math.log(1 + PHI_INV**(-k)) / math.log(4)

# 法 1: k = 1-n (n=1->k=0, n=2->k=-1, ...)
ELL_N1 = [ell_from_k(1-n) for n in range(1, N_D + 1)]
# 法 2: k = 0..43 (n=1->k=0, n=44->k=43)
ELL_N2 = [ell_from_k(n-1) for n in range(1, N_D + 1)]

print("="*75)
print("  K_Chain 44-site DOS — 從本徵值譜直接計算")
print("="*75)

# 顯示幾種可能嘅 ell_n 映射
print(f"\n  ell_n 映射比較:")
print(f"  {'n':>4s} {'gamma_n':>10s} {'ell_n(gamma)':>14s} {'ell_n(k=1-n)':>14s} {'ell_n(k=n-1)':>14s}")
for n in [1, 2, 3, 4, 5, 7, 11, 14, 22, 28, 33, 44]:
    # 從 gamma_n 映射到 ell: ell = log_4(1/gamma_n) 或類似
    gamma_n = 4 * math.sin(math.pi * n / 88)**2
    # 如果 gamma_n = phi^(-L+ell_n) 即 ell_n = L + log_phi(gamma_n)
    if gamma_n > 0:
        ell_gamma = L + math.log(gamma_n) / math.log(PHI)
    else:
        ell_gamma = -999
    print(f"  {n:>4d} {gamma_n:>10.6f} {ell_gamma:>14.4f} {ELL_N1[n-1]:>14.4f} {ELL_N2[n-1]:>14.4f}")

# ================================================================
# 4. 自然 DOS: 從 spectral weight + Lorentzian 展寬
# ================================================================
# 用 gamma_n 作為 spectral weight，Lorentzian 展寬 gamma_lorentz
# DOS(ell) = sum_n gamma_n / pi * gamma_lorentz / ((ell-ell_n)^2 + gamma_lorentz^2)

def compute_dos(el_vals, ell_n, gamma_lorentz):
    """DOS from spectral weight x Lorentzian"""
    dos = np.zeros_like(el_vals)
    for n in range(N_D):
        gn = gamma[n]  # spectral weight = K_Chain eigenvalue
        d = el_vals - ell_n[n]
        lorentz = 1/math.pi * gamma_lorentz / (d**2 + gamma_lorentz**2)
        dos += gn * lorentz
    return dos / np.sum(gamma)  # normalize

# 測試幾種 ell_n 映射
el_grid = np.linspace(0, 2.5, 500)

for gamma_name, gamma_l in [('gamma=0.05', 0.05), ('gamma=0.1', 0.1), ('gamma=0.2', 0.2)]:
    print(f"\n{'─'*75}")
    print(f"  DOS 形狀 ({gamma_name})")
    print(f"{'─'*75}")
    
    for map_name, ell_n in [('k=1-n', ELL_N1), ('k=n-1', ELL_N2)]:
        dos = compute_dos(el_grid, ell_n, gamma_l)
        # 找峰值
        peak_idx = np.argmax(dos)
        peak_ell = el_grid[peak_idx]
        peak_val = dos[peak_idx]
        print(f"  {map_name:>10s}: peak at ell={peak_ell:.4f}, dos={peak_val:.6f}")

# ================================================================
# 5. 關鍵：從 gamma_n 自然推出 ell_n
# ================================================================
# K_Chain 模式 n 嘅能量 gamma_n 對應 K_Tree 層級 ell_n
# 當 gamma_n = mu(m) 時，能量匹配
# mu(m) = phi^(L-m) 對應 ell = m (K_Tree level)
# 所以 ell_n = m where mu(m) ≈ gamma_n
# m = L - log_phi(gamma_n)

print(f"\n{'─'*75}")
print(f"  從 gamma_n 自然映射到 ell_n")
print(f"{'─'*75}")
print(f"  ell_n = L - log_phi(gamma_n) = {L:.4f} - log_phi(gamma_n)")
print(f"  {'n':>4s} {'gamma_n':>10s} {'ell_n':>10s} {'1+z_n':>10s} {'z_n':>10s}")

ell_n_gamma = []
for n in range(1, N_D + 1):
    gn = gamma[n-1]
    if gn > 0:
        ell_n = L - math.log(gn) / math.log(PHI)
    else:
        ell_n = 999
    ell_n_gamma.append(ell_n)
    if n in [1, 2, 3, 4, 5, 7, 11, 14, 22, 28, 33, 44] or n == N_D:
        z_n = 4**ell_n - 1
        print(f"  {n:>4d} {gn:>10.6f} {ell_n:>10.4f} {1+z_n:>10.4f} {z_n:>10.4f}")

# 用 gamma_n 映射計算 DOS
print(f"\n{'─'*75}")
print(f"  DOS 形狀 (從 gamma_n 自然映射)")
print(f"{'─'*75}")

for gamma_name, gamma_l in [('gamma=0.05', 0.05), ('gamma=0.1', 0.1), ('gamma=0.2', 0.2)]:
    dos = compute_dos(el_grid, ell_n_gamma, gamma_l)
    peak_idx = np.argmax(dos)
    peak_ell = el_grid[peak_idx]
    peak_val = dos[peak_idx]
    print(f"  {gamma_name}: peak ell={peak_ell:.4f}, dos={peak_val:.6f}")

# ================================================================
# 6. 比較自然 DOS vs Gaussian Ansatz
# ================================================================
print(f"\n{'─'*75}")
print(f"  自然 DOS vs Gaussian Ansatz")
print(f"{'─'*75}")

# Gaussian Ansatz
ell_0 = math.log(2) / math.log(4)  # 0.5
sigma = 0.5 * math.log(PHI) / math.log(4)  # 0.1736
phi_3 = PHI_INV ** 3

dos_natural = compute_dos(el_grid, ell_n_gamma, 0.1)
dos_gauss = phi_3 * np.exp(-(el_grid - ell_0)**2 / (2 * sigma**2))

print(f"  {'ell':>8s} {'DOS_nat':>10s} {'DOS_gauss':>10s} {'ratio':>10s}")
for i in range(0, len(el_grid), 50):
    print(f"  {el_grid[i]:>8.4f} {dos_natural[i]:>10.6f} {dos_gauss[i]:>10.6f} {dos_natural[i]/max(dos_gauss[i],1e-10):>10.4f}")

# 歸一化自然 DOS 同 Gaussian 比較
peak_nat = np.max(dos_natural)
dos_nat_norm = dos_natural / peak_nat
dos_gauss_norm = dos_gauss / np.max(dos_gauss)

print(f"\n  歸一化對比:")
print(f"  {'ell':>8s} {'DOS_nat_norm':>14s} {'Gauss_norm':>12s}")
for i in range(0, len(el_grid), 50):
    print(f"  {el_grid[i]:>8.4f} {dos_nat_norm[i]:>14.6f} {dos_gauss_norm[i]:>12.6f}")

# 分析自然 DOS 嘅形狀
print(f"\n{'─'*75}")
print(f"  自然 DOS 形狀分析")
print(f"{'─'*75}")

# Lorentzian fit
def lorentzian(x, x0, gamma, amp):
    return amp * gamma**2 / ((x - x0)**2 + gamma**2)

peak_idx = np.argmax(dos_natural)
x0_fit = el_grid[peak_idx]
amp_fit = dos_natural[peak_idx]
# Find HWHM
half_max = amp_fit / 2
left_idx = np.where(dos_natural[:peak_idx] <= half_max)[0]
right_idx = np.where(dos_natural[peak_idx:] <= half_max)[0]
if len(left_idx) > 0 and len(right_idx) > 0:
    hwhm_left = el_grid[peak_idx] - el_grid[left_idx[-1]]
    hwhm_right = el_grid[peak_idx + right_idx[0]] - el_grid[peak_idx]
    gamma_fit = (hwhm_left + hwhm_right) / 2
    print(f"  峰值位置: ell = {x0_fit:.4f}")
    print(f"  峰值振幅: DOS = {amp_fit:.6f}")
    print(f"  HWHM: left={hwhm_left:.4f}, right={hwhm_right:.4f}")
    print(f"  自然寬度 gamma = {gamma_fit:.4f}")
    print(f"  Gaussian sigma = {sigma:.4f} (vs gamma = {gamma_fit:.4f})")
    print(f"  ell_0 = {ell_0:.4f} (vs peak = {x0_fit:.4f})")
    print(f"  phi^-3 = {phi_3:.6f} (vs peak height = {amp_fit:.6f})")

# 結論
print(f"\n{'─'*75}")
print(f"  結論")
print(f"{'─'*75}")
print(f"")
print(f"  自然 DOS 從 gamma_n 譜直接計算:")
print(f"  - 形狀: 接近 Lorentzian (高斯係假定)")
print(f"  - 峰值位置: 由 gamma_n 經 ell = L - log_phi(gamma_n) 決定")
print(f"  - 峰值振幅: 由 spectral weight gamma_n 加權和決定")
print(f"")
print(f"  下一步: 證明 partial trace 自然壓縮出")
print(f"  delta(ell) = phi^-3 * Lorentz(ell - ell_0, Gamma)")
print(f"  其中 Gamma 由 K_Chain 色散關係 d^2omega/dk^2 決定")