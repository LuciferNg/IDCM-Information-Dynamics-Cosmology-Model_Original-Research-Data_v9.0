# UNCOVER Data Release 3 — EAZY Photometric Redshift Analysis

## 1. 基本資料 (Basic Information)

- **報告名稱**: UNCOVER_DR3_EAZY
- **觀測天區 (Field)**: Abell 2744 (Hubble Frontier Field cluster)
- **儀器 (Instrument)**: JWST NIRCam + MegaScience medium bands
- **紅移測量方法**: EAZY template-fitting photometric redshifts
- **參考文獻**: Suess et al. (2024); Weaver et al. (2024)
- **分析日期**: 2026-08-02
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Test the IDCM aliasing hypothesis using the UNCOVER DR3 SUPER photometric catalog with EAZY photometric redshifts. This is the largest photometric catalog in the Abell 2744 field with 74,020 sources.

## 3. 數據範圍 (Data Scope)

- **Catalog**: UNCOVER DR3 SUPER Photometric Catalog (74,020 sources)  
- **Field**: Abell 2744  
- **Filters**: JWST NIRCam broad + medium bands + MegaScience + HST  
- **Redshift method**: EAZY  
- **Quality cut**: chi² < 10  
- **Total sources**: 74,020  
- **Good EAZY fits (chi²<10)**: 29,885  
- **z>7 (EAZY)**: 1,914  
- **z>8 (EAZY)**: 1,581  
- **z>10 (EAZY)**: 1,157  
- **z>15 (EAZY)**: 691  
- **Spectroscopic redshifts (DR3)**: 524 (max z=6.327)  
- **Note**: EAZY photometric redshifts at z>10 are unreliable

## 4. 分析方法 (Method)

EAZY template-fitting photometric redshifts

## 5. 結果數據 (Results)

EAZY template-fitting photometric redshifts. Quality cut: chi²<10. The catalog includes both EAZY photoz and a small number of spec-zs (max z=6.327).

### 5.1 Aliasing 點計數

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 364 |
| z=6.9 | 648 |
| z=7.7 | 107 |
| z=8.2 | 123 |
| z=8.5 | 108 |
| z=8.9 | 90 |
| z=9.2 | 118 |
| z=9.5 | 162 |
| z=10.0 | 100 |
| z=13.5 | 35 |
| z=14.0 | 39 |

### 5.2 φ-ratio 測試

φ = 1.618

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 364/648 | 0.562 | 65.3% |
| 6.9→7.7 | 648/107 | 6.056 | 274.3% |
| 7.7→8.2 | 107/123 | 0.87 | 46.2% |
| 8.2→8.5 | 123/108 | 1.139 | 29.6% |
| 8.5→8.9 | 108/90 | 1.2 | 25.8% |
| 8.9→9.2 | 90/118 | 0.763 | 52.9% |
| 9.2→9.5 | 118/162 | 0.728 | 55.0% |
| 9.5→10.0 | 162/100 | 1.62 | 0.1% |
| 10.0→13.5 | 100/35 | 2.857 | 76.6% |
| 13.5→14.0 | 35/39 | 0.897 | 44.5% |

## 6. 分析結論 (Analysis)

- **z>15 (EAZY)**: 691 — EAZY photoz at high z are unreliable  
- **φ-ratio**: 9.5→10.0 = 1.620 (0.1% from φ) — likely random coincidence  
- **EAZY vs LePHARE**: EAZY gives more sources at z>15 than LePHARE, suggesting EAZY is less conservative at high z  
- **Cross-check**: DR4 spec-zs (max z=13.164) show no EAZY photoz matches at z>15

## 7. 結論 (Conclusion)

UNCOVER DR3 EAZY photometric redshifts show z>15 = 691, but these are unreliable due to template-fitting degeneracies at high z. The DR4 spectroscopic data (max z=13.164) contradicts the EAZY high-z photoz. EAZY photoz are not reliable for the z>15 aliasing test.
