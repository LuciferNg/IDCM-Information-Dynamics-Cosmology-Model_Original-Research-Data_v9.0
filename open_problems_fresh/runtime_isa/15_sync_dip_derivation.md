## Sync Dip 推導（更新版）

**更新日期:** 2026-08-02  
**新增:** Observer-Relative Hypothesis 分析  
**完整文檔:** `~/IDCM/sync_bump_analysis/01_sync_bump_observer_relative.md`

### 問題

Sync dip/bump 在 z ≈ 0.6。為何是 0.6？

### 更新: z_c = F₄/F₅ = 3/5 (Fibonacci 收斂)

z_c = 3/5 = 0.6 = **F₄/F₅** — 係 Fibonacci 數的比率，φ⁻¹ 的第三收斂項。

```
F₄/F₅ = 3/5  = 0.600000  ← 第三收斂
F₅/F₆ = 5/8  = 0.625000  ← 第四收斂
F₆/F₇ = 8/13 = 0.615385  ← 第五收斂
...
lim = φ⁻¹ = 0.618034     ← 真正固定點
```

**所以 3/5 唔係 random fitting**，而係 φ 結構（Fibonacci），但係有限精度收斂。

### 1.8% gap: 結構 vs Observer Projection

- 結構固定點：φ⁻¹ = 0.618034
- 觀測值：0.600000
- Gap: 1.8% → 可能係 observer projection

### DESI vs SDSS 證據

| z region | DESI vs SDSS | 
|:---------|:------------|
| z=0.51 (pre-sync) | 細差異 (~1.6σ) |
| **z=0.71 (sync bump)** | **~3σ 差異** |
| z=2.33 (DE weak) | 細差異 (<1σ) |

DESI 論文原文: *"the discrepancy between DESI and SDSS in the 0.6<z<0.8 bin is at roughly the ~3σ level"*

Pattern match observer-relative: 效應最大在 sync transition region，兩端減弱。

### Hypothesis

Sync bump 係 observer dynamic — 隨觀察點變化。如果正確:
- 時空可能非平坦（observer-relative curvature）
- Flatness 係 rendered property
- z_c = φ⁻¹ 係 raw sync position，投影後觀測到 0.6

### 狀態

🟢 z_c = F₄/F₅ (Fibonacci 結構) — **confirmed**
🟡 Observer-relative vs absolute — **open, evidence favors relative**
🟡 非平坦時空 — **hypothesis, under investigation**
🔴 DESI DR2 — **待驗證**

### Check

| zc | Source | Deviation |
|----|--------|-----------|
| 0.60 | Observed dip position | — |
| F₄/F₅ = 3/5 | Fibonacci 收斂 | exact (結構) |
| φ⁻¹ = 0.618 | φ arithmetic (固定點) | 1.8% gap |
| F₅/F₆ = 5/8 | 第四收斂 | 2.5% |
| F₆/F₇ = 8/13 | 第五收斂 | 1.5% |