# IDCM H(z) 與 BAO 推導記錄

## 狀態：OPEN PROBLEM — 未解決

## 問題

IDCM 需要一個 mechanism 去解釋 H(z) 觀測（DESI BAO），而呢個 mechanism 唔係「暗能量」。
目前結構上未有成功嘅推導。

## 已知結構事實

- ✅ K_Chain = 44-site fixed ring, R_H = 4129.94 Mpc
- ✅ 時間 = 操作維（遞迴 C_{n+1}=1/(1+C_n)）
- ✅ 紅移 = 相位落差（Phase Shift），唔係空間膨脹
- ✅ Rendering depth = 13.47 Gyr（因果視界）
- ✅ BAO = λ_sync/2 = 147.44 Mpc（K_Chain SYNC 諧波）
- ✅ Ω_Λ = 4/(φ⁴-1) = 0.683282（結構常數）
- ✅ Ω_m = 1 - Ω_Λ = 0.316718
- ✅ z<1.2 無演化（Flat）— 經質量控制後確認

## 嘗試過嘅方法

### 方法 A: 色散關係 → 未完成

### 方法 B: K_Tree 層次 H(z)
H(z) = H₀ × √(Ω_Λ + Ω_m(z))
其中 Ω_m(z) = Ω_m × (Σ_{n<N_d/(1+z)} γ_n)/(Σ γ_n)
**結果：** H(z) 隨 z 遞減（同觀測相反）→ DM/rd=74.95 vs DESI 39.32 (+108σ) ❌

### 方法 C: SYNC 相位累積
DM(z) = (R_H/π) × ln(1+z)
**結果：** DM/rd=10.73 vs DESI 39.32 (-86.6σ) ❌

### 方法 D: 指數拉伸
DM(z) = R_H × ((1+z)^(1/β)-1)
**結果：** β=3: DM/rd=13.82 vs DESI 39.32 (-77.3σ) ❌

### 方法 E: 操作步數積分
DM(z) = ∫ R_H/(1+z') dz' = R_H × ln(1+z)
**結果：** 同方法 C，❌

### 方法 F: K_Tree 投影卷積
D(z) = R_H/ln(4) × (3/2) × (1-(1+z)^(-2/3))
**結果：** DM/rd=16.72 vs DESI 39.32 (-68.5σ) ❌

### FLRW + IDCM 參數
H(z) = H₀ × √(Ω_m(1+z)³ + Ω_Λ)
**結果：** DM/rd=36.24 vs DESI 39.32 (-9.3σ) ❌（最近但仲差好遠）

### 方法 G: 冪律 γ=const
θ(z) = 2π/28 × (1+z)^(-γ)
γ=1.995 最佳擬合
**結果：** χ²/dof=253 ❌

### 方法 H: 色散修正
θ(z) = 2π/28 × (1+z)^(-1/v_g(z))
v_g(z) = cos(π×28/(88×(1+z)))
**結果：** χ²/dof=6815 ❌

### 方法 I: 積分色散
θ(z) = 2π/28 × exp(-∫₀ᶻ dz'/(1+z')/v_g(z'))
**結果：** χ²/dof=3072 ❌

## DESI BAO 數據

| z_eff | tracer | DM/rd | err | θ_BAO(°) |
|:-----:|:------:|:----:|:---:|:--------:|
| 0.295 | LRG | 7.97 | 0.14 | 7.19 |
| 0.510 | LRG | 12.99 | 0.19 | 4.41 |
| 0.706 | LRG | 17.62 | 0.33 | 3.25 |
| 0.930 | ELG_LRG | 22.97 | 0.49 | 2.49 |
| 1.317 | QSO | 30.62 | 1.04 | 1.87 |
| 1.491 | QSO | 34.72 | 1.30 | 1.65 |
| 2.330 | Lyα | 39.32 | 0.33 | 1.46 |

來源: DESI DR1 (arXiv:2404.03001) + DESI DR2 Lyα (arXiv:2404.03002)

## 關鍵發現

### 1. DESI 嘅 DM 係 ΛCDM 衍生幻覺
Gemini 指出：DESI 嘅 DM/rd 唔係直接量度，係假設 ΛCDM 膨脹後反推。IDCM 打呢個數係 category error。正確做法：直接預測原始 BAO 角度 θ_BAO(z) 或 correlation function ξ(s)。

### 2. 簡單投影模型全部 fail
所有由 K_Chain 結構推導出嘅投影模型（冪律、色散、能量）都唔 fit DESI 數據。
χ²/dof 由 253 到 6百萬，全部 fail。

### 3. 根本問題
- 1D K_Chain 44-site → 3D 天球投影嘅數學算子未知
- BAO 角度隨 z 嘅變化由咩機制決定？
- 點解 ΛCDM FLRW 做到 ~1% 精度？

## 下一步需要

1. 建立完整嘅「相位-視角映射矩陣」
2. 從 K_Chain 44-mode 色散直接預測原始 BAO correlation function ξ(s⊥, s∥)
3. 避免經 ΛCDM DM 做中間人
4. 需要 idcm-core 嘅完整 P(k) 模型

## 相關檔案

- `40_hz_derivation.py` — H(z) 推導 v1
- `40_hz_derivation_v2.py` — H(z) 推導 v2（Gemini insight）
- `41_bao_full_derivation.py` — BAO 角度預測 v1
- `41_bao_full_derivation_v2.py` — BAO 角度預測 v2（色散修正）
- `39_time_first_principles.md` — 時間第一原理推導（已完成）
- `39_time_first_principles.py` — 時間推導驗證腳本

## 狀態標籤

🟡 OPEN — 未解決，需要新 insight