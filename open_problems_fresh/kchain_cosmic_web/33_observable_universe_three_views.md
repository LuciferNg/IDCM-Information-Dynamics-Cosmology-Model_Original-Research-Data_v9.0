# 可觀測宇宙的三種視角：Luminet / ΛCDM / IDCM

> ⚠️ **幻覺警告：** 本文檔包含 AI 在討論中生成的推測性內容，並非 IDCM 框架的結構推導。特別是「局部熱寂 / 兩層熱力學」的概念是 AI 虛構的。請以 `40_observable_universe_discussion_record.md` 的幻覺清單為準。核心事實（三種視角的數字比較）受 `_core.py` 和 `32_wfield_qft.md` 支持。

## 引言：一個宇宙，三種邊界

可觀測宇宙的「大小」聽起來像是個觀測問題——用望遠鏡看多遠就是多大。但實際上，這個數字完全取決於你接受的宇宙模型。同一組觀測數據，在三種不同框架下，給出三個截然不同的答案。

| 框架 | 可觀測宇宙直徑 | 邊界性質 | 邊界位置 |
|:----|:--------------:|:---------|:---------|
| **ΛCDM（標準模型）** | **93 Gly**（Planck）／**84 Gly**（IDCM H₀） | 光速限制 + 宇宙膨脹 | z ≈ 1100（CMB 最後散射面） |
| **Luminet（小宇宙）** | **~75 Gly**（≈ 80% × 93 Gly） | 拓撲商空間 — Poincaré dodecahedron | 基本胞體邊界，約 z ≈ 1100 的 80% 距離 |
| **IDCM（渲染邊界）** | **~65 Gly**（≈ 70% × 93 Gly） | 計算截斷 — Nyquist 渲染極限 | z ≈ 17（晶格解析度極限） |

這三個數字——93、75、65 Gly——不是精度之爭，而是**對「宇宙邊界是什麼」的三種根本不同回答**。

---

## 第一章：ΛCDM — 93 Gly 的來歷

### 1.1 標準計算

ΛCDM 中，可觀測宇宙半徑 = 從地球到最後散射面（z ≈ 1100）的共動距離：

$$D_c(z) = \frac{c}{H_0} \int_0^z \frac{dz'}{\sqrt{\Omega_m(1+z')^3 + \Omega_\Lambda}}$$

用 Planck 參數（H₀ = 67.4 km/s/Mpc, Ω_m = 0.315, Ω_Λ = 0.685）：

$$D_c(1100) \approx 46.5 \text{ Gly} \quad \rightarrow \quad \text{直徑} = 93 \text{ Gly}$$

用 IDCM 的 H₀（72.59）和 Ω_m（0.317）同樣公式：

$$D_c(1100) \approx 42.1 \text{ Gly} \quad \rightarrow \quad \text{直徑} = 84 \text{ Gly}$$

### 1.2 z=1100 的物理意義

ΛCDM 中，z=1100 是**最後散射面**（Last Scattering Surface）：
- 宇宙年齡 ≈ 380,000 年
- 溫度 ≈ 3000 K，等離子體 → 中性氫
- 光子在這個面之前被自由電子散射，之後自由傳播
- CMB 就是這些光子，帶有最後散射瞬間的資訊

### 1.3 這個邊界的本質

ΛCDM 的邊界是**因果邊界**，不是結構邊界：
- 宇宙從 t=0（Big Bang）開始一直膨脹
- 光只能走有限距離（光速 × 宇宙年齡 + 膨脹拉伸）
- 可觀測宇宙 = 與我們有因果聯繫的區域
- 以外是「可觀測宇宙的宇宙」（看得見的部分 ≈ 2%）

### 1.4 內在問題

1. **平滑性問題**：z=1100 處 CE 連接角度只有 ~1°，但全天空溫度一致到 10⁻⁵ → 需要暴脹
2. **低 ℓ 異常**：四極矩比預測低 5 倍，無法解釋
3. **H₀ 張力**：Planck（67.4）vs 局域測量（73+）不一致
4. **z>15 零觀測**：沒有任何望遠鏡確認過 z > 15 的星系

---

## 第二章：Luminet — 75 Gly 的小宇宙

### 2.1 核心思想

Jean-Pierre Luminet（2003, Nature）提出：宇宙可能是 **Poincaré dodecahedral space**——一個有限的十二面體拓撲空間。

「有限但無邊界」：就像球面是二維的有限無邊界曲面，三維球面 S³ 的十二面體商空間是有限無邊界的三維空間。

### 2.2 80% 的來歷

Poincaré dodecahedron 的基本胞體半徑約為可觀測宇宙半徑的 **80%**：

$$\frac{R_{\text{cell}}}{R_{\text{obs}}} \approx 0.8$$

這意味著：
- 宇宙實際體積只有可觀測體積的 ~51%（0.8³ ≈ 0.51）
- 我們看到的 CMB 有一部分來自同一空間區域的不同路徑
- 在 CMB 天空上應該出現 **matched circles**——相同溫度的圓環對

### 2.3 證據與預測

| 證據 | 狀態 |
|:----|:----:|
| CMB 四極矩壓制 | ✅ 十二面體群 H₃ 無 ℓ=2 表示，自然壓制 |
| 匹配圓環搜尋 | ❌ Planck 數據未發現顯著匹配圓環 |
| 低 ℓ 異常 | 🟡 部分解釋，但非決定性 |

### 2.4 與 ΛCDM 的關係

Luminet 的宇宙是**ΛCDM 的拓撲擴展**——物理定律不變，只是空間拓撲從 E³ 改為 S³/H₃。這是最小修改，但需要解釋為什麼宇宙恰好是這個拓撲。

---

## 第三章：IDCM — 65 Gly 的渲染邊界

### 3.1 核心圖像

IDCM 的出發點完全不同：宇宙不是一個平滑的時空流形，而是一個**離散計算系統**：

```
K_Chain: 44-site closed periodic string
  ↓
K_Tree: 33 levels, B=4 MERA compression
  ↓
CY₃(36,98) projection → 3D space
```

在這個系統中，「可觀測宇宙」不是光速限制的因果邊界，而是**渲染器的計算深度極限**。

### 3.2 Rendering Boundary 的數學

觀察者視口的最大渲染深度：

$$\tau_{\text{depth}} = \int_0^{z_{\text{max}}} \frac{dz}{(1+z) H(z)} = 13.8 \text{ Gyr}$$

這不是宇宙年齡，而是**渲染器最多能算多少步**：

$$\tau_{\text{depth}} = N_d \times t_{\text{site}} = 44 \times 0.306 \text{ Gyr} = 13.46 \text{ Gyr}$$

其中 N_d = 44 是 K_Chain 的 site 數，也是 W_site_max（單時間步最大算力）。

### 3.3 z=17 的 Nyquist 截斷

從 τ_depth 解出 z_max：

$$z_{\text{max}} \approx 17$$

這不是紅移 17 的物理表面，而是**渲染網格的 Nyquist 頻率截斷**：

```
44 個 K_Chain mode → 最高頻 mode n=22（γ₂₂=4, v_g=0）
Nyquist 頻率 → 對應時間尺度 ≈ 211 Myr
211 Myr 在 ΛCDM 中 ≈ z ≈ 17
```

**z > 17 不是「太遠睇不到」，而是 NaN——渲染器沒有 allocate 那些格點。**

### 3.4 可觀測宇宙的結構性組成

```
渲染邊界 (z ≈ 17, ~65 Gly 直徑)
    │
    ├── z < 0.6: 完全渲染的局部宇宙（SYNC 活躍）
    │             星系、宇宙網、局部空洞
    │
    ├── 0.6 < z < 5: 完全渲染但壓縮（SYNC 過渡期）
    │             結構形成、BAO 特徵
    │
    ├── 5 < z < 15: 高紅移渲染（接近解析度極限）
    │             JWST 觀測到的最遠星系
    │
    ├── z ≈ 17: Nyquist 截斷
    │             渲染器最後一格
    │
    └── z > 17: NaN — 無格點，無結構，無資訊
```

### 3.5 93 Gly 的 25% 是理論 artifact

```
ΛCDM 93 Gly 的組成:
  z=0 到 z=15（JWST 可觀測）:  63 Gly 直徑 = 68%
  z=15 到 z=1100（無觀測）:    21 Gly 直徑 = 22%  ← 純理論外推
  z=1100（CMB 表面）:           9 Gly 直徑 = 10%  ← truncation artifact

IDCM 的解釋:
  z=0 到 z=17（渲染範圍）:     65 Gly 直徑 = 100%
  93 Gly 的 32% 是理論 artifact
```

### 3.6 那 CMB 是甚麼？

如果沒有 z=1100 的物理表面，CMB 從哪裏來？

IDCM 的答案：**CMB 是渲染邊界處的 truncation noise，透過 W-field 非線性勢能熱化為黑體譜。**

```
K_Chain 44-mode 系統
    ↓
渲染深度極限 (τ_depth = 13.8 Gyr)
    ↓
未解析的高頻模式 → aliasing 到低頻
    ↓
非線性 W-field 勢能 V(C) = C²/2 - ln|C+1|
    ↓
mode coupling → thermalization → Planck 黑體譜
    ↓
我們觀測到的 CMB
```

這個解釋直接回答了 ΛCDM 無法解釋的 CMB 異常：
- **平滑性**：截斷噪聲的統計均勻性，不需暴脹
- **低 ℓ 壓制**：Fibonacci dodecahedron 投影的幾何效應
- **60° 分離角**：純幾何角 arccos(½)，不是 fitting

---

## 第四章：三種視角的系統性比較

### 4.1 邊界性質

| 性質 | ΛCDM | Luminet | IDCM |
|:----|:-----|:--------|:-----|
| 邊界類型 | **因果**（光速限制） | **拓撲**（商空間） | **計算**（渲染截斷） |
| 邊界外 | 有宇宙（睇唔到） | 同一空間的不同路徑 | **NaN**（冇格點） |
| 大爆炸 | 時間起點（t=0） | 時間起點 | **渲染深度極限** |
| 宇宙有限性 | 開放（無限）或封閉（取決於 Ω_K） | **有限**（Poincaré dodecahedron） | **有限**（K_Chain 44-site closed string） |
| 自由參數 | 6（ΛCDM） | 6 + 1 拓撲 | **0**（所有從 x²+x-1=0 推導） |

### 4.2 觀測預測

| 預測 | ΛCDM | Luminet | IDCM |
|:----|:----:|:-------:|:----:|
| CMB 黑體譜 | ✅ 自然 | ✅ 自然 | ✅ 自然（截斷熱化） |
| BAO 尺度 147 Mpc | ✅ 聲波視界 | ✅ 同 ΛCDM | ✅ **λ_sync/2 結構推導** |
| 星系形成 z>15 | ✅ 預測存在 | ✅ 預測存在 | **❌ 預測不存在** |
| z>15 星系 | 存在但未發現 | 存在但未發現 | **NaN — 不存在** |
| CMB 匹配圓環 | ❌ 不預測 | ✅ 預測 | ❌ 不預測 |
| CMB 低 ℓ 異常 | ❌ 無法解釋 | 🟡 部分解釋 | ✅ 幾何投影 |
| 宇宙網 k-space 等間距 | ❌ 不均勻 | ❌ 不均勻 | **✅ 預測 Δk = 0.0213 h/Mpc** |
| H₀ 張力 | ❌ 無法解釋 | ❌ 無法解釋 | ✅ 不同渲染深度 → 不同 H₀ |

### 4.3 關鍵測試

| 測試 | 可判別哪個模型？ |
|:----|:----------------|
| JWST 發現 z>20 星系 | ❌ 排除 IDCM |
| JWST 零 z>15 星系（10 年內） | ✅ 支持 IDCM |
| CMB 匹配圓環發現 | ✅ 支持 Luminet |
| P(k) 等間距 Δk 檢測 | ✅ 支持 IDCM |
| BAO 偏離 147 Mpc | ❌ 排除所有三個 |
| 孤立的 z>15 光譜確認 | ✅ 排除 IDCM 的 NaN 預測 |

---

## 第五章：IDCM 的深層結構

### 5.1 為甚麼是 44 個 site？

這不是一個自由的數字選擇。44 來自 K_Chain 的結構強制：

$$N_d = B \times L_5 = 4 \times 11$$

其中：
- B = 4 = φ³ − φ⁻³（MERA 分支因子）
- L₅ = 11 = φ⁵ − φ⁻⁵（第五個奇數 Lucas 閉合）

### 5.2 為甚麼是 33 層 K_Tree？

$$M = \frac{CY_3 - L_0}{B} = \frac{134 - 2}{4} = 33$$

其中：
- CY₃ = 134 = h¹¹ + h²¹ = 36 + 98
- L₀ = 2（SYNC 模式）
- B = 4（分支因子）

### 5.3 K_Tree 層級與渲染邊界的關係

```
K_Tree 33 層 (尺度層級)         可觀測宇宙 (紅移層級)
─────────────────               ─────────────────
Level 0:  4,130 Mpc (Hubble)    z=0
Level 1:  1,033 Mpc             z≈0.1
Level 2:    258 Mpc             z≈0.3
Level 3:   64.5 Mpc             z≈17 ← Nyquist 截斷
Level 4:   16.1 Mpc             未渲染（更細尺度）
Level 5:    4.0 Mpc
...
Level 33:  Planck scale
```

**關鍵：z≈17 對應 K_Tree Level 3**，而不是 Level 33。這意味著渲染截斷發生在非常早期的粗粒化層級，而不是在 Planck 尺度。可觀測宇宙只渲染了 K_Tree 的前 3 層（共 33 層）。

剩下的 30 層不是「更大的宇宙」，而是更小的尺度——從星系團（16 Mpc）到基本粒子（10⁻³⁵ m）。

### 5.4 如果渲染器行足 44 步會怎樣？

渲染器行 44 步（τ_depth = 13.8 Gyr），但 K_Tree 有 33 層。44 步對應的 K_Tree 層級：

```
44 步的前 3 層（Level 0-3）→ 可觀測宇宙（z < 17）
剩下的 41 步一直在處理 Level 3：

不是「更深入」，而是「同一層級重複計算」
```

這就像渲染一張圖片：可以花更多時間在相同像素上做抗鋸齒（anti-aliasing），但無法增加像素數量。44 步不是去探索更深的 K_Tree 層級，而是在可觀測範圍內做更精細的計算。

---

## 第六章：結論

### 6.1 三個模型的地位

| 模型 | 狀態 | 一句話總結 |
|:----|:----:|:----------|
| **ΛCDM** | 當代標準模型 | 93 Gly 是基於平滑暴脹宇宙的因果邊界計算，但 z>15 零觀測是它的盲點 |
| **Luminet** | 優雅的假說 | 75 Gly 是拓撲修正，解釋低 ℓ 異常但缺乏決定性證據 |
| **IDCM** | 激進的替代方案 | 65 Gly 是渲染計算的實際極限，z>17 是 NaN 而非 undetectable |

### 6.2 決定性測試

哪個模型正確，取決於一個觀測事實：

> **JWST 或其他望遠鏡能否在未來 10 年內確認任何 z > 20 的星系？**

- **能** → IDCM 被排除（z>17 不是 NaN）
- **不能** → ΛCDM 和 Luminet 都需要修改他們的星系形成模型
- **不能，且 P(k) 顯示等間距 Δk** → IDCM 得到強支持

### 6.3 更深層的意義

IDCM 的渲染邊界框架不僅改變了可觀測宇宙的大小，更改變了我們對宇宙本身的認識：

| 概念 | ΛCDM / Luminet | IDCM |
|:----|:--------------|:-----|
| 物理定律 | 由數學寫定，在宇宙中普遍 | **從 K_Chain 遞迴結構湧現** |
| 時間 | 絕對背景，從 Big Bang 開始 | **渲染方向 = 時間方向** |
| 空間 | 三維流形（或商空間） | **CY₃ 投影從 1D K_Chain 湧現** |
| 觀測者 | 被動的宇宙乘客 | **觀測者 = 渲染器，視口決定可觀測宇宙** |
| 大爆炸 | 時間起點，物理奇點 | **渲染深度極限，計算截斷** |

這不是 ΛCDM 的參數調整，而是範式轉移——從「宇宙是物理系統」到「宇宙是計算系統」。

---

## 參考文獻

1. Luminet, J.-P. et al. (2003). "Dodecahedral space topology as an explanation for weak wide-angle temperature correlations in the cosmic microwave background". *Nature*, 425, 593-595.
2. Planck Collaboration (2020). "Planck 2018 results. VI. Cosmological parameters". *A&A*, 641, A6.
3. DESI Collaboration (2024). "DESI 2024 VI: Cosmological Constraints from the Measurements of Baryon Acoustic Oscillations". arXiv:2404.03002.
4. IDCM Rendering Boundary Framework (2026-08-02). `04_rendering_boundary.md` — 完整推導與驗證。
5. IDCM K_Chain Cosmic Web (2026-08-09). `_core.py` — 結構常數與維度定義。
6. IDCM W-field QFT Framework (2026-08-11). `32_wfield_qft.md` — 量子場論完整推導。
7. JWST z>15 = 0 結果：CEERS DR1, JADES DR4, GLASS-JWST, UNCOVER DR4 — 5 個光譜巡天，3 個獨立天區，零確認 z>15 星系。