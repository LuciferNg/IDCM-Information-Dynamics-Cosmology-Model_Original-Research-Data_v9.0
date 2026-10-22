# W-field 晶格膨脹 H(z) 推導嘗試

**日期：** 2026-08-10
**腳本：** `idcm_wfield_expansion.py`
**狀態：** ❌ 失敗
**文件：** `references/wfield-lattice-expansion-hz.md`

## 1. 目標

由 K_Chain 模式佔據隨 redshift 演化推導 H(z)，唔用 FLRW 嘅 Friedmann equation。

## 2. 方法

### 2.1 假設

1. K_Chain 有 44 個模式，每個模式有能量 γ_n = 4 sin²(πn/88)
2. 喺唔同 redshift，active 嘅模式數目唔同
3. 高 z（早期）更多模式 active
4. 總物質密度 = Σ active 模式嘅 γ_n
5. 暗能量密度 = constant（W-field tension）

### 2.2 推導

```
n_active = N_d / B^ℓ, ℓ = log_B(z+1)
matter_ratio = Σ_{n=1}^{n_active} γ_n / (N_d/2)
E²(z) = Ω_L + Ω_m · matter_ratio
```

### 2.3 數值

| z | ℓ | n_active | matter_ratio | H(z) |
|:-:|:-:|:--------:|:----------:|:----:|
| 0.00 | 0.00 | 44 | 1.955 | 102.1 |
| 0.50 | 0.58 | 26 | 1.130 | 79.1 |
| 1.00 | 1.00 | 11 | 0.383 | 69.9 |
| 2.33 | 1.48 | 6 | 0.146 | 62.5 |
| 5.00 | 1.93 | 4 | 0.071 | 60.5 |
| 10.00 | 2.32 | 4 | 0.071 | 60.1 |
| 15.00 | 2.50 | 4 | 0.071 | 60.0 |
| 17.00 | 2.54 | 4 | 0.071 | 60.0 |

## 3. 結果

**H(z) 隨 z 遞減（102 → 60 km/s/Mpc），違反觀測 ❌**

```
DM/rd = 67.16 vs DESI 39.32 → +84.4σ ❌
```

## 4. 失敗原因

### 4.1 方向錯

高 z 應該更多模式 active → 更大物質密度 → 更快膨脹 → H(z) 更大。但我嘅模型顯示 H(z) 遞減。

### 4.2 根本問題

模式數目同膨脹速率嘅關係唔係咁直接。Active 模式多唔代表 H(z) 大 — 能量密度嘅 scaling 先係關鍵。

### 4.3 正確嘅 scaling

FLRW 用 ρ_m ∝ (1+z)³，呢個 scaling 來自 adiabatic expansion。IDCM 嘅模式佔據可能都有類似嘅 scaling，但係由唔同機制產生。

## 5. 教訓

| 學到嘅嘢 | 影響 |
|:---------|:------|
| 模式數目 → H(z) 嘅關係唔 trivial | 需要用場論方法 |
| ρ_m ∝ (1+z)³ 係 robust | 唔係 FLRW 獨有 |
| 需要真正嘅膨脹模型 | 唔係 counting modes |

## 6. 腳本

`/home/wsl/IDCM/sync_bump_analysis/idcm_wfield_expansion.py` (277 行)

## 7. 參考

- `idcm_core.py` — W-field lattice action
- `references/idcm-cosmology-closed-loop-derivation.md` — Layer 9.3