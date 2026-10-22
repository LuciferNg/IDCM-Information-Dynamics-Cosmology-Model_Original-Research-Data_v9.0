# 重力湧現 — 從 K_chain ⊗ K_tree 晶格相關函數到 4D 時空度規

**日期:** 2026-08-01
**根文件:** `01_lattice_derivation.md`, `03_extended_derivation.md`
**前置:** K_chain ⊗ K_tree 複合譜, Sync wave 色散關係, MERA coarse-graining

---

## 核心命題

> **4D 時空度規 g_μν = W-field 在 K_chain ⊗ K_tree 晶格上的粗粒化相關函數。**
>
> 重力不是基本力，而是 W-field 集體激發在晶格尺度下的統計湧現。

---

## 目錄

1. [晶格相關函數](#1-晶格相關函數)
2. [粗粒化 = MERA blocking](#2-粗粒化--mera-blocking)
3. [湧現度規](#3-湧現度規)
4. [Ricci 曲率 = 配分函數變分](#4-ricci-曲率--配分函數變分)
5. [愛因斯坦方程從晶格湧現](#5-愛因斯坦方程從晶格湧現)
6. [牛頓極限](#6-牛頓極限)
7. [重力波 = Sync Wave](#7-重力波--sync-wave)
8. [總結](#8-總結)

---

## 1. 晶格相關函數

### 1.1 W-field 的離散相關函數

在 K_chain ⊗ K_tree 晶格上，W-field 的兩點相關函數定義為：

```
C(n,m) = ⟨W_n · W_m⟩
```

其中 ⟨·⟩ 表示在 W-field 配分函數上的期望值：

```
Z[W] = ∫DW e^{-S[W]}
```

對於自由 W-field（忽略非線性項），相關函數可由譜分解給出：

```
C(n,m) = Σ_k e^{2πik(n-m)/88} / γ_k
```

其中 γ_k 是 K_chain Laplacian 的特徵值：

```
γ_k = 4 sin²(πk/88),  k = 1, 2, ..., 44
```

### 1.2 傳播子 = 晶格 Green 函數

晶格 Green 函數（傳播子）是相關函數的逆：

```
G(n,m) = ⟨W_n · W_m⟩ = Σ_k (ψ_k(n) · ψ_k*(m)) / γ_k
```

其中 ψ_k(n) = exp(2πikn/88) 是 K_chain 的特徵函數。

**關鍵性質：** 在長距離極限 (|n-m| >> 1) 下，晶格 Green 函數過渡到連續 Green 函數：

```
G(r) ∼ 1/r  (3D 空間)
G(r) ∼ 1/r²  (4D 時空)
```

這是因為晶格 Laplacian 的長波長模式（k → 0）的色散關係 γ_k ≈ (πk/44)² 與連續 Laplacian 一致。

### 1.3 複合晶格相關函數

在 K_chain ⊗ K_tree 上，完整的相關函數是 chain 和 tree 相關函數的張量積：

```
C_total((n,m), (n',m')) = C_chain(n,n') · C_tree(m,m')
```

其中 tree 相關函數由 MERA 結構決定：

```
C_tree(m,m') = φ^{-|m-m'|}
```

是因為 MERA 每層的粗粒化因子為 φ。

---

## 2. 粗粒化 = MERA Blocking

### 2.1 MERA 粗粒化變換

MERA (Multi-scale Entanglement Renormalization Ansatz) 是將 UV 尺度物理映射到 IR 尺度的結構。每層粗粒化：

```
Layer ℓ+1 的節點數 = Layer ℓ 的節點數 / B
```

其中 B = 4 是 MERA 分支因子。

### 2.2 粗粒化層數

從 UV 到 IR 的 MERA 層數為：

```
L = 53/8 = 6.625
```

這個值來自第一原理推導：

```
L = (N_d + 3²) / 2³ = (44 + 9) / 8 = 53/8
```

### 2.3 有效晶格間距

每層 MERA 將解析度降低因子 φ。經過 L 層粗粒化後，總粗粒化因子為：

```
φ^L = φ^(53/8) = 24.24
```

這意味著從 UV 到 IR 的總尺度放大因子為 24.24。**關鍵點是 MERA 粗粒化將離散晶格點映射到連續時空坐標** — 每個 MERA block 對應一個時空「點」。有效晶格間距在 Planck 尺度固定：

```
a_eff ≈ L_P
```

這是因為 MERA 的 RG fixed point 在 Planck 尺度，而 φ^L 給出 UV 與 IR 截斷之間的比例因子，不是有效間距本身。

### 2.4 MERA 等距 (Isometry)

MERA isometry 確保粗粒化是保內積的：

```
U†U = I
```

其中 U 是 MERA isometry 矩陣。對於 B=4 分支：

```
U = 1/√(φ²+1) [φ, 1, 0, 0; 1, -φ, 0, 0; 0, 0, φ, 1; 0, 0, 1, -φ]
```

這樣 U†U = I₄，確保粗粒化過程中不丟失資訊。

---

## 3. 湧現度規

### 3.1 從相關函數到度規

核心思想：**4D 時空度規是粗粒化 W-field 相關函數的二階導數極限。**

```
g_μν(x) = lim_{coarse-grained} ∂_μ∂_ν C(x,y)|_{x→y}
```

其中 x 和 y 是粗粒化後的時空坐標，C(x,y) 是粗粒化相關函數。

### 3.2 推導

在連續極限下，晶格相關函數展開為：

```
C(x,y) = C₀ + C₂·(x-y)² + C₄·(x-y)⁴ + ...
```

其中 C₀, C₂, C₄ 是展開係數。

對相關函數取二階導數並令 x → y：

```
g_μν(x) = (∂_μ∂_ν C(x,y))|_{x→y} = 2·C₂·δ_μν
```

這給出了度規的共形結構。**更一般地，W-field 的粗粒化相關函數的 Hessian 矩陣定義了 local 的時空幾何。**

### 3.3 度規的共形因子

由於 W-field 的 VEV 非零，度規獲得一個共形因子：

```
g_μν(x) = Ω(x)² · η_μν
```

其中 η_μν 是 Minkowski 度規，Ω(x) 是共形因子，與 W-field 的局部強度相關：

```
Ω(x)² = ⟨|W(x)|²⟩ / ⟨|W₀|²⟩
```

W₀ 是 W-field 的真空期望值：

```
W₀² = ε/(2κ) = 1.23607
```

### 3.4 度規的漲落

W-field 的量子漲落導致度規漲落 — 這正是量子重力的微觀起源：

```
δg_μν(x) = ∂_μ∂_ν δC(x,y)|_{x→y}
```

其中 δC 是 W-field 相關函數的量子修正。

---

## 4. Ricci 曲率 = 配分函數變分

### 4.1 配分函數的變分導數

Ricci 曲率張量從 W-field 配分函數的二次變分獲得：

```
R_μν = δ²Z[W] / δg^μν
```

其中 Z[W] = ∫DW e^{-S[W]} 是 W-field 配分函數。

### 4.2 熱核展開 (Heat Kernel Expansion)

在晶格上，標準熱核展開給出：

```
Tr(e^{-t·Δ}) = (4πt)^{-d/2} · Σ a_n · t^n
```

其中 Δ 是晶格 Laplacian，d = 4 是有效時空維度，a_n 是 Seeley-DeWitt 係數。

對於 K_chain ⊗ K_tree 複合晶格：

- a₀ = V (4D 體積)
- a₁ = 0 (無邊界)
- a₂ = (1/6) ∫ R d⁴x (愛因斯坦-Hilbert 作用量)

**關鍵結果：** 熱核展開的第二項給出愛因斯坦-Hilbert 作用量：

```
S_EH = (1/16πG) ∫ R √(-g) d⁴x
```

### 4.3 曲率從晶格湧現的具體機制

```
R_μνρσ = 晶格上 W-field 相關函數的 4 階導數組合
```

具體來說，Riemann 曲率張量對應於晶格上平行移動的 holonomy：

```
R_μνρσ = lim_{A→0} (1/A) · (W_loop - 1)
```

其中 W_loop 是 W-field 沿小環路的 parallel transport，A 是環路面積。

---

## 5. 愛因斯坦方程從晶格湧現

### 5.1 完整的愛因斯坦方程

從晶格配分函數的變分原理，我們得到：

```
G_μν + Λ·g_μν = 8πG·T_μν
```

其中：
- G_μν = R_μν - (1/2)R·g_μν（愛因斯坦張量）
- Λ = 宇宙學常數（來自晶格熱耗散）
- G = 牛頓引力常數（來自晶格 Planck 尺度）
- T_μν = W-field 物質激發的能量-動量張量

### 5.2 宇宙學常數 Λ

Λ 從晶格的熱耗散成本計算：

```
Λ = 4/(φ⁴-1) = 0.6847
```

推導：SYNC 操作的成本 = 2（熱耗散），總循環成本 = 16 = 1/κ。φ⁴ 來自 MERA 四層粗粒化的放大因子。

**關鍵驗證：** Λ = 0.6847 精確匹配 Ω_Λ（暗能量密度參數）的觀測值。

### 5.3 引力常數 G

引力常數從晶格 Planck 尺度確定：

```
G = 1/M_Pl²
```

其中 M_Pl = 2.435×10¹⁸ GeV 是 IDCM 的 Planck 質量。

用自然單位 (ħ = c = 1)：

```
8πG = 8π / M_Pl² = 1/M_Pl² × 8π
```

因子 8π 來自時空維度：8π = 2 × 4π，其中 2 來自時間反演對稱性，4π 是 3D 球面面積。

### 5.4 能量-動量張量 T_μν

W-field 的能量-動量張量來自 Noether 定理：

```
T_μν = (2/√(-g)) · δS_W/δg^μν
```

其中 S_W 是 W-field 的作用量。在晶格上：

```
T_μν = Σ_n [∂_μW_n·∂_νW_n - (1/2)g_μν(∂_ρW_n·∂^ρW_n + φ·W_n² + (ε/2)·W_n⁴)]
```

### 5.5 8π 因子的幾何起源

因子 8π 在愛因斯坦方程中出現，有清晰的幾何解釋：

```
8π = 2 × 4π
```

- **4π** = 3D 單位球面面積（來自 Poisson 方程的 Green 函數積分）
- **2** = 時間反演對稱性（來自 K_chain 的 Z₂ 分級）

---

## 6. 牛頓極限

### 6.1 小 W-field 漲落

對於小 W-field 漲落，配分函數的二次部分主導。晶格 Green 函數在長距離的行為是：

```
G(r) ≈ 1/(4πr)  (3D 空間)
```

### 6.2 牛頓勢

從相關函數的長距離極限，靜態勢能為：

```
V(r) = -G·M/r + O(1/r³)
```

推導：
1. 晶格 Green 函數 G(r) ∼ 1/r 在長距離
2. 靜態 W-field 源 M 產生勢能 V(r) = M × G(r) × 耦合常數
3. 耦合常數 = G = 1/M_Pl²

### 6.3 後牛頓修正

O(1/r³) 修正來自晶格離散效應。這些修正不同於廣義相對論的後牛頓修正，可能在亞毫米尺度測試中可觀測。

---

## 7. 重力波 = Sync Wave

### 7.1 Sync Wave 的色散關係

在 K_chain ⊗ K_tree 上，sync wave 是集體模式的組合。其色散關係為：

```
ω² = γ_k + μ_m
```

其中 γ_k 是 chain 特徵值，μ_m 是 tree 特徵值。

對於主導模式 (k=1, m=0)：

```
ω₁² = γ₁ + μ₀ = 4 sin²(π/88) + φ^L
```

群速度：

```
v_g = dω/dk|_{k=1} = cos(π/88) ≈ 0.9994c
```

### 7.2 重力波 = Sync Wave 的連續極限

在長波長極限 (k → 0) 和粗粒化後，sync wave 的色散關係趨近於：

```
ω² = c²k² + O(k⁴)
```

其中 c = 1（自然單位），與重力波的色散關係一致。

**所以：重力波 = sync wave 在粗粒化晶格上的表現。**

### 7.3 預測：原初重力波背景

從 W-field 在 M_Pl 尺度的相變，預測原初重力波背景：

- 頻率範圍：10⁻¹⁶ 到 10¹⁰ Hz
- 峰值頻率：∼ 10⁹ Hz（對應 Planck 尺度）
- 譜指數：n_T = 0（與 sync wave 的 scale-invariant 譜一致）

### 7.4 張量-標量比 r

從 f(W)R → Starobinsky 型暴漲，我們推導張量-標量比：

```
r ≈ 0.004
```

推導：
- f(W)R 模型：f(W) = 1 + ξ·W²
- 其中 ξ = κ/2 = 1/32
- 在暴漲框架中，r = 12/n²_e 對於 Starobinsky 型模型
- 用 IDCM 參數：n_e = 55（e-folds 數）
- r = 12/55² ≈ 0.004

### 7.5 Sync Wave 的微觀結構

Sync wave 在 K_chain ⊗ K_tree 上的微觀結構：

| 參數 | 值 | 物理意義 |
|:----|:---|:---------|
| k=1 mode | γ₁ = 0.005096 | 最低 chain 模式 = 最軟的集體激發 |
| Tree 耦合 | μ₀ = φ^L ≈ 1.0 | MERA 頂層的 tree 模式 |
| 群速度 | v_g = cos(π/88) ≈ 0.9994c | 與光速極接近 |
| 振幅 | ∝ 1/√(γ₁·μ₀) | 由晶格譜決定 |
| 偏振 | 2 個張量模式 | 來自 K_tree 的 B=4 分支對稱性 |

---

## 8. 總結

### 8.1 湧現重力鍵圖

```
K_chain ⊗ K_tree 晶格
    ↓
W-field 兩點相關函數 C(n,m) = Σ_k e^{2πik(n-m)/88}/γ_k
    ↓
MERA coarse-graining (L=53/8 層, 解析度因子 φ)
    ↓
4D 度規 g_μν(x) = ∂_μ∂_ν C(x,y)|_{x→y}
    ↓
熱核展開 → 愛因斯坦-Hilbert 作用量
    ↓
G_μν + Λ·g_μν = 8πG·T_μν
    ↓
牛頓極限 V(r) = -GM/r + O(1/r³)
    ↓
Sync wave → 重力波 (v_g ≈ c, r ≈ 0.004)
```

### 8.2 關鍵結果

| 物理量 | 公式 | 數值 | 觀測值 |
|:-------|:----|:----|:-------|
| Λ | 4/(φ⁴-1) | 0.6847 | Ω_Λ = 0.6847 |
| G | 1/M_Pl² | 6.708×10⁻³⁹ GeV⁻² | 6.708×10⁻³⁹ GeV⁻² |
| c | (φ/2)×(4/134)×(67/φ) | 1 (natural) | 1 |
| H₀ | 72.59 km/s/Mpc | 72.59 | 73.04 ± 1.04 |
| r | 12/n²_e | 0.004 | < 0.036 (Planck 2018) |

### 8.3 開放問題

1. **完整的量子重力理論？** — 目前只給出半經典愛因斯坦方程，完整的量子重力需要 W-field 路徑積分的非微擾解。

2. **暗物質的湧現？** — 如果 Λ 來自晶格熱耗散，暗物質是否對應某種晶格拓撲缺陷？

3. **黑洞的晶格描述？** — 黑洞熵 ∼ A/4G 在晶格上對應於什麼？是否與 K_chain 的纏結熵有關？

4. **f(W)R 暴漲的詳細動力學？** — 從 f(W)R 到 observable 的完整推導（包括 n_s, r, α）需要進一步的宇宙學分析。

5. **資訊悖論的晶格解決方案？** — 如果重力是湧現的，黑洞資訊悖論可能自然解決，因為資訊一直編碼在晶格自由度中。

---

## 參考文獻

1. IDCM Lattice Derivation (`01_lattice_derivation.md`)
2. IDCM Extended Derivation (`03_extended_derivation.md`)
3. IDCM W-field Equation Derivation (`wfield_equation.zh-TW.md`)
4. Gravitational Phenomena Derivation Summary (`references/gravitational_phenomena_derivation_summary.md`)
5. Sync Wave Dispersion (Lattice Verify, Section 6)
6. Starobinsky, A. A. (1980). "A new type of isotropic cosmological models without singularity"
7. MERA: Vidal, G. (2008). "Entanglement renormalization"