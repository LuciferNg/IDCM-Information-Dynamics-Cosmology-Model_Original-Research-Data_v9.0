# W-field 量子動力學 — 從遞迴結構推導宇宙重啟時間

> 📖 **完整量子場論框架：** [`32_wfield_qft.md`](32_wfield_qft.md) — 包含 Lagrangian、正則量子化、模式展開、路徑積分、bounce 解、奇點正則化等完整推導。本文件為簡化摘要。

## 第一原理

從 0,1 出發：

```
x² + x - 1 = 0 → φ
  → ε = φ⁻¹/4
  → κ = (εφ)² = 1/16
  → N_d = 44 (K_Chain sites)
  → M = 33 (K_Tree depth)
  → L3 = 4 (branching factor)
```

## W-field 勢能

### 遞迴動力學

遞迴：$C_{n+1} = 1/(1 + C_n)$

連續極限：
$$\frac{dC}{dt} = \frac{1}{1+C} - C = -\frac{C^2 + C - 1}{1+C} = -\frac{(C - \varphi^{-1})(C + \varphi)}{1+C}$$

固定點：
- $C = \varphi^{-1} \approx 0.618$（穩定，吸引子）
- $C = -\varphi \approx -1.618$（不穩定，排斥子）
- $C = -1$（奇點，不可穿越）

### 勢能積分

$$\frac{dC}{dt} = -\frac{dV}{dC}$$

$$V(C) = \int \frac{(C - \varphi^{-1})(C + \varphi)}{1+C} dC = \int \left[C - \frac{1}{C+1}\right] dC$$

$$V(C) = \frac{C^2}{2} - \ln|C+1| + \text{const}$$

設 $V(\varphi^{-1}) = 0$：

| 位置 | V(C) | 意義 |
|:----|:----:|:-----|
| $C = \varphi^{-1}$ | 0 | 真空（吸引子） |
| $C = 0$ | 0.290 | 勢壘到 C=0 |
| $C = -\varphi$ | 2.080 | 不穩定固定點 |
| $C = -1$ | $\infty$ | 奇點（不可穿越） |

### 勢能形狀

```
V(C)
  ^
  |            ____
  |          /      \
  |        /          \
  |      /              \
  |    /                  \
  |  /                      \
  |/                          \
  +----|---|------|------|------|----> C
     -1.618  -1      0   0.618
     勢壘頂   奇點   中間   真空
```

## 量子漲落（QFT 框架）

> ⚠️ **修正：** 舊版文件將 $\sqrt{\kappa}=0.25$ 直接視為量子漲落幅度，但 $\kappa$ 是四階耦合常數，**不是**場漲落幅度。正確的量子漲落由 harmonic oscillator 基態給出（見 [`32_wfield_qft.md`](32_wfield_qft.md) §3.2）。

$$ \kappa = \frac{1}{16} \quad \text{(四階耦合常數，非直接漲落)} $$

真空附近 harmonic 展開：

$$ V(C) \approx \frac{1}{2} V''(\varphi^{-1})(C - \varphi^{-1})^2 $$

$$ V''(\varphi^{-1}) = 1 + \frac{1}{(\varphi^{-1}+1)^2} = 1.382 $$

$$ \omega_0 = \sqrt{V''(\varphi^{-1})} = 1.176 $$

**量子漲落幅度（harmonic oscillator 基態）：**

$$ \langle\Delta\phi^2\rangle = \frac{1}{2\omega_0} = 0.425 $$

$$ \sqrt{\langle\Delta\phi^2\rangle} = 0.652 \quad \text{(約為 } \sqrt{\kappa}=0.25 \text{ 的 2.6 倍)} $$

**44-mode 晶格場平均：**

$$ \sqrt{\langle\Delta\phi^2\rangle}_{\text{lattice}} = \sqrt{\frac{1}{N_d}\sum_{k=1}^{44}\frac{1}{2\omega_k}} = 0.540 $$

## WKB 穿隧（QFT 框架）

### 單 site 穿隧

穿隧路徑：$\varphi^{-1} \to 0$

WKB 指數（Simpson 數值積分，見 [`32_wfield_qft.py`](32_wfield_qft.py)）：

$$ S_{\text{WKB}} = \int_0^{\varphi^{-1}} \sqrt{2V(C)} \, dC = 0.231177 $$

$$ S_B^{(1)} = 2 \times S_{\text{WKB}} = 0.462354 $$

單 site bounce 作用量 $S_B^{(1)} = 0.462$。

單 site 重啟時間：

$$ t_{\text{restart}} = \tau_0 \cdot e^{S_B^{(1)}} = 0.486 \text{ Gyr}$$

但呢個太短（地球已 4.6 Gyr），因為宇宙係 44-site 系統，唔係單 site。

### 真空穩定性（QFT 框架）

量子漲落幅度 $\sqrt{\langle\Delta\phi^2\rangle} = 0.652$ 與勢壘高度 $\Delta V = 0.290$ 比較：

$$ \frac{\Delta V}{\sqrt{\langle\Delta\phi^2\rangle \, V''(\phi_0)}} = \frac{0.290}{0.652 \times 1.176} = 0.379 $$

比值 < 1 → **真空不穩定**，量子漲落足以觸發逃逸（見 [`32_wfield_qft.md`](32_wfield_qft.md) §3.3-3.4）。

### 集體穿隧（44-site uniform + 梯度）

K_Chain 梯度項增加勢壘：
$$\mathcal{L} = \sum_n \left[\frac{1}{2}(\partial_t \varphi_n)^2 - \frac{1}{2}\gamma_n(\varphi_n - \varphi_{n-1})^2 - V(\varphi_n)\right]$$

$$\gamma_n = 4\sin^2\left(\frac{\pi n}{88}\right)$$

$$\langle \gamma_n \rangle = 2.0$$

$$\frac{1}{2}\langle\gamma\rangle(\Delta\varphi)^2 = 0.382$$

| 量 | 無梯度 | 有梯度 |
|:---|:-----:|:-----:|
| 勢壘高度 | 0.290 | 0.672 |
| 2S_eff | 0.462 | 0.711 |
| 44-site 2S_eff | 20.34 | 31.29 |
| t_restart | 2.09 × 10⁸ Gyr | 1.18 × 10¹³ Gyr |

### 最終結果

| 機制 | 2S | $t_{\text{cycle}}$ | 來源 |
|:----|:--:|:------------------:|:-----|
| **WKB 44-site uniform** | **20.34** | **$2.09 \times 10^8$ Gyr** | 最佳估計（QFT 框架） |
| WKB 44-site + 梯度 | 31.29 | $1.18 \times 10^{13}$ Gyr | 保守估計（含梯度修正） |
| Gaussian 漲落 | 20.94 | $7.64 \times 10^8$ Gyr | 量子漲落主導逃逸 |
| 舊結構 $1/\kappa$ | 16 | $2.72 \times 10^6$ Gyr | 粗估（已淘汰） |

其中 $\tau_0 = t_{\text{site}} = R_H/(44c) = 0.306$ Gyr，$t_{\text{cycle}} = \tau_0 \cdot e^{2S}$。

精確 bounce 作用量來自 QFT 框架（見 `32_wfield_qft.md` §5-7）：

$$ S_B^{(44)} = N_d \times 2 \times S_{\text{WKB}} = 44 \times 0.462354 = 20.344 $$

$$ S_B^{\text{grad}} = 44 \times 2 \times S_{\text{eff}} = 31.286 $$

## 時間尺度比較

| 尺度 | 時間 | 備註 |
|:----|:----:|:-----|
| 宇宙年齡 | 13.8 Gyr | — |
| 地球年齡 | 4.6 Gyr | 遠小於重啟時間 ✅ |
| SYNC 相位週期 | 26.94 Gyr | 宇宙網季節 |
| 紅矮星壽命 | 10⁴ Gyr | 在重啟前死亡 ✅ |
| **循環時間 t_cycle** | **1.18 × 10¹³ Gyr** | **宇宙重啟週期** |
| 熱寂（3D 投影） | ~10¹⁰⁰ yr | 可經歷多次重啟 |

## 循環次數

$$\frac{\text{熱寂時間}}{t_{\text{cycle}}} = \frac{10^{100} \text{ yr}}{1.18 \times 10^{22} \text{ yr}} = 8.5 \times 10^{77} \text{ 次循環}$$

## 每次循環

1. 熱寂（遞迴收斂至 $\varphi^{-1}$）
2. W-field 量子漲落累積
3. 集體穿隧越過勢壘
4. 逃離 $\varphi^{-1}$ 吸引子
5. $C_{n+1} = 1/(1+C_n)$ 重新收斂
6. $\varepsilon$、$\kappa$ 重新生成
7. 新宇宙誕生

## 關鍵假設

1. W-field 勢能來自遞迴 $C_{n+1} = 1/(1+C_n)$ 的連續極限，精確
2. WKB 穿隧為半經典近似，指數 $\pm 10\%$
3. 44-site 集體穿隧假設所有 site 同時穿隧，保守估計
4. K_Chain 梯度項使用平均 $\gamma_n$，實際需 mode-by-mode 計算
5. K_Tree 多層次修正未包含（會增加重啟時間）
6. 量子場論框架（`32_wfield_qft.md`）已完成 Lagrangian → 真空衰變率的完整推導鏈，包括：
   - 正則量子化與 44 模式對角化
   - 路徑積分表述與 bounce 解
   - 奇點正則化證明
   - 三種逃逸機制比較（uniform bounce、梯度修正、Gaussian 漲落）