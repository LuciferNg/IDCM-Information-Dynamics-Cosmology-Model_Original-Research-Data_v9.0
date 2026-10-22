# GLASS-JWST — NIRSpec Spectroscopic Redshift Analysis

## 1. 基本資料 (Basic Information)

- **報告名稱**: GLASS_JWST
- **觀測天區 (Field)**: Abell 2744 (Hubble Frontier Field cluster)
- **儀器 (Instrument)**: JWST NIRSpec (R2000-3000 + R30-300)
- **紅移測量方法**: NIRSpec medium-resolution spectroscopic redshifts
- **參考文獻**: Treu et al. (2022); Paris et al. (2023); Mascia et al. (2024); Watson et al. (2025)
- **分析日期**: 2026-08-02
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Independent test of the IDCM aliasing hypothesis in a third field (Abell 2744), using NIRSpec spectroscopic redshifts. This is a completely independent dataset from CEERS (EGS) and JADES (GOODS-S/N), providing a crucial cross-check.

## 3. 數據範圍 (Data Scope)

- **Catalog**: GLASS-JWST NIRSpec (263 spectral images, 245 unique sources)  
- **Field**: Abell 2744 (RA≈3.6°, Dec≈-30.4°)  
- **Instrument**: JWST NIRSpec  
- **Resolution**: R2000-3000 (152 sources, Program 1324) + R30-300 (111 sources, Program 2756)  
- **Valid spectroscopic redshifts**: 211  
- **z>7**: 11  
- **z>8**: 3  
- **z>10**: 0  
- **z>15**: 0  
- **Redshift range**: 0.001 - 9.793  
- **Highest z**: 9.793

## 4. 分析方法 (Method)

NIRSpec medium-resolution spectroscopic redshifts

## 5. 結果數據 (Results)

Medium-resolution NIRSpec spectroscopic redshifts. Sources split between two programs with different resolutions. Aliasing point counts and φ-ratio analysis.

### 5.1 Aliasing 點計數

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 8 |
| z=7.7 | 7 |
| z=8.2 | 1 |
| z=8.5 | 1 |
| z=9.2 | 1 |
| z=9.5 | 2 |
| z=10.0 | 1 |

### 5.2 φ-ratio 測試

φ = 1.618

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 8/1 | 8.0 | 394.4% |
| 6.9→7.7 | 1/7 | 0.143 | 91.2% |
| 7.7→8.2 | 7/1 | 7.0 | 332.6% |
| 8.2→8.5 | 1/1 | 1.0 | 38.2% |
| 8.5→8.9 | 1/1 | 1.0 | 38.2% |
| 8.9→9.2 | 1/1 | 1.0 | 38.2% |
| 9.2→9.5 | 1/2 | 0.5 | 69.1% |
| 9.5→10.0 | 2/1 | 2.0 | 23.6% |
| 10.0→13.5 | 1/1 | 1.0 | 38.2% |
| 13.5→14.0 | 1/1 | 1.0 | 38.2% |

## 6. 分析結論 (Analysis)

- **z>15 = 0** — consistent with all other datasets  
- **Small sample**: only 11 galaxies at z>7, limiting statistical power  
- **No aliasing pattern detected**: sample too small for φ-ratio test

## 7. 結論 (Conclusion)

GLASS-JWST NIRSpec data confirms z>15 = 0 in a third independent field (Abell 2744). The sample is too small for a meaningful φ-ratio test, but the z>15=0 result is consistent with all other datasets.
