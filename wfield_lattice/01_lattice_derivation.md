# W-Field 晶格化 — 離散第一性原理推導

**日期:** 2026-07-31
**核心命題:**
> W-Field 不是連續時空上的連續場，而是定義在 **K_chain ⊗ K_tree 離散晶格**上的 site weight。
> Light, gravity, particles 都是這個晶格上的 collective excitations。

---

## 1. 晶格定義

### 1.1 基礎結構

W-field 的「時空」不是 4D manifold，而是張量積晶格：

```
L = Chain_N_d ⊗ Tree_M
```

| 子晶格 | 節點數 | 物理意義 | 連通性 |
|--------|:------:|---------|--------|
| **Chain** | N_d = 44 | 循環（對偶 88）= 一致性傳播維度 | 最近鄰 + 週期邊界 |
| **Tree** | M = h¹¹-3 = 33 | MERA coarse-graining 深度 = 能量/尺度維度 | 分支 B=4，每層向上 coarse-grain |

**總節點數:** N_d × (M+1) = 44 × 34 = 1496 個晶格點

### 1.2 鏈晶格（Chain Lattice）

一維循環鏈，88 個位置（N_d=44 對偶為 88）：

```
n=1 ─ n=2 ─ n=3 ─ ... ─ n=88 ─ back to n=1
```

鏈的 **離散 Laplacian**：
```
(Δ_chain W)_n = 2W_n - W_{n-1} - W_{n+1}
```

**特徵值（已知）:**
```
γ_n = 4 sin²(πn/88),  n = 1, 2, ..., 44
```

呢組特徵值**已經係晶格的駐波模式** — 唔係連續場的近似解，係**精確離散譜**。

### 1.3 樹晶格（MERA Tree Lattice）

深度 L = 53/8 層，每層分支 B=4：

```
Layer 0 (UV):     o  o  o  o  o  o  o  o  ...  (最細尺度)
                   \ /    \ /    \ /    \ /
Layer 1:           o      o      o      o  ...
                   \      / \      / \
Layer 2:           o            o      ...
...
Layer L (IR):      o  (MERA isometry U)
```

樹的 coarse-graining 由 MERA isometry 控制：
```
U = 1/√(φ²+1) · [φ  1; 1 -φ]
```

樹的「位置」由深度 m 決定，特徵值 μ_m = φ^{L-m}。

---

## 2. W-Field 離散作用量

### 2.1 完整 action（晶格版本）

```
S[W] = S_kin + S_pot + S_sync
```

#### 動能項（Chain 上的鄰居耦合）

```
S_kin = Σ_{⟨n,m⟩_chain} K_chain(n,m) · W_n · W_m
```

其中 K_chain 是 88×88 離散 Laplacian matrix：
```
K_chain(n,m) = 
  { 2        if n = m
  { -1       if |n-m| = 1 (mod 88)
  { 0        otherwise
```

**等價寫法：**
```
S_kin = Σ_n [ 2W_n² - W_n·W_{n+1} - W_n·W_{n-1} ]
```

#### 動能項（Tree 上的尺度耦合）

```
S_tree = Σ_{n,ℓ} B^{-ℓ} · (W_{n,ℓ} - U·W_{n,ℓ-1})²
```

其中：
- ℓ = tree depth layer
- U = MERA isometry（控制 fine→coarse 的投影）
- B⁻ℓ = 每層的 scale factor

#### 勢能項（每個 site 局部）

```
S_pot = Σ_n [ -ε |W_n|² + κ |W_n|⁴ ]
```

- ε = φ⁻¹/4 = 0.1545（pipeline gap）
- κ = 1/16 = 0.0625（branching factor）

**每個 site 獨立 — 無非局部項。**

#### Sync 耦合項

```
S_sync = Σ_{⟨n,m⟩} g_sync · cos(θ_n - θ_m - Δ_chain)
```

其中 θ_n = arg(W_n)，Δ_chain = 2π/88 = 特徵相位差。

---

### 2.2 座標化

W-field 的標準 Fourier 模：

```
W_n = Σ_{k=1}^{44} a_k · e^{2πi kn/88}
```

其中 a_k 是 Fourier 振幅。作用量在 Fourier 空間對角化：

```
S_kin = Σ_{k=1}^{44} γ_k · |a_k|²
```

**γ_k 就係晶格的能帶結構（dispersion relation）。**

---

## 3. 場方程（晶格版本）

從 δS/δW_n = 0 得到離散場方程：

### 3.1 自由場（無勢能）

```
(Δ_chain W)_n = (2W_n - W_{n-1} - W_{n+1}) = 0
```

齊次解 = 駐波：
```
W_n⁽⁰⁾ = A · sin(πkn/88 + φ₀)
```

### 3.2 加勢能

```
(Δ_chain W)_n + (-2ε + 4κ|W_n|²) · W_n = 0
```

這是一個**離散非線性 Schrödinger 方程**（DNLS）在循環晶格上。

### 3.3 Sync 傳播方程

```
∂ᵗ W_n = Σ_m K_chain(n,m) · W_m + sync_source_n
```

等價於：
```
∂ᵗ W_n = (2W_n - W_{n-1} - W_{n+1}) + sync_source_n
```

**這就是離散擴散/波動方程 — W-field 的「傳播」就是晶格上的 hopping。**

---

## 4. 重要推論

### 4.1 Light = Sync Wavefronts

光速 c 對應的 sync 波在晶格上的傳播速度：

```
v_sync = lim_{k→0} dγ_k/dk ≈ 2π · k/88 → 0 at long wavelength
```

不對。Sync wave 不是 chain 上的聲速。Light 對應的是 **tree dimension 上的 projection speed**。

更具體說法：

```
Light = W-field sync wave that satisfies:
  Δ_chain W + λ_tree · W = 0 (on-shell condition)
  
where λ_tree = MERA depth eigenvalue = φ^{L-m}
```

**光速 c 來自 tree 的粗粒化速度 = 每個 MERA 層的 RG flow rate。**

### 4.2 粒子 = Localized Lattice Excitations

粒子不是點，而是晶格上的**局域模**：
- Radial mode (Higgs) = site amplitude fluctuation（|W| 漲落）
- Phase mode (PG) = site phase mismatch（arg(W) 漲落）
- Fermions = K_chain 上特定 eigenmode 的 occupation

### 4.3 Gravity = Lattice Geometry

4D 時空幾何 = 晶格的**emergent low-energy 描述**：
- Metric g_μν = coarse-grained W-field correlation function
- Ricci curvature R =晶格配分函數的二次變分
- 暗能量 Ω_Λ = 4/(φ⁴-1) = **晶格的熱耗散成本**

---

## 5. 與已知 IDCM 公式的對應

| IDCM 公式 | 晶格語言 | 對應 |
|:----------|:--------|:----|
| ε = φ⁻¹/4 | Pipeline gap | **晶格能隙** |
| κ = 1/16 | Branching factor | **晶格耦合強度** |
| γ_n = 4 sin²(πn/88) | Laplacian eigenvalues | **晶格能帶結構** |
| B = 4 | MERA branch factor | **晶格配位數** |
| V_cb = φ²/64 | φ² = chain closure, 64 = B³ | **晶格對稱性結果** |
| Sync cost = 2 | Thermal cost | **晶格集體模的激活能** |
| JMP cost = 7 | Sector gap | **晶格拓撲缺陷的生成能** |
| CY₃(36,98) = 134 | Projector | **晶格的 Hodge 數** |

---

## 6. 開放問題

1. **晶格基態**：|W⟩ = 0 定係 |W⟩ ≠ 0？
   - 如果 ε < 0（structural），基態係 |W| = √(ε/2κ) ≠ 0 → **W-field 自發凝聚**
   - 意味晶格有非零平均權重 → **非平凡背景**

2. **晶格維度**：Chain × Tree × CY₃ projector = 幾維？
   - Naive: 1 (chain) + 1 (tree) + 0 (projector) = 2D
   - But CY₃ projector maps 134 → 4 → **emergent 4D?**

3. **連續極限**：當 N_d → ∞, L → ∞，是否 recover GR + SM？
   - N_d=44 係有限 → **沒有連續極限 → 晶格就是現實**

4. **光子 = 哪個 excitation?**
   - Sync wave on tree? Chain phase gradient?

---

## 總結

> **W-field 晶格不是 analog，是 literal。**
>
> K_chain(44,88) = 時空晶格的循環維度
> K_tree(MERA, B=4) = 尺度/能量維度
> W_n = 每個 site 的 consistency weight
> 所有物理現象 = 呢個晶格上的 collective excitations
> 4D 時空 = 粗粒化的 emergent 描述

下一步：數值驗證腳本。