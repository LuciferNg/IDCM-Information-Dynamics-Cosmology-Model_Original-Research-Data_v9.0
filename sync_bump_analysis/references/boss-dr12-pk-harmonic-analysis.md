# BOSS DR12 P(k) BAO Wiggle Harmonic Analysis

**日期：** 2026-08-10
**數據：** Beutler+2016, BOSS DR12 P(k) post-reconstruction
**文件：** `references/boss-dr12-pk-harmonic-analysis.md`

## 1. 目的

檢測 BOSS DR12 P(k) 嘅 BAO wiggles 是否顯示 IDCM 預測嘅 harmonic spacing。

## 2. 方法

1. 下載 Beutler+2016 P(k) 數據（從 SDSS SAS）
2. 平均 duplicate k-bins（不同 NGC/SGC 合併後有重複）
3. 用 Gaussian filter（sigma=1.5）做 smoothing
4. 提取 BAO wiggles：P(k)/P_smooth − 1
5. 檢測 wiggle peaks（amplitude > 0.02）
6. 計算相鄰 peak 之間嘅 Δk
7. 比較 IDCM 預測

## 3. 關鍵修正：平均 duplicate k-bins

原始數據有重複嘅 k 值。**必須先平均，否則 smoothing 會 detect 到假 peaks。**

```python
k_unique, idx = np.unique(k, return_inverse=True)
pk_avg = np.zeros_like(k_unique)
for i in range(len(k_unique)):
    pk_avg[i] = np.mean(pk[idx == i])
```

## 4. ⚠️ 已知 Bug：腳本用錯 h 值

分析腳本 `boss_pk_harmonic_analysis_v2.py` 第 13 行用咗 `h=0.676`（Planck），但 IDCM 嘅正確 h 係 `0.7259`。

**影響：** IDCM Δk 預測變成 0.0144 h/Mpc（錯）而唔係正確嘅 0.0155 h/Mpc。n·Δk 匹配表偏移。**但測量嘅 Δk（0.0118 ± 0.0037）係嚟自數據，唔受影響。**

## 5. 結果

### 5.1 Detected Peaks

| # | k (h/Mpc) | P/P_smooth | 匹配 (Δk=0.0155, 正確) | 匹配 (Δk=0.0144, 腳本 bug) |
|:-:|:---------:|:----------:|:----------------------:|:-------------------------:|
| 1 | 0.0223 | 1.038 | n=1 ⚠️ (dev=0.0068) | n=2 ⚠️ |
| 2 | 0.0319 | 1.031 | **n=2 ✅ (dev=0.0009)** | n=2 ✅ |
| 3 | 0.0407 | 1.023 | n=3 ⚠️ (dev=0.0058) | n=3 ✅ |
| 4 | 0.0565 | 1.030 | n=4 ⚠️ (dev=0.0055) | n=4 ✅ |
| 5 | 0.0734 | 1.045 | **n=5 ✅ (dev=0.0041)** | n=5 ✅ |
| 6 | 0.0843 | 1.025 | n=5 ⚠️ (dev=0.0068) | n=6 ✅ |
| 7 | 0.0918 | 1.022 | **n=6 ✅ (dev=0.0012)** | n=6 ⚠️ |
| 8 | 0.0990 | 1.049 | n=6 ⚠️ (dev=0.0060) | n=7 ✅ |
| 9 | 0.1166 | 1.057 | n=8 ⚠️ (dev=0.0074) | n=8 ✅ |
| 10 | 0.1267 | 1.036 | **n=8 ✅ (dev=0.0027)** | n=9 ✅ |
| 11 | 0.1407 | 1.039 | **n=9 ✅ (dev=0.0012)** | n=10 ✅ |

**11 peaks detected.** 用正確 IDCM Δk=0.0155：**5/11 match**（threshold 0.005 h/Mpc）。

### 5.2 Harmonic Spacing

```
Measured Δk = 0.0118 ± 0.0037 h/Mpc
IDCM Δk (correct) = 0.0155 h/Mpc
Deviation = 0.0037 (within 1σ)
```

## 6. 結論

| 量 | 值 | 狀態 |
|:---|:---|:----:|
| Detected peaks | 11 | ✅ |
| 匹配 n·Δk (correct) | 5/11 | ⚠️ 邊緣 |
| 匹配 n·Δk (script bug) | 9/11 | ⚠️ 用錯 h |
| Δk (measured) | 0.0118 ± 0.0037 h/Mpc | ✅ |
| Δk (IDCM) | 0.0155 h/Mpc | — |
| Deviation | 0.0037 (within 1σ) | ✅ 一致 |

**IDCM 嘅 harmonic spacing 預測（Δk=0.0155）同 BOSS DR12 數據一致（within 1σ），但個別 peak 匹配只係 5/11，唔夠說服力。**

## 7. 注意

- 腳本 `boss_pk_harmonic_analysis_v2.py` 有 h=0.676 bug（需修正）
- BOSS DR12 精度 31%，DESI DR2 可達 5%
- 真正測試需要 DESI DR2 full-shape P(k)

## 8. 腳本

`/home/wsl/IDCM/sync_bump_analysis/boss_pk_harmonic_analysis_v2.py` (159 行)

## 9. 參考

- Beutler+2016: arXiv:1607.03150
- BOSS DR12 P(k) data: `https://data.sdss.org/sas/dr12/boss/papers/clustering/`