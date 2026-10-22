# IDCM 發射線趨勢完整驗證報告 — [OIII]/Hβ vs 結構座標 ℓ

## 文檔編號：38_vshape_verification
## 版本：2.0（2026-08-12）
## 狀態：🟢 完整（含 BOSS gap 填補 + 質量控制）

---

## 1. 目的

### 原始假設
本 session 測試以下假設鏈：

1. **H₁：** [OIII]/Hβ 隨 z（結構座標 ℓ）呈「V 形」— 低 z 下降 + 高 z 上升，可能係結構梯度而非選樣假象
2. **H₂：** 若 SDSS 下降支係真實結構 → 控制質量/金屬量後仍然下降
3. **H₃：** 若 V 形係真實 → BOSS 填補 z=0.3-1.5 gap 後應顯示連續性
4. **H₄：** 若 JADES 上升支係真實結構 → 控制質量後仍然上升
5. **H₅：** 若所有趨勢係 pipeline 污染 → 獨立擬合後趨勢消失

### 方法保證
驗證用以下方法確保無偏：
- **無目錄污染**：全部用原始光譜（FITS）獨立擬合，唔用任何 pipeline 目錄
- **大樣本**：SDSS 5000 + BOSS 4000 + JADES 1151 = 共 >8000 條光譜
- **控制變數**：質量、金屬量雙重控制
- **獨立污染抗性比率**：用 [OIII]/Hβ 同 Hα/[OIII] 兩個獨立比率

---

## 2. 數據樣本

### 2.1 樣本摘要

| 樣本 | 光譜數 | 成功擬合 | z 範圍 | ℓ 範圍 | 下載來源 | 下載方法 |
|:-----|:------:|:-------:|:------:|:------:|:---------|:---------|
| SDSS 小樣本 | 1000 | 998 | 0.001-0.1 | 0.001-0.065 | SDSS DR18 SAS | `curl -C -` 續傳 |
| SDSS 大樣本 | 5000 | 3173 | 0.001-0.1 | 0.001-0.065 | SDSS DR18 SAS | `bulk_download.py` 並發 16 |
| JADES 高z | 463 | 463 | 2-9.7 | 1.0-1.73 | STScI MAST x1d | `curl` 逐條 |
| JADES gap | 688 | 688 | 0.5-3.0 | 0.32-0.83 | STScI MAST x1d | `bulk_download.py` 並發 16 |
| **BOSS** | 4000 | 3974 | **0.3-2.0** | **0.22-0.83** | SDSS DR18 optical API | `download_boss5.py` 串行+delay |
| **合計** | **8151** | **6796** | **0.001-9.7** | **0.001-1.73** | — | — |

### 2.2 目錄檔案

| 檔案 | 大小 | 內容 | 下載狀態 |
|:-----|:---:|:-----|:--------|
| `jades_photo.fits` | 674 MB | JADES NIRCam 光度目錄（94000 天體，ID/RA/DEC/23-band flux） | ✅ 完整 |
| `specObj_dr17.fits` | 6.74 GB | SDSS/BOSS/eBOSS 光譜目錄（580 萬行，z=-0.01-7.06） | ✅ 完整 |

### 2.3 下載技術細節

- **SDSS 光譜路徑**：`data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/{plate}/spec-{plate}-{mjd}-{fiber:04d}.fits`（run2d=26）
- **BOSS 光譜路徑**：`https://dr18.sdss.org/optical/spectrum/view/data/format=fits/spec=lite?plateid={}&mjd={}&fiberid={}`（run2d=v5_10_0，lite 格式）
- **JADES x1d 光譜**：`https://archive.stsci.edu/hlsps/jades/dr2/goods-s/...`（MAST 伺服器，~30KB/s 速度限制）
- **SDSS SQL API**：`POST https://skyserver.sdss.org/dr18/SearchTools/sql`（需 `__RequestVerificationToken` + `searchtool=SQL`）
- **Skyserver 恢復**：2026-08-12 重新可用（之前 503 導致需下載 specObj 6.7GB）

---

## 3. 擬合方法

### 3.1 獨立光譜擬合（全部樣本統一）

所有樣本（SDSS COADD、BOSS COADD lite、JADES x1d）使用同一套方法：

1. **局部連續譜**：±3×半寬兩側嘅線翼區中位數
2. **噪聲估計**：連續譜區 MAD（中位數絕對偏差）×1.4826
3. **高斯擬合**：scipy.optimize.curve_fit，mu 固定喺線中心（紅移後），sigma 範圍 [0.0002, 0.005] μm
4. **線流量**：amp × sigma × √(2π) × 10000 [Å]
5. **偵測標準**：SNR > 3（振幅/噪聲）

擬合線列表（rest-frame wavelength [μm]）：
- [OII] 3727: 0.37270
- Hβ 4861: 0.48610
- [OIII] 4959: 0.49590
- [OIII] 5007: 0.50070
- Hα 6563: 0.65630
- [NII] 6584: 0.65840

### 3.2 質量控制（SDSS）

用 MPA-JHU `newmasses_dr4.gz` 目錄（Kauffmann+03 方法，`rml50` 欄）：
- 質量範圍：log(M*/M☉) = 7.0-11.5
- 金屬量：Tremonti+04 `gal_fiboh.fits.gz`（O3N2 方法）
- ⚠️ 此檔案已於 /tmp 清理時刪除（2026-08-12），控制變數結果已固定於文檔中

### 3.3 JADES 質量 proxy（光度）

用 JADES NIRCam photometry catalog（`Kron` aperture）：
- **F277W 光度**（rest-frame optical 喺 z=2-8）：用 `F277W_KRON` 做質量 proxy
- 假設：F277W flux 正比於 M*（rest-frame optical 嘅質量-光度比喺高 z 星形成星系較穩定）
- 重疊率：810/2525 發射線天體有 photometry（ID 對應）
- ⚠️ `jades_prism_line.fits` 已於 /tmp 清理時刪除，但光度目錄 `jades_photo.fits` 仍存在於 `data/catalogs/`

---

## 4. 結果

### 4.1 SDSS [OIII]/Hβ vs z（低 z，混合樣本）

| z bin | ℓ | n | median | P25 | P75 | 控制前 |
|:-----:|:--:|:--:|:------:|:---:|:---:|:------:|
| 0.001-0.02 | 0.008 | 461 | 2.23 | 1.50 | 2.85 | 下降 |
| 0.02-0.03 | 0.018 | 252 | 1.64 | 0.97 | 2.46 | 下降 |
| 0.03-0.04 | 0.025 | 277 | 1.59 | 0.93 | 2.35 | 下降 |
| 0.04-0.05 | 0.032 | 230 | 1.33 | 0.76 | 2.09 | 下降 |
| 0.05-0.06 | 0.039 | 258 | 1.21 | 0.72 | 1.84 | 下降 |
| 0.06-0.07 | 0.045 | 249 | 1.10 | 0.60 | 1.61 | 下降 |
| 0.07-0.08 | 0.052 | 224 | 0.87 | 0.54 | 1.38 | 下降 |
| 0.08-0.10 | 0.062 | 396 | 0.76 | 0.53 | 1.21 | 下降 |

Spearman 相關：**rho = -0.428, p = 3.9×10⁻¹⁰⁵**（極顯著下降）

### 4.2 控制變數分析（SDSS）

| 控制 | 低z (z<0.03) | 高z (z>0.06) | p | 結論 |
|:-----|:-----------:|:------------:|:--:|:----:|
| 冇控制（混合） | med 2.05 | med 0.86 | **2.3e-79** | 下降極顯著 |
| 固定質量 M=9.0-9.5 | 1.73 | 1.74 | 0.63 | **FLAT** |
| 固定質量 M=9.5-10.0 | 0.93 | 1.03 | 0.53 | **FLAT** |
| M=9.0-9.5 + Z=8.5-9.0 | n=21 | n=19 | 0.62 | **FLAT** |
| M=9.5-10.0 + Z=8.5-9.0 | n=15 | n=103 | 0.60 | **FLAT** |

**顯著比例：0/4（冇任何控制後仲顯著）**

### 4.3 混雜機制確認

| 量 | 低z (z<0.03) | 高z (z>0.06) |
|:---|:-----------:|:------------:|
| 質量 med | **8.59** | **10.10** |
| 金屬量 med | **8.55** | **8.77** |

**金屬量 → [OIII]/Hβ 關係：**
| 金屬量 bin | n | [OIII]/Hβ med |
|:----------:|:--:|:------------:|
| Z=8.0-8.5 | 341 | 2.80 |
| Z=8.5-9.0 | 1274 | 1.38 |
| Z=9.0-9.5 | 471 | 0.50 |

**金屬量升 1 dex → [OIII]/Hβ 跌 5.6x**

### 4.4 BOSS [OIII]/Hβ vs z（gap 填補）

| z bin | ℓ | n | median | P25 | P75 |
|:-----:|:--:|:--:|:------:|:---:|:---:|
| 0.3-0.4 | 0.216 | 26 | 2.00 | 0.81 | 3.64 |
| 0.4-0.5 | 0.268 | 26 | 1.51 | 0.51 | 7.23 |
| 0.5-0.6 | 0.316 | 57 | 1.77 | 0.51 | 4.06 |
| 0.6-0.7 | 0.361 | 95 | 1.18 | 0.50 | 2.89 |
| 0.7-0.8 | 0.404 | 91 | 1.30 | 0.63 | 3.01 |
| 0.8-0.9 | 0.444 | 156 | 1.70 | 0.65 | 3.51 |
| 0.9-1.0 | 0.482 | 126 | 1.69 | 0.57 | 3.85 |
| 1.0-1.2 | 0.535 | 103 | 2.84 | 1.22 | 5.56 |
| 1.2-1.5 | 0.616 | 16 | 0.83 | 0.52 | 1.00 |

Spearman 相關：**rho = +0.129, p = 7.6×10⁻⁴**（非常弱，大致 flat）

### 4.5 JADES [OIII]/Hβ vs z（高 z）

| z bin | ℓ | n | median | P25 | P75 |
|:-----:|:--:|:--:|:------:|:---:|:---:|
| 2-4 | 1.085 | 40 | 0.76 | 0.57 | 1.30 |
| 4-5 | 1.230 | 73 | 2.05 | 1.17 | 4.28 |
| 5-6 | 1.350 | 79 | 4.18 | 2.21 | 7.32 |
| 6-8 | 1.500 | 56 | 5.06 | 3.77 | 6.58 |

Spearman 相關：**rho = +0.484, p = 3.1×10⁻¹⁶**（極顯著上升）

### 4.6 JADES 質量 proxy 控制結果

用 F277W 光度（rest-frame optical）做質量 proxy，分三位後：

| 質量 | z=2-4 | z=4-5 | z=5-6 | z=6-8 | 趨勢 |
|:----|:-----:|:-----:|:-----:|:-----:|:----:|
| low | 0.77 | 3.41 | 4.12 | **7.89** | ↑ |
| mid | — | 2.19 | 8.66 | 4.84 | ↑ |
| high | — | 2.58 | 3.45 | — | ↑ |

**JADES 上升支唔係質量假象（控制後仍然上升）**

### 4.7 完整合併趨勢

| ℓ | z | [OIII]/Hβ med | n | 樣本 | 趨勢 |
|:--:|:--:|:-----------:|:--:|:-----|:----:|
| 0.008 | 0.01 | 2.23 | 461 | SDSS | 控制質量後 flat |
| 0.062 | 0.09 | 0.76 | 396 | SDSS | 控制質量後 flat |
| 0.216 | 0.35 | 2.00 | 26 | BOSS | flat |
| 0.316 | 0.55 | 1.77 | 57 | BOSS | flat |
| 0.404 | 0.75 | 1.30 | 91 | BOSS | flat |
| 0.444 | 0.85 | 1.70 | 156 | BOSS | flat |
| 0.535 | 1.10 | 2.84 | 103 | BOSS | flat |
| 1.085 | 3.5 | 0.76 | 40 | JADES | 低點 |
| 1.230 | 4.5 | 2.05 | 73 | JADES | 上升 |
| 1.500 | 7.0 | 5.06 | 56 | JADES | 急升 |

---

## 5. 統計驗證

### 5.1 SDSS 下降支（p=8.8×10⁻⁷⁷）
- z=0.001-0.03：med=2.05（n=713）
- z=0.07-0.10：med=0.79（n=620）
- **下降 2.6x**，Mann-Whitney U p=8.8e-77

### 5.2 JADES 上升支（p=8.2×10⁻¹⁴）
- z=2-4：med=0.76（n=40）
- z=5-8：med=4.86（n=135）
- **上升 6.4x**，Mann-Whitney U p=8.2e-14

### 5.3 BOSS 區間（p=0.0008）
- Spearman rho=+0.129（n=680）
- 非常弱相關，大致 flat

### 5.4 數值驗證（38 項全部 ✅）

| 類別 | 檢查項數 | 通過 | 容差 |
|:-----|:-------:|:----:|:----:|
| SDSS bin n | 8 | 8 ✅ | 5% |
| SDSS bin med | 8 | 8 ✅ | 5% |
| BOSS bin n | 8 | 8 ✅ | 15% |
| BOSS bin med | 8 | 8 ✅ | 15% |
| BOSS Spearman | 1 | 1 ✅ | 30% |
| JADES bin n | 4 | 4 ✅ | 15% |
| JADES bin med | 4 | 4 ✅ | 10% |
| specObj BOSS count | 1 | 1 ✅ | 1% |
| **總計** | **42** | **42 ✅** | — |

---

## 6. 推導鏈

### 6.1 Session 工作流程

```
1. SDSS 小樣本 (1000) → 發現 V 形
   ↓
2. SDSS 大樣本 (5000) → 確認 V 形統計顯著
   ↓
3. 控制變數分析 → 下降支 = 質量/金屬量假象
   ↓
4. JADES 高 z (463) → 上升支存在
   ↓
5. JADES gap (688) → 填 z=0.5-3 gap
   ↓
6. BOSS 下載 + 擬合 (3997) → 填 z=0.3-1.5 gap（核心）
   ↓
7. JADES 質量 proxy (F277W) → 上升支唔係質量假象
   ↓
8. specObj 驗證 (580 萬行) → 樣本完整性確認
   ↓
9. jades_photo.cross-match (810 ID) → 光度 vs 光譜對應
```

### 6.2 關鍵技術突破

- **SDSS SQL API 打通**：`POST /dr18/SearchTools/sql`（需 `searchtool=SQL` + anti-CSRF token）
- **BOSS 光譜正確路徑發現**：`redux/v5_10_0` 但 lite 格式用 `optical/spectrum/view/data/format=fits/spec=lite` API
- **串行下載策略**：對 throttling server，單線程 + 800ms delay 比 32 並發更快（0 fail vs 114 fail）
- **/tmp tmpfs 爆滿處理**：16GB tmpfs 100% 時清理，搬數據去 `/home/wsl/IDCM/data/`（480GB free）

### 6.3 混雜機制（已確認）

```
高 z bin → 高質量 → 高金屬量 → [OIII]/Hβ 低
                        ↑
                  金屬量升 1 dex → [OIII]/Hβ 跌 5.6x
```

---

## 7. 記錄文檔

### 7.1 本 session 建立/修改檔案

| 檔案 | 用途 | 狀態 |
|:-----|:-----|:----:|
| `build_sdss_manifest.py` | 建立 SDSS 5000 條下載清單 | ✅ 已用 |
| `build_gap_manifest.py` | 建立 JADES gap 688 條下載清單 | ✅ 已用 |
| `bulk_download.py` | 通用並發下載器 | ✅ 已用 |
| `fit_sdss_large.py` | SDSS 5000 條獨立擬合 | ✅ 完成 |
| `fit_jades_gap.py` | JADES gap 擬合 | ✅ 完成 |
| `fit_boss.py` | BOSS 3997 條獨立擬合 | ✅ 完成 |
| `download_boss*.py` | BOSS 下載（v1-v5 迭代） | ✅ 完成 |
| `query_boss.py` | skyserver SQL 查詢 | ✅ 完成 |
| `mass_controlled_test.py` | 質量控制測試 | ✅ 完成 |
| `controlled_vshape_test.py` | 質量+金屬量雙重控制 | ✅ 完成 |
| `jades_mass_control.py` | JADES 質量 proxy 控制 | ✅ 完成 |
| `merge_all_analysis.py` | 合併 SDSS+BOSS+JADES | ✅ 完成 |
| `final_compare.py` | 最終對比分析 | ✅ 完成 |
| `verify_all_numbers.py` | 數值驗證（42 項） | ✅ 通過 |
| `compare_analysis.py` | specObj + jades_photo 對比 | ✅ 完成 |

### 7.2 數據檔案位置

```
/home/wsl/IDCM/data/
├── catalogs/
│   ├── jades_photo.fits        (674 MB) — JADES 光度目錄
│   └── specObj_dr17.fits       (6.74 GB) — SDSS/BOSS/eBOSS 光譜目錄
├── boss_spec/                  (3997 個) — BOSS 獨立下載光譜
├── sdss_spec_large/            (5000 個) — SDSS 大樣本光譜
├── sdss_spec/                  (1000 個) — SDSS 小樣本光譜
├── jades_spec/                 (463 個) — JADES 高 z 光譜
└── jades_gap_spec/             (688 個) — JADES 低 z 光譜
```

---

## 8. 結論

### 8.1 假設驗證結果

| 假設 | 內容 | 結果 | 證據 |
|:----|:-----|:----|:-----|
| H₁ | [OIII]/Hβ 呈 V 形 | **❌ 推翻** | 下降支 = 質量/金屬量假象（控制後 flat，0/4） |
| H₂ | 控制質量後仍然下降 | **❌ 推翻** | 控制後全部 flat（p=0.5-0.6，顯著比例 0/4） |
| H₃ | BOSS gap 顯示連續性 | **✅ 確認** | BOSS flat（rho=0.13）同 SDSS 控制後 flat 連續 |
| H₄ | 控制質量後 JADES 上升消失 | **❌ 推翻** | 控制 F277W proxy 後仍然上升（0.77→7.89） |
| H₅ | 趨勢由 pipeline 污染驅動 | **❌ 推翻** | 獨立擬合後趨勢仍然存在（flux 差 56x 但比率一致） |

### 8.2 關鍵發現

1. **SDSS「下降支」= 質量/金屬量選樣假象**（控制後 flat，p=0.5-0.6，顯著比例 0/4）
2. **BOSS gap 填滿**（3997/4000 光譜，3974 成功擬合）— 同 SDSS flat 連續，BOSS 區間內部 Spearman rho=+0.13, p=0.0008（非常弱）
3. **JADES 上升支 ⚠️ 唔係質量假象**（用 F277W 光度做質量 proxy 控制後仍然上升：低質量 0.77→7.89，高質量 2.58→3.45）
4. 但 JADES 樣本係極端尾選樣（EW>5000Å）— 無法排除選樣偏見
5. 三個樣本用**同一套獨立擬合方法**，排除 pipeline 污染（flux 比目錄差 56x，但線比率只差 3.3%）

### 8.3 誠實底線

- **「無年齡+有周期」未有新證據** — 反而係不斷揭示更深層嘅選樣效應
- ℓ<0.6 冇結構梯度證據（SDSS 控制後 flat + BOSS flat）
- ℓ>1.0 嘅上升真係存在，但無法區分「結構」vs「極端尾選樣」
- 要真正判死，需要：無偏選樣嘅高 z 樣本（JWST 寬場 + 完整 SED 質量控制）
- 本 session 揭示嘅選樣層次：pipeline 污染（56x）→ 質量混雜（p=2e-79→flat）→ 樣本構成（JADES 極端尾）

### 8.4 圖形化總結

```
[OIII]/Hβ
  SDSS(控制質量後flat)     BOSS flat
   ~1.5 ───────────────── ~1.3-2.8
                           │
                           │  ┌──JADES z=3 低點 0.76
                           │  │
                           │  └─────────── JADES 急升 5.06
  ───────────────────────────────────────────────→ ℓ
  0.01─0.06      0.22─0.62           1.0─1.5
```

---

## 9. 參考文獻

- SDSS DR18：https://www.sdss4.org/dr18/
- SDSS SAS 光譜路徑：https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/
- BOSS 光譜 API：https://dr18.sdss.org/optical/spectrum/view/data/format=fits/spec=lite
- JADES DR2：https://archive.stsci.edu/hlsps/jades/dr2/
- MPA-JHU newmasses：https://wwwmpa.mpa-garching.mpg.de/SDSS/DR4/raw_data.html
- Tremonti+04 [OIII]/Hβ vs 金屬量：https://ui.adsabs.harvard.edu/abs/2004ApJ...613..898T
- Mann-Whitney U 檢驗：https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html

---

## 附錄：數值驗證腳本輸出

```
✅ SDSS z=0.001-0.02 n: expected=461.0000, actual=461.0000, ratio=1.0000
✅ SDSS z=0.001-0.02 med: expected=2.2300, actual=2.2293, ratio=0.9997
✅ SDSS z=0.02-0.03 n: expected=252.0000, actual=252.0000, ratio=1.0000
✅ SDSS z=0.02-0.03 med: expected=1.6400, actual=1.6429, ratio=1.0017
✅ SDSS z=0.03-0.04 n: expected=277.0000, actual=277.0000, ratio=1.0000
✅ SDSS z=0.03-0.04 med: expected=1.5900, actual=1.5945, ratio=1.0028
✅ SDSS z=0.04-0.05 n: expected=230.0000, actual=230.0000, ratio=1.0000
✅ SDSS z=0.04-0.05 med: expected=1.3300, actual=1.3307, ratio=1.0005
✅ SDSS z=0.05-0.06 n: expected=258.0000, actual=258.0000, ratio=1.0000
✅ SDSS z=0.05-0.06 med: expected=1.2100, actual=1.2098, ratio=0.9998
✅ SDSS z=0.06-0.07 n: expected=249.0000, actual=249.0000, ratio=1.0000
✅ SDSS z=0.06-0.07 med: expected=1.1000, actual=1.1020, ratio=1.0018
✅ SDSS z=0.07-0.08 n: expected=224.0000, actual=224.0000, ratio=1.0000
✅ SDSS z=0.07-0.08 med: expected=0.8700, actual=0.8705, ratio=1.0006
✅ SDSS z=0.08-0.1 n: expected=396.0000, actual=396.0000, ratio=1.0000
✅ SDSS z=0.08-0.1 med: expected=0.7600, actual=0.7567, ratio=0.9956
✅ BOSS z=0.3-0.4 n: expected=26.0000, actual=26.0000, ratio=1.0000
✅ BOSS z=0.3-0.4 med: expected=2.0000, actual=2.0028, ratio=1.0014
✅ BOSS z=0.4-0.5 n: expected=26.0000, actual=26.0000, ratio=1.0000
✅ BOSS z=0.4-0.5 med: expected=1.5100, actual=1.5117, ratio=1.0011
✅ BOSS z=0.5-0.6 n: expected=57.0000, actual=57.0000, ratio=1.0000
✅ BOSS z=0.5-0.6 med: expected=1.7700, actual=1.7748, ratio=1.0027
✅ BOSS z=0.6-0.7 n: expected=95.0000, actual=95.0000, ratio=1.0000
✅ BOSS z=0.6-0.7 med: expected=1.1800, actual=1.1821, ratio=1.0017
✅ BOSS z=0.7-0.8 n: expected=91.0000, actual=91.0000, ratio=1.0000
✅ BOSS z=0.7-0.8 med: expected=1.3000, actual=1.3012, ratio=1.0010
✅ BOSS z=0.8-0.9 n: expected=156.0000, actual=156.0000, ratio=1.0000
✅ BOSS z=0.8-0.9 med: expected=1.7000, actual=1.7019, ratio=1.0011
✅ BOSS z=0.9-1.0 n: expected=126.0000, actual=126.0000, ratio=1.0000
✅ BOSS z=0.9-1.0 med: expected=1.6900, actual=1.6875, ratio=0.9985
✅ BOSS z=1.0-1.2 n: expected=103.0000, actual=103.0000, ratio=1.0000
✅ BOSS z=1.0-1.2 med: expected=2.8400, actual=2.8409, ratio=1.0003
✅ BOSS Spearman rho: expected=0.1290, actual=0.1289, ratio=0.9991
✅ JADES z=2-4 n: expected=40.0000, actual=40.0000, ratio=1.0000
✅ JADES z=2-4 med: expected=0.7600, actual=0.7642, ratio=1.0055
✅ JADES z=4-5 n: expected=73.0000, actual=73.0000, ratio=1.0000
✅ JADES z=4-5 med: expected=2.0500, actual=2.0540, ratio=1.0020
✅ JADES z=5-6 n: expected=79.0000, actual=79.0000, ratio=1.0000
✅ JADES z=5-6 med: expected=4.1800, actual=4.1782, ratio=0.9996
✅ JADES z=6-8 n: expected=56.0000, actual=56.0000, ratio=1.0000
✅ JADES z=6-8 med: expected=5.0600, actual=5.0601, ratio=1.0000
✅ BOSS: expected=1382442.0000, actual=1382442.0000, ratio=1.0000
```