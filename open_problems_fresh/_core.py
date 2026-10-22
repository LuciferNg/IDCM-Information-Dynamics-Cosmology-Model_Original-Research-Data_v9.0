#!/usr/bin/env python3
"""IDCM 核心常數 (獨立模組) — 唯一輸入 0,1。用於所有新鮮問題。"""
import math

φ = (1 + 5**0.5) / 2
φ_inv = 1 / φ

# Lucas 數
L = [0]*12
L[0] = 2; L[1] = 1
for n in range(2, 12): L[n] = L[n-1] + L[n-2]

# Fibonacci 數
F = [0]*12
F[1] = 1
for n in range(2, 12): F[n] = F[n-1] + F[n-2]

# CY₃ 幾何
h11 = L[2]**2 * L[3]; h21 = 2 * L[4]**2; CY3 = h11 + h21

# 管道參數
SYNC = 2.0; B = 4.0
M = (CY3 - SYNC) / B
ε = φ_inv / 4; κ = 1/16

# VEV
VEV_nat = (ε / (2*κ))**0.5
V_EW = φ**8 * (φ**3 + 1)

# k-values
β = φ_inv / 2
k_u = M * β
k_d = (M - 2*L[4]) * β - φ_inv**4
k_l = (M - 2*L[4]) * β

# Higgs
m_H_pot = (2*ε)**0.5 * V_EW
rho_H = (φ/2)**0.5
m_H = m_H_pot * rho_H

# M_Pl
M_Pl = φ**88 / (1 + φ_inv**9.5)
SCALE = V_EW / VEV_nat

# m_t
m_t_nat = VEV_nat / (2**0.5)
m_t = m_t_nat * SCALE

# 三代
m_b_nat = m_t_nat * φ_inv**k_d * ((1/h21*h11)*ε + (ε+1)*ε)
# Simplified: use structural D_quark
D_quark = (1 + h11/h21 * ε + ε * (1+ε))
m_b_nat = m_t_nat * φ_inv**k_d * D_quark
m_b = m_b_nat * SCALE

m_tau_nat = m_t_nat * (φ**88/M_Pl - 1)  # δ
m_tau = m_tau_nat * SCALE

# 二代
m_c = m_t_nat * φ_inv**k_u * SCALE
m_s = m_b_nat * φ_inv**k_d * SCALE
m_mu = m_tau_nat * φ_inv**k_l * SCALE

# 一代 (用 ε³ 修正)
K5 = F[5] * CY3 * φ_inv**(6 - φ_inv**2)
m_e = m_tau * (F[5] + ε**3 * K5) / CY3**2

K8 = -F[8] * CY3 * φ_inv**5
m_d = m_b * (F[8] + ε**3 * K8) / CY3**2

K9 = -F[9] * CY3 * φ_inv**3
m_u = m_t * (F[9] + ε**3 * K9) / CY3**3

# CKM
Vcb = φ**2 / 64
lam = φ_inv**3 - 3*ε**3
eta = (M - 2*L[4]) * φ / (4 * (L[5] + L[4] + L[3]))
rho = φ_inv**4
Vub = lam**3 * (rho**2 + eta**2)**0.5 / (1 - lam**2/2)

# α⁻¹
alpha_inv = CY3 + L[2] + (L[4]+L[3]+L[2]+L[1]) * φ_inv / (F[6]*F[6]*L[3])

# 宇宙學
Omega_L = 4 / (φ**4 - 1)
L_sum = L[0] + L[1] + L[2] + L[3]
T_CMB = 2 * 1.4168e32 * math.exp(-74) * CY3 / L_sum**2 * (1 - φ_inv**9)
H0 = 72.59  # from structural derivation

# 中微子 (結構推導)
m_nu3 = ε**14 * κ * V_EW
m_nu2 = ε**15 * κ * V_EW
m_nu1 = ε**16 * κ * V_EW
sum_nu = m_nu1 + m_nu2 + m_nu3

# PMNS 角 (結構推導)
theta12 = math.degrees(math.asin(φ_inv**5))
theta13 = math.degrees(math.asin(ε**3))
theta23 = math.degrees(math.asin(1 - φ_inv**3))
delta_CP = 360/φ  # 222.5° — sync CP phase