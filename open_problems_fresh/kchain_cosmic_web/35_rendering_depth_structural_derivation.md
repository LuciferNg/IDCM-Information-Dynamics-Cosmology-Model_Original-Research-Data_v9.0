# 渲染深度與 z=17 Nyquist 截斷的結構推導

## 核心問題

K_Chain 永恆 ←→ 渲染深度有限 (13.8 Gyr) 嘅張力。

## 第一步：τ_depth 係因果視界，唔係宇宙年齡

### 結構推導

K_Chain = 44-site closed periodic string，從 x²+x-1=0 推導。

**t_site** = 相鄰 site 嘅光傳播時間：
$$t_{\text{site}} = \frac{R_H}{44c} = \frac{1}{44H_0} = 0.306 \text{ Gyr}$$

**τ_depth** = 光環繞 K_Chain 環一圈嘅時間：
$$\tau_{\text{depth}} = 44 \times t_{\text{site}} = \frac{1}{H_0} = 13.46 \text{ Gyr}$$

| 量 | 公式 | 值 |
|:--|:-----|:--:|
| site spacing | a = R_H/44 | 93.9 Mpc |
| t_site | a/c | 0.306 Gyr |
| **τ_depth** | **44 × t_site** | **13.46 Gyr** |
| 1/H₀ | Hubble time | 13.47 Gyr (±0.045%) |

**結論：τ_depth 係 K_Chain 環的 light-crossing time，即係因果視界。唔係「宇宙年齡」— 而係「環有幾大」。**

### 類比

一個圓周長 13.46 光年嘅環：
- 光環繞一圈 = 13.46 年（因果視界）
- 問「個環有幾老？」係 category error — 環係幾何結構，13.46 年係周長，唔係年齡

---

## 第二步：z=17 係 Nyquist 截斷，唔係時間邊界

### 結構推導

K_Chain 44-site 離散化 → 離散 Laplacian 本徵值：
$$\gamma_n = 4 \sin^2\left(\frac{\pi n}{88}\right), \quad n = 0,1,\dots,87$$

Mode n=22（half-Nyquist）：
$$\gamma_{22} = 4 \sin^2\left(\frac{22\pi}{88}\right) = 4 \sin^2\left(\frac{\pi}{4}\right) = 2$$

Characteristic time：
$$\tau_{22} = \frac{t_{\text{site}}}{\sqrt{\gamma_{22}}} = \frac{t_{\text{site}}}{\sqrt{2}} = \frac{0.306}{\sqrt{2}} = 216.4 \text{ Myr}$$

**216.4 Myr 喺 ΛCDM 中對應幾多紅移？**

| 紅移 | Universe Age |
|:----:|:-----------:|
| z=15 | 248.7 Myr |
| **z=16.55** | **216.4 Myr** |
| z=17 | 208.3 Myr |
| z=18 | 192.1 Myr |

**→ t_site/√2 ≈ 216 Myr 對應 ΛCDM z ≈ 16.55 ≈ 17**

### Nyquist 截斷的物理意義

```
K_Chain 44-site 離散化
  ↓
Mode n=22: γ_22 = 2, characteristic time = t_site/√2 = 216 Myr
  ↓
呢個係 K_Chain 離散結構可以 resolve 嘅最短時間尺度
  ↓
ΛCDM 中呢個時間尺度對應 z ≈ 17
  ↓
z > 17: K_Chain 嘅離散時間結構無法被 K_Tree 分辨
  ↓
z > 17 = NaN（無格點）
```

### 同 K_Tree 嘅關係（一致性檢查）

K_Tree ℓ = log₄(1+z)：
- ℓ=2.00 (z=15): scale = 258 Mpc, 覆蓋 2.75 個 K_Chain sites
- ℓ=2.08 (z=17): scale = 229 Mpc, 覆蓋 2.44 個 K_Chain sites
- ℓ=2.23 (z=21): scale = 206 Mpc, 覆蓋 2.09 個 K_Chain sites（空間 Nyquist）
- ℓ=2.73 (z=43): scale = 94 Mpc, 覆蓋 1.00 個 K_Chain site（空間完全解析）

z=17 嘅空間 Nyquist 條件：ℓ ≥ log₄(22) = 2.23 → z ≥ 21

**所以 z=17 嘅截斷唔係空間 Nyquist（嗰個係 z≈21）。** z=17 係**時間 Nyquist** — K_Chain mode n=22 嘅 characteristic time = 216 Myr 對應嘅紅移。

---

## 第三步：張力消失

### 兩個面向，同一個結構

```
┌─────────────────────────────────────────────────────────────┐
│                 K_Chain 44-site 閉環                          │
│              (從 x²+x-1=0 推導，無時間參數)                    │
│                      │                                        │
│          ┌───────────┴───────────┐                            │
│          │                       │                            │
│     因果視界                    Nyquist 截斷                    │
│     (τ_depth)                  (z=17)                         │
│          │                       │                            │
│ 光環繞 44 步所需時間      K_Chain mode n=22 嘅                  │
│ 44 × t_site = 13.46 Gyr   characteristic time                  │
│ = 1/H₀                    t_site/√2 = 216 Myr                  │
│          │                       │                            │
│ 答案: 「有幾遠」           答案: 「有幾清」                      │
│ (how far)                (how resolved)                       │
│          │                       │                            │
│ K_Chain 環的周長          K_Chain 環的離散像素                  │
│ = 13.46 光年              = 44 格                             │
└─────────────────────────────────────────────────────────────┘
```

### 無矛盾

| Claim | 類型 | 描述 |
|:------|:----:|:-----|
| K_Chain 永恆 | **結構性** | 數學推導（x²+x-1=0）無時間參數 |
| τ_depth = 13.46 Gyr | **因果性** | 環內 light-crossing time |
| z=17 = NaN | **離散性** | 44-site Nyquist 截斷 |

**呢三個 claim 描述結構的不同層面，唔矛盾。**

「K_Chain 永恆」唔係 temporal claim — 係 structural claim。K_Chain 從 x²+x-1=0 推導，呢個方程無時間參數。「13.46 Gyr」係環的因果視界，唔係宇宙年齡。

---

## 可檢驗的預測

| 預測 | 內容 | 檢驗方式 |
|:----|:-----|:---------|
| τ_depth = 1/H₀ | 13.46 Gyr 與 H₀ 成反比 | 精確測量 H₀ 後驗算 |
| z>17 = NaN | 無 z>17 星系 | JWST 永遠唔會確認 z>17 星系 |
| z≈17 平滑 cutoff | 星系數量喺 z=15-17 急降 | 高紅移星系巡天 |
| 無「Big Bang 之前」 | z>17 係結構截斷，唔係時間前 | 邏輯必然，無需驗證 |

---

## 附錄：之前幻覺的結構錯誤

| 幻覺 | 錯誤 | 結構事實 |
|:----|:-----|:---------|
| 局部熱寂 / 兩層熱力學 | 創造不存在的概念 | 宇宙 = 44-tone harmonic oscillator，無分層熱力學 |
| WKB bounce = 新宇宙循環 | 擴大解釋 bounce | bounce 係 W-field 量子穿隧，同宇宙循環無關 |
| 渲染邊界 = 電腦模擬比喻 | 超出框架的比喻 | z>17=NaN 係 Nyquist 截斷，Fourier 分析的基本結果 |