# Lattice Engine 擴展 Plan — 五方向一次過

> **For Hermes:** Implement phases sequentially using delegate_task subagents. Each phase produces derivation + verification.

**目標:** 將 IDCM Lattice Engine 從 U(1) gauge + Higgs 擴展到完整 SM + 重力

**依賴圖:**
```
Phase 1: 非 Abel 規範 (SU(2)×SU(3))
  ├──→ Phase 2: 費米子 Dirac 算符 (lattice doubling 解決)
  │        ↓
  ├──→ Phase 3a: 完整 SM Lagrangian 組裝
  │
  └──→ Phase 3b: 重力湧現 (parallel path)
              ↓
       Phase 4: Paper 撰寫
```

---

## Phase 1: 非 Abel 規範對稱性 SU(2)×SU(3)

**Goal:** 從 K_tree 的 B=4 branch symmetry 推導 SU(2)×SU(3) gauge sector

**Key idea:** Tree branching factor B=4. SU(2)×SU(3) has 3+8=11 generators, rank 1+2=3. CY₃ h¹¹=36 decomposes as 8+3+1+24 — the 8+3 match SU(3)+SU(2). The tree branch indices carry the internal symmetry.

**Files to create:**
- `wfield_lattice/su2_su3/09_gauge_derivation.md` — 推導
- `wfield_lattice/su2_su3/10_gauge_verify.py` — 驗證 15/15

**Verification targets:**
- B=4 branches → SU(2)×SU(3) generator count = 11
- Lattice covariant derivative with non-abelian connection
- Gauge kinetic term = Σ tr(1 - U_plaq)
- Wilson plaquette action from lattice

---

## Phase 2: 費米子 Dirac 算符 on Lattice

**Goal:** 建構無 doubling 問題的 lattice Dirac operator

**Key idea:** K_chain 的 Z₂ grading (d={3,2,0}) 自然避開 Nielsen-Ninomiya doubling — chain 的 88 nodes 中，只有一半 carry physical chiral modes

**Files to create:**
- `wfield_lattice/fermion/11_dirac_lattice_derivation.md` — 推導
- `wfield_lattice/fermion/12_dirac_lattice_verify.py` — 驗證

**Verification targets:**
- Wilson term from K_chain Laplacian (natural, not ad-hoc)
- No doublers from Z₂ grading
- Chiral modes k={1,4,5} = 3 generations
- Dirac spectrum matches known masses

---

## Phase 3a: 完整 SM Lagrangian 組裝

**Goal:** 將所有 sector 合成一個 lattice Lagrangian

**已有 pieces:**
- ✅ U(1) gauge: S = Σ(1 - cos A_n)
- ✅ Higgs: VEV + radial mode + phase mode
- ✅ Yukawa: y_f = φ^(-k_f)
- 🔴 SU(2)×SU(3) gauge (Phase 1)
- 🔴 Fermion kinetic (Phase 2)

**Files to create:**
- `wfield_lattice/lagrangian/13_full_sm_lattice.md` — 完整 Lagrangian
- `wfield_lattice/lagrangian/14_full_sm_verify.py` — 驗證

**Verification targets:**
- All 5 sectors present (gauge + fermion + Higgs + Yukawa + gravity)
- Zero free parameters (all from φ)
- Lagrangian matches SM in continuum limit

---

## Phase 3b: 重力湧現 (parallel to 3a)

**Goal:** Einstein tensor from K_chain ⊗ K_tree partition function

**Key idea:** 4D metric g_μν = coarse-grained W-field correlation function. Ricci curvature = 晶格配分函數的二次變分.

**Files to create:**
- `wfield_lattice/gravity/15_gravity_emergent.md` — 推導
- `wfield_lattice/gravity/16_gravity_verify.py` — 驗證

**Verification targets:**
- Einstein tensor from lattice partition function
- Λ = 4/(φ⁴-1) = 0.6847 matches IDCM
- Newtonian limit from lattice
- Gravitational waves = sync wave on large scales

---

## Phase 4: Paper 撰寫

**Goal:** 將所有成果編譯為一篇完整 paper

**Title:** "W-Field as a Lattice Field Theory on K_chain ⊗ K_tree: Emergent SM from 0,1"

**Structure:**
1. Introduction — 0,1 → φ → lattice
2. Lattice definition — K_chain ⊗ K_tree
3. Sync wave → light, c=1
4. Zero mode → U(1) gauge
5. Non-Abelian gauge from tree
6. Fermions on lattice, no doubling
7. Higgs & PG from radial/phase modes
8. Full SM Lagrangian (zero free parameters)
9. Gravity as emergent geometry
10. Predictions + verification (76/76 tests)

**Files to create:**
- `wfield_lattice/paper/17_paper.md` — 完整 paper

---

## Execution Checklist

```
□ Phase 1: SU(2)×SU(3) gauge — derivation + verify (15/15)
□ Phase 2: Lattice Dirac operator — derivation + verify (15/15)
□ Phase 3a: Full SM Lagrangian — assembly + verify (15/15)
□ Phase 3b: Gravity emergence — derivation + verify (15/15)
□ Phase 4: Paper — 10 sections, all derived
```

去馬！