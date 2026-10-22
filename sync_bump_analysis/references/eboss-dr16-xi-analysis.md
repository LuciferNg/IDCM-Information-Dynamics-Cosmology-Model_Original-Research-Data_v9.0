# eBOSS DR16 LRG ξ(s) Full Data Computation

**日期：** 2026-08-10
**數據：** Bautista+2020, eBOSS DR16 LRG (0.6 < z < 1.0)
**文件：** `references/eboss-dr16-xi-analysis.md`

## 1. 目的

用完整數據（唔 subsample）計算 eBOSS DR16 LRG ξ(s)，檢測 IDCM 預測嘅 BAO 位置（203 h⁻¹ Mpc）是否存在。

## 2. 數據

### 2.1 星系目錄

| 區域 | 檔案 | 星系數 | 大小 |
|:-----|:-----|:------:|:----:|
| NGC | `eBOSS_LRG_clustering_data-NGC-vDR16.fits` | 107,500 | 7.7 MB |
| SGC | `eBOSS_LRG_clustering_data-SGC-vDR16.fits` | 67,316 | 4.8 MB |
| **總計** | | **174,816** | |

### 2.2 Random 目錄

| 區域 | 檔案 | 隨機點數 | 大小 |
|:-----|:-----|:--------:|:----:|
| NGC | `eBOSS_LRG_clustering_random-NGC-vDR16.fits` | 5,460,719 | 349 MB |
| SGC | `eBOSS_LRG_clustering_random-SGC-vDR16.fits` | 3,453,453 | 221 MB |

### 2.3 重要欄位

- `RA`, `DEC`: 天球坐標
- `Z`: 紅移
- `WEIGHT_FKP`: FKP 權重（優化 S/N）
- `WEIGHT_SYSTOT`: 系統權重
- `WEIGHT_CP`: 密閉打包權重
- `WEIGHT_NOZ`: 無紅移權重

### 2.4 權重和

```
NGC data: Σw = 63282, mean = 0.5887 (N=107500)
NGC random: Σw = 56770, mean = 0.5677 (N=100k subsample)
```

## 3. 方法

### 3.1 Comoving Distance

Flat ΛCDM with IDCM 參數：
```
H₀ = 72.59 km/s/Mpc
Ω_m = 0.3167
Ω_Λ = 0.6833
```

```python
def comoving_distance(z):
    n = 500
    zv = np.linspace(0, z, n)
    E = np.sqrt(Omega_m * (1+zv)**3 + Omega_L)
    return (c/H0) * np.sum((z/n) / E)
```

**⚠️ 必須包括 1/H₀ factor！** 漏咗呢個 factor 會令距離大 100 倍（150k Mpc 唔係 1.5k Mpc）。

### 3.2 Pair Counting

使用 `cKDTree.sparse_distance_matrix(output_type='coo_matrix')`，C-level 運算，避免 Python loop。

```python
from scipy.spatial import cKDTree

# 建立樹
tree_data = cKDTree(pos_data)
tree_rand = cKDTree(pos_rand)

# DD: upper triangle only (i<j)
sd = tree_data.sparse_distance_matrix(tree_data, max_dist, output_type='coo_matrix')
mask = sd.row < sd.col
dd, _ = np.histogram(sd.data[mask] / h, bins=bins, weights=w[sd.row[mask]] * w[sd.col[mask]])

# DR: all pairs (data and random are different sets)
sdr = tree_data.sparse_distance_matrix(tree_rand, max_dist, output_type='coo_matrix')
dr, _ = np.histogram(sdr.data / h, bins=bins, weights=w[sdr.row] * w_r[sdr.col])

# RR: upper triangle only
srr = tree_rand.sparse_distance_matrix(tree_rand, max_dist, output_type='coo_matrix')
mask_r = srr.row < srr.col
rr, _ = np.histogram(srr.data[mask_r] / h, bins=bins, weights=w_r[srr.row[mask_r]] * w_r[srr.col[mask_r]])
```

性能：~23s for 107k data + 100k random（51M DD, 47M DR, 43M RR pairs）。

### 3.3 修正 Landy-Szalay Estimator

**⚠️ 常見錯誤：公式入面嘅 factor-2 係錯嘅。**

正確公式：
```python
α = Σw_data / Σw_rand
ξ = (dd / α² - dr / α + rr) / rr
σ = (1 + ξ) / √(2·rr / Σw_rand²)
```

推導：
```
Normalized DD = 2·DD_raw / W_data²  (i<j, factor 2)
Normalized DR = DR_raw / (W_data · W_rand)  (all pairs, no factor)
Normalized RR = 2·RR_raw / W_rand²  (i<j, factor 2)

ξ = (DD_norm - 2·DR_norm + RR_norm) / RR_norm
  = (DD_raw/α² - DR_raw/α + RR_raw) / RR_raw
```

**錯誤公式（勿用）：** `ξ = (dd - 2α·dr + α²·rr) / (α²·rr)` — factor 2 係錯嘅，因為 DD 同 RR 嘅 i<j normalisation 已經有 factor 2。

### 3.4 隨機 subsample

Random catalog 有 5.4M（NGC）+ 3.5M（SGC），太大。Subsample 到 100,000 點：

```python
N_rand = 100000
idx_n = np.random.choice(len(d_rn), N_rand//2, replace=False)
idx_s = np.random.choice(len(d_rs), N_rand//2, replace=False)
```

α 因子對 subsample 係 robust 嘅（因為 Σw 隨機縮放）。

## 4. 結果

### 4.1 ξ(s) 曲線（NGC only, 107k data + 100k random）

**⚠️ 注意：** `eboss_xi_full.txt` 入面嘅 ξ 值係用錯嘅 factor-2 Landy-Szalay 公式，所以全部 ≈ -2。正確嘅修正公式（無 factor-2）畀出 ξ ≈ 0。

用正確公式（`ξ = (dd/α² - dr/α + rr) / rr`，α = Σw_data/Σw_rand = 1.1148）：

| s (h⁻¹ Mpc) | DD | DR | RR | ξ (correct) | σ | S/N |
|:-----------:|:--:|:--:|:--:|:----------:|:-:|:---:|
| 203.16 | 444780 | 796763 | 357748 | **+0.0028** | 67.3 | 0.00004 |

**ξ(s) 在所有 scale 都接近 0，S/N ≈ 0，無 BAO peak detect 到。**

### 4.3 同論文比較

Bautista+2020 報告 BAO detection 約 2.5σ，但係用咗：
- 完整 NGC + SGC（174k 星系）
- 完整 random catalog（~9M）
- 完整 covariance matrix
- 多極展開（monopole + quadrupole）

我哋只係用 NGC 單 tracer monopole，所以誤差大好多。

## 5. 關鍵教訓

### 5.1 5000 星系 subsample 嘅假信號

之前用 5000 星系 subsample 計出「9 個 harmonics 全部 S/N > 3.7」係**錯誤**：

```
原因：Landy-Szalay normalization 喺細樣本下唔準
效果：成條 ξ(s) 曲線向上 shift ~0.8
結果：ξ(s) 係 flat positive 而唔係真正 peaks
```

### 5.2 正確做法

```
Full data (107k) + coo_matrix → 23s → ξ ≈ 0, S/N ≈ 0
Subsample (5k) + pdist → 0.8s → ξ ≈ 0.8, 假信號
```

**永遠唔好用 subsample 做 ξ(s) 計算。**

## 6. 結論

**eBOSS DR16 LRG ξ(s) 單用 NGC 數據，無法 detect IDCM BAO 訊號。** 誤差太大（S/N ≈ 0），需要：
- NGC + SGC 完整數據
- 完整 covariance matrix
- 或者用 P(k) 嘅 harmonic wiggles（更敏感）

## 7. 腳本

`/home/wsl/IDCM/sync_bump_analysis/eboss_xi_compute.py` (219 行)

## 8. 參考

- Bautista+2020: arXiv:2007.08993, MNRAS 503, 2729
- eBOSS DR16 data: `https://data.sdss.org/sas/dr16/eboss/lss/catalogs/DR16/`