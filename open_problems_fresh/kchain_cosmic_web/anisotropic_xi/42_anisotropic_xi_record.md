# IDCM ξ(s⊥, s∥) 各向異性相關函數 — 直接投影驗證

## 背景

### 問題源起
之前用 K_Chain 投影模型對比 ΛCDM 嘅 DM/r_d（comoving distance / sound horizon），χ² 從 253 飆升到 6 百萬。原因：

- **DM/r_d 係 ΛCDM 嘅衍生量** — 經 ∫ dz/H(z) 積分建構，內含連續膨脹空間假設
- K_Chain 係離散 44-site 1D ring，相位結構完全不同
- 任何簡單解析函數（∫ dz/v_g、指數拉伸）都無法橋接呢兩個度量空間

### 解決方案：直接去原始配置空間 ξ(s⊥, s∥)

ξ(s⊥, s∥) 係 redshift-space 嘅星系點分佈直接算出嚟嘅統計量，未經 ΛCDM 距離積分汙染。K_Chain 嘅 44-mode 諧波必須直接喺呢個空間留下腳印。

---

## 方法論

### K_Chain 2D 相關函數理論模型

從 44-mode 駐波疊加建構 ξ(σ, π)：

1. **諧波系列**（monopole ξ₀）：
   - λ_sync/n, n=2..20
   - 每個諧波有振幅 A_n ∝ γ_n/L_n（γ_n = 4 sin²(πn/88)，L_n = Lucas 數）
   - BAO = λ_sync/2 = 147.44 Mpc = n=2 最強干涉條紋

2. **阻抗/反射模型**（quadrupole ξ₂）：
   - 阻抗 Z_n = γ_n / |v_g(n)|，v_g(n) = cos(πn/88)
   - 反射 R_n = (Z_n - Z_{n-1}) / (Z_n + Z_{n-1})
   - 反射率各向異性 → 視線方向 vs 橫向嘅不對稱
   - 理論 ξ₂(s) ∝ Σ R_n · A_n · cos(2πs/λ_n)

3. **SYNC 相位調製**：
   - θ_n = n × 2π/88
   - 沿視線方向（π/σ 方向）投影

### 數據

- **BOSS DR12** (Ross+2016): post-recon monopole + quadrupole + covariance
  - 3 個紅移 bin: z1≈0.38, z2≈0.51, z3≈0.61
  - 尺度範圍: 2.5-197.5 h⁻¹ Mpc (39 bins)
  - 5 個 bincent 偏移版本 (bincent 0..4)

### 驗證方法

1. 直接 χ² 檢驗：ξ₀(s) 同 ξ₂(s) 一齊 fit
2. Covariance matrix 處理 monopole-quadrupole 交叉項
3. 零自由參數（所有 K_Chain 參數從 x²+x-1=0 導出）

---

## 預期結果

如果 K_Chain 正確：
- ξ₀(s) 應顯示 λ_sync/n 諧波系列
- ξ₂(s) 應顯示阻抗反射嘅各向異性特徵
- 特徵尺度：λ_sync/2=147.44 Mpc, λ_sync/3=98.29 Mpc, λ_sync/4=73.72 Mpc

如果 K_Chain 錯誤：
- 諧波系列不存在 → ξ₀(s) 只顯示單一 BAO peak
- 各向異性模式不匹配 → ξ₂(s) 擬合失敗