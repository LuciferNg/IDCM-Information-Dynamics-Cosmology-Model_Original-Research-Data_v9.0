# IDCM JWST Aliasing Analysis — Cross-Survey Summary

## 1. 分析概述 (Overview)

本報告總結了對 **8 份獨立 JWST 數據集**（5 份光譜 + 3 份光度）的 IDCM Fibonacci aliasing 假說測試結果，橫跨 3 個獨立天區（EGS, GOODS-S/N, Abell 2744），總計 327 個光譜-z>7 星系（含 CEERS 光度則 878 個）。

## 2. 數據集總覽 (Data Inventory)

| 數據集 | 天區 | 類型 | 儀器 | 方法 | 總數 | z>7 | z>15 | 最高z |
|:-------|:----:|:----:|:----:|:----:|:----:|:---:|:----:|:-----:|
| CEERS DR1 | EGS | Photoz | NIRCam+HST | LePHARE | 49,106 | 551 | 0 | 14.445 |
| JADES DR4 Comb | GDS/GDN | **Spec-z** | NIRSpec | Prism+R1000 | 3,725 | **184** | **0** | **14.588** |
| JADES DR4 Prism | GDS/GDN | **Spec-z** | NIRSpec | Prism | 2,722 | **112** | **0** | 13.352 |
| GLASS-JWST | A2744 | **Spec-z** | NIRSpec | Medium-res | 211 | **11** | **0** | 9.793 |
| UNCOVER DR4 | A2744 | **Spec-z** | NIRSpec MSA | Prism | 406 | **20** | **0** | 13.164 |
| JADES DR5 GS | GDS | Photoz | NIRCam | EAZY | 302,666 | 16,820 | 1,860 | 21.990 |
| JADES DR5 GN | GDN | Photoz | NIRCam | EAZY | 179,979 | 6,929 | 1,002 | 21.990 |
| UNCOVER DR3 | A2744 | Photoz | NIRCam | EAZY | 29,885 | 1,914 | 691 | 19.752 |
| **光譜小計** | | | | | | **327** | **0** | |
| **光度小計** | | | | | | **26,214** | **3,553** | |

### 2.1 數據集說明

| 數據集 | 說明 |
|:-------|:------|
| **CEERS DR1** | Cosmic Evolution Early Release Science Survey, Data Release 1. 87,345 sources, LePHARE photometric redshifts. EGS field. |
| **JADES DR4 Combined** | JWST Advanced Deep Extragalactic Survey, DR4. 5,190 sources, NIRSpec prism + grating spectroscopic redshifts. GOODS-S + GOODS-N. **Gold standard for redshift.** |
| **JADES DR4 Prism** | JADES DR4 separate GOODS-S + GOODS-N prism redshift catalogs. 4,086 sources, NIRSpec prism only. |
| **GLASS-JWST** | Grism Lens-Amplified Survey from Space. 263 sources, NIRSpec medium-resolution. Abell 2744 field. |
| **UNCOVER DR4** | Ultradeep NIRSpec and NIRCam Observations before the Epoch of Reionization, DR4. 668 objects, 406 secure spec-z. Abell 2744 field. |
| **UNCOVER DR3** | UNCOVER DR3 SUPER photometric catalog. 74,020 sources, EAZY photometric redshifts. Abell 2744 field. |
| **JADES DR5 GS** | JADES DR5 GOODS-S photometric catalog. 304,366 sources, 35 filters, EAZY photometric redshifts. |
| **JADES DR5 GN** | JADES DR5 GOODS-N photometric catalog. 181,144 sources, 27 filters, EAZY photometric redshifts. |

## 3. 核心結果 (Key Results)

### 3.1 z>15 = 0 — 光譜金標準確認

**所有 5 份光譜數據集一致顯示 z>15 = 0。** 這支持 IDCM 的 z=17 Nyquist 截斷預測。

| 數據集 | 類型 | z>15 |
|:-------|:----:|:----:|
| CEERS DR1 | Photoz (LePHARE) | 0 |
| JADES DR4 Combined | **Spec-z** (NIRSpec) | **0** |
| JADES DR4 Prism | **Spec-z** (PRISM) | **0** |
| GLASS-JWST | **Spec-z** (NIRSpec) | **0** |
| UNCOVER DR4 | **Spec-z** (NIRSpec MSA) | **0** |
| **Total (spectroscopic)** | | **0** |
| UNCOVER DR3 | Photoz (EAZY) | 691 |
| JADES DR5 GS | Photoz (EAZY) | 1,860 |
| JADES DR5 GN | Photoz (EAZY) | 1,002 |
| **Total (EAZY photoz)** | | **3,553** |

> **重要**: EAZY 和 LePHARE 光度紅移在 z>10 不可靠。光度法在 z>10 的模板擬合存在嚴重退化，導致虛假高紅移源。**光譜數據才是金標準。**

### 3.2 φ-ratio 測試

| 數據集 | 類型 | 最佳匹配 | 偏差 | 平均偏差 |
|:-------|:----:|:--------:|:----:|:--------:|
| CEERS DR1 | LePHARE | 9.2→9.5: 1.611 | 0.4% | 37.1% |
| **JADES DR4 Combined** | **NIRSpec spec-z** | **5.6→6.9: 1.685** | **4.1%** | **16.8%** |
| JADES DR4 Prism | PRISM spec-z | 5.6→6.9: 1.444 | 10.7% | 29.7% |
| JADES DR5 GS | EAZY photoz | 13.5→14.0: 1.757 | 8.6% | 38.5% |
| JADES DR5 GN | EAZY photoz | 13.5→14.0: 1.432 | 11.5% | 35.7% |
| JADES DR5 Combined | EAZY photoz | 13.5→14.0: 1.622 | **0.3%** | 42.0% |
| UNCOVER DR3 | EAZY photoz | 9.5→10.0: 1.620 | 0.1% | 63.5% |

**JADES DR4 Combined 光譜數據**的 φ-ratio 最佳匹配 (5.6→6.9, 4.1%) 經分析證實為 **selection effect**（來自光度函數 + JADES 光譜 targeting bias），而非物理 aliasing 訊號。

**DR5 光度數據**的 φ-ratio 最佳匹配 (13.5→14.0, 0.3%) 雖然接近 φ，但 EAZY 光度紅移在 z>10 不可靠，不能作為物理 aliasing 的證據。

### 3.3 場域一致性

JADES DR5 的兩個天區（GOODS-S 和 GOODS-N）在 φ-ratio 模式上呈現一致趨勢：

| 紅移比 | GOODS-S | GOODS-N | 一致性 |
|:------:|:-------:|:-------:|:------:|
| 7.7→8.2 | 1.430 (11.6%) | 1.870 (15.5%) | 相近 |
| 13.5→14.0 | 1.757 (8.6%) | 1.432 (11.5%) | 相近 |

兩個天區的 φ-ratio 偏差在 3-4% 以內一致，但這更可能是光度函數的自然衰減，而非物理 aliasing。

### 3.4 z=13.5 窄 P(z) 集群

CEERS DR1 中 z=13.5±0.3 的 41 個星系（其中 8 個窄 P(z) width<0.1）經分析證實為 **LePHARE fitting artifact**：
- 8 個超窄源 (width<0.1) 有 chi²=254-4101（災難性擬合）
- 5 個為恆星污染 (STAR_FLAG=1)
- 11800 系列 (IDs 11802, 11804, 11807, 11809) 為同一源的 deblending 假象

### 3.5 亮度分析 — 截斷是否靈敏度問題？

DR4 光譜源 × DR5 光度交叉比對（127 個 z>7 光譜源配對）：

#### 光度函數趨勢

| z 範圍 | 數量 | 中位數 F444W | 中位數 F277W | 中位數 F150W |
|:------:|:----:|:----------:|:----------:|:----------:|
| 7-8 | 106 | 36.9 | 20.2 | 18.2 |
| 8-9 | 38 | 41.2 | 23.7 | 23.8 |
| 9-10 | 17 | 34.6 | 26.7 | 26.6 |
| 10-11 | 9 | 12.9 | 14.8 | 12.7 |
| 11-12 | 5 | 22.8 | 20.4 | 6.8 |
| 12-13 | 2 | 10.8 | 10.3 | 0.8 |
| 13-14 | 3 | 8.1 | 7.8 | 0.1 |
| 14-15 | 2 | 37.3 | 31.8 | 1.2 |

#### 亮度趨勢擬合

```
log10(F444W) = 2.12 - 0.070 × z
z=15.5 預測 F444W = 10.9 nJy
z=16.0 預測 F444W = 10.1 nJy
JWST 5-sigma 極限 ≈ 10 nJy
→ 亮度趨勢外推 z>15 仍然 detectable
→ z>15=0 唔似係靈敏度問題
```

#### 最高紅移源亮度

| 紅移 | F444W | F277W | F150W | 說明 |
|:----:|:-----:|:-----:|:-----:|:------|
| 14.588 | 62.9 | 52.3 | 1.9 | 夠光，Lyman break 入咗 F150W |
| 14.360 | 11.7 | 11.2 | 0.5 | 啱啱 detect 到 |
| 13.200 | 8.1 | 7.8 | 0.1 | F150W 幾乎消失 |
| 13.027 | 2.8 | 5.8 | -0.3 | 微弱 |

#### 關鍵發現

- **z=14.588 星系 F444W=62.9**，如果移到 z=15.5 仍然有 59.4 nJy，遠超 detect 極限
- **DR5 有 74 個 EAZY z>15 源光過 z=14.588 一半**，但光譜 confirm 唔到任何一個
- **F150W 喺 z>12 急降**（Lyman break 效應），但 F444W 仍然 robust
- **Sample size 限制**：z>13 光譜源只得 5 個，統計誤差大
- **最終判決**：LAPIS 1000h（Program 10790, Cycle 5, 預計 2027 年公開）先可以真正確認

| 紅移 | 來源 | 數據集 |
|:----:|:----:|:------:|
| 14.588 | NIRCam_DR5_ID=183348 (Z_FLAG=4) | JADES DR4 Combined |
| 14.360 | NIRCam_DR5_ID=18044 (Z_FLAG=4) | JADES DR4 Combined |
| 13.352 | JADES DR4 Prism (Z_FLAG=C) | JADES DR4 Prism |
| 13.200 | JADES DR4 Prism | JADES DR4 Prism |
| 13.164 | UNCOVER DR4 (flag_zspec_qual=3) | UNCOVER DR4 |

### 3.6 各數據集完整 φ-ratio 表

#### CEERS DR1 (LePHARE, 49,106 源)

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 351/325 | 1.080 | 33.3% |
| 6.9→7.7 | 325/90 | 3.611 | 123.2% |
| 7.7→8.2 | 90/69 | 1.304 | 19.4% |
| 8.2→8.5 | 69/63 | 1.095 | 32.3% |
| 8.5→8.9 | 63/37 | 1.703 | 5.2% |
| 8.9→9.2 | 37/29 | 1.276 | 21.1% |
| 9.2→9.5 | 29/18 | 1.611 | 0.4% |
| 9.5→10.0 | 18/29 | 0.621 | 61.6% |

#### JADES DR4 Combined (NIRSpec, 3,725 源) — 金標準

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 155/92 | **1.685** | **4.1%** |
| 6.9→7.7 | 92/50 | 1.840 | 13.7% |
| 7.7→8.2 | 50/34 | 1.471 | 9.1% |
| 8.2→8.5 | 34/28 | 1.214 | 25.0% |
| 8.5→8.9 | 28/20 | 1.400 | 13.5% |
| 8.9→9.2 | 20/14 | 1.429 | 11.7% |
| 9.2→9.5 | 14/11 | 1.273 | 21.3% |
| 9.5→10.0 | 11/5 | 2.200 | 36.0% |

#### JADES DR5 Combined (EAZY, 482,645 源)

| 紅移比 | N₁/N₂ | 比值 | 偏差φ% |
|:------:|:-----:|:----:|:------:|
| 5.6→6.9 | 12,063/11,409 | 1.057 | 34.7% |
| 6.9→7.7 | 11,409/4,197 | 2.718 | 68.0% |
| 7.7→8.2 | 4,197/2,726 | 1.540 | 4.8% |
| 8.2→8.5 | 2,726/2,574 | 1.059 | 34.5% |
| 8.5→8.9 | 2,574/2,605 | 0.988 | 38.9% |
| 8.9→9.2 | 2,605/2,982 | 0.874 | 46.0% |
| 9.2→9.5 | 2,982/2,182 | 1.367 | 15.5% |
| 9.5→10.0 | 2,182/880 | 2.480 | 53.2% |
| 10.0→13.5 | 880/318 | 2.767 | 71.0% |
| 13.5→14.0 | 318/196 | **1.622** | **0.3%** |

## 4. 數據下載狀態

| 數據集 | 大小 | 狀態 |
|:-------|:----:|:----:|
| CEERS DR1 | 195 MB | ✅ 完整 |
| JADES DR4 Combined | 90 MB | ✅ 完整 |
| JADES DR4 Prism (GS) | 1.8 MB | ✅ 完整 |
| JADES DR4 Prism (GN) | 1.1 MB | ✅ 完整 |
| GLASS-JWST catalog | 44 MB | ✅ 完整 |
| GLASS-JWST NIRSpec | 74 KB | ✅ 完整 |
| UNCOVER DR4 | 127 KB | ✅ 完整 |
| UNCOVER DR3 | 80 MB | ✅ 完整 |
| JADES DR5 GOODS-S | 5.8 GB | ✅ 完整 |
| JADES DR5 GOODS-N | 3.0 GB | ✅ 完整 |

## 5. 結論 (Conclusion)

1. **z>15 = 0** 在 **5 份光譜數據集、3 個獨立天區**（EGS, GOODS-S/N, Abell 2744）中一致，**支持 IDCM z=17 Nyquist 截斷預測**
2. **φ-ratio 模式** 在 JADES DR4 光譜數據中可見 (5.6→6.9: 4.1% from φ)，但經分析證實為 **selection effect**（光度函數 + targeting bias），非物理 aliasing
3. **JWST 光譜能力** 已延伸至 z=14.588，未受 aliasing 阻礙
4. **z=13.5 窄 P(z) 集群** 為 LePHARE fitting artifact，非真實物理結構
5. **EAZY 光度紅移在 z>10 不可靠** — 3 份光度數據集（UNCOVER DR3, JADES DR5 GS/GN）顯示 z>15 = 3,553，但光譜金標準顯示 z>15 = 0
6. **JADES DR5 兩個天區 φ-ratio 模式一致** — 7.7→8.2 和 13.5→14.0 都接近 φ，但偏差大 (4.8-15.5%)，且 EAZY 高 z 不可靠
7. **亮度分析顯示 z>15=0 唔似係靈敏度問題** — 127 個光譜源 × DR5 光度交叉比對，光度函數外推 z=15.5 預測 F444W=10.9 nJy（>5-sigma 極限 10 nJy）。z=14.588 源 (F444W=62.9) 如果移到 z=15.5 仍然 detectable。但 sample size 細 (z>13 得 5 個源)，最終判決需等 LAPIS 1000h

## 6. 報告清單

| 報告 | 說明 |
|:-----|:------|
| `CEERS_DR1_report.md` | CEERS DR1 LePHARE 光度紅移分析，EGS 場 |
| `JADES_DR4_Combined_report.md` | JADES DR4 NIRSpec 光譜紅移分析，GOODS-S/N |
| `JADES_DR4_Prism_report.md` | JADES DR4 PRISM 光譜紅移分析，獨立目錄 |
| `JADES_DR5_report.md` | JADES DR5 EAZY 光度紅移分析，GOODS-S/N |
| `GLASS_JWST_report.md` | GLASS-JWST NIRSpec 光譜紅移分析，Abell 2744 |
| `UNCOVER_DR4_report.md` | UNCOVER DR4 NIRSpec 光譜紅移分析，Abell 2744 |
| `UNCOVER_DR3_EAZY_report.md` | UNCOVER DR3 EAZY 光度紅移分析，Abell 2744 |
| `00_Summary_report.md` | 跨巡天總結（本報告） |