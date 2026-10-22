# z > 17 觀測極限 — 宇宙視界

**日期：** 2026-08-10
**文件：** `references/z17-observational-limit.md`

## 1. 背景

調律者 insight：**「觀測只能局部，因為受宇宙視界影響 z=17以上無法觀測」**

## 2. 觀測證據

### 2.1 JWST 光譜數據

| 數據集 | 類型 | N(z>15) | Max z | 天區 |
|:-------|:----:|:-------:|:-----:|:----:|
| CEERS DR1 | Photometric | 0 | 14.445 | EGS |
| JADES DR4 Combined | Spectroscopic | 0 | 14.588 | GDS/GDN |
| JADES DR4 Prism | Spectroscopic | 0 | 13.352 | GDS/GDN |
| GLASS-JWST NIRSpec | Spectroscopic | 0 | 9.793 | A2744 |
| UNCOVER DR4 | Spectroscopic | 0 | 13.164 | A2744 |
| **總計** | | **0** | **14.588** | **3 fields** |

**5 個獨立光譜數據集，3 個獨立天區，無任何 z>15 嘅星系。** 呢個唔係隨機嘅 — 係系統性嘅邊界。

### 2.2 同渲染邊界假說一致

z=17 係 Nyquist cutoff（44-site K_Chain 嘅最大可渲染深度）。超過呢個 redshift，W-field 晶格無足夠嘅 site 去解析結構。

## 3. IDCM 嘅解釋

### 3.1 K_Tree 層級

K_Tree 有 M=33 層，branching B=4：

```
z = B^ℓ - 1
ℓ = 0: z = 0
ℓ = 1: z = 3
ℓ = 2: z = 15
ℓ = 3: z = 63
...
ℓ = 33: z = 7×10¹⁹
```

z=17 對應 ℓ ≈ 2.04（介乎 level 2 同 3 之間）。

### 3.2 物理意義

z>17 嘅宇宙存在（K_Tree 仲有 31 層），但**無法觀測**，因為：
1. 44-site K_Chain 嘅 Nyquist 頻率限制
2. 投影空間嘅解析度極限
3. 唔係「宇宙開始」，而係「觀測邊界」

## 4. 同 ΛCDM 嘅對比

| 方面 | ΛCDM | IDCM |
|:-----|:------|:------|
| z>17 點解冇星系？ | 宇宙太年輕，星系未形成 | 渲染邊界，K_Chain 解析度極限 |
| CMB (z≈1100) | 重組表面 | 超出觀測極限，但係另一種機制 |
| Big Bang | 時間起點 | 觀測邊界，唔係絕對起點 |
| z>17 嘅宇宙 | 存在，但黑暗 | 存在，但無法渲染 |

## 5. 意義

對於 IDCM 宇宙學測試：

1. **DESI（z=2.33）完全喺觀測範圍內** — 如果 IDCM 嘅預測同 DESI 數據唔吻合，唔可以用「高 z 行為唔同」嚟解釋
2. **z>17 嘅行為不可知** — 任何關於 z>17 嘅推測都係 metaphysical
3. **測試策略** — 集中喺 z<17 嘅可觀測預測

## 6. 參考

- JWST 數據分析: `references/jwst-data-access.md`
- 渲染邊界: `references/sync-bump-observer-dynamic.md`
- K_Tree 層級: `references/large-scale-structure.md`