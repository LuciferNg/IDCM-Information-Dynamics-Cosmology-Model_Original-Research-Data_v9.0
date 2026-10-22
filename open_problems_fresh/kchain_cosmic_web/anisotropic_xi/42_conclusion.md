# 42 — ξ(s⊥, s∥) 直接投影驗證結果

## 核心發現

### 1. IDCM BAO 位置喺 BOSS DR12 數據範圍之外 🚨

| 量 | 值 |
|:--|:----:|
| IDCM BAO (λ_sync/2) | 147.44 Mpc = **203.1 h⁻¹Mpc** |
| BOSS DR12 s_max | 177.5 h⁻¹Mpc |
| 差距 | **25.6 h⁻¹Mpc**（數據唔夠遠） |

**呢個係關鍵局限：** BOSS DR12 嘅最大尺度（177.5 h⁻¹Mpc）唔夠睇到 IDCM 嘅 BAO peak（203.1 h⁻¹Mpc）。
之前嘅 EMD 分析（17/19 harmonics）檢測到嘅係 n≥3 嘅高階諧波，n=2（BAO）根本喺數據範圍外。

### 2. 諧波系列 n=3..20 全部喺 BOSS 範圍內 ✅

全部 18 個諧波位置（n=3..20）都有 S/N >> 3 嘅檢測。
位置偏差：-0.67 ± 6.01 h⁻¹Mpc（~6% 精度，受 BOSS 嘅 2.5 h⁻¹Mpc binning 限制）。

### 3. ξ₂(s) 阻抗反射模型 — 相關 r ≈ -0.23

ξ₂/ξ₀ 比率嘅實測 vs 預測相關為負值（r ≈ -0.23），表示阻抗反射模型嘅方向性預測同數據不一致。

可能原因：
- 平滑 spline 嘅 broadband 分離唔夠好（BOSS 只有 36 個數據點）
- 阻抗模型需要更精細嘅處理（例如考慮 RSD 嘅非線性效應）
- 需要用 DESI 嘅更大範圍數據做驗證

### 4. 直接 2D ξ(σ, π) 預測已建構

從 44-mode 諧波疊加 + 阻抗反射 + SYNC 相位，建構咗零自由參數嘅 2D 理論模型。
檔案：`43_kchain_2d_xi.py`
結果：`43_kchain_2d_xi.json`

## 下一步

### 短期：DESI 數據
DESI DR2 嘅 BAO 測量去到 z=2.33，尺度範圍更大。
需要 DESI 嘅 ξ(s⊥, s∥) 或 multipole 數據。

### 中期：改善各向異性模型
阻抗反射模型嘅 ξ₂/ξ₀ 預測同數據方向相反。
需要重新審視 R_n 嘅符號約定同 LOS 投影嘅幾何。

### 長期：從原始星系目錄計算 ξ(s⊥, s∥)
唔用 post-reconstruction 數據，直接用 BOSS 或 DESI 嘅原始星系目錄
計算 2D 相關函數，完全避開 ΛCDM 嘅任何處理步驟。

## 檔案

- `42_anisotropic_xi_record.md` — 方法論記錄
- `42_anisotropic_xi.py` — v1: 全模型 χ²（失敗，broadband 主導）
- `42_anisotropic_xi_v2.py` — v2: EMD 諧波分離（EMD 有 bug，36 點太少）
- `42_anisotropic_xi_v3.py` — v3: 平滑 spline 諧波分離（成功運行）
- `43_kchain_2d_xi.py` — 2D ξ(σ, π) 理論預測建構
- `42_results_v3.json` — v3 結果
- `43_kchain_2d_xi.json` — 2D 預測結果