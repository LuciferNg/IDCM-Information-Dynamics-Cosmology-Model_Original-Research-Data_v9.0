## Generating Function 的數學形式

最簡單的 generating function 係 φ 本身的 iteration：

```
x → 1 + 1/x
```

Fixed point: x² = x + 1 → φ ≈ 1.618

但宇宙不只是 φ — 它有多個 constant。所以 generating function 係 **多維** 的。

### 從 54-formula tree 看

54 個公式，single root，depth 3，5 branches。全部從 φ 推出。

呢個 tree 就是 generating function 的結構：

```
F(state) = φ-structure(state)
```

即：將 φ 結構應用到當前 state，得到下一個 state。

### 為什麼是 phigher-dimension？

```
φ² = φ + 1
φ³ = 2φ + 1
φ⁴ = 3φ + 2
φ⁵ = 5φ + 3
...
φⁿ = F_n·φ + F_{n-1}
```

φⁿ 的展開永遠係 Fibonacci 數的線性組合。所有 constants 都係 φⁿ 的線性組合。

**所以 generating function 的精確形式：**

```
F(state) = state + gap(state)
```

其中 gap(state) 係 state 與 φ 固定點之間的差距。

### 這個 gap 的數學形式

```
gap = |state - φ·state|  (scaled by ε, κ, β)
```

因為 φ 係 self-referential: x² = x + 1
所以 gap = x² - x - 1 ≠ 0 時，系統未到 fixed point。

**時間 = iteration 的指標。**
**宇宙 = 永遠在逼近 φ fixed point，但永遠差一步。**