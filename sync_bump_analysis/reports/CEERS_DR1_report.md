# CEERS Data Release 1 — Photometric Redshift Analysis

## 1. 基本資料 (Basic Information)

- **報告名稱**: CEERS_DR1
- **觀測天區 (Field)**: EGS (Extended Groth Strip)
- **儀器 (Instrument)**: JWST NIRCam + HST ACS/WFC3
- **紅移測量方法**: LePHARE template-fitting photometric redshifts
- **參考文獻**: Cox et al. (2025); Finkelstein et al. (2025); Bagley et al. (2023)
- **分析日期**: 2026-08-02
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Test the IDCM Fibonacci aliasing hypothesis using the largest available JWST photometric redshift catalog. Specifically, check if the redshift distribution at IDCM-predicted aliasing points (5.6, 6.9, 7.7, 8.2, 8.5, ...) follows the φ-ratio pattern N(z₁)/N(z₂) ≈ φ, and verify the z=17 Nyquist cutoff prediction (z>15 = 0).

## 3. 數據範圍 (Data Scope)

- **Catalog**: CEERS DR1 (87,345 sources)  
- **Field**: EGS (RA≈215°, Dec≈53°)  
- **Filters**: 7 JWST/NIRCam (F115W–F444W) + 7 HST (F435W–F160W)  
- **Redshift method**: LePHARE  
- **Quality cut**: z_med>0, z_lo>0.5, nbands≥5  
- **Quality sources**: 49,106  
- **z>7 (quality)**: 551  
- **z>8 (quality)**: 287  
- **z>10**: 152  
- **z>15**: 0  
- **Redshift range**: 0.509 - 14.445

## 4. 分析方法 (Method)

LePHARE template-fitting photometric redshifts

## 5. 結果數據 (Results)

Photometric redshifts from LePHARE template fitting. Quality flags applied: z_med>0, z_lo>0.5 (68% CI lower bound > 0.5), nbands≥5 (minimum 5 filters detected). Aliasing point counts within ±0.3 window. φ-ratio test: N(z₁)/N(z₂) compared to φ=1.618.

### 5.1 Aliasing 點計數

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 351 |
| z=6.9 | 325 |
| z=7.7 | 90 |
| z=8.2 | 69 |
| z=8.5 | 63 |
| z=8.9 | 37 |
| z=9.2 | 29 |
| z=9.5 | 18 |
| z=10.0 | 29 |
| z=13.5 | 40 |
| z=14.0 | 46 |

### 5.2 φ-ratio 測試

φ = 1.618

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 351/325 | 1.08 | 33.3% |
| 6.9→7.7 | 325/90 | 3.611 | 123.2% |
| 7.7→8.2 | 90/69 | 1.304 | 19.4% |
| 8.2→8.5 | 69/63 | 1.095 | 32.3% |
| 8.5→8.9 | 63/37 | 1.703 | 5.2% |
| 8.9→9.2 | 37/29 | 1.276 | 21.1% |
| 9.2→9.5 | 29/18 | 1.611 | 0.4% |
| 9.5→10.0 | 18/29 | 0.621 | 61.6% |
| 10.0→13.5 | 29/40 | 0.725 | 55.2% |
| 13.5→14.0 | 40/46 | 0.87 | 46.3% |

## 6. 分析結論 (Analysis)

- **z>15 = 0** — consistent with IDCM z=17 Nyquist cutoff prediction  
- **z=13.5 cluster**: 41 galaxies at z=13.5±0.3 — 8 with narrow P(z) (width<0.1, chi²=254–4101) identified as LePHARE fitting artifact; 5 STAR_FLAG=1 stellar contamination; 11800-series (IDs 11802, 11804, 11807, 11809) confirmed as deblending artifact  
- **φ-ratio**: Best match at z=9.2→9.5 (1.611, 0.4% from φ), but not consistent across all points (mean dev 37.1%)  
- **EAZY vs LePHARE**: LePHARE photoz produce more artifacts at high z than EAZY

## 7. 結論 (Conclusion)

CEERS DR1 LePHARE photometric redshifts show z>15 = 0, consistent with the IDCM z=17 Nyquist cutoff prediction. However, the z=13.5 narrow P(z) cluster is an artifact. The φ-ratio pattern is weak and inconsistent (mean dev 37.1%). The photometric redshift method is prone to systematic artifacts at high z.
