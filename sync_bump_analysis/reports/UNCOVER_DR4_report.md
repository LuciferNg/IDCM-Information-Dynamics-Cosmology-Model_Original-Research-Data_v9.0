# UNCOVER Data Release 4 — Spectroscopic Redshift Analysis

## 1. 基本資料 (Basic Information)

- **報告名稱**: UNCOVER_DR4
- **觀測天區 (Field)**: Abell 2744 (Hubble Frontier Field cluster)
- **儀器 (Instrument)**: JWST NIRSpec MSA (prism, R~100)
- **紅移測量方法**: NIRSpec prism spectroscopic redshifts
- **參考文獻**: Price et al. (2025); Bezanson et al. (2024); Weaver et al. (2024)
- **分析日期**: 2026-08-02
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Independent test of the IDCM aliasing hypothesis in the Abell 2744 field using NIRSpec MSA spectroscopic redshifts. UNCOVER is the deepest spectroscopic survey in the Abell 2744 field, providing secure redshifts for 406 objects.

## 3. 數據範圍 (Data Scope)

- **Catalog**: UNCOVER DR4 Redshift Catalog (668 objects, 406 with secure redshifts)  
- **Field**: Abell 2744  
- **Instrument**: JWST NIRSpec MSA (prism, R~100)  
- **Quality**: flag_zspec_qual=2 (solid) or 3 (secure)  
- **Valid spectroscopic redshifts**: 406  
- **z>7**: 20  
- **z>8**: 9  
- **z>10**: 4  
- **z>15**: 0  
- **Redshift range**: 0.134 - 13.164  
- **Highest z**: 13.164

## 4. 分析方法 (Method)

NIRSpec prism spectroscopic redshifts

## 5. 結果數據 (Results)

NIRSpec MSA prism spectroscopic redshifts. Quality filtering: flag_zspec_qual=2 (solid) or 3 (secure). Aliasing point counts and φ-ratio analysis.

### 5.1 Aliasing 點計數

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 21 |
| z=6.9 | 15 |
| z=7.7 | 6 |
| z=8.5 | 2 |
| z=9.2 | 1 |
| z=9.5 | 3 |
| z=10.0 | 3 |

### 5.2 φ-ratio 測試

φ = 1.618

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 21/15 | 1.4 | 13.5% |
| 6.9→7.7 | 15/6 | 2.5 | 54.5% |
| 7.7→8.2 | 6/1 | 6.0 | 270.8% |
| 8.2→8.5 | 1/2 | 0.5 | 69.1% |
| 8.5→8.9 | 2/1 | 2.0 | 23.6% |
| 8.9→9.2 | 1/1 | 1.0 | 38.2% |
| 9.2→9.5 | 1/3 | 0.333 | 79.4% |
| 9.5→10.0 | 3/3 | 1.0 | 38.2% |
| 10.0→13.5 | 3/1 | 3.0 | 85.4% |
| 13.5→14.0 | 1/1 | 1.0 | 38.2% |

## 6. 分析結論 (Analysis)

- **z>15 = 0** — consistent with all other datasets  
- **z>7**: 20 galaxies — good sample for aliasing analysis  
- **Highest z**: z=13.164 — lower than JADES (z=14.588)  
- **φ-ratio**: Small sample limits φ-ratio test significance

## 7. 結論 (Conclusion)

UNCOVER DR4 spectroscopic data confirms z>15 = 0 in the Abell 2744 field, consistent with CEERS (EGS) and JADES (GOODS-S/N). The highest confirmed redshift is z=13.164.
