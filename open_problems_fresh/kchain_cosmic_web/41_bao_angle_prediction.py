#!/usr/bin/env python3
"""
IDCM BAO v3 — 直接預測原始角度 Δθ，唔經 ΛCDM DM
==================================================
跳離 ΛCDM 嘅 DM 框架，直接從 K_Chain 44-site 結構預測
BAO 嘅原始角度尺度 θ_BAO(z)。

核心 insight:
- 紅移 = 相位落差 (Phase Shift) = 操作步數 (Mapping Depth)
- K_Chain 44-site 嘅 SYNC 諧波直接對應天球上嘅角度波動
- BAO 角度 = 44-site 離散色散嘅投影
- 唔需要「距離」，只需要「相位-視角映射」
"""
import math
import numpy as np

print("=" * 80)
print("  IDCM BAO v3 — 直接預測原始 BAO 角度")
print("=" * 80)

# ================================================================
# 0. 基本參數
# ================================================================
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
N_d = 44
B = 4
R_H = 4129.94  # Mpc
c_mpc_gyr = 306.6

# BAO 結構尺度
lambda_sync = 2 * math.pi * R_H / 88  # 294.88 Mpc
rd = lambda_sync / 2  # 147.44 Mpc

# K_Chain site spacing
dx = R_H / N_d  # 93.86 Mpc

# BAO 對應嘅 site 數
n_BAO = rd / dx  # 147.44 / 93.86 = 1.57 sites
print(f"\n基本參數:")
print(f"  R_H = {R_H:.2f} Mpc")
print(f"  Δx = R_H/44 = {dx:.4f} Mpc")
print(f"  λ_sync = {lambda_sync:.4f} Mpc")
print(f"  BAO rd = {rd:.4f} Mpc")
print(f"  BAO 對應 site 數 = {n_BAO:.4f}")

# ================================================================
# 1. K_Chain 天球投影
# ================================================================
print(f"\n{'─'*80}")
print(f"  1. K_Chain 44-site 天球投影")
print(f"{'─'*80}")

# K_Chain 係 1D ring，44 個 site 均勻分佈
# 喺天球上，44 個 site 投影為 44 個「方向」
# 每兩個相鄰 site 嘅角距離: 2π/44 rad = 8.18°

theta_site = 2 * math.pi / N_d  # rad
theta_site_deg = theta_site * 180 / math.pi
print(f"  相鄰 site 角距離: {theta_site:.4f} rad = {theta_site_deg:.4f}°")

# BAO 對應嘅角度（在 full rendering 下）
theta_BAO_z0 = n_BAO * theta_site
theta_BAO_z0_deg = theta_BAO_z0 * 180 / math.pi
print(f"  BAO 角度 (z=0): {theta_BAO_z0:.4f} rad = {theta_BAO_z0_deg:.4f}°")

# ================================================================
# 2. 紅移 = 相位落差 → 角度隨 z 變化
# ================================================================
print(f"\n{'─'*80}")
print(f"  2. 紅移 = 相位落差 → BAO 角度隨 z 變化")
print(f"{'─'*80}")

# 喺 IDCM，紅移 z 對應 K_Tree level ℓ = log_B(1+z)
# 喺 level ℓ，44-site 嘅「有效角距離」被壓縮
# 因為高 z 對應細尺度，天球上嘅投影更集中

# 但 BAO 嘅物理尺度 (rd) 係結構常數
# 喺唔同 z，BAO 嘅角尺度 = BAO 物理尺度 / 投影距離

# 而我哋唔用 ΛCDM 嘅 DM，改用 K_Chain 嘅「相位視角」
# 每個紅移 z 對應嘅「視角尺度」由 K_Chain 色散決定

# 方法 H: 直接從 K_Chain 色散預測 BAO 角度
# 思路: BAO 角度 = 44-site 嘅 SYNC 諧波在天球上嘅投影
# 唔同 z 對應唔同 K_Tree level，level 越高 (z 越高) 角度越細

# 最簡單嘅投影模型: 
# θ_BAO(z) = θ_BAO(0) / (1+z)^γ
# 其中 γ 係投影指數

# 先試 γ=1 (線性壓縮)
print(f"  θ_BAO(z) = θ_BAO(0) / (1+z)^γ\n")
print(f"  {'z':<8} {'γ=0.5':<12} {'γ=1.0':<12} {'γ=1.5':<12} {'γ=2.0':<12}")
print(f"  {'-'*56}")
for z in [0.0, 0.5, 1.0, 2.33, 3.0, 5.0, 10.0, 15.0]:
    row = f"  {z:<8.2f}"
    for gamma in [0.5, 1.0, 1.5, 2.0]:
        theta = theta_BAO_z0 / (1+z)**gamma
        row += f" {theta*180/math.pi:<12.4f}"
    print(row)

# ================================================================
# 3. 對比 DESI 原始 BAO 角度
# ================================================================
print(f"\n{'─'*80}")
print(f"  3. 對比 DESI 原始 BAO 角度")
print(f"{'─'*80}")

# DESI DR2 Lyα BAO 測量:
# DM/rd = 39.32 ± 0.33 (transverse)
# 呢個數係假設 ΛCDM 後反推
# 真正嘅原始觀測係 BAO 嘅角度尺度 Δθ

# 喺 ΛCDM: θ_BAO(z) = rd / DM(z)
# 所以: θ_BAO(z=2.33) = 147.44 / 5796 = 0.0254 rad = 1.46°

# 但呢個角度係 ΛCDM 嘅 DM 反推，唔係直接量度
# 真正直接量度嘅係 correlation function ξ(s) 入面嘅 BAO peak 位置

# 所以 IDCM 應該預測 ξ(s) 入面 BAO peak 嘅位置
# 而唔係 θ_BAO

# 喺 IDCM，ξ(s) 嘅 BAO peak 喺 s = 147.44 Mpc
# 呢個係結構常數，同 z 無關
# 但 ξ(s) 係用 ΛCDM 嘅 DM 計算嘅「距離」
# 如果改用 IDCM 嘅距離，BAO peak 位置會唔同

# 真正嘅直接測試: 預測 ξ(s) 喺 147 Mpc 附近嘅形狀同 ΛCDM 嘅分別
# 但呢個需要完整嘅 power spectrum 計算，唔係而家做到

print(f"\n  DESI 原始觀測量:")
print(f"  BAO 在 2D correlation function ξ(s⊥, s∥) 中")
print(f"  s⊥ = DM/rd × rd = transverse scale")
print(f"  s∥ = DH/rd × rd = radial scale")
print(f"  DESI Lyα: DM/rd = 39.32, DH/rd = 26.28\n")

print(f"  喺 ΛCDM 框架下:")
print(f"  s⊥(z=2.33) = 39.32 × 147.44 = 5796 Mpc")
print(f"  s∥(z=2.33) = 26.28 × 147.44 = 3875 Mpc\n")

print(f"  喺 IDCM 框架下，BAO 係結構常數:")
print(f"  s⊥ = s∥ = rd = 147.44 Mpc")
print(f"  但呢個係「相位空間」嘅距離，唔係 ΛCDM 嘅 comoving 距離")
print(f"  需要一個映射: s_ΛCDM = f(s_IDCM, z)")

# ================================================================
# 4. 關鍵 insight: BAO 係 K_Chain 嘅諧波，唔係聲波視界
# ================================================================
print(f"\n{'─'*80}")
print(f"  4. BAO 嘅 IDCM 本質: K_Chain 諧波")
print(f"{'─'*80}")

# 喺 IDCM，BAO 唔係重子聲波振盪嘅殘留
# 而係 K_Chain 44-mode 嘅 SYNC 諧波:
# k_sync = 88/R_H = 0.0213 h/Mpc
# BAO 係 k_sync/2 嘅一階諧波 = 0.01065 h/Mpc

# 喺 ΛCDM，BAO 係一個「標準尺」(standard ruler)
# 喺 IDCM，BAO 係一個「標準頻率」(standard frequency)

# 呢個頻率喺唔同紅移嘅觀測值，直接反映
# 紅移-z 嘅對應關係

k_sync = 88 / R_H
k_BAO = k_sync / 2
print(f"  SYNC 波數: k_sync = {k_sync:.6f} h/Mpc")
print(f"  BAO 波數: k_BAO = {k_BAO:.6f} h/Mpc")
print(f"  BAO 波長: λ_BAO = {2*math.pi/k_BAO:.4f} Mpc")
print(f"  BAO 尺度: s_BAO = π/k_BAO = {math.pi/k_BAO:.4f} Mpc\n")

# 喺唔同 K_Tree level ℓ，BAO 嘅觀測波數會變化:
# k_obs(ℓ) = k_BAO × B^ℓ = k_BAO × (1+z)
# 因為高 z 對應細尺度，波數變大

print(f"  BAO 觀測波數隨 z:")
print(f"  k_obs(z) = k_BAO × (1+z)\n")
print(f"  {'z':<8} {'k_obs':<14} {'λ_obs':<14} {'θ_BAO':<14}")
print(f"  {'-'*50}")
for z in [0.0, 0.5, 1.0, 2.33, 3.0, 5.0]:
    k_obs = k_BAO * (1+z)
    lam_obs = 2*math.pi/k_obs
    theta = 2*math.pi / (N_d/2) / (1+z)  # 粗略估計
    print(f"  {z:<8.2f} {k_obs:<14.6f} {lam_obs:<14.4f} {theta*180/math.pi:<14.4f}")

# ================================================================
# 5. 直接預測 DESI 嘅 BAO 信號
# ================================================================
print(f"\n{'─'*80}")
print(f"  5. 預測 DESI BAO 在 IDCM 框架下嘅表現")
print(f"{'─'*80}")

# IDCM 嘅 BAO 預測:
# 1. BAO 尺度 = λ_sync/2 = 147.44 Mpc (結構常數)
# 2. 喺 correlation function ξ(s) 入面，BAO peak 喺 s = 147.44 Mpc
# 3. 但 ξ(s) 嘅「s」係用 ΛCDM 嘅 DM 計算
# 4. 如果用 IDCM 嘅「相位距離」取代 ΛCDM 嘅 comoving 距離
#    BAO peak 會喺唔同位置

# 關鍵: DESI 用 ΛCDM 嘅模板去 fit BAO
# 如果 IDCM 正確，用 ΛCDM 模板 fit 會產生系統性偏差
# 呢個偏差可以量度

print(f"\n  IDCM 預測 DESI BAO:")
print(f"  1. BAO 尺度: s = 147.44 Mpc (常數)")
print(f"  2. 紅移行為: s(z) = s × (1+z)^0 = 常數")
print(f"  3. 同 ΛCDM 分別: ΛCDM 嘅 BAO 尺度隨 z 變化")
print(f"     (因為 sound horizon 係固定 comoving scale)")
print(f"  4. 關鍵測試: compare ξ(s) at z=0.5 vs z=2.33")
print(f"     ΛCDM: BAO peak 喺相同 s (comoving)")
print(f"     IDCM: BAO peak 喺相同 s (physical)")

# ================================================================
# 6. 總結: 下一步
# ================================================================
print(f"\n{'─'*80}")
print(f"  6. 總結")
print(f"{'─'*80}")

print(f"""
Gemini 嘅 insight 係啱嘅:
  DESI 嘅 DM 係 ΛCDM 嘅衍生幻覺，IDCM 唔應該去打佢。
  正確路徑: 從 K_Chain 44-site 結構直接預測原始 BAO 角度。

但目前 IDCM 未有完整嘅「相位-視角映射矩陣」。
需要建立以下數學工具:
  1. 44-site K_Chain → 天球投影嘅角度譜
  2. 每個 K_Tree level ℓ 對應嘅角分辨率
  3. BAO 諧波在唔同 ℓ 嘅投影
  4. 直接預測 ξ(s) 嘅 BAO peak 位置

開放問題:
  IDCM 嘅 BAO 尺度 (147.44 Mpc) 係 comoving 定 physical？
  如果係 physical，high-z 嘅 BAO 角度會比 ΛCDM 大。
  如果係 comoving，同 ΛCDM 無分別。
  呢個分別係關鍵測試。
""")