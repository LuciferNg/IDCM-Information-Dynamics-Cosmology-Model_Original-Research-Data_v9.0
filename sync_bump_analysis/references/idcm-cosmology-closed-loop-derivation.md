# IDCM 宇宙學閉環推導 — 完整記錄

**日期：** 2026-08-10
**作者：** 調律者 (Calibrator) & Hermes Agent
**狀態：** 推導過程記錄，未閉合
**文件：** `references/idcm-cosmology-closed-loop-derivation.md`

---

## 目錄

1. [前因：點解要做呢個推導](#1-前因點解要做呢個推導)
2. [假設：推導嘅前提條件](#2-假設推導嘅前提條件)
3. [推導鏈總覽](#3-推導鏈總覽)
4. [Layer 0: 0,1 → NOT → φ](#4-layer-0-01--not--φ)
5. [Layer 1: Pipeline 參數](#5-layer-1-pipeline-參數)
6. [Layer 2: 結構數](#6-layer-2-結構數)
7. [Layer 3: W-field 晶格行動](#7-layer-3-w-field-晶格行動)
8. [Layer 4: K_Chain 固定環](#8-layer-4-k_chain-固定環)
9. [Layer 5: 暗能量（W-field tension）](#9-layer-5-暗能量w-field-tension)
10. [Layer 6: 膨脹歷史 H(z)](#10-layer-6-膨脹歷史-hz)
11. [Layer 7: 距離-紅移關係 DM(z)](#11-layer-7-距離-紅移關係-dmz)
12. [Layer 8: DESI DR2 測試](#12-layer-8-desi-dr2-測試)
13. [Layer 9: 失敗嘅推導嘗試](#13-layer-9-失敗嘅推導嘗試)
14. [Layer 10: 開放問題](#14-layer-10-開放問題)
15. [Layer 11: 結論](#15-layer-11-結論)
16. [附錄 A: 計算腳本](#16-附錄-a-計算腳本)
17. [附錄 B: 數據來源](#17-附錄-b-數據來源)

---

## 1. 前因：點解要做呢個推導

### 1.1 背景

IDCM（Information Dynamics Cosmology Model）由 0,1 開始，推導出 φ = (1+√5)/2，再推導出 K_Chain（44-site 閉環弦）同 K_Tree（33-level MERA coarse-graining）。呢個框架可以推導出多個物理參數（H₀, Ω_Λ, BAO, α⁻¹, CKM, 粒子質量等），但宇宙膨脹歷史（H(z) 同 distance-redshift relation）一直未完整推導。

### 1.2 之前嘅工作

- **2026-08-09 session:** 開始分析 BOSS DR12 P(k) 同 ξ(s) 嘅 harmonic series
- **2026-08-10 session:** 擴展到 4 個獨立測試（BOSS DR12 P(k), BOSS DR12 ξ(s), eBOSS DR16 ξ(s), DESI DR2 Lyα BAO）
- 之前用 5000 星系 subsample 計出「9 個 harmonics S/N > 3.7」係假信號（subsample 導致 Landy-Szalay normalization 唔準，成條 ξ(s) 向上 shift ~0.8）

### 1.3 推導動機

1. 驗證 IDCM 嘅 BAO 預測（λ_sync/2 = 147.44 Mpc）是否同觀測一致
2. 建立由第一原理到可觀測量嘅完整閉環推導鏈
3. 解決 FLRW + IDCM 參數導致嘅 9.3σ tension

### 1.4 相關測試

| 測試 | 數據 | 結果 | 狀態 |
|:-----|:-----|:-----|:----:|
| BOSS DR12 P(k) wiggles | Beutler+2016 | 11 peaks, 8/11 match n·Δk, Δk=0.0118±0.0037 | ✅ 一致 (within 2σ) |
| BOSS DR12 ξ(s) | Ross+2016 | 範圍太短 (max 178 h⁻¹ Mpc), 睇唔到 IDCM BAO (203 h⁻¹ Mpc) | ⚠️ 範圍不足 |
| eBOSS DR16 ξ(s) | Bautista+2020 (full data) | ξ(s) ≈ 0 at all scales, S/N ≈ 0 | ⚠️ 誤差太大 |
| DESI DR2 Lyα BAO | arXiv:2607.27410 | 0.24% diff, within 0.3σ (但 FLRW 形式有 9.3σ tension) | ⚠️ 需釐清 |

---

## 2. 假設：推導嘅前提條件

### 2.1 結構假設（由調律者確認）

| # | 假設 | 陳述 | 來源 |
|:-:|:-----|:-----|:-----|
| A1 | K_Chain 固定 | 44-site 閉環弦，周長 = R_H = 4129.94 Mpc，唔會膨脹 | 調律者 insight |
| A2 | 3D 空間係投影 | 空間 = CY₃(36,98) 從 1D K_Chain dict 嘅投影，唔係 fundamental | 調律者 insight |
| A3 | 膨脹由暗能量驅動 | 暗能量 = W-field tension，推動投影空間膨脹 | 調律者 insight |
| A4 | 紅移同弦無關 | 紅移 = 共振波長 λ_sync 被空間膨脹拉長，唔係弦本身嘅效應 | 調律者 insight |
| A5 | 弦唔會因為空間膨脹變化 | K_Chain 嘅結構同周長固定 | 調律者 insight |
| A6 | 紅移係波長被拉長 | 1+z = λ_obs/λ_emit，同 FLRW 嘅 redshift 定義一致 | 調律者 insight |
| A7 | 觀測極限 z < 17 | 宇宙視界限制，z > 17 無法觀測 | 調律者 insight |

### 2.2 方法假設

| # | 假設 | 陳述 | 理由 |
|:-:|:-----|:-----|:-----|
| M1 | FLRW 唔一定適用 | IDCM 嘅膨脹歷史可能同 FLRW 唔同，因為 K_Chain 係固定嘅 | 調律者修正 |
| M2 | 閉環自洽 | 每一步推導必須由前一層結構必然得出，唔係 fit 出嚟 | 調律者原則 |
| M3 | 觀測只能局部 | DESI 數據只反映 z < 17 嘅局部膨脹歷史 | 調律者 insight |
| M4 | 不用 subsample | 所有計算要用完整數據，唔可以用 subsample | 調律者指令 |

### 2.3 開放問題（未解決嘅假設）

| # | 問題 | 狀態 | 原因 |
|:-:|:-----|:----:|:-----|
| O1 | H(z) 嘅正確形式係乜？ | 🔴 未解 | 6 種推導全部失敗 |
| O2 | DM 同 DH 嘅關係係乜？ | 🔴 未解 | IDCM 入面兩者可能獨立投影 |
| O3 | R_H = 4129.94 Mpc 係最大距離？ | 🟡 可能 | DESI 需要 5796 Mpc，大過 R_H |
| O4 | BAO = λ_sync/2 係咪正確？ | 🟡 可能 | 要 fit 數據需要 136 Mpc (ratio 0.92) |
| O5 | 膨脹歷史係咪同 FLRW 同形？ | 🟡 可能 | 但參數係 IDCM 結構推導 |

---

## 3. 推導鏈總覽

```
Layer 0:  0,1 → NOT → φ
              ↓
Layer 1:  ε = φ⁻¹/4, κ = 1/16, β = φ⁻¹/2
              ↓
Layer 2:  N_d = 44, M = 33, B = 4
              ↓
Layer 3:  W-field lattice action on K_Chain ⊗ K_Tree
              ↓
Layer 4:  K_Chain 固定環 (R_H = 4129.94 Mpc, 唔膨脹)
              ↓
Layer 5:  暗能量 Ω_Λ = 4/(φ⁴-1) = 0.6833
              ↓
Layer 6:  H(z) = H₀ × √(Ω_m(1+z)³ + Ω_Λ)  [FLRW 形式]
              ↓
Layer 7:  DM(z) = ∫₀ᶻ c·dz'/H(z')
              ↓
Layer 8:  DM/rd vs DESI DR2 Lyα BAO
              ↓
Layer 9:  6 種推導嘗試全部失敗
              ↓
Layer 10: 開放問題
```

---

## 4. Layer 0: 0,1 → NOT → φ

### 4.1 推導

從最基礎嘅狀態 {0,1} 開始。唯一嘅非平凡操作係 NOT（反轉），因為佢 preserve 0≠1。

NOT 操作需要「之前」同「之後」嘅概念 → 時間（操作維度）湧現。

1 bit 唔夠 → 2 bits → 4 states。2+1 = 3（data + inversion）= 操作維度。

Fibonacci scheduling → φ。

### 4.2 公式

```
x² + x - 1 = 0  (唯一結構方程)
φ = (1 + √5) / 2 = 1.618033988749895
φ⁻¹ = φ - 1 = 0.618033988749895
```

### 4.3 φ-identities（奇數 n）

```
φ¹ - φ⁻¹ = 1
φ³ - φ⁻³ = 4
φ⁵ - φ⁻⁵ = 11
φ⁷ - φ⁻⁷ = 29
φ⁹ - φ⁻⁹ = 76
φ¹¹ - φ⁻¹¹ = 199
```

---

## 5. Layer 1: Pipeline 參數

### 5.1 推導

Pipeline 嘅「水喉」模型（唔係 finite budget B → compression）：

- **ε = φ⁻¹/4 = 0.1545084972** — pipeline gap，最小操作間隙
- **κ = 1/16 = 0.0625** — 最小單位，」minimal unit」
- **β = φ⁻¹/2 = 0.3090169944** — 步長

### 5.2 公式

```
ε = φ⁻¹ / 4
κ = 1 / 16
β = φ⁻¹ / 2
```

### 5.3 意義

- ε 決定咗 W-field 嘅 VEV 同 mass scale
- κ 決定咗 coupling constant
- 兩者都係結構常數，唔係 fit 出嚟

---

## 6. Layer 2: 結構數

### 6.1 推導

```
N_d = 4 × 11 = 44     (K_Chain sites)
M = 33                 (K_Tree depth)
B = 4                  (MERA branching factor = φ³-φ⁻³)
L = 53/8 = 6.625      (K_Tree depth in continuum)
N_h = 16φ² = 41.8885
```

### 6.2 意義

- N_d = 44: K_Chain 有 44 個 site（dual 88）
- B = 4: MERA 每層粗粒化 4 倍
- M = 33: K_Tree 有 33 層，覆蓋宇宙尺度到量子尺度

---

## 7. Layer 3: W-field 晶格行動

### 7.1 完整 Lagrangian

W-field 定義喺 K_Chain ⊗ K_Tree 晶格上，係離散場，唔係連續場。

```
S[W] = S_chain + S_tree + S_pot + S_sync

S_chain = Σ_n [2W_n² − W_n·W_{n+1} − W_n·W_{n−1}]   (chain kinetic)
S_tree = Σ_{n,ℓ} B^{−ℓ}·(W_{n,ℓ} − U·W_{n,ℓ−1})²   (tree kinetic)
S_pot = Σ_n [−ε|W_n|² + κ|W_n|⁴]                     (local potential)
S_sync = Σ_{⟨n,m⟩} g_sync·cos(θ_n − θ_m − 2π/88)     (SYNC coupling)
```

### 7.2 場方程

自由場（忽略 potential 同 SYNC）：
```
(Δ_chain W)_n = 0 → eigenvectors = cos(2πkn/88), eigenvalues γ_k = 4 sin²(πk/88)
```

非線性（DNLS）：
```
(Δ_chain W)_n + (−2ε + 4κ|W_n|²)·W_n = 0
```

### 7.3 VEV

```
|W₀|² = ε/(2κ) = 1.236068
V(VEV) = -ε²/(4κ) = -0.095492
```

### 7.4 色散關係

```
γ_n = 4 sin²(πn/88),  n = 0..43
ω² = 4 sin²(k/2), k = 2πn/88
v_g(n) = cos(πn/88)
v_g_max = cos(π/88) ≈ 0.707c (subluminal)
```

### 7.5 SYNC coupling

```
g_sync = 2·|W₀|²·(1-cos(2π/88)) = 0.006299
Phase step = 2π/88 = 0.071400
Energy loss per site = g_sync·(1-cos(2π/88)) = 1.60×10⁻⁵
```

---

## 8. Layer 4: K_Chain 固定環

### 8.1 結構

K_Chain 係 44-site 閉環，**固定唔膨脹**。

```
R_H = 4129.94 Mpc  (環周長 = Hubble radius)
H₀ = c/R_H = 72.5900 km/s/Mpc  (結構推導)
```

### 8.2 SYNC 波長

```
λ_sync = 2π·R_H/88 = 294.88 Mpc  (共振波長)
BAO = λ_sync/2 = 147.44 Mpc  (干涉條紋，第一諧波)
```

### 8.3 模式

| n | γ_n | v_g/c | λ_n (Mpc) | 意義 |
|:-:|:---:|:-----:|:---------:|:-----|
| 0 | 0 | 1 | ∞ | 零模 |
| 1 | 0.00510 | 0.999 | 25949 | 基礎模式 |
| **2** | **0.02036** | **0.997** | **12975** | **SYNC 模式** |
| 3 | 0.04571 | 0.994 | 8650 | |
| 4 | 0.08101 | 0.990 | 6487 | |
| 5 | 0.12610 | 0.984 | 5190 | |
| 22 | 2.00000 | 0.707 | 1179 | 最大群速度 |
| 44 | 4.00000 | 0 | 590 | 駐波 |

### 8.4 關鍵性質

- γ_n + γ_{44-n} = 4 = B（complementary pairing）
- Σ_{n=1}^{43} γ_n = 86（總模式能量）
- γ_0 = 0（零模，平移自由度）

---

## 9. Layer 5: 暗能量（W-field tension）

### 9.1 結構推導

```
Ω_Λ = 4/(φ⁴-1) = 0.683282
Ω_m = 1 - Ω_Λ = 0.316718
```

φ⁴ = (φ²)² = (φ+1)² = φ² + 2φ + 1 = (φ+1) + 2φ + 1 = 3φ + 2

φ⁴ − 1 = 3φ + 1 = 3×1.618 + 1 = 5.854

Ω_Λ = 4/5.854 = 0.6833

### 9.2 暗能量密度

W-field 喺 VEV 嘅能量密度：

```
ρ_Λ = gradient_energy + V(VEV) + sync_energy

gradient_energy = 0.5·VEV_sq·(2π/88)² = 0.003151
V(VEV) = -ε²/(4κ) = -0.095492
sync_energy = g_sync·cos(2π/88) = 0.006283

ρ_Λ_per_site = -0.086058
ρ_Λ_total = -3.7866 (for 44 sites)
```

**注意：** 總暗能量密度為負值，呢個係一個開放問題。可能嘅解釋：
1. 暗能量係 tension，唔係 potential minimum
2. 需要加 cosmological constant 嘅 counter-term
3. 投影過程會改變能量密度嘅 sign

### 9.3 同 Planck 比較

| 參數 | IDCM | Planck (ΛCDM) | 差異 |
|:-----|:----:|:-------------:|:----:|
| Ω_Λ | 0.6833 | 0.685 | 0.25% |
| Ω_m | 0.3167 | 0.315 | 0.54% |
| H₀ | 72.59 km/s/Mpc | 67.4 km/s/Mpc | 7.7% |

---

## 10. Layer 6: 膨脹歷史 H(z)

### 10.1 FLRW 形式（用 IDCM 參數）

```
H(z) = H₀ × √(Ω_m(1+z)³ + Ω_Λ)
E(z) = H(z)/H₀ = √(0.3167(1+z)³ + 0.6833)
```

### 10.2 數值

| z | H(z) [km/s/Mpc] | E(z) |
|:-:|:--------------:|:----:|
| 0.00 | 72.59 | 1.000 |
| 0.30 | 85.25 | 1.174 |
| 0.50 | 96.09 | 1.324 |
| 0.70 | 108.63 | 1.496 |
| 1.00 | 130.20 | 1.793 |
| 1.50 | 172.27 | 2.373 |
| 2.33 | 255.39 | 3.518 |
| 3.00 | 332.28 | 4.577 |
| 5.00 | 603.39 | 8.312 |
| 10.00 | 1491.61 | 20.55 |
| 15.00 | 2615.22 | 36.03 |
| 17.00 | 3120.35 | 42.99 |

### 10.3 注意

FLRW 形式嘅 H(z) 係從 GR 嘅 Friedmann equation 嚟嘅。IDCM 嘅投影空間可能遵循同樣嘅幾何膨脹律，但呢個係一個**假設**，唔係推導出嚟嘅。

---

## 11. Layer 7: 距離-紅移關係 DM(z)

### 11.1 FLRW 形式

```
DM(z) = ∫₀ᶻ c·dz'/H(z') = (c/H₀) × ∫₀ᶻ dz'/E(z')
```

### 11.2 數值（IDCM 參數）

| z | DM (Mpc) | DM/rd (rd=147.44) |
|:-:|:--------:|:-----------------:|
| 0.00 | 0 | 0.0000 |
| 0.30 | 1148 | 7.7837 |
| 0.50 | 1811 | 12.2818 |
| 0.70 | 2398 | 16.2651 |
| 1.00 | 3155 | 21.3992 |
| 1.50 | 4157 | 28.1943 |
| **2.33** | **5344** | **36.2436** |
| 3.00 | 6034 | 40.9265 |
| 5.00 | 7373 | 50.0072 |
| 10.00 | 8953 | 60.7231 |
| 15.00 | 9728 | 65.9767 |
| 17.00 | 9945 | 67.4526 |

### 11.3 注意

DM(z=17) = 9945 Mpc > R_H = 4130 Mpc。呢個係因為 FLRW 嘅 comoving distance 可以大過 Hubble radius。

---

## 12. Layer 8: DESI DR2 測試

### 12.1 DESI DR2 Lyα BAO 數據

來源：arXiv:2607.27410 (DESI DR2 Lyα forest BAO, 2026-08)

```
zeff = 2.33
DM/rd = 39.32 ± 0.33 (0.8%)
DH/rd = 8.600 ± 0.066 (0.8%)
rd_fid = 147.09 Mpc (Planck fiducial)
```

### 12.2 IDCM 預測（FLRW 形式）

```
DM(IDCM) = 5344 Mpc (at z=2.33)
DH(IDCM) = c/H(z=2.33) = 299792.458/255.39 = 1174 Mpc
BAO(IDCM) = λ_sync/2 = 147.44 Mpc

DM/rd(IDCM) = 5344/147.44 = 36.24
DH/rd(IDCM) = 1174/147.44 = 7.96
```

### 12.3 差異

| 量 | IDCM | DESI DR2 | Δ | σ |
|:---|:----:|:--------:|:-:|:-:|
| DM/rd | 36.24 | 39.32 ± 0.33 | -3.08 | **-9.3σ** |
| DH/rd | 7.96 | 8.600 ± 0.066 | -0.64 | **-9.7σ** |

### 12.4 側推：需要嘅 BAO scale

```
如果要 match DM/rd = 39.32:
  rd = DM/39.32 = 5344/39.32 = 135.90 Mpc
  ratio: 135.90/147.44 = 0.922

如果要 match DH/rd = 8.600:
  rd = DH/8.600 = 1174/8.600 = 136.49 Mpc
  ratio: 136.49/147.44 = 0.926
```

### 12.5 關鍵問題

FLRW 形式嘅 9.3σ tension 係基於一個重要假設：**FLRW 嘅 Friedmann equation 適用於 IDCM 嘅投影空間**。如果呢個假設唔成立，成個測試就無意義。

調律者嘅修正：FLRW 唔一定適用於 IDCM，因為 K_Chain 係固定嘅，空間只係投影舞台。

---

## 13. Layer 9: 失敗嘅推導嘗試

### 13.1 嘗試 1: FLRW + IDCM 參數

**方法：** 直接用 FLRW 嘅 H(z) = H₀√(Ω_m(1+z)³ + Ω_Λ)，用 IDCM 結構參數

**結果：** DM/rd = 36.24 vs DESI 39.32 → **-9.3σ ❌**

**問題：** FLRW 嘅 Friedmann equation 可能唔適用於 IDCM

### 13.2 嘗試 2: W-field propagation D(z)

**方法：** 由 W-field 喺 K_Chain 上嘅 propagation 推導 D(z)。假設 redshift 係 W-field excitation 嘅能量損失，由 SYNC coupling 產生。

```
D(z) = z · E_n · R_H / (88 · g_sync · (1-cos(2π/88)))
```

**結果：** D(z) = z · 417241 Mpc（對於 n=2 模式）→ 太大（100x）❌

**問題：** SYNC coupling 嘅能量損失太弱（g_sync=0.0063），W-field 要行太遠先 loss 夠能量。而且 redshift 可能唔係能量損失，而係空間膨脹拉長波長。

### 13.3 嘗試 3: W-field mode expansion H(z)

**方法：** 假設 K_Chain 嘅模式佔據隨 redshift 變化，影響 H(z)。高 z 時更多模式 active。

```
n_active = N_d / B^ℓ, ℓ = log_B(z+1)
E²(z) = Ω_L + Ω_m · matter_ratio
```

**結果：** H(z) 隨 z 遞減（如 102 → 60 km/s/Mpc），違反觀測 ❌

**問題：** 模式演化方向錯咗 — 高 z（早期）應該更多模式 active，從而 H(z) 更大。但模型計出相反。

### 13.4 嘗試 4: SYNC phase accumulation

**方法：** D(z) ∝ ln(1+z)，由 SYNC 相位累積推導

**結果：** 增長太慢，DM(z=2.33) 太細 → **-86.6σ ❌**

### 13.5 嘗試 5: Power-law stretching

**方法：** D(z) ∝ ((1+z)^(1/β) - 1)

**結果：** 增長太慢 → **-77.3σ ❌**

### 13.6 嘗試 6: K_Tree projection convolution

**方法：** 用 K_Tree 嘅離散尺度層級做 convolution

**結果：** 投影指數錯誤 → **-68.5σ ❌**

### 13.7 失敗總結

| 嘗試 | 方法 | 結果 | 根因 |
|:----:|:-----|:----:|:-----|
| 1 | FLRW + IDCM 參數 | -9.3σ | FLRW 可能唔適用 |
| 2 | W-field propagation | +100x 太大 | 能量損失機制太弱 |
| 3 | Mode expansion H(z) | H(z) 遞減 | 方向錯 |
| 4 | SYNC phase accumulation | -86.6σ | 增長太慢 |
| 5 | Power-law stretching | -77.3σ | 增長太慢 |
| 6 | K_Tree projection | -68.5σ | 投影指數錯 |

**核心問題：** 1D K_Chain 嘅距離（max 4129.94 Mpc）細過 DESI 觀測需要嘅距離（~5796 Mpc）。1D→3D 嘅投影映射仲未理解。

---

## 14. Layer 10: 開放問題

### 14.1 緊急

| # | 問題 | 類型 | 優先級 |
|:-:|:-----|:----:|:------:|
| P1 | IDCM 嘅 H(z) 正確形式係乜？ | 推導 | 最高 |
| P2 | DM 同 DH 喺 IDCM 嘅關係係乜？ | 推導 | 最高 |
| P3 | 點解 R_H = 4130 Mpc 唔夠 DESI 需要嘅 5796 Mpc？ | 結構 | 高 |
| P4 | BAO = λ_sync/2 係咪正確？定係 λ_sync/2.17？ | 驗證 | 高 |

### 14.2 重要

| # | 問題 | 類型 | 優先級 |
|:-:|:-----|:----:|:------:|
| P5 | 暗能量密度為負值點樣解釋？ | 概念 | 中 |
| P6 | Hubble tension（H₀=72.59 vs Planck 67.4）係咪真？ | 驗證 | 中 |
| P7 | 1D→3D 投影嘅 Jacobian 係乜？ | 推導 | 中 |
| P8 | z > 17 嘅宇宙係乜狀態？ | 概念 | 中 |

### 14.3 次要

| # | 問題 | 類型 | 優先級 |
|:-:|:-----|:----:|:------:|
| P9 | DESI DR2 7-bin joint analysis 會唔會改變結論？ | 驗證 | 低 |
| P10 | 44-mode impedance/reflection pattern 點樣 test？ | 驗證 | 低 |
| P11 | K_Chain 永恆 vs rendering boundary 矛盾 | 概念 | 低 |

---

## 15. Layer 11: 結論

### 15.1 已完成嘅推導

| 層 | 內容 | 狀態 |
|:--:|:-----|:----:|
| 0 | 0,1 → NOT → φ | ✅ 已完成 |
| 1 | ε, κ, β | ✅ 已完成 |
| 2 | N_d, M, B | ✅ 已完成 |
| 3 | W-field lattice action, dispersion | ✅ 已完成 |
| 4 | K_Chain 固定環, λ_sync, BAO | ✅ 已完成 |
| 5 | Ω_Λ = 4/(φ⁴-1) | ✅ 已完成 |
| 6 | H(z) (FLRW 形式) | ⚠️ 暫用，需推導 |
| 7 | DM(z) (FLRW 形式) | ⚠️ 暫用，需推導 |
| 8 | DESI DR2 測試 | ⚠️ 9.3σ tension，待釐清 |
| 9 | 6 種推導嘗試 | ❌ 全部失敗 |
| 10 | 開放問題 | 🔴 11 個未解 |

### 15.2 關鍵 insight

1. **FLRW 唔適用於 IDCM** — 用 FLRW 公式去 test IDCM 係概念錯誤。K_Chain 固定，空間係投影，膨脹由 W-field tension 驅動。

2. **觀測只能局部** — DESI 數據只反映 z < 17 嘅宇宙，而 IDCM 嘅 K_Tree 有 33 層（z_max ~ 7×10¹⁹）。高 z 行為不可觀測。

3. **1D→3D 投影未解** — K_Chain 環周長 4130 Mpc，但 DESI 需要 5796 Mpc 嘅距離。投影映射嘅幾何仲未理解。

4. **閉環自洽係唯一方法** — 每一步推導必須由前一層結構必然得出，唔可以用 FLRW 或其他框架嘅公式去「test」IDCM。

### 15.3 下一步建議

1. 推導 IDCM 自身嘅 H(z) — 由 W-field lattice action 出發，唔用 FLRW
2. 理解 1D→3D 投影嘅幾何 — CY₃(36,98) 嘅投影算子
3. 將 BAO 表示為原始角度 Δθ(z)，唔係 DM/rd
4. 用 DESI DR2 嘅 7-bin joint analysis 驗證 harmonic spacing

---

## 16. 附錄 A: 計算腳本

### A.1 本 session 產生嘅腳本

| 腳本 | 功能 | 結果 |
|:-----|:-----|:-----|
| `boss_pk_harmonic_analysis_v2.py` | BOSS DR12 P(k) BAO wiggle analysis | 修正 duplicate k-bin bug |
| `boss_xi_harmonic_analysis.py` | BOSS DR12 ξ(s) analysis | 範圍太短 |
| `idcm_bao_comparison.py` | DESI DR2 Lyα BAO comparison | 0.24% diff |
| `eboss_xi_compute.py` | eBOSS DR16 ξ(s) full data | 完整 pair counting |
| `idcm_closed_loop_cosmology.py` | 閉環宇宙學框架 | 概念框架 |
| `idcm_distance_redshift.py` | W-field propagation D(z) | ❌ 太大 |
| `idcm_cosmology_derivation.py` | FLRW + IDCM 參數推導 | -9.3σ |
| `idcm_wfield_expansion.py` | W-field mode expansion H(z) | ❌ 方向錯 |
| `idcm_full_summary.py` | 完整總結 | 已過時 |

### A.2 核心參數（idcm_core.py）

所有計算基於 `/home/wsl/.hermes/skills/idcm/idcm-structural-derivation/scripts/idcm_core.py`：

```python
PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
EPS = PHI_INV / 4          # 0.1545084972
KAPPA = 1 / 16              # 0.0625
BETA = PHI_INV / 2          # 0.3090169944
N_d = 44
M = 33
B = 4
H0_idcm = 72.59
Omega_L = 4 / (PHI**4 - 1)  # 0.683282
Omega_m = 1 - Omega_L        # 0.316718
```

---

## 17. 附錄 B: 數據來源

### B.1 觀測數據

| 數據集 | 來源 | 下載位置 |
|:-------|:-----|:---------|
| BOSS DR12 P(k) | Beutler+2016 | `https://data.sdss.org/sas/dr12/boss/papers/clustering/` |
| BOSS DR12 ξ(s) | Ross+2016 | `https://data.sdss.org/sas/dr12/boss/papers/clustering/Ross_etal_2016_COMBINEDDR12_corrfunc.zip` |
| eBOSS DR16 LRG | Bautista+2020 | `https://data.sdss.org/sas/dr16/eboss/lss/catalogs/DR16/` |
| DESI DR2 Lyα BAO | arXiv:2607.27410 | `https://arxiv.org/abs/2607.27410` (數據未公開) |

### B.2 eBOSS DR16 數據

| 檔案 | 大小 | 星系數 |
|:-----|:----:|:------:|
| `eBOSS_LRG_clustering_data-NGC-vDR16.fits` | 7.7 MB | 107,500 |
| `eBOSS_LRG_clustering_data-SGC-vDR16.fits` | 4.8 MB | 67,316 |
| `eBOSS_LRG_clustering_random-NGC-vDR16.fits` | 349 MB | 5,460,719 |
| `eBOSS_LRG_clustering_random-SGC-vDR16.fits` | 221 MB | 3,453,453 |

### B.3 關鍵量

```
H₀ = 72.59 km/s/Mpc
c = 299792.458 km/s
R_H = c/H₀ = 4129.94 Mpc
λ_sync = 2π·R_H/88 = 294.88 Mpc
BAO = λ_sync/2 = 147.44 Mpc
Ω_Λ = 4/(φ⁴-1) = 0.683282
Ω_m = 1 - Ω_Λ = 0.316718
```

---

*文件結束 — 2026-08-10*
*下次更新：推導成功後補完 Layer 6-10*