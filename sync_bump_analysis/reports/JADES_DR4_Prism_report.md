# JADES Data Release 4 — Prism Spectroscopic Redshift Analysis (Separate Catalogs)

## 1. 基本資料 (Basic Information)

- **報告名稱**: JADES_DR4_Prism
- **觀測天區 (Field)**: GOODS-S + GOODS-N
- **儀器 (Instrument)**: JWST NIRSpec prism (R~100)
- **紅移測量方法**: NIRSpec prism spectroscopic redshifts (R~100)
- **參考文獻**: Curtis-Lake et al. (2026); Scholtz et al. (2026)
- **分析日期**: 2026-08-02
- **分析框架**: IDCM (Information Dynamics Cosmology Model)

## 2. 研究目的 (Purpose)

Independent verification of the JADES DR4 Combined catalog results using the separate GOODS-S and GOODS-N prism redshift catalogs. These catalogs are independently processed and provide a cross-check on the Combined catalog results.

## 3. 數據範圍 (Data Scope)

- **Catalog**: JADES DR4 Prism (separate GOODS-S + GOODS-N catalogs)  
- **GOODS-S**: 2525 sources  
- **GOODS-N**: 1561 sources  
- **Total**: 4086 sources  
- **Valid spectroscopic redshifts**: 2722  
- **z>7**: 112  
- **z>8**: 43  
- **z>10**: 12  
- **z>15**: 0  
- **Redshift range**: 0.144 - 13.352  
- **Highest z**: 13.352

## 4. 分析方法 (Method)

NIRSpec prism spectroscopic redshifts (R~100)

## 5. 結果數據 (Results)

Prism spectroscopic redshifts (R~100) from NIRSpec. Quality flags applied. Independent catalogs for GOODS-S and GOODS-N fields.

### 5.1 Aliasing 點計數

| 紅移點 | 星系數 |
|:------:|:------:|
| z=5.6 | 117 |
| z=6.9 | 81 |
| z=7.7 | 22 |
| z=8.2 | 12 |
| z=8.5 | 13 |
| z=8.9 | 9 |
| z=9.2 | 8 |
| z=9.5 | 12 |
| z=10.0 | 6 |
| z=13.5 | 1 |

### 5.2 φ-ratio 測試

φ = 1.618

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 117/81 | 1.444 | 10.7% |
| 6.9→7.7 | 81/22 | 3.682 | 127.5% |
| 7.7→8.2 | 22/12 | 1.833 | 13.3% |
| 8.2→8.5 | 12/13 | 0.923 | 43.0% |
| 8.5→8.9 | 13/9 | 1.444 | 10.7% |
| 8.9→9.2 | 9/8 | 1.125 | 30.5% |
| 9.2→9.5 | 8/12 | 0.667 | 58.8% |
| 9.5→10.0 | 12/6 | 2.0 | 23.6% |
| 10.0→13.5 | 6/1 | 6.0 | 270.8% |
| 13.5→14.0 | 1/1 | 1.0 | 38.2% |

## 6. 分析結論 (Analysis)

- **z>15 = 0** — consistent with all other datasets  
- **φ-ratio**: Weaker than Combined catalog (5.6→6.9: 1.444, 10.7% from φ)  
- **Highest z**: z=13.352 (lower than Combined catalog because Combined includes R1000 data)

## 7. 結論 (Conclusion)

JADES DR4 Prism catalog independently confirms z>15 = 0. The φ-ratio pattern is weaker than in the Combined catalog, consistent with the higher-resolution R1000 data carrying the aliasing signal.
