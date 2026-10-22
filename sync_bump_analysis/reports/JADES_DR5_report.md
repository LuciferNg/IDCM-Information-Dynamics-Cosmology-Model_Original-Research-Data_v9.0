# JADES Data Release 5 — EAZY Photometric Redshift Analysis

## 1. 基本資料 (Basic Information)

- **報告名稱**: JADES_DR5
- **觀測天區 (Field)**: GOODS-S (Great Observatories Origins Deep Survey - South) + GOODS-N (Great Observatories Origins Deep Survey - North)
- **儀器 (Instrument)**: JWST NIRCam (27-35 filters)
- **紅移測量方法**: EAZY template-fitting photometric redshifts
- **參考文獻**: Eisenstein et al. (2026); Scholtz et al. (2026); Curtis-Lake et al. (2026); Brammer et al. (2008, EAZY)
- **分析日期**: 2026-08-03
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Test the IDCM Fibonacci aliasing hypothesis using the largest available JWST photometric redshift catalog from JADES DR5. This is the most recent data release (2026) with the deepest NIRCam photometry in the GOODS-S and GOODS-N fields. The EAZY photometric redshifts provide a massive sample (482,645 sources) for statistical analysis of the redshift distribution at IDCM-predicted aliasing points (5.6, 6.9, 7.7, 8.2, 8.5, ...). The φ-ratio pattern N(z₁)/N(z₂) ≈ φ is tested, and the z=17 Nyquist cutoff prediction (z>15 = 0) is verified against the available spectroscopic data.

## 3. 數據範圍 (Data Scope)

### 3.1 GOODS-S

- **Catalog**: JADES DR5 GOODS-S Photometric Catalog (304,366 sources)
- **Field**: GOODS-S (RA≈53°, Dec≈-28°)
- **Filters**: 35 NIRCam filters (broad + medium bands)
- **Redshift method**: EAZY (z_ml = maximum likelihood photometric redshift)
- **Quality cut**: z_ml > 0, z_ml < 25, finite
- **Valid EAZY z_ml**: 302,666
- **Prob_gt_7 > 0.5**: 23,945 (high-confidence z>7)
- **z>7 (EAZY)**: 16,820
- **z>8 (EAZY)**: 10,552
- **z>10 (EAZY)**: 4,575
- **z>15 (EAZY)**: 1,860
- **Redshift range**: 0.015 - 21.990
- **Max z**: 21.990
- **HDUs**: 13 (FILTERS, FLAG, SIZE, CIRC, CIRC_BSUB, CIRC_CONV, CIRC_BSUB_CONV, KRON, KRON_CONV, MIRI, PHOTOZ, PHOTOZ_KRON)
- **PHOTOZ columns**: ID, z_spec, z_a, z_ml, chi_a, l68, u68, l95, u95, l99, u99, nfilt, z_peak, chi_peak, z025, z160, z500, z840, z975, Prob_gt_5-9, z_bins, Prob_z_bins

### 3.2 GOODS-N

- **Catalog**: JADES DR5 GOODS-N Photometric Catalog (181,144 sources)
- **Field**: GOODS-N (RA≈189°, Dec≈62°)
- **Filters**: 27 NIRCam filters (broad + medium bands)
- **Redshift method**: EAZY (z_ml = maximum likelihood photometric redshift)
- **Quality cut**: z_ml > 0, z_ml < 25, finite
- **Valid EAZY z_ml**: 179,979
- **Prob_gt_7 > 0.5**: 11,387 (high-confidence z>7)
- **z>7 (EAZY)**: 6,929
- **z>8 (EAZY)**: 3,944
- **z>10 (EAZY)**: 2,047
- **z>15 (EAZY)**: 1,002
- **Redshift range**: 0.015 - 21.990
- **Max z**: 21.990
- **HDUs**: 13 (FILTERS, FLAG, SIZE, CIRC, CIRC_BSUB, CIRC_CONV, CIRC_BSUB_CONV, KRON, KRON_CONV, MIRI, PHOTOZ, PHOTOZ_KRON)
- **PHOTOZ columns**: ID, z_spec, z_a, z_ml, chi_a, l68, u68, l95, u95, l99, u99, nfilt, z_peak, chi_peak, z025

## 4. 分析方法 (Method)

EAZY template-fitting photometric redshifts (Brammer et al. 2008). The maximum likelihood redshift (z_ml) is used as the primary redshift estimate. The EAZY code fits a linear combination of template SEDs to the observed photometry in 27-35 NIRCam filters (broad + medium bands). The redshift probability distribution (PDF) is sampled at discrete points, and the peak of the PDF (z_peak) is also provided.

Quality cuts:
- z_ml > 0, z_ml < 25, finite values
- Prob_gt_7 > 0.5 for high-confidence z>7 sample

Aliasing analysis:
- Aliasing point counts within ±0.3 window at IDCM-predicted aliasing points
- φ-ratio test: N(z₁)/N(z₂) compared to φ=1.618
- Comparison between GOODS-S and GOODS-N for independent verification

## 5. 結果數據 (Results)

### 5.1 Aliasing 點計數

#### GOODS-S

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 7,894 |
| z=6.9 | 7,570 |
| z=7.7 | 2,922 |
| z=8.2 | 2,044 |
| z=8.5 | 1,964 |
| z=8.9 | 2,061 |
| z=9.2 | 2,349 |
| z=9.5 | 1,624 |
| z=10.0 | 584 |
| z=13.5 | 202 |
| z=14.0 | 115 |

#### GOODS-N

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 4,169 |
| z=6.9 | 3,839 |
| z=7.7 | 1,275 |
| z=8.2 | 682 |
| z=8.5 | 610 |
| z=8.9 | 544 |
| z=9.2 | 633 |
| z=9.5 | 558 |
| z=10.0 | 296 |
| z=13.5 | 116 |
| z=14.0 | 81 |

### 5.2 φ-ratio 測試

φ = 1.618

#### GOODS-S

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 7,894/7,570 | 1.043 | 35.6% |
| 6.9→7.7 | 7,570/2,922 | 2.591 | 60.1% |
| 7.7→8.2 | 2,922/2,044 | 1.430 | 11.6% |
| 8.2→8.5 | 2,044/1,964 | 1.041 | 35.7% |
| 8.5→8.9 | 1,964/2,061 | 0.953 | 41.1% |
| 8.9→9.2 | 2,061/2,349 | 0.877 | 45.8% |
| 9.2→9.5 | 2,349/1,624 | 1.446 | 10.6% |
| 9.5→10.0 | 1,624/584 | 2.781 | 71.9% |
| 10.0→13.5 | 584/202 | 2.891 | 78.7% |
| 13.5→14.0 | 202/115 | 1.757 | 8.6% |

#### GOODS-N

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 4,169/3,839 | 1.086 | 32.9% |
| 6.9→7.7 | 3,839/1,275 | 3.011 | 86.1% |
| 7.7→8.2 | 1,275/682 | 1.870 | 15.5% |
| 8.2→8.5 | 682/610 | 1.118 | 30.9% |
| 8.5→8.9 | 610/544 | 1.121 | 30.7% |
| 8.9→9.2 | 544/633 | 0.859 | 46.9% |
| 9.2→9.5 | 633/558 | 1.134 | 29.9% |
| 9.5→10.0 | 558/296 | 1.885 | 16.5% |
| 10.0→13.5 | 296/116 | 2.552 | 57.7% |
| 13.5→14.0 | 116/81 | 1.432 | 11.5% |

#### COMBINED GOODS-S + GOODS-N

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 12,063/11,409 | 1.057 | 34.7% |
| 6.9→7.7 | 11,409/4,197 | 2.718 | 68.0% |
| 7.7→8.2 | 4,197/2,726 | 1.540 | 4.8% |
| 8.2→8.5 | 2,726/2,574 | 1.059 | 34.5% |
| 8.5→8.9 | 2,574/2,605 | 0.988 | 38.9% |
| 8.9→9.2 | 2,605/2,982 | 0.874 | 46.0% |
| 9.2→9.5 | 2,982/2,182 | 1.367 | 15.5% |
| 9.5→10.0 | 2,182/880 | 2.480 | 53.2% |
| 10.0→13.5 | 880/318 | 2.767 | 71.0% |
| 13.5→14.0 | 318/196 | 1.622 | 0.3% |

### 5.3 高置信度樣本 (Prob_gt_7 > 0.5)

| 指標 | GOODS-S | GOODS-N |
|:----|:------:|:-------:|
| Prob_gt_7 > 0.5 | 23,945 | 11,387 |
| z>7 (high conf) | 15,058 | 6,499 |
| z>15 (high conf) | 1,860 | 1,002 |

## 6. 分析結論 (Analysis)

### 6.1 z>15 計數

- **DR5 EAZY z>15**: 1,860 (GOODS-S) + 1,002 (GOODS-N) = 2,862 combined
- **DR4 NIRSpec z>15**: 0 (confirmed spectroscopic)
- **結論**: EAZY photometric redshifts at z>10 are unreliable. The spectroscopic gold standard (JADES DR4, 5,190 sources, z_max=14.588) shows z>15 = 0. The EAZY z>15 counts are artifacts of template-fitting degeneracies at high redshift, not real physical sources.

### 6.2 φ-ratio 測試

- **GOODS-S 最佳匹配**: 7.7→8.2 = 1.430 (11.6% from φ), 13.5→14.0 = 1.757 (8.6% from φ)
- **GOODS-N 最佳匹配**: 7.7→8.2 = 1.870 (15.5% from φ), 13.5→14.0 = 1.432 (11.5% from φ)
- **Combined 最佳匹配**: 7.7→8.2 = 1.540 (4.8% from φ), 13.5→14.0 = 1.622 (0.3% from φ)
- 兩個天區獨立顯示相同 pattern，但 EAZY 高 z 不可靠

### 6.3 場域一致性

GOODS-S 和 GOODS-N 的 φ-ratio 模式在 7.7→8.2 和 13.5→14.0 呈現一致趨勢，但偏差幅度不同：
- 7.7→8.2: GOODS-S 11.6% vs GOODS-N 15.5%
- 13.5→14.0: GOODS-S 8.6% vs GOODS-N 11.5%

這表明模式可能來自光度函數的自然衰減，而非物理 aliasing。

### 6.5 DR4 × DR5 交叉比對 — EAZY 可靠性測試

DR4 光譜紅移 × DR5 光度交叉比對（127 個 z>7 光譜源配對）：

#### EAZY 系統性偏差

| 光譜 ID | DR4 spec-z | DR5 EAZY z_ml | 偏差 | 說明 |
|:-------:|:----------:|:-------------:|:----:|:------|
| 41544 | 3.749 | 16.95 | +13.20 | EAZY 嚴重高估 |
| 1069453 | 3.973 | 15.86 | +11.89 | EAZY 嚴重高估 |
| 1119489 | 11.167 | 16.14 | +4.97 | EAZY 高估 |
| 183348 | 14.588 | 14.38 | -0.21 | 良好匹配 |
| 18044 | 14.360 | 14.33 | -0.03 | 良好匹配 |

**6 個 DR5 EAZY z>15 候選體有 DR4 光譜覆蓋嘅全部係假陽性。**

#### 亮度分析 — 截斷是否靈敏度問題？

| z 範圍 | 數量 | 中位數 F444W |
|:------:|:----:|:----------:|
| 7-8 | 106 | 36.9 |
| 8-9 | 38 | 41.2 |
| 9-10 | 17 | 34.6 |
| 10-11 | 9 | 12.9 |
| 11-12 | 5 | 22.8 |
| 12-13 | 2 | 10.8 |
| 13-14 | 3 | 8.1 |
| 14-15 | 2 | 37.3 |

**光度函數擬合**: log10(F444W) = 2.12 - 0.070 × z
- z=15.5 預測 F444W = 10.9 nJy（> 5-sigma 極限 10 nJy）
- z=14.588 源 (F444W=62.9) 如果移到 z=15.5 仍然有 59.4 nJy
- **z>15=0 唔似係靈敏度問題**
- Sample size 限制: z>13 得 5 個光譜源，誤差大

| 測試 | DR5 EAZY (光度) | DR4 NIRSpec (光譜) |
|:----|:--------------:|:-----------------:|
| z>15 | 2,862 | 0 |
| 最高 z | 21.990 | 14.588 |
| φ-ratio 5.6→6.9 | 1.057 (34.7%) | 1.685 (4.1%) |
| 可靠性 | 低 (高 z 不可靠) | 高 (金標準) |

## 7. 結論 (Conclusion)

1. **JADES DR5 EAZY photoz 顯示 z>15 = 2,862，但不可靠** — EAZY 在高紅移 (z>10) 的模板擬合存在退化，導致虛假高紅移源
2. **光譜金標準 (JADES DR4) 顯示 z>15 = 0** — EAZY 的高 z 計數是光度法 artifact
3. **φ-ratio 模式在兩個天區一致** — 7.7→8.2 和 13.5→14.0 都接近 φ，但偏差大 (4.8-15.5%)
4. **EAZY 不適合用於 IDCM z>15 測試** — 光度法在 z>10 不可靠，必須使用光譜數據
5. **亮度分析顯示 z>15=0 唔似係靈敏度問題** — 光度函數外推 z=15.5 預測 F444W=10.9 nJy (>5σ)，但 sample size 細 (z>13 得 5 個源)，最終判決需等 LAPIS 1000h
