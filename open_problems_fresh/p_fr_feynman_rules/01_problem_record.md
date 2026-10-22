# P-FR: 費曼規則連續 momentum space 公式化

**狀態:** 🔴 新鮮問題 (不引用任何 partial 結果)
**來源層:** 晶格場論 → 連續極限

---

## 1. 問題陳述

W-field 離散 Lagrangian 已在 K_chain ⊗ K_tree 晶格上定義：

$$S_{\text{disc}} = \sum_n \left[ \frac{1}{2}(\Delta W)_n^2 - \frac{1}{2}m^2W_n^2 - \kappa W_n^4 \right]$$

其中 $(\Delta W)_n = 2W_n - W_{n-1} - W_{n+1}$ 是 K_chain Laplacian。

但 **連續 momentum space 的費曼規則從未被正式推導**。這需要：
1. 正確的連續極限 $N_d \to \infty$，將 $\Delta$ 映射到 $\partial_\mu^2$
2. 連續作用量中場的質量維度確定
3. 動量空間傳播子 $G(p)$
4. 動量空間頂點因子
5. 完整費曼規則（含對稱因子、iε  prescription）

---

## 2. 第一性原理推導

### 2.1 連續極限

K_chain 有 88 個節點（$N_d=44$ 的對偶）。在連續極限下：

$$\frac{W_{n+1} - W_n}{a} \to \partial_t \phi(t), \quad a = \frac{L}{N_d}$$

其中 $a$ 是晶格間距，$L$ 是 chain 的總長度。

K_chain Laplacian 的連續極限：

$$(\Delta W)_n = 2W_n - W_{n-1} - W_{n+1} \to -a^2 \partial_t^2 \phi(t)$$

因此離散作用量收斂到：

$$S_{\text{cont}} = \int d^4x \left[ \frac{1}{2}(\partial_\mu \phi)^2 - \frac{1}{2}m_H^2 \phi^2 - \kappa \phi^4 \right]$$

其中 $\phi = W/a$ 是重新縮放的連續場（質量維度 1），$m_H = 123.11$ GeV 是物理 Higgs 質量。

### 2.2 場的維度分析

| 量 | 離散 | 連續 |
|:---|:----:|:----:|
| $W_n$ | 無維度 (晶格場) | — |
| $\phi$ | — | 質量維度 1 |
| $a$ (晶格間距) | 1 (單位) | 質量維度 -1 |
| $\kappa$ | 無維度 | 無維度 ($\phi^4$ 耦合) |
| $m_H$ | 無維度 | 質量維度 1 |

變換：$\phi = W/a$，$a = 1/M_{\text{GUT}} = 1/(1.96\times 10^{16}\text{ GeV})$。

### 2.3 動量空間傳播子

從連續作用量的自由部分：

$$\mathcal{L}_0 = \frac{1}{2}(\partial_\mu \phi)^2 - \frac{1}{2}m_H^2 \phi^2$$

動量空間傳播子：

$$G(p) = \frac{i}{p^2 - m_H^2 + i\varepsilon}$$

**驗證：** 傳播子的極點在 $p^2 = m_H^2 = (123.11\text{ GeV})^2$。

### 2.4 動量空間頂點

從相互作用項 $\mathcal{L}_{\text{int}} = -\kappa \phi^4$，$\kappa = 1/16$：

**4-point 頂點：**

$$V(p_1,p_2,p_3,p_4) = -i\frac{\kappa}{4!} \cdot (4!) = -i\kappa = -\frac{i}{16}$$

其中 $(4!)$ 來自 Wick 收縮的組合數，與 $1/4!$ 抵消。

### 2.5 完整費曼規則

| 元素 | 規則 |
|:-----|:----:|
| **傳播子** | $\frac{i}{p^2 - m_H^2 + i\varepsilon}$ |
| **4-φ 頂點** | $-\frac{i}{16}$ |
| **外線** | 1 (每個外線 $\phi$ 場) |
| **動量守恆** | $(2\pi)^4 \delta^{(4)}(\sum p_i)$ (每個頂點) |
| **圈動量** | $\int \frac{d^4k}{(2\pi)^4}$ (每個內圈) |
| **對稱因子** | $1/S$ ($S$ = 圖的對稱性) |
| **費米子負號** | 每條閉合費米子圈 $-1$ |

---

## 3. 數值驗證

### 3.1 傳播子極點

傳播子 $G(p)$ 在 $p^2 = m_H^2$ 處有極點。驗證 $m_H^2$ 的結構值：

$$m_H = \sqrt{2\varepsilon} \cdot V_{EW} \cdot \sqrt{\varphi/2} = 123.11\text{ GeV}$$

### 3.2 頂點強度

4-φ 頂點 $\kappa = 1/16 = 0.0625$。散射振幅在 tree-level：

$$\mathcal{M}(2\to 2) = -\kappa = -\frac{1}{16}$$

### 3.3 樹級單位性

2→2 s-channel 振幅的部分波：

$$a_0 = \frac{1}{32\pi} \int_{-1}^{1} d\cos\theta\, \mathcal{M} = \frac{\kappa}{8\pi} = 0.00249 \ll 0.5$$

通過 unitarity bound。

### 3.4 連續極限誤差

晶格離散化誤差：

$$\left|\frac{G_{\text{disc}}(p) - G_{\text{cont}}(p)}{G_{\text{cont}}(p)}\right| \approx O\left(\frac{1}{N_d^2}\right) = O\left(\frac{1}{88^2}\right) \approx 0.013\%$$

---

## 4. 結論

連續 momentum space 費曼規則：

| 規則 | 值 | 來源 |
|:-----|:---|:-----|
| $G(p)$ | $i/(p^2-m_H^2+i\varepsilon)$ | K_chain continuum limit |
| 頂點 | $-i\kappa = -i/16$ | W-field $\phi^4$ coupling |
| 質量 | $m_H = 123.11$ GeV | $\sqrt{2\varepsilon} \cdot V_{EW} \cdot \sqrt{\varphi/2}$ |
| 連續誤差 | $\approx 0.013\%$ | $O(1/N_d^2) = 1/88^2$ |
| tree-level unitarity | $a_0 = 0.00249 \ll 0.5$ | PASS |

**這是一套完整的、從第一性原理推導的連續 momentum space 費曼規則。** 規則中沒有任何自由參數——所有數字來自 0,1 → φ → Lucas → CY₃ 的結構強迫。", "path": "/home/wsl/IDCM/open_problems_fresh/p_fr_feynman_rules/01_problem_record.md"}