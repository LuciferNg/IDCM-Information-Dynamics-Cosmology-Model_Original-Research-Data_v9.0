# W-field Propagation D(z) 推導嘗試

**日期：** 2026-08-10
**腳本：** `idcm_distance_redshift.py`
**狀態：** ❌ 失敗
**文件：** `references/wfield-propagation-distance-redshift.md`

## 1. 目標

由 W-field 喺 K_Chain 上嘅 propagation 推導 distance-redshift relation D(z)，唔用 FLRW。

## 2. 方法

### 2.1 假設

1. W-field 係 K_Chain 上嘅離散場
2. SYNC coupling 產生能量損失
3. Redshift = W-field excitation 嘅能量損失
4. 距離 = propagation steps × site spacing

### 2.2 推導

W-field 嘅色散關係：
```
ω² = 4 sin²(k/2), k = 2πn/88
E_n = ω_n = 2|sin(πn/88)|
```

SYNC coupling：
```
g_sync = 2·|W₀|²·(1-cos(2π/88)) = 0.006299
phase_step = 2π/88 = 0.071400
energy_loss_per_step = g_sync·(1-cos(2π/88)) = 1.605×10⁻⁵
```

Redshift 係累積能量損失：
```
z = N · loss / E_initial
N = z · E_initial / loss
```

距離：
```
D(z) = N · (R_H/88) = z · E_n · R_H / (88 · g_sync · (1-cos(2π/88)))
```

### 2.3 數值

For SYNC mode (n=2):
```
E₂ = 2|sin(π/44)| = 0.142678
D(z) = z · 0.142678 · 4129.94 / (88 · 0.006299 · 0.002549)
     = z · 417241 Mpc
```

## 3. 結果

| z | D(z) (IDCM) | D(z) (Hubble law) | 差異 |
|:-:|:-----------:|:-----------------:|:----:|
| 0.5 | 208,621 Mpc | 2,065 Mpc | 101x |
| 1.0 | 417,241 Mpc | 4,130 Mpc | 101x |
| 2.33 | 972,172 Mpc | 9,623 Mpc | 101x |

**DM/rd = 6593.7 vs DESI 39.32 → +19862σ ❌**

## 4. 失敗原因

### 4.1 能量損失太弱

```
g_sync = 0.006299
loss_per_step = 1.605×10⁻⁵
E₂ = 0.142678
steps_to_lose_all_energy = 0.142678/1.605×10⁻⁵ = 8890
distance = 8890 × 4129.94/88 = 417241 Mpc
```

需要 8890 步先 loss 晒所有能量，即係 417k Mpc，比 Hubble radius 大 100 倍。

### 4.2 概念錯誤

**Redshift 可能唔係 energy loss。** 調律者修正：
> 「紅移只是共震的波長被空間膨脹拉長了」

所以 redshift 係空間膨脹拉長波長，唔係 W-field 能量損失。

## 5. 教訓

| 學到嘅嘢 | 影響 |
|:---------|:------|
| Redshift 唔係 energy loss | 重新理解 redshift 本質 |
| SYNC coupling 太弱 | 能量損失機制唔 work |
| 需要空間膨脹模型 | 唔係 propagation 模型 |

## 6. 腳本

`/home/wsl/IDCM/sync_bump_analysis/idcm_distance_redshift.py` (164 行)

## 7. 參考

- `idcm_core.py` — W-field lattice action
- `references/idcm-cosmology-closed-loop-derivation.md` — Layer 9.2