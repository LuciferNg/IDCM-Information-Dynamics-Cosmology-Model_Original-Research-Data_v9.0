# JADES Data Release 4 — Spectroscopic Redshift Analysis (Combined Catalog)

## 1. 基本資料 (Basic Information)

- **報告名稱**: JADES_DR4_Combined
- **觀測天區 (Field)**: GOODS-S + GOODS-N
- **儀器 (Instrument)**: JWST NIRSpec (R100 prism + R1000 gratings)
- **紅移測量方法**: NIRSpec prism spectroscopic redshifts (R~100) + medium-resolution gratings (R~1000)
- **參考文獻**: Curtis-Lake et al. (2026); Scholtz et al. (2026); Eisenstein et al. (2026)
- **分析日期**: 2026-08-02
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Test the IDCM Fibonacci aliasing hypothesis using the largest available JWST spectroscopic redshift catalog. Spectroscopic redshifts are the gold standard for redshift measurement — they are not affected by template-fitting degeneracies that plague photometric redshifts. This is the definitive test of whether the φ-ratio pattern is physical or a selection effect.

## 3. 數據範圍 (Data Scope)

- **Catalog**: JADES DR4 Combined (5,190 sources across 5 HDUs)  
- **Fields**: GOODS-S (RA≈53°, Dec≈-28°) + GOODS-N (RA≈189°, Dec≈62°)  
- **Instrument**: JWST NIRSpec  
- **Mode**: Prism (R~100) + Medium-resolution gratings (R~1000)  
- **Valid spectroscopic redshifts**: 3725  
- **z>7**: 184  
- **z>8**: 76  
- **z>10**: 21  
- **z>15**: 0  
- **Redshift range**: 0.142 - 14.588  
- **Highest redshift**: z=14.588 (NIRCam_DR5_ID=183348)  
- **Second highest**: z=14.36 (NIRCam_DR5_ID=18044)

## 4. 分析方法 (Method)

NIRSpec prism spectroscopic redshifts (R~100) + medium-resolution gratings (R~1000)

## 5. 結果數據 (Results)

Spectroscopic redshifts from NIRSpec prism (R~100) and medium-resolution gratings (R~1000). Quality flags applied: Z_FLAG filtering. Aliasing point counts within ±0.3 window. φ-ratio test: N(z₁)/N(z₂) compared to φ=1.618. Luminosity function simulation to test if the φ-ratio pattern is from selection effects.

### 5.1 Aliasing 點計數

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 155 |
| z=6.9 | 92 |
| z=7.7 | 50 |
| z=8.2 | 34 |
| z=8.5 | 28 |
| z=8.9 | 20 |
| z=9.2 | 14 |
| z=9.5 | 11 |
| z=10.0 | 5 |

### 5.2 φ-ratio 測試

φ = 1.618

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 155/92 | 1.685 | 4.1% |
| 6.9→7.7 | 92/50 | 1.84 | 13.7% |
| 7.7→8.2 | 50/34 | 1.471 | 9.1% |
| 8.2→8.5 | 34/28 | 1.214 | 25.0% |
| 8.5→8.9 | 28/20 | 1.4 | 13.5% |
| 8.9→9.2 | 20/14 | 1.429 | 11.7% |
| 9.2→9.5 | 14/11 | 1.273 | 21.3% |
| 9.5→10.0 | 11/5 | 2.2 | 36.0% |
| 10.0→13.5 | 5/1 | 5.0 | 209.0% |
| 13.5→14.0 | 1/1 | 1.0 | 38.2% |

## 6. 分析結論 (Analysis)

- **z>15 = 0** — consistent with IDCM z=17 Nyquist cutoff  
- **φ-ratio at 5.6→6.9**: 1.685 (4.1% from φ) — best match in all datasets  
- **Mean φ deviation**: 16.8% — better than CEERS photometric (37.1%)  
- **However**: φ-ratio pattern identified as selection effect from luminosity function + JADES spectroscopic targeting strategy, NOT physical aliasing  
- **Highest confirmed z**: z=14.588 (JADES DR4, Z_FLAG=4)  
- **z>14.5**: 2 galaxies confirmed spectroscopically, demonstrating JWST can reach z≈14.6 without aliasing obstruction

## 7. 結論 (Conclusion)

JADES DR4 spectroscopic data shows z>15 = 0, consistent with the IDCM z=17 Nyquist cutoff. The φ-ratio at 5.6→6.9 (1.685, 4.1% from φ) is the best match across all datasets, but is a selection effect from the luminosity function + spectroscopic targeting, not physical aliasing. The highest confirmed redshift is z=14.588.
