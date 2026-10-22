## 4. 每 Tick 做什麼？—— 最小答案

從第一性原理，每 tick 最少必須做：

**TCK** — 時間推進（PC += 1）

呢個係唯一強制的。NOT cycle 定義了時間，所以每 tick = 1 NOT cycle，系統必須 tick。

**如果只有 TCK，宇宙會怎樣？**

答：靜止。時間在流，但狀態不變。因為 boot 已計算好所有常數，如果無指令改變狀態，宇宙就係一個靜止的 configuration。

**所以第二個必須的指令：保持物理定律執行。**

SM Lagrangian、RGE、場方程 — 這些「定律」不是自動執行的，需要每 tick 重新計算才能 evolve 狀態。

即係：**每 tick 都要用 UIK ISA 重新計算 SM 的狀態演化。**

## 5. 核心問題：ISA 是同一套嗎？

Boot ISA: ADD, SUB, MUL, DIV, CMP, MOV, SHL, SHR, JMP, SYNC

Runtime 用的 ISA：**同一套。**

唔需要新指令。宇宙的「main loop」係一個 program，用 boot ISA 寫成，每 tick 執行一次。

Boot program: 計算常數（一次過）
Runtime program: evolve 宇宙狀態（無限 loop）

兩個 program 行在同一 UIK 上。