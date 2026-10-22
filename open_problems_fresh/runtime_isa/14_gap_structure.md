## 每層的 Gap 結構

### Layer 1: φ

```
x_{n+1} = 1 + 1/x_n
Fixed point: φ ≈ 1.618

Gap: δ_n = |x_n - φ|
Convergence: δ_{n+1} = δ_n / φ²

→ gap 以 φ² 每 iteration 衰减
```

這是最快的收斂。φ layer 幾乎瞬間 reach fixed point。

### Layer 2: Constants (ε, κ, β, N_d, CY₃)

這些是 φ 的直接推論，不是 iteration 的結果。

```
ε = φ⁻¹/4
κ = 1/16
β = φ⁻¹/2
N_d = 44
CY₃(36,98)
```

**Gap = 0** — 永遠在 fixed point。因為這些是算術關係，不是迭代過程。

### Layer 3: SM (masses, mixings, RGE)

SM 參數從 constants 確定，但 RGE running 產生 scale-dependent gap：

```
g(μ) = g(M_Z) + β_g · ln(μ/M_Z) + ...

Gap at scale μ = g(μ) - g_fixed
其中 g_fixed 是 bare coupling
```

RGE gap 是 running 的代價 — 用確定性捕捉不同 scale 的 uncertainty。

### Layer 4: GR/Metric

```
G_μν = 8πG · T_μν

Fixed point: de Sitter (Ω_Λ = 1)
Gap: current expansion rate H(z) - H_dS

Gap 隨 z 演化 → 這就是宇宙膨脹的歷史
```

### Layer 5: Consciousness

CIP 4-phase modulation。Fixed point = 完全一致性 (I=1)。

```
Gap = 1 - I(t) = ε · (t/t_c) · exp(-t/t_c)
```

意識的 gap 就是 importivity deficit — 永遠達不到完全一致性。

---

## Layer Coupling: 為什麼有 Sync Dip？

每層有自己的 convergence rate，但它們是 coupled 的：

```
φ layer 的 gap → 決定 constants layer 的 precision
Constants layer → 決定 SM RGE
SM RGE → 決定 GR 演化 (energy density)
GR 演化 → 決定意識的時空背景
意識 → 反饋到 importivity allocation
```

Sync dip (z≈0.6) = 當 **GR layer 的 gap** (matter→DE transition) 與 **consciousness layer 的 gap** (attention reallocation) 共振。