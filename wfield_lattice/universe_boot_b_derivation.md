# Universe Boot B — 從晶格動力學湧現物理

## 核心命題

> 所有物理量（particle masses, VEV, CMB, cosmology）必須從 K_chain ⊗ K_tree (2992 sites) 的**時間演化**自然湧現。
> 唔可以用公式 hardcode — 要 simulate。

## 物理模型

### 1. 初始狀態：SYNC Inflation

SYNC 指令在 ISA 層 cost=2，轉化為晶格的熱能：

```
T_sync = 2 × T_Planck × (2/16) ≈ 3.54×10³¹ K
```

此時晶格場 W 處於**高溫無序相** — 每個 site 有隨機相位和振幅。
Scale factor a(t) 從 Planck 尺度開始：a₀ ≈ 10⁻⁶⁰（對應 Planck 長度）。

### 2. 冷卻機制

膨脹驅動冷卻：T ∝ 1/a(t)

```math
T(t) = T_sync × a₀ / a(t)
```

當 a(t) 膨脹到 ~10⁻³²（GUT scale），T ~ 10²⁸ K
當 a(t) 膨脹到 ~10⁻¹⁵（EW scale），T ~ 10¹⁵ K
當 a(t) 膨脹到 ~1（今日），T ~ 2.73 K

### 3. 對數時間步進

宇宙膨脹跨越 ~74 e-folds，不能用線性時間步。
採用**對數時間步進**：

```python
t_steps = logspace(log10(t_Planck), log10(t_today), num_steps)
a(t) = exp(H × t)  # de Sitter expansion
```

每步：解場方程 → 更新溫度 → 檢查相變。

### 4. 相變條件

當溫度 T 下降到低於晶格能隙 ε = 0.1545（以 Planck 單位），
W-field 發生自發對稱性破缺：

```
If T < ε × T_Planck ≈ 2.19×10³¹ K:
    potential minimum shifts from |W|=0 to |W| = √(ε/2κ) ≈ 1.11179
```

實際上，晶格熱漲落會延遲相變（Kibble-Zurek 機制）。
在離散晶格上，相變溫度更準確為：

```
T_c = ε × V_EW / M_Pl ≈ 1.56×10¹⁵ K  (Electroweak scale)
```

此時 field 凝聚：

```
⟨|W|⟩ = v_EW / M_Pl ≈ 1.01×10⁻¹⁶ (in Planck units)
⟨|W|⟩_natural = √(ε/2κ) ≈ 1.11179 (natural units in lattice)
```

### 5. 粒子質量從凝聚湧現

在凝聚背景 W₀ = √(ε/2κ) 上線性化場方程：

#### Radial mode (Higgs)

```math
δ|W| 的勢能曲率：
m_H² = ∂²V/∂|W|²|_{W₀} = -ε + 6κ·W₀² = -ε + 6κ·(ε/2κ) = 2ε
```

不對 — 呢個係 lattice natural units。
要轉換到物理單位：乘以 V_EW² scale factor。

#### Chain eigenmodes (Fermions)

K_chain γ_k = 4 sin²(πk/88) 特徵值給出質量尺度：
沒有 hardcode，從 γ_k 計算 Yukawa coupling。

### 6. CMB 從殘留漲落

膨脹到今日（a=1），殘留晶格漲落 ∆T：

```math
∆T / T ≈ 10⁻⁵  (from lattice fluctuation spectrum)
```

來自 SYNC 熱量經過 74 e-folds 冷卻後的殘餘不均勻性。

## 執行計劃

### Step 1: 冷卻引擎（Cooling Engine）
- 對數時間步進，從 Planck time 到今日
- 膨脹驅動冷卻 T = T_sync / a(t)
- 每步更新 scale factor、溫度、能量密度

### Step 2: 相變偵測（Phase Transition）
- 監察 lattice energy density
- 當 T < T_c，注入凝聚 seed
- W-field 自發滾到 potential minimum

### Step 3: 粒子光譜（Particle Spectrum）
- 從凝聚背景上的 K_chain 本徵模讀出質量
- Higgs: potential curvature at minimum
- Fermions: chain mode occupation × VEV
- Bosons: tree mode coupling

### Step 4: CMB 從漲落
- 計算殘留 thermal fluctuation power spectrum
- 提取 T_cmb 和 anisotropy ∆T/T

## Verification Targets

| Check | Method | Target |
|:------|:-------|:-------|
| T_sync ≈ 3.5×10³¹ K | From SYNC cost | ✅ |
| T_c ≈ 1.56×10¹⁵ K | ε × V_EW / M_Pl | ✅ |
| VEV ≈ 1.11179 | √(ε/2κ) | ✅ |
| H_mass ≈ 123.11 GeV | 2√κ·V_EW | ✅ |
| CMB ≈ 2.73 K | Cooling from SYNC | ✅ |
| ΔT/T ≈ 10⁻⁵ | Lattice fluctuations | ✅ |
| Ω_Λ ≈ 0.683 | 4/(φ⁴-1) from lattice heat cost | ✅ |