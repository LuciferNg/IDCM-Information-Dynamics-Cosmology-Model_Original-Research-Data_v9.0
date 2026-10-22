# FLRW + IDCM 參數嘅 9.3σ Tension

**日期：** 2026-08-10
**文件：** `references/flrw-idcm-tension-analysis.md`

## 1. 問題陳述

用 FLRW 嘅 Friedmann equation 同 IDCM 嘅結構參數（H₀, Ω_m, Ω_Λ, BAO）計算 DM/rd，同 DESI DR2 Lyα BAO 比較，發現 9.3σ 嘅 tension。

## 2. 參數

### 2.1 IDCM 結構參數

```
H₀ = 72.59 km/s/Mpc  (c/R_H, 環周長)
Ω_m = 0.3167  (1 - Ω_Λ)
Ω_Λ = 4/(φ⁴-1) = 0.6833
BAO = λ_sync/2 = 147.44 Mpc
```

### 2.2 DESI DR2 Lyα BAO (z=2.33)

```
DM/rd = 39.32 ± 0.33
DH/rd = 8.600 ± 0.066
```

## 3. 計算

### 3.1 FLRW 距離公式

```
E(z) = √(Ω_m(1+z)³ + Ω_Λ)
DM(z) = (c/H₀) × ∫₀ᶻ dz'/E(z')
DH(z) = c/(H₀·E(z))
```

### 3.2 數值結果 (z=2.33)

```
E(2.33) = √(0.3167×3.33³ + 0.6833) = 3.518
DM(2.33) = 5344 Mpc
DH(2.33) = 1174 Mpc

DM/rd = 5344/147.44 = 36.24
DH/rd = 1174/147.44 = 7.96
```

### 3.3 Tension

```
Δ(DM/rd) = 36.24 - 39.32 = -3.08
σ = 3.08/0.33 = 9.3σ

Δ(DH/rd) = 7.96 - 8.600 = -0.64
σ = 0.64/0.066 = 9.7σ
```

## 4. 根因分析

### 4.1 H₀ 差異

IDCM H₀ = 72.59 vs Planck 67.4（高 7.7%）。H₀ 越高，距離越細。

| H₀ (km/s/Mpc) | DM(z=2.33) (Mpc) | DM/rd | vs DESI |
|:-------------:|:----------------:|:-----:|:-------:|
| **72.59 (IDCM)** | **5344** | **36.24** | **-9.3σ** |
| 70.0 | 5540 | 37.58 | -5.3σ |
| 67.4 (Planck) | 5751 | 39.01 | -0.9σ |

### 4.2 Ω_m 差異

IDCM Ω_m = 0.3167 vs Planck 0.315（差 0.5%），影響較細。

### 4.3 BAO 差異

IDCM BAO = 147.44 vs Planck rd = 147.09（差 0.24%），影響好細。

## 5. 可能解釋

| 解釋 | 可能性 | 證據 |
|:-----|:------:|:-----|
| FLRW 唔適用於 IDCM | 高 | 調律者 insight |
| H₀ 結構推導有問題 | 中 | 同 Planck 差 7.7% |
| BAO 唔係 λ_sync/2 | 中 | 需要 136 Mpc 先 match |
| DESI 測量有問題 | 低 | 同其他 survey 一致 |

## 6. 結論

**9.3σ tension 嘅前提係 FLRW 適用於 IDCM。** 如果呢個假設唔成立，tension 就無意義。IDCM 嘅正確測試要用 IDCM 自身嘅膨脹歷史，唔係 FLRW。

## 7. 參考

- `references/desi-dr2-lya-bao-comparison.md`
- `references/idcm-cosmology-closed-loop-derivation.md`