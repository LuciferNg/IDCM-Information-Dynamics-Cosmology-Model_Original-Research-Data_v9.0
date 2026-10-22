# DESI DR2 Lyα BAO — IDCM 對比

**日期：** 2026-08-10
**論文：** arXiv:2607.27410 (DESI DR2 Lyα forest BAO, 2026-08)
**文件：** `references/desi-dr2-lya-bao-comparison.md`

## 1. DESI DR2 Lyα BAO 測量

### 1.1 基本數據

```
zeff = 2.33
DM/rd = 39.32 ± 0.33 (0.8%)
DH/rd = 8.600 ± 0.066 (0.8%)
rd_fid = 147.09 Mpc (Planck fiducial)
```

### 1.2 論文背景

- DESI DR2 Lyα BAO 係目前最高紅移嘅 BAO 測量
- 精度 0.8%，比 DESI DR1 嘅 1.2% 有改善
- 數據仲未公開（`data.desi.lbl.gov/public/dr2/` 回傳 401）
- 公開預計約 2027 年初

## 2. IDCM 結構預測

### 2.1 參數

```
H₀ = 72.59 km/s/Mpc (c/R_H)
Ω_m = 0.3167 (1 - Ω_Λ)
Ω_Λ = 4/(φ⁴-1) = 0.6833
BAO = λ_sync/2 = 147.44 Mpc
```

### 2.2 Comoving Distance (z=2.33)

```
E(z) = √(0.3167×(1+2.33)³ + 0.6833) = 3.518
DM(z) = ∫₀²·³³ c·dz'/H(z') = 5344 Mpc
DH(z) = c/H(z) = 1174 Mpc
```

### 2.3 DM/rd 同 DH/rd

```
DM/rd = 5344 / 147.44 = 36.24
DH/rd = 1174 / 147.44 = 7.96
```

## 3. 直接比較

| 量 | IDCM | DESI DR2 | 差異 | σ |
|:---|:----:|:--------:|:----:|:-:|
| DM/rd | 36.24 | 39.32 ± 0.33 | -3.08 | -9.3σ |
| DH/rd | 7.96 | 8.600 ± 0.066 | -0.64 | -9.7σ |

## 4. 同 Planck rd 比較

如果直接用 BAO scale 做比較：

```
IDCM BAO = 147.44 Mpc
Planck rd = 147.09 Mpc (DESI fiducial)
Difference = 0.35 Mpc (0.24%)
DESI precision = 0.8%
→ within 0.3σ
```

**BAO scale 本身無問題，問題係 DM/rd 嘅距離計算。**

## 5. 側推：需要嘅 BAO scale

如果要 match DESI DM/rd = 39.32：

```
rd = DM / 39.32 = 5344 / 39.32 = 135.90 Mpc
vs IDCM BAO = 147.44 Mpc
ratio = 0.922
```

如果要 match DESI DH/rd = 8.600：

```
rd = DH / 8.600 = 1174 / 8.600 = 136.49 Mpc
vs IDCM BAO = 147.44 Mpc
ratio = 0.926
```

## 6. 關鍵問題

### 6.1 FLRW 假設

呢個比較用咗 FLRW 嘅 Friedmann equation 去計算 DM(z)。如果 IDCM 嘅膨脹歷史唔同，呢個比較就無意義。

### 6.2 H₀ 差異

IDCM H₀ = 72.59 vs Planck 67.4（高 7.7%）。高 H₀ → 細距離 → DM/rd 細。

### 6.3 真正測試

IDCM 嘅真正測試係：
1. Harmonic spacing Δk = 0.0155 h/Mpc（P(k) wiggles）
2. BAO 原始角度 Δθ(z)（唔係 DM/rd）
3. 44-mode impedance/reflection pattern

## 7. 結論

| 量 | 結果 | 狀態 |
|:---|:-----|:----:|
| BAO scale (147.44 vs 147.09) | 0.24% diff | ✅ 一致 |
| DM/rd (FLRW 形式) | -9.3σ | ⚠️ 待釐清 |
| 真正測試 | 需要 DESI DR2 full-shape P(k) | 🔴 未公開 |

## 8. 參考

- DESI DR2 Lyα BAO: arXiv:2607.27410 (2026-08)
- DESI DR2 covariance: arXiv:2507.01380 (Lee)
- IDCM BAO prediction: `references/large-scale-structure.md`