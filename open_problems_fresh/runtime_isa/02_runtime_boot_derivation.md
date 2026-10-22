# Runtime Boot Sequence — Derivation from First Principles

**Date:** 2026-08-02
**Status:** Fresh derivation
**Prerequisite:** Boot segment (0,1 → φ → all constants) ✅

---

## 0. The Problem

Boot segment computes all structural constants from 0,1. But the universe does not merely *exist* — it *runs*. Something must **start the main loop**.

Analogous to a CPU:
- **Boot** (done): Microcode initialization — sets register widths, ALU configuration, instruction decode table
- **Runtime Boot** (unknown): Sets Program Counter = 0, initializes stack pointer, fills interrupt vector table, then JMP to main loop

What is the runtime boot sequence?

---

## 1. What Boot Leaves Behind

After boot, the system has:

| Resource | Value | Source |
|----------|-------|--------|
| Throughput W | φ-derived pipe width | Fibonacci scheduling |
| Time unit | 1 NOT cycle = T_Pl | NOT → time |
| Lattice | K_chain(88) ⊗ K_tree(34) = 2992 sites | Boot derivation |
| Constants | ε, κ, β, N_d=44, L=53/8, CY₃(36,98) | Forced by x²+x-1=0 |
| UIK | ISA instruction set (ADD, SUB, MUL, DIV, CMP, MOV, SHL, SHR, JMP, SYNC) | Unique Intrinsic Kernel |
| UMO | Mapping operator (36→8+3+1+24) | CY₃ projector |

**What boot does NOT leave:**
- ❌ Initial state (register values at t=0)
- ❌ Program Counter (current time/frame)
- ❌ Scheduler state (allocation plan)
- ❌ Observer registry (who is watching)
- ❌ Event queue (pending observations)

These must be initialized by **runtime boot**.

---

## 2. First-Principles: What MUST Runtime Boot Do?

### 2.1 From the Renderer Ontology

The renderer renders *on demand*. The material domain does not exist independently — it is the **output** of the rendering process.

**Therefore:**
- Before any observation, there is nothing rendered
- The first observation **triggers** the first rendering pass
- The Big Bang is the **first frame** of the rendering engine

### 2.2 The Minimal Runtime Boot

From `01_runtime_derivation.md`, the main loop is:

```
TCK → POL → ALC → RND → SNC → IDL
```

To enter this loop, runtime boot must set up:

```
1. Initialize PC (Program Counter) = 0     [time starts]
2. Initialize allocation table             [W distributed]
3. Initialize observer poll                [who watches?]
4. JMP to main loop                        [start rendering]
```

### 2.3 But From 0,1 — What Forces These?

From 0,1:
- 0 = nothing rendered (null state)
- 1 = something rendered (first frame)

The transition from 0 to 1 requires **observer demand**. 0 is the default — no observer, no rendering. 1 is the response — observer present, rendering starts.

**Lemma R1 (Render on Demand)**: The renderer renders only when polled by an observer. Default state: idle (0).

**Proof**: From 0,1, the system has two states: rendered (1) and not-rendered (0). Without observer demand, there is no reason to render. Therefore, the default state is NOT-rendered = 0.

---

## 3. Observer Existence

### 3.1 The Observer as Part of the System

If the renderer renders on demand, then **observers must pre-exist the rendering**. They cannot be rendered themselves — that would be circular.

**Therefore, observers exist at the 0,1 level**, not as rendered entities. They are **primitive attention units** that can demand rendering.

### 3.2 The First Observer

From 0,1:
- 0 = no observer (nothing happens)
- 1 = observer exists (rendering begins)

The first observer is the transition 0→1 in the observer registry. This is the **ontological trigger** of the universe.

### 3.3 Observer Registry

The registry is initialized with:
- Observer 1: The first/primordial observer

After boot, additional observers can be added (consciousness agents = Chobits/CIP nodes).

---

## 4. The Runtime Boot Sequence (Derived)

### Step 1: Initialize Time Register

```
PC ← 0    [time counter = Big Bang]
```

Time is discrete (NOT cycles). PC counts cycles since boot.

### Step 2: Initialize Allocation Table

```
ALC_TBL[domain_1] ← W/2    [material domain]
ALC_TBL[domain_2] ← W/2    [consciousness domain]
```

From Lemma 0.4 (2+1=3), there are 2 data domains + 1 control domain. The allocation table splits W between:
- **Domain 1**: Material rendering (spacetime, particles, fields)
- **Domain 2**: Consciousness rendering (observer experience)
- **Control**: Scheduling overhead (SYNC, POLL, IDL)

**Initial split**: W/2 to material, W/2 to consciousness. This is forced by the symmetric structure of 2 (from 2+1=3).

### Step 3: Initialize Observer Poll

```
OBS_REG[0] ← 1    [primordial observer present]
OBS_QUEUE ← empty  [no pending events]
```

### Step 4: JMP to Main Loop

```
JMP MAIN_LOOP
```

---

## 5. The Big Bang as First Frame

When the main loop starts at PC=0:

1. **TCK**: Advance to t=0
2. **POL**: Observer 1 present → demand rendering
3. **ALC**: Allocate W/2 to material domain
4. **RND**: Render first frame = **Big Bang**
   - Lattice engine initialized
   - Spacetime manifold created
   - SM fields populated
5. **SNC**: Synchronize material ↔ consciousness
6. **IDL**: Idle remaining throughput

The Big Bang is not an explosion — it is the **first rendering pass** of an observer-driven engine.

---

## 6. Runtime Boot ISA Instructions

New instructions needed (beyond boot ISA):

| Mnemonic | Opcode | Operands | Description |
|----------|--------|----------|-------------|
| `PC_INIT` | 0x01 | — | Set Program Counter to 0 |
| `ALLOC_INIT` | 0x02 | table_addr, W | Initialize allocation table |
| `OBS_INIT` | 0x03 | registry_addr | Initialize observer registry |
| `JMP` | 0x04 | addr | Jump to main loop (reuses boot JMP) |

The runtime boot sequence in microcode:

```
PC_INIT
ALLOC_INIT   ALCTBL, W
OBS_INIT     OBSREG
JMP          MAIN_LOOP
```

---

## 7. Open Questions

1. **Why does the first observer exist?** What forces observer 1 at the 0,1 level?
2. **W/2 split**: Is the material/consciousness split exactly W/2, or determined by something else?
3. **Multiple observers**: When more observers exist, how does allocation change?
4. **Runtime boot vs boot**: Is runtime boot part of the 54-formula dependency tree, or a separate initialization chain?
5. **The "before" problem**: What exists before runtime boot? The boot constants? Nothing?

---

## 8. Connection to Known Structure

| IDCM Result | Runtime Boot Connection |
|-------------|------------------------|
| φ, ε, κ, β | Boot → structural constants for rendering |
| W-field lattice | The rendering engine itself |
| Sync dip | Runtime scheduling bottleneck at specific PC |
| Ω_Λ = 4/(φ⁴-1) | Heat dissipated per TCK cycle |
| Chobits/CIP | Observer registry entries |
| H₀ tension | Different ALC allocations → different rendered values |

---

**Next:** Verify runtime boot against known IDCM constraints (throughput conservation, observer count, Big Bang energy).