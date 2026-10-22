# BOSS DR12 ξ(s) Harmonic Analysis

**日期：** 2026-08-10
**數據：** Ross+2016, BOSS DR12 post-reconstruction correlation function
**文件：** `references/boss-dr12-xi-harmonic-analysis.md`

## 1. 目的

檢測 BOSS DR12 ξ(s) 是否顯示 IDCM 預測嘅 BAO peak 位置（203 h⁻¹ Mpc = λ_sync/2）。

## 2. 數據

Ross+2016 提供 BOSS DR12 合併後嘅 correlation function，post-reconstruction，3 個 redshift bins。

數據位置：`https://data.sdss.org/sas/dr12/boss/papers/clustering/Ross_etal_2016_COMBINEDDR12_corrfunc.zip`

## 3. 方法

1. 下載並解壓 Ross+2016 corrfunc zip
2. 提取 z3 bin（最高 redshift）嘅 post-reconstruction monopole
3. 將 s 從 h⁻¹ Mpc 轉換為 Mpc（用 IDCM h=0.7259）
4. 可視化 ξ(s) 並檢測 BAO peak
5. 比較 IDCM 預測位置

## 4. 結果

### 4.1 數據範圍

```
BOSS DR12 ξ(s) 數據範圍: 0.5 - 177.5 h⁻¹ Mpc
IDCM BAO 位置: 203 h⁻¹ Mpc
```

**IDCM BAO 超出數據範圍！** 最大 s=177.5 h⁻¹ Mpc < 203 h⁻¹ Mpc。

### 4.2 可觀測嘅 harmonic

| Harmonic | s (h⁻¹ Mpc) | 喺範圍內？ |
|:--------:|:-----------:|:---------:|
| λ_sync/2 (BAO) | 203.1 | ❌ 超出 |
| λ_sync/3 | 137.5 | ✅ |
| λ_sync/4 | 102.5 | ✅ |
| λ_sync/5 | 82.5 | ✅ |
| λ_sync/6 | 67.5 | ✅ |
| λ_sync/7 | 57.5 | ✅ |
| λ_sync/8 | 52.5 | ✅ |
| λ_sync/9 | 47.5 | ✅ |
| λ_sync/10 | 42.5 | ✅ |

### 4.3 結論

**BOSS DR12 ξ(s) 數據範圍太短（max 178 h⁻¹ Mpc），無法 detect IDCM BAO peak（203 h⁻¹ Mpc）。** 需要 eBOSS DR16（max 250 h⁻¹ Mpc）或 DESI 先睇到。

## 5. 腳本

`/home/wsl/IDCM/sync_bump_analysis/boss_xi_harmonic_analysis.py` (122 行)

## 6. 參考

- Ross+2016: arXiv:1607.03145, MNRAS 464, 1168
- BOSS DR12 corrfunc: `https://data.sdss.org/sas/dr12/boss/papers/clustering/Ross_etal_2016_COMBINEDDR12_corrfunc.zip`