# IDCM v9.0 — W-Field-Lattice

**Information Dynamics Cosmology Model（資訊動力學宇宙論模型）— 9th Generation**

> `W-Field-Lattice` 係版本代號：W-field 唔再係連續時空上的連續場，而係定義在 `K_chain ⊗ K_tree` 離散晶格上的 site weight。
>
> v9.0 的職責係**落地**：v8.0 抽到指令集，但指令冇執行的地方。本版補上硬件 —— 1496 個晶格點、四項 action、一條色散關係；常數由「公式的係數」變成「晶格的能帶結構」。

## 緣起

v8.0 用反向編譯證明 45 條公式可以由 5-core ISA 生成，`Forest = 1`、`Confidence = 1.00`。呢個結果回答咗「公式用幾多步算」，但冇回答「喺邊度算」。

三個缺口在 v8.0 全部以「假設」形式存在：

- opcode 冇空間：`LOAD` / `STORE` / `POW` 唔知自己喺邊個點執行，所以冇維度、冇傳播、冇光速
- 冇動力學：boot 一次過算出常數，但冇場方程、冇色散關係、冇傳播子
- 費米子量子化（P20–P25）用連續 QFT 極限做，晶格只被引用為「來源」，從未被寫成 action

結果係：`c`、光、重力、粒子全部係**被假設**的，唔係被導出的。一句話可以概括 v8.0 的邊界：**知道指令，唔知道機器。**

v9.0 因此做三件事：

1. **建機器**：把 W-field 放上 `K_chain ⊗ K_tree`（44 × 34 = 1496 點），寫完整 action
2. **導色散**：由 action 解出 `ω² = γ_k μ_m`，令常數變成能帶結構而非係數
3. **驗集體模**：光 = `k=1` 模、規範 = 零模、Higgs = 徑向模、PG = 相位模、重力 = 配分函數的二次變分

驗收標準：一個物理對象只有在「晶格上是邊個模」講得清時，先算導出。

## 版本演進：v8.0 → v9.0

IDCM 係**逆向工程**：由已觀測的常數與結構反推生成機制。版本分野唔係假設改變，而係**逆推對象的層級改變** —— v8.0 逆推到「指令」，v9.0 逆推到「晶格」。

### 前版：v8.0 — Compiled-Cosmology

- 本體：反向編譯六段流水線（token → role → grammar → dialect → IR → ISA），24 Clean Corpus 全部 `Forest = 1`
- 指令：5-core（LOAD/STORE/POW/DIV/SQRT），`2+1=3`；執行層 11 opcode，`SYNC = 2`、`JMP = 7` ticks
- 缺口：P20–P26 費米子量子化用連續 QFT 極限（`(i∂̸−m)ψ=0`、`Y_ij = κ∫ψ_iψ_jφ_H`）完成，晶格未入 action
- 成果：P1–P26 逐題結案，玻色子質量 `m_W = 80.383`、`m_H = 125.028 GeV`

### 根因：語法身份唔等於物理身份

| 問題 | v8.0 的處理 | 後果 |
|---|---|---|
| 傳播子由邊嚟 | 由離散方程 Fourier 變換「得到」`G(p) = i/(p²−M_n²)` | 有傳播子，但冇色散關係支撐 |
| 光速由邊嚟 | 未處理 | `c` 係輸入，唔係輸出 |
| 規範對稱由邊嚟 | 由 CY₃ Hodge 分解 `8+3+1+24 = 36` 指定 | 對稱群被指派，唔係由作用量湧現 |
| 費米子自由度 | 連續 Dirac 方程 | 冇 lattice doubling 問題，因為根本冇晶格 |
| 重力 | `f(W)R` 耦合，外部假設 | 幾何係外加的 |

一句話：**v8.0 證明「公式可執行」，未證明「宇宙有 substrate」。**

### 本版：v9.0 六件事

1. **晶格定義** — `Chain_44 ⊗ Tree_33`，88 個循環位置（44 對偶）、B = 4 分支、`L = 53/8` 層，共 1496 點
2. **作用量** — `S = S_kin(chain) + S_tree + S_pot + S_sync`，四項全寫出，無非局部項
3. **色散** — `ω² = γ_k μ_m`，`γ_n = 4 sin²(πn/88)`、`μ_m = φ^(L−m)`；`k=1` 模群速度 0.9996 ⟹ 光
4. **對稱性** — `γ₀ = 0` 零模 ⟹ 常數平移不變 ⟹ U(1)；再由 `B = 4` 分支與 CY₃ 得 SU(2)×SU(3)（57/57）
5. **費米子** — 晶格 Dirac 算符，`Z₂` grading 令 88 點中只有一半帶物理 chiral mode，避開 Nielsen-Ninomiya doubling（35/35）
6. **重力** — Einstein 張量 = 晶格配分函數的二次變分；`Λ = 4/(φ⁴−1)` 為熱耗散成本（20/20）

## 研究路線

七層，每層輸出係下一層的輸入：

**L1 晶格定義層** — `K_chain ⊗ K_tree`

- Chain：88 位置循環，離散 Laplacian `(ΔW)_n = 2W_n − W_{n−1} − W_{n+1}`，`γ_n = 4 sin²(πn/88)`
- Tree：MERA 深度 `L = 53/8`，分支 `B = 4`，`μ_m = φ^(L−m)`，跨越 8 個數量級（`φ^6.625 = 24.24` → `φ^−26.375 = 3.08×10⁻⁶`）
- 總節點：`N_d × (M+1) = 44 × 34 = 1496`

**L2 作用量層** — 四項，無非局部項

- `S_kin = Σ_n [2W_n² − W_n W_{n+1} − W_n W_{n−1}]`
- `S_tree = Σ_{n,ℓ} B^{−ℓ} (W_{n,ℓ} − U·W_{n,ℓ−1})²`，`U = 1/√(φ²+1) · [φ, 1; 1, −φ]`
- `S_pot = Σ_n [−ε abs(W_n)² + κ abs(W_n)⁴]`，`ε = φ⁻¹/4`、`κ = 1/16`
- `S_sync = Σ g_sync · cos(θ_n − θ_{n−1} − 2π/88)`

**L3 色散與集體模層** — 邊個模係邊個物理對象

- `ω_k = 2 sin(πk/88)`：`k=1` 得 `ω = 0.0714`、`v_g = 0.9996`；`k=44` 得 `ω = 2.0`、`v_g = 0`（Nyquist 駐波）
- 光 = 第一個非零傳播模（`k=1`），唔係最大群速度（`k→0` 時 diverges）
- 零模 `γ₀ = 0` ⟹ U(1) 規範；`W_n → W_n + const` 為其平移
- 徑向漲落 = Higgs、相位漲落 = pseudo-Goldstone；`ω² = ½γ_k + ½μ_m + 2ε`

**L4 規範與費米子層** — 對稱性與 doubler

- SU(2)×SU(3)：`B = 4` 分支 + `8+3+1+24 = 36 = h¹¹`；Wilson plaquette `Σ tr(1 − U_plaq)`（57/57）
- 晶格 Dirac：`D = γ^μ(∇_μ + A_μ) + m + (½)Δ_chain`；Wilson 項由 K_chain Laplacian 自然出現
- `Z₂` grading `d = {3,2,0}`：88 點中一半帶物理 mode ⟹ 無 doubler（35/35）

**L5 重力與宇宙學層** — 幾何由配分函數湧現

- `g_μν` = 粗粒化 W-field 關聯函數；Ricci = 配分函數二次變分；`S_EH = (1/16πG)∫R`
- `c_4D = (φ/2)(4/134)(67/φ) = 1`（原 `×44` 版 6% 偏差由繞數 `67/φ` 閉合）
- `Λ = 4/(φ⁴−1) = 0.683`；`T_CMB = 2.728 K`（0.06%）；`r = 12/55² ≈ 0.004`
- 同步轉變 `z_c = F₄/F₅ = 3/5`；渲染深度與 `z₁₇` Nyquist 極限

**L6 觀測層** — 譜線與相關函數

- 語料：SDSS 1000 + 5000、BOSS 4000、JADES 463（高 z）+ 688（gap），合計 8151 條譜、6796 條成功擬合，`z = 0.001–9.7`
- 量：`[OIII]/Hβ` 與 `Hα/[OIII]` 兩個污染抗性比率；質量、金屬量雙重控制
- 大尺度：`ξ(s)`、`ξ(σ,π)` 多極、`BAO = λ_sync/2 = 147.44 Mpc`、`H(z) = H₀(1+z)^{α(z)}`

**L7 缺口層** — `open_problems_fresh/`

- 18 個目錄，主題 slug 命名（無 O 號）；3 個空目錄（`impedance_coupling`、`ktree_projection`、`nonlinear_collapse`）
- 費曼規則、δ_CP、膠子散射、散射振幅已新鮮推導；runtime ISA、P(k)、σ₈、小波與疊加仍開放

## 項目結構

```
IDCM-v9.0--W-Field-Lattice/
├── README.md                            # 本檔
├── wfield_lattice/                      # 晶格本體：推導與驗證成對（NN_ 編號 01–19）
│   ├── 01_lattice_derivation.md          # 晶格定義、四項 action、場方程、四項推論（266 行）
│   ├── 02_lattice_verify.py              # 晶格譜與守恆量驗證
│   ├── 03_extended_derivation.md         # 光速、零模 → U(1)、複合色散（226 行）
│   ├── 04_extended_verify.py             # 延伸推導驗證（26/26）
│   ├── structural_forcing.md / .py       # 結構強迫：24.5% → 1.3% → 0.06%
│   ├── cy3_topological_operator.md       # CY₃ 拓撲算子：D_quark 一對多收斂（303 行）
│   ├── verify_cy3_operator.py
│   ├── expansion_plan.md                 # Phase 1–4 擴展計劃（依賴圖 + 驗證目標）
│   ├── universe_boot.py / universe_boot_b.py   # boot sequence 執行器
│   ├── universe_boot_b_derivation.md     # T_sync、T_c、VEV、m_H、T_CMB 逐項
│   ├── verify_boot_b.py
│   ├── full_closure_test.py              # 全域閉合測試
│   ├── gen1_structural.py                # 第一代費米子結構式
│   ├── winding/05_chain_winding_closure.md + 06_verify  # 繞數閉合 c 的 6% 偏差
│   ├── mass_gap/07_higgs_kinetic_closure.md + 08_verify  # Higgs 11% gap → φ/2（20/20）
│   ├── su2_su3/09_gauge_derivation.md + 10_verify        # SU(2)×SU(3)（57/57）
│   ├── fermion/11_dirac_lattice_derivation.md + 12_verify # 晶格 Dirac，免 doubler（35/35）
│   ├── lagrangian/13_full_sm_lattice.md + 14_verify       # 完整 SM lattice Lagrangian（20/20）
│   ├── gravity/15_gravity_emergent.md + 16_verify         # Einstein 張量從配分函數（20/20）
│   ├── isa_lattice/18_isa_lattice_mapping.md + 19_verify  # ISA ↔ 晶格對映（313/313）
│   └── paper/17_paper.md                 # 十節完整 paper
├── open_problems_fresh/                 # 18 個目錄（主題 slug，無 O 號）
│   ├── _core.py                          # 共用核心：晶格譜、常數、資料載入
│   ├── p_fr_feynman_rules/               # 費曼規則：傳播子 + 頂點 + 么正性
│   ├── p_nu_delta_cp/                    # δ_CP 與混合角分辨
│   ├── p_qcd_gluon_scattering/           # SU(3) 膠子散射、α_s running
│   ├── p_sa_scattering_amplitudes/       # 散射振幅與 1-loop β
│   ├── runtime_isa/（15 份）              # boot vs runtime、意識、生成函數、同步凹陷
│   ├── kchain_cosmic_web/（46 份）        # 宇宙網、V 形驗證、宇宙命運、暗物質推導
│   ├── anisotropic_xi/                   # ξ(σ,π) 多極分解
│   ├── sigma8_norm/                      # σ₈ 歸一化
│   ├── sigma_sync/                       # σ_sync 諧波尺度變異數算子
│   ├── sync_transition/                  # mode-by-mode 活化模型
│   ├── wavelet_toolbox/（9 支 + emd_engine.py）  # EMD／小波／horizon aliasing
│   ├── stacking_toolbox/                 # 疊加波形（單檔 239 行）
│   ├── redshift_evolution/               # 諧波振幅 vs z（單檔 180 行）
│   ├── pk_chain_spectrum/                # 由 γ_n 導 P(k)
│   ├── impedance_coupling/               # 空目錄（未開推）
│   ├── ktree_projection/                 # 空目錄
│   └── nonlinear_collapse/               # 空目錄
├── data/                                 # 觀測語料（不入 git 的大檔）
│   ├── boss_spec/（3997 個 FITS）          # BOSS DR12 星系譜
│   ├── sdss_spec/（1000）、sdss_spec_large/（5000）
│   ├── jades_spec/（463）、jades_gap_spec/（688）
│   ├── planck/、desi_dr2/、catalogs/       # 外部資料集與樣本清單
├── sync_bump_analysis/                   # 同步 bump/dip 獨立子庫（z_c、rendering boundary、Bagpipes 擬合）
├── paper/
│   ├── self_stress_test.md               # 六項自我壓力測試（373 行）
│   └── verify_stress_test.py             # 逐章驗證腳本
├── articles/宇宙Q&A_用常識解釋宇宙的設計.md  # 科普文章
├── 頂層分析腳本（59 支）                   # 下載、譜擬合、控制變數、V 形驗證、渲染深度
├── 擬合結果 JSON                          # sdss 998 / boss 3974 / sdss_large 3173 / jades 688 + 463
└── venv_sed                              # SED 擬合虛擬環境（不計入源碼統計）
```

## 狀態快照

```
晶格：K_chain(88) ⊗ K_tree(33 層, B=4) = 44 × 34 = 1496 點
晶格驗證：gauge 57/57 ｜ Dirac 35/35 ｜ Higgs 20/20 ｜ 重力 20/20
          lattice Lagrangian 20/20 ｜ ISA 對映 313/313 ｜ 延伸推導 26/26

open_problems_fresh：18 個目錄（3 個空目錄未開推）
  全部閉合 6 ｜ 部分閉合 5 ｜ 開放 3

觀測語料：下載 8151 條譜，成功擬合 6796 條（z = 0.001–9.7，ℓ = 0.001–1.73）
文檔：104 份 .md；腳本：244 支 .py（不計 venv_sed）
壓力測試：六項全 PASS（paper/self_stress_test.md），但同文明列 QFT 結構缺失清單
```

> `open_problems_fresh/` 用主題 slug 命名，唔用 O 號；本 README 的 O122–O135 係跨版本 register 對應到同一批主題的編號，用於追溯，唔代表 v9.0 當時有此編號。

## 已閉合關鍵結果（選錄）

- **晶格作用量（2026-07-31，`wfield_lattice/01_lattice_derivation.md`）**：`S = S_kin + S_tree + S_pot + S_sync`，四項全寫出且無非局部項；44 × 34 = 1496 點；`γ_n = 4 sin²(πn/88)`、`μ_m = φ^(L−m)`
- **光 = `k=1` 模（`03_extended_derivation.md` §A.5）**：`ω_k = 2 sin(πk/88)`；`k=1` 得 `v_g = 0.9996`、`k=44` 得 `v_g = 0`；光速係第一個非零傳播模，唔係 `k→0` 極限
- **光速閉合（`winding/05_chain_winding_closure.md`）**：`c = (φ/2)(4/134) × 44 = 1.0626`（+6% 偏差）；改用繞數 `67/φ = 134/(2φ)` 得 `c = 1`，偏差由 dual-pair 共享自由度的 1/2 因子吸收
- **零模 → U(1)（`03_extended_derivation.md` §B）**：`γ₀ = 0` ⟹ `W_n → W_n + const` 不變 ⟹ 規範對稱；`S_gauge = Σ(1 − cos A_n)`，小 A 極限 → `A²/2`，光子零質量（B2–B6 全過）
- **Higgs 11% gap 閉合（`mass_gap/07_higgs_kinetic_closure.md`，20/20）**：`m_H² = 2ε V_EW² × (φ/2) = V_EW²/4 = 4κ V_EW²`；`φ/2` 為 MERA isometry 的結構 eigenvalue，非拟合
- **完整晶格 Lagrangian（`lagrangian/13_full_sm_lattice.md`，20/20）**：五扇區齊備 —— Wilson plaquette 規範（57/57）、晶格 Dirac（35/35）、Higgs 動能（20/20）、重力（20/20）、Yukawa `y_f = φ^(−k_f)`
- **T_CMB（`cy3_topological_operator.md`、`structural_forcing.md`）**：`T_CMB = 2 × T_Pl × e⁻⁷⁴ × 134/100 × (1 − φ⁻⁹) = 2.728 K`，與 PDG 2.73 K 差 0.06%；兩級修正 24.5% → 1.3% → 0.06%
- **觀測負結果（`kchain_cosmic_web/38_vshape_verification.md`，2026-08-12）**：`[OIII]/Hβ` 的「V 形」下降支經質量／金屬量雙重控制後全部 flat（顯著比例 0/4，`p = 0.5–0.6`）⟹ 下降支判為選樣假象；`ℓ < 0.6` 無結構梯度證據

## 驗證紀律

v9.0 的嚴謹性分六層：晶格入場券 → 連續極限 → 樣本外控制 → 數字紀律 → 記錄紀律 → 路徑紀律。任一層不過，結果只停留「模的類比」。

### 一、入場券：晶格四問

| 問題 | 要求 | 失敗處置 |
|---|---|---|
| 晶格定義 | 點數、連通性、邊界條件寫死 | 缺失 ⟹ 不准稱晶格推導 |
| 作用量完整 | 動能、尺度、勢能、同步四項齊 | 缺項 ⟹ 標「唯象」 |
| 色散可導 | `ω²` 必須由 action 解出，唔可以外借 | 直接寫結果 ⟹ 標「假設」 |
| 模有物理對應 | 每個集體模要講明對應邊個觀測對象 | 講唔出 ⟹ 退回 L3 |

### 二、連續極限紀律

- 連續極限誤差要報階：`O(1/N_d²)`（本版 `N_d = 44` 有限 ⟹ 嚴格講無連續極限，晶格即現實）
- 唔准用「連續極限下成立」代替有限 `N` 的計算；`N_d = 44` 的譜就係最終譜
- 與連續 QFT 對照時，要同時報兩邊的定義域（`κ` 混淆、GeV 標度、場縮放三項為已知陷阱）

### 三、樣本外與控制變數（觀測層）

- 任何趨勢先過三重控制：質量、金屬量、樣本構成
- 控制後仍顯著才算結構；控制後 flat 就寫 flat，並報 `p` 與顯著比例（本版 0/4）
- 兩個獨立污染抗性比率要一致（`[OIII]/Hβ` vs `Hα/[OIII]`；flux 差 56× 但比率只差 3.3%）
- 選樣偏見要寫入「誠實底線」，唔可以留到結論段才提

### 四、數字紀律

- 禁手設標度：`σ₈ = √A_chain × 0.1` 的 `0.1` 要明文標為 scaling factor，唔准當結構常數
- 任何擬合要報 dof 與 `χ²/dof`；`P(k)` 的振幅若由 `χ²` 最小化得出，即屬 1 個自由標度
- 誤差報百分比；修正項要指來源（`φ/2` 為 isometry eigenvalue、`e⁻⁷⁴` 為 59 + 15 段能量）
- 跨版本引用先核歸一化：v9 用 `μ_m = φ^(L−m)`，v7 用 `φ^(291.5−m)`，唔可互換

### 五、記錄紀律

- 每份推導配一支 `NN_verify.py`，編號對齊（`07_...md` ↔ `08_...py`）
- 失敗與推翻照留：V 形的 H1／H2／H4／H5 四項推翻記錄不改寫，只加「誠實底線」段
- 六項自我壓力測試同文明列 QFT 缺失清單（無完整 Lagrangian、無 RGE、無圈修正的時代已過，但仍保留原文）
- v9 與 v10 的裁決差異並列，唔以新結論覆蓋舊記錄

### 六、路徑與命名

- `wfield_lattice/` 子模組用兩位數 `NN_` 對齊 Phase 順序（05 winding → 19 isa_lattice）
- `open_problems_fresh/` 用主題 slug（`p_qcd_gluon_scattering`），唔用 O 號；跨版本追溯靠 register 的 slug 對映
- 子問題碼雙字母＋數字（`SP1`）為 v8.0 遺留，本版沿用；禁單字母＋數字
- `data/` 內大檔（FITS、tar.gz）不入 git，只留 manifest 與擬合結果 JSON

## O/P/M 系列全列表

> 本 repo 只含 O 系列對應主題（P 系列在 v8.0，M 系列在 v11.0）。編號取自跨版本 register 的 slug 對映（`o124_qcd_gluon_scattering` 等），v9.0 當時只有主題目錄名。

| 編號 | 標題 | 核心發現 | 狀態 |
|------|------|----------|------|
| O122 | Feynman 規則從 W-field 晶格推導 | `G(p) = i/(p²−m_H²)`、`−i/16` 頂點、`a₀ = 0.00249`；連續極限誤差 `O(1/N_d²)` | 全部閉合 |
| O123 | 中微子 δ_CP 與混合角分辨 | `δ_CP = 360°/φ = 222.5°` 為唯一結構解；`θ₁₂ = 33.8°`、`θ₁₃ = 8.4°`、`θ₂₃ = 49.1°` | 全部閉合 |
| O124 | QCD 膠子散射（非微擾） | SU(3) 由 `8+3+1+24` 出；`b₀ = 7` ⟹ `α_s(M_Z) = 0.118`、`Λ_QCD ≈ 0.045 GeV`、gg→gg ≈ 0.36 pb | 全部閉合 |
| O125 | 散射振幅與圈修正 | `β_κ = 3κ²/16π² = 7.42×10⁻⁵`、`κ(M_Z) = 0.0601`、`a₀ ≪ 0.5`（么正性安全） | 全部閉合 |
| O126 | Runtime ISA：boot 之後每 tick 做甚麼 | 15 份推導；`z_c = F₄/F₅ = 3/5`；`f_θ` 下轉換 1.8% gap 未閉合 | 部分閉合 |
| O127 | 宇宙網各向異性 ξ(s) 與 V 形驗證 | 8151 條譜、6796 條擬合；V 形下降支判為質量／金屬量假象（控制後 0/4） | 部分閉合 |
| O128 | σ₈ 歸一化 | `σ₈ = √A_chain × 0.1`，`A_chain = Σ 4sin²(πn/88)/n²`；`0.1` 為手設標度 | 部分閉合 |
| O129 | σ_sync 諧波尺度變異數算子 | `σ_sync²(R_n) = ∫ξ(s)W(s;R_n)ds`，`R_n = λ_sync/(2n)`；以諧波尺度取代 8 h⁻¹Mpc | 部分閉合 |
| O130 | 小波／EMD 分解工具箱 | 9 支腳本：EMD pipeline、impedance、hz、pk、horizon aliasing、φ 比率測試；無判定 | 開放 |
| O131 | 疊加波形分析 | `01_stacked_waveform.py` 單檔 239 行；本 repo 無驗證或判定記錄 | 開放 |
| O132 | 紅移演化：諧波振幅 vs z | `01_derive_evolution.py` 單檔 180 行；對 BOSS DR12 與 eBOSS DR16 分箱；無判定 | 開放 |
| O133 | 由 K_Chain 譜導出 P(k) | `P(k) = Σ γ_n G(k−k_n)`、`R_H = 4129.94 Mpc`；振幅由 χ² 最小化擬合（1 自由標度） | 部分閉合 |
| O134 | CY₃ 拓撲算子 | `T_CMB = 2.728 K`（0.06%）；`D_quark = 1 + 36/98·ε` 同時收 m_b 與 m_s | 全部閉合 |
| O135 | Structural forcing：結構強迫閉合 | 24.5% → 1.3% → 0.06% 兩級修正；`T_CMB` 全因子由 ISA 成本與 Lucas 數強迫 | 全部閉合 |

> 狀態欄係 v9.0 當時自評（依各目錄的驗證計數與判定文字）。跨版本 register 於 v10.0 重審後另有裁決，與本表並列供追溯：O124 部分閉合（v9 的 15/15 PASS 判為自指或恆真）、O125／O126／O128／O133／O134／O135 於有限譜重建後閉合、O130–O132 仍開放。