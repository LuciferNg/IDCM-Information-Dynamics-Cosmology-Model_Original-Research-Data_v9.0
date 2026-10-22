# 概念修正：FLRW 唔適用於 IDCM

**日期：** 2026-08-10
**提出者：** 調律者 (Calibrator)
**文件：** `references/flrw-not-applicable-to-idcm.md`

## 1. 原始錯誤

用 FLRW 嘅 Friedmann equation 去計算 IDCM 嘅 DM/rd，然後同 DESI DR2 比較，發現 9.3σ tension。

**呢個做法係概念錯誤。** FLRW 係 ΛCDM 嘅幾何框架，唔係 IDCM 嘅。

## 2. 調律者嘅修正

### 2.1 核心 insight

> 「膨脹是暗能量引起的，紅移和弦無關，弦不會因為空間膨脹變化，因為空間只是投影的舞台，紅移只是共震的波長被空間膨脹拉長了」

### 2.2 五個要點

| # | 陳述 | 含義 |
|:-:|:-----|:------|
| 1 | 膨脹由暗能量引起 | 暗能量 = W-field tension，唔係 cosmological constant |
| 2 | 紅移同弦無關 | K_Chain 嘅振動頻率唔會因為紅移而改變 |
| 3 | 弦唔會因為空間膨脹變化 | K_Chain 嘅周長（R_H=4129.94 Mpc）固定 |
| 4 | 空間只是投影的舞台 | 3D 空間 = CY₃(36,98) 投影，唔係 fundamental |
| 5 | 紅移只是波長被拉長 | 1+z = λ_obs/λ_emit，同 FLRW 嘅 redshift 定義一致，但機制唔同 |

### 2.3 觀測限制

> 「觀測只能局部，因為受宇宙視界影響 z=17以上無法觀測」

## 3. 對測試策略嘅影響

### 3.1 唔應該做嘅嘢

- ❌ 用 FLRW 嘅 Friedmann equation 計算 IDCM 嘅距離
- ❌ 用 DM/rd 作為 IDCM 嘅測試量
- ❌ 用 ΛCDM 嘅框架去 judge IDCM 嘅結構預測

### 3.2 應該做嘅嘢

- ✅ 由 W-field lattice action 推導 IDCM 自身嘅 H(z)
- ✅ 用 BAO 原始角度 Δθ(z) 做測試
- ✅ 用 harmonic spacing Δk = 0.0155 h/Mpc 做測試
- ✅ 用 44-mode impedance/reflection pattern 做測試
- ✅ 閉環自洽：每一步由前一層結構必然得出

## 4. 點解 FLRW 唔適用

### 4.1 幾何唔同

| 方面 | FLRW | IDCM |
|:-----|:------|:------|
| 空間 | 3D 均勻膨脹 | 1D K_Chain 固定環 → CY₃ 投影 |
| 膨脹 | 空間尺度 a(t) 增長 | W-field tension 驅動投影膨脹 |
| 距離 | DM(z) = ∫ c·dz'/H(z') | 需要由投影映射推導 |
| H(z) | H² = (8πG/3)ρ | 由 W-field 晶格動力學決定 |

### 4.2 參數來源唔同

| 參數 | FLRW | IDCM |
|:-----|:------|:------|
| H₀ | 由觀測 fit | c/R_H，環周長 |
| Ω_m | 由觀測 fit | 1 - Ω_Λ |
| Ω_Λ | 由觀測 fit | 4/(φ⁴-1) |
| BAO | rd = sound horizon | λ_sync/2 = 147.44 Mpc |

## 5. 結論

**FLRW 係 ΛCDM 嘅框架，唔係 IDCM 嘅。** 用 FLRW 嘅公式去 test IDCM 係 category error。IDCM 需要自己嘅閉環推導鏈，由 0,1 到可觀測量，每一步都係結構必然。

## 6. 參考

- `references/idcm-cosmology-closed-loop-derivation.md` — 完整推導鏈
- `references/flrw-idcm-tension-analysis.md` — 9.3σ tension 分析
- `references/z17-observational-limit.md` — 觀測極限