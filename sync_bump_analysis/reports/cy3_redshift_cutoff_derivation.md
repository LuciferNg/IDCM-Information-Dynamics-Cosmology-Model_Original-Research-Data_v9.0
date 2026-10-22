# CY₃ Redshift Cutoff — Exact Derivation

## 1. 問題設定

從 IDCM 結構推導，宇宙係一個 finite throughput rendering system。最大紅移 $z_{\\text{max}}$ 係 rendering pipeline 嘅 Nyquist 截斷點。

**已知：**
- 最高光譜確認紅移：$z_{\\text{obs}} = 14.588$（JADES DR4, NIRCam_ID=183348）
- 光度法 EAZY 顯示 $z>15 = 0$（光譜金標準確認）
- Nyquist 估計：$z \\approx 17$

## 2. 同步凸起類比

同步凸起（sync bump）來自 6 步 Fibonacci 排程：
$$[F_1, F_2, F_3, F_4, F_5, F_6] = [1, 1, 2, 3, 5, 8]$$

第 5 步（SNC）累積分配：
$$z_c = \\frac{\\sum_{i=1}^{5} F_i}{\\sum_{i=1}^{6} F_i} = \\frac{12}{20} = \\frac{3}{5} = \\frac{F_4}{F_5} = 0.6$$

這是 $\\varphi^{-1}$ 連分數嘅第 3 收斂項。

## 3. 高紅移截斷 — CY₃ 推導

K_chain 有 $N_d = 44$ 個節點。Nyquist 頻率係 $n = N_d/2 = 22$，即係最大可分辨模式數。

**但紅移唔係模式數本身。** 紅移係 scale factor $a = 1+z$，而 scale factor 同 rendering 嘅「步數」成指數關係。

關鍵結構：$\\varphi$ 嘅連分數收斂到 $\\varphi$ 需要無限步。有限 throughput 限制咗收斂深度。

**收斂誤差：**
$$|\\varphi - \\frac{F_{n+1}}{F_n}| \\approx \\frac{1}{F_n \\cdot F_{n+1}} \\approx \\frac{1}{\\varphi^{2n+1}}$$

當收斂誤差小於 rendering 嘅最小可分辨單位 $\\kappa = 1/16$ 時，進一歩收斂冇意義。

**最大可分辨步數：**
$$\\frac{1}{\\varphi^{2n+1}} = \\kappa \\implies \\varphi^{2n+1} = 16 \\implies 2n+1 = \\log_\\varphi(16) = \\frac{\\ln 16}{\\ln \\varphi} = \\frac{2.7726}{0.4812} = 5.76$$

$$n \\approx 2.38 \\text{（呢個唔 work）}$$

## 4. 替代推導：CY₃ 投影算子

CY₃(36,98) 係投影算子，從 W-field 嘅內部模式投影到 4D 時空。

最大投影距離（即最大紅移）由 CY₃ 嘅 Hodge 數決定：

$$z_{\\text{max}} = \\frac{N_d}{\\varphi^2} = \\frac{44}{\\varphi^2}$$

**推導：**
- $N_d = 44$ 係 K_chain 維度（因果域數目）
- $\\varphi^2 = \\varphi + 1 = \\frac{3+\\sqrt{5}}{2} \\approx 2.618$ 係 MERA 分支因子 $B = \\varphi^3-\\varphi^{-3}=4$ 嘅平方... 唔係，$\\varphi^2 = B + \\varphi^{-2} = 4 + 0.146 = 4.146$... 唔啱。

**更正：** $\\varphi^2 = \\varphi + 1$，係 Fibonacci 數列嘅特徵值。$N_d/\\varphi^2$ 係 chain 維度嘅 $\\varphi^{-2}$ 投影。

## 5. 另一推導：Lucas 數截斷

Lucas 數列：$L_0=2, L_1=1, L_2=3, L_3=4, L_4=7, L_5=11, L_6=18, L_7=29, L_8=47, \\ldots$

z_max = 17 = L₆ - 1 = h¹¹/2 - 1

其中：
- L₆ = 18 係第 6 個 Lucas 數
- h¹¹ = 36 係 CY₃ 嘅 Kähler 模數
- h¹¹/2 = L₆ = 18（結構性相等）

**代數展開：**
$$z_{\\text{max}} = L_6 - 1 = (\\varphi^6 + \\varphi^{-6}) - 1 = 17.944 + 0.056 - 1 = 17$$

**同步凸起 vs 高紅移截斷對稱性：**

| 特徵 | 同步凸起 (sync bump) | 高紅移截斷 (high-z cutoff) |
|:----|:-------------------:|:------------------------:|
| Pipeline 位置 | 第 5 步 SNC | 第 6 步 IDL（終點） |
| 公式 | $z_c = F_4/F_5 = 3/5$ | $z_{\\text{max}} = L_6 - 1 = 17$ |
| 數列 | Fibonacci $F_4, F_5$ | Lucas $L_6$ |
| 值 | 0.6 | 17 |
| 物理意義 | 有限算力嘅第 5 階截斷指紋 | 有限算力嘅最終 rendering 邊界 |

**為何 $L_6$ 而非 $L_5$ 或 $L_7$？**
- $L_5 = 11$：對應 $z=10$，係 aliasing 級數中嘅點，唔係截斷
- $L_6 = 18$：$z=17$，係 Nyquist 截斷，rendering 極限
- $L_7 = 29$：$z=28$，太大，已超出 JWST 能力

**與 CY₃ 嘅直接關係：**
$$z_{\\text{max}} = L_6 - 1 = \\frac{h^{11}}{2} - 1 = \\frac{36}{2} - 1 = 17$$

即係 CY₃ 嘅 Kähler 模數 $h^{11}=36$ 直接決定最大紅移。

## 6. 驗證與觀測

| 公式 | 值 | 與觀測符合 |
|:----|:--:|:----------:|
| $N_d/\\varphi^2$ | 16.807 | 高於 $z=14.588$，預測 $z>15$ 仍有空間 |
| $\\varphi^6 - 1$ | 16.944 | 高於 $z=14.588$，接近 Nyquist 估計 |
| $L_6 - 1$ | 17.000 | 整數 cutoff，最簡潔 |

**觀測約束：**
- 光譜最高 $z=14.588$，低於全部 3 個候選值
- $z>15 = 0$ 但 sample size 細（$z>13$ 得 5 個源）
- DR5 EAZY 顯示 $z=15-17$ 有光度候選體但全部係假陽性
- **最終判決需等 LAPIS 1000h** 確認 $z>15$ 是否真係 $0$

## 7. 開放問題

1. 3 個候選公式邊個係正確？
2. 截斷係 schematic（漸進）定 step function（突然）？
3. 如果 $z_{\\text{max}} = 17$，點解最高觀測值係 $14.588$ 而唔係 $17$？
4. 截斷 redshift 同 CY₃ Hodge 數嘅具體關係？