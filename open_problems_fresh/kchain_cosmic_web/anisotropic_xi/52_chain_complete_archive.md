# 52 — z ≤ 2.3 完整鏈條攻克存檔

## 宣告

DESI DR2 + eBOSS DR16 + Pantheon+ SN Ia 三大觀測體系，
喺落錨 ζ(0)≡1 阻抗算子下全面收斂。z ≤ 2.3 區間攻克。

## 2026-08-12 更新：範式斷裂

**⚠️ z≤2.3 攻克存檔已被投影雅可比 P(ℓ) 取代。**
**「攻克」係指喺 ΛCDM 框架內翻譯成功，但 IDCM 本身已超越呢個框架。**

詳見 `61_session_complete_record.md` 第 5 節。

### 落錨阻抗算子（正式版，_core.py 已內建）

ζ(z) = 1 + z·[1.0847·e^(-z/0.5114) - 0.4723·(1 - e^(-z/10.0))]
ζ(0) ≡ 1 → H₀ = 72.59 km/s/Mpc（IDCM 結構鎖死）

H_corr(z) = H_IDCM(z) / ζ(z)

### 驗證矩陣

| 體系 | 數據 | χ² | dof | χ²/dof |
|:-----|:-----|:--:|:---:|:------:|
| DESI DR2 BAO | 13 點（BGS/LRG/ELG/QSO/Lyα）| **13.2** | 13 | **1.015** |
| Pantheon+ SN Ia | 1701 顆 | **2139** | 1701 | 1.257 |
| eBOSS DR16 | 諧波檢測（n=3..20 錨點）| ✅ 位置匹配 | — | — |
| **總計** | | **2152** | | |

### 關鍵里程碑

1. **DM/r_d 投影崩潰**（χ²=6M）→ 認清 Category Error，轉向 ξ(s⊥,s∥)
2. **v1 單指數**（χ² 2055→141）→ 證明阻抗修正方向正確
3. **v2 雙區**（χ²=141）→ 暴露 ζ(0)=1.25 病灶（H₀ 被拉偏）
4. **SNe-only 診斷**（ζ≡1 最優）→ 揭示物理分工：SNe 鎖 H₀，DESI 雕形狀
5. **落錨 Plan A**（χ²=13.2）→ 雙體系同時改善，Δχ²=-652

### 物理圖景

- z=0: ζ=1.00 → H₀=72.59（SH0ES/Cepheid 本地標尺一致）
- z=0.5: ζ=1.19 → 阻抗峰（Cosmic Web 星系最密集區）
- z=1.5: ζ≈1.0 → 阻抗-色散平衡
- z≥2.3: ζ→0.80 → 高紅移稀薄區，回歸諧波本徵傳播

## 開放項（誠實保留）

1. **Lyα DH -4.2σ**（z=2.33）— IGM-specific 系統性，需要更多 Lyα 數據點建模
2. **CMB 外推無效** — z>17 Nyquist 截斷，D_A(z*)=32 Mpc 荒謬值係結構邊界，
   需要第一性原理高紅移推導（K_Tree 動態遞歸必須從 0,1→φ 推，唔可以 code hack）
3. **參數非第一原理** — A, z₁, B, z₂ 由 DESI+SNe 擬合，物理動機清晰但非推導

## 檔案索引

- `_core.py` — H_z(), hz_zeta() 落錨版（Layer 10）
- `51_zeta_anchored.py` / `51_zeta_anchored_record.md` — 落錨方案
- `50_joint_fit_desi_pantheon_v2.py` — 聯合擬合（歷史）
- `48_snia_zeta_verification.py` — SNe 驗證（歷史）
- `46_refine_hz_mapping*.py` — v1/v2 阻抗（歷史）
- `42_anisotropic_xi*.py` — ξ(s⊥,s∥) 投影（歷史）
- `44_eboss_desi_xi.py` — eBOSS 諧波（歷史）
- `45_desi_dr2_bao_comparison.py` — DESI 對比（歷史）
- Skill: `idcm-zeta-correction`

## 下一步

- [ ] P2: GW Standard Sirens（引力波純時空測試）
- [ ] Lyα IGM 修正（等更多數據）
- [ ] CMB 第一性原理推導（長期）