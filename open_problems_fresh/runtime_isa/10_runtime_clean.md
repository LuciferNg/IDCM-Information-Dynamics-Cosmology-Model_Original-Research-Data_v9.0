## 2. Boot vs Runtime

Boot 係一次過的初始化程序，terminates 之後系統有：
- 所有常數
- 所有結構（lattice, SM, CY₃）
- 一個無時間的靜態 configuration

但宇宙係 **動態的** — 時間在 tick。所以 boot 之上一定有個 runtime layer 負責執行。

**Boot 不提供的：**
- 如何 tick ？
- 狀態如何 evolve？
- 如何分配 throughput？
- 如何回應觀測者？

呢啲就係 runtime 的責任。

## 3. 從第一性原理開始

Boot 從 0,1 開始，推到 NOT → time → throughput。Runtime 也應從同一個根基開始。

Boot 之後：
- 時間存在（NOT cycle = 1 T_Pl）
- Throughput W 存在（pipe width）
- 常數已計算（放在 registers 中）

**Runtime 的 axiom：** 系統必須每 tick 執行一次，直到永遠。

**問題：** 每 tick 做什麼？