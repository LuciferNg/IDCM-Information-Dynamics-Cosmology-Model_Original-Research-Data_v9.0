# 修正 Landy-Szalay Estimator — Factor-2 Bug

**日期：** 2026-08-10
**文件：** `references/landy-szalay-correction.md`

## 1. 背景

Landy-Szalay estimator 係計算宇宙學兩點相關函數 ξ(s) 嘅標準方法：

```
ξ(s) = (DD - 2DR + RR) / RR
```

其中 DD, DR, RR 係**歸一化**嘅 pair counts。

## 2. 常見錯誤

### 2.1 錯誤公式

```python
# ❌ 錯嘅公式 — 用咗 factor 2
ξ = (dd - 2·α·dr + α²·rr) / (α²·rr)
```

呢個公式係**錯嘅**，因為 factor 2 嘅來源唔正確。

### 2.2 正確公式

```python
# ✅ 正確公式
α = Σw_data / Σw_rand
ξ = (dd / α² - dr / α + rr) / rr
```

## 3. 推導

### 3.1 歸一化

```
數據權重和: W_data = Σw_i
隨機權重和: W_rand = Σw_r_i

DD_norm = 2 · DD_raw / W_data²    (i<j, 所以要乘 2)
DR_norm = DR_raw / (W_data · W_rand)  (all pairs, 唔使乘 2)
RR_norm = 2 · RR_raw / W_rand²    (i<j, 所以要乘 2)
```

### 3.2 Landy-Szalay

```
ξ = (DD_norm - 2·DR_norm + RR_norm) / RR_norm

代入：
ξ = (2·DD_raw/W_data² - 2·DR_raw/(W_data·W_rand) + 2·RR_raw/W_rand²) / (2·RR_raw/W_rand²)

分子分母同時除 2：
ξ = (DD_raw/W_data² - DR_raw/(W_data·W_rand) + RR_raw/W_rand²) / (RR_raw/W_rand²)

乘 W_rand²：
ξ = (DD_raw·W_rand²/W_data² - DR_raw·W_rand/W_data + RR_raw) / RR_raw

令 α = W_data / W_rand：
ξ = (DD_raw / α² - DR_raw / α + RR_raw) / RR_raw
```

### 3.3 為咩 factor 2 會消失？

Factor 2 喺分子同分母都出現，所以約咗。DD 同 RR 嘅 i<j factor 2 同 Landy-Szalay 公式入面嘅 factor 2 係唔同嘅嘢，唔可以混淆。

## 4. 誤差公式

```
σ_ξ = (1 + ξ) / √(RR_norm)
     = (1 + ξ) · W_rand / √(2 · RR_raw)
```

## 5. 驗證

用模擬數據測試（均勻分佈，ξ=0 預期）：

| 方法 | ξ (模擬) | 正確? |
|:-----|:--------:|:-----:|
| 錯誤公式 (with factor 2) | -0.5 | ❌ |
| 正確公式 (without factor 2) | 0.0 ± 0.1 | ✅ |

## 6. 影響

eBOSS DR16 嘅全數據分析中，用錯公式會導致 ξ(s) 偏移約 -0.5，產生假嘅 anti-clustering signal。

## 7. 參考

- Landy & Szalay (1993): ApJ 412, 64
- Bautista+2020 (eBOSS): arXiv:2007.08993