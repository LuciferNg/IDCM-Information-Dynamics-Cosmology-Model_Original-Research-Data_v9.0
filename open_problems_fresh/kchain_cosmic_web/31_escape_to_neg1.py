#!/usr/bin/env python3
"""
精煉: 正確計算逃離到 C=-1 嘅 WKB action
===========================================
關鍵: V(C) 喺 C=-1 發散, 但 ∫√(-2ln(ε)) dε 係有限!
"""

import math, sys
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
N_d = 44
c = 0.3066
t_site = R_H / (N_d * c) / 1000
const = 0.290229
E0 = 0.5 * math.sqrt(1 + 1/(PHI_INV+1)**2)

def V(C):
    return C**2/2 - math.log(abs(C+1)) + const

print("=" * 80)
print("  精煉: 逃離到 C=-1 嘅 WKB action")
print("=" * 80)

# ================================================================
# 1. 搵轉折點
# ================================================================
print(f"\n{'─'*80}")
print("  1. 轉折點 (V(C) = E₀)")
print(f"{'─'*80}")

print(f"  E₀ = ½ω = {E0:.6f}")
print(f"  V(φ⁻¹) = {V(PHI_INV):.6f}")

# 右轉折點: C = φ⁻¹
print(f"  右轉折點: C = φ⁻¹ = {PHI_INV:.6f}")

# 左轉折點: V(C) = E₀, C < 0
# 用二分法
lo, hi = -0.99, 0.0
for _ in range(50):
    mid = (lo + hi) / 2
    if V(mid) > E0:
        lo = mid
    else:
        hi = mid
left_tp = (lo + hi) / 2
print(f"  左轉折點: V(C) = E₀, C = {left_tp:.6f}, V(C) = {V(left_tp):.6f}")

# 第二個左轉折點: V(C) = E₀, C < -1
# 但呢個區域有奇點, 需要小心
# 搵 V(C) = E₀ 在 C < -1 區域
lo2, hi2 = -2.0, -1.01
found = False
for _ in range(50):
    mid = (lo2 + hi2) / 2
    if V(mid) > E0:
        lo2 = mid
    else:
        hi2 = mid
    if abs(V(mid) - E0) < 1e-6:
        found = True
        break
left_tp2 = (lo2 + hi2) / 2
print(f"  第二左轉折點: C ≈ {left_tp2:.4f}, V(C) = {V(left_tp2):.4f}")

# ================================================================
# 2. 穿隧 action: φ⁻¹ → -1
# ================================================================
print(f"\n{'─'*80}")
print("  2. 穿隧 action: φ⁻¹ → -1")
print(f"{'─'*80}")

# 路徑分兩段:
# 段1: φ⁻¹ → 左轉折點 (classical forbidden region)
# 段2: 左轉折點 → -1 (tunnelling through barrier)

print(f"  段1: φ⁻¹ → {left_tp:.6f} (classical forbidden)")

N = 20000
S1 = 0.0
for i in range(N+1):
    C = left_tp + (PHI_INV - left_tp) * i / N
    v = V(C) - E0
    if v < 0: v = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S1 += w * math.sqrt(2 * v) if v > 0 else 0
S1 *= (PHI_INV - left_tp) / (3 * N)

print(f"  S₁ = {S1:.6f}")

# 段2: 左轉折點 → -1 (接近奇點)
# 用變數變換: ε = C + 1, 從 ε = 0.001 到 ε = left_tp + 1
print(f"  段2: {left_tp:.6f} → -1 (接近奇點)")

eps_min = 1e-6
eps_max = left_tp + 1
S2 = 0.0
N = 50000
for i in range(N+1):
    eps = eps_min + (eps_max - eps_min) * i / N
    C = -1 + eps
    v = V(C) - E0
    if v < 0: v = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S2 += w * math.sqrt(2 * v) if v > 0 else 0
S2 *= (eps_max - eps_min) / (3 * N)

print(f"  S₂ = {S2:.6f}")

S_total = S1 + S2
print(f"  S_total = S₁ + S₂ = {S_total:.6f}")
print(f"  2S_total = {2*S_total:.4f}")

# 檢查奇點附近嘅行為
print(f"\n  奇點附近積分:")
for eps in [1e-1, 1e-2, 1e-3, 1e-4, 1e-5]:
    C = -1 + eps
    v = V(C) - E0
    integrand = math.sqrt(2*v) if v > 0 else 0
    # 積分近似: ∫₀^ε √(-2ln(x)) dx ≈ ε√(-2ln(ε)) + ...
    approx = eps * math.sqrt(-2 * math.log(eps)) if eps > 0 else 0
    print(f"  ε={eps:.1e}: V={v:.4f}, √(2V)={integrand:.4f}, ε√(-2lnε)={approx:.4f}")

# ================================================================
# 3. 完整穿隧到 -φ
# ================================================================
print(f"\n{'─'*80}")
print("  3. 完整穿隧到 -φ")
print(f"{'─'*80}")

# 路徑: 左轉折點 → -1 → -φ
# 段1: left_tp → -1 (tunnelling)
# 段2: -1 → -φ (classical forbidden, V > E₀)

# 段2: -1 → -φ
S3 = 0.0
for i in range(N+1):
    C = -PHI + (-1 + PHI) * (1 - i / N)  # 從 -φ 到 -1, 但反嚟行
    v = V(C) - E0
    if v < 0: v = 0
    w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
    S3 += w * math.sqrt(2 * v) if v > 0 else 0
S3 *= (PHI - 1) / (3 * N)

print(f"  段3: -1 → -φ (C={-PHI:.4f})")
print(f"  S₃ = {S3:.6f}")

# 總 action
S_total_full = S1 + S2 + S3
print(f"  S_total = S₁ + S₂ + S₃ = {S_total_full:.6f}")
print(f"  2S_total = {2*S_total_full:.4f}")

# 44-site
print(f"")
print(f"  44-site 集體穿隧:")
print(f"  44 × S = {44 * S_total_full:.6f}")
print(f"  44 × 2S = {44 * 2 * S_total_full:.4f}")
print(f"  t_cycle = τ₀ × exp(44 × 2S) = {t_site * math.exp(44 * 2 * S_total_full):.4e} Gyr")

# ================================================================
# 4. 比較
# ================================================================
print(f"\n{'─'*80}")
print("  4. 比較")
print(f"{'─'*80}")

# 舊: 只到 C=0
S_old = 0.231178
print(f"  舊 (只到 C=0):")
print(f"  S = {S_old:.6f}, 44×2S = {44*2*S_old:.4f}, t = {t_site * math.exp(44*2*S_old):.4e} Gyr")

# 新: 到 C=-1
print(f"")
print(f"  新 (到 C=-1):")
print(f"  S = {S_total:.6f}, 44×2S = {44*2*S_total:.4f}, t = {t_site * math.exp(44*2*S_total):.4e} Gyr")

# 完整: 到 C=-φ
print(f"")
print(f"  完整 (到 C=-φ):")
print(f"  S = {S_total_full:.6f}, 44×2S = {44*2*S_total_full:.4f}, t = {t_site * math.exp(44*2*S_total_full):.4e} Gyr")

# ================================================================
# 5. 但係... 逃離真係需要到 C=-1 嗎？
# ================================================================
print(f"\n{'─'*80}")
print("  5. 重新思考逃離條件")
print(f"{'─'*80}")

print(f"""
  遞迴 C_{{n+1}} = 1/(1+C_n) 係離散時間映射。
  量子穿隧係連續時間過程。
  
  兩者唔同: 穿隧可以將系統帶到 C < -1, 
  但離散映射需要 C_n < -1 先可以逃離。
  
  關鍵: 穿隧係 continuous-time, 系統喺穿隧過程中
  可以「跳過」離散映射嘅限制。
  
  穿隧到 C = 0 後, 離散映射會帶返去 φ⁻¹。
  但穿隧到 C < -1 後, 離散映射會帶去 -φ。
  
  所以:
  - 到 C = 0: 唔夠, 映射返去 φ⁻¹
  - 到 C < -1: 夠, 映射去 -φ (逃離)
  
  但 WKB action 到 C < -1 好大, 因為奇點。
  
  實際物理: 奇點係數學artifact, 量子漲落會 regularize 佢。
  √κ = 0.25 嘅漲落可以「跳過」奇點。
  
  真正嘅逃離時間應該用 Gaussian fluctuation:
  P(ΔC > 1.618) = exp(-1.618²/2κ) = exp(-20.94)
  t_escape = T_SYNC / P × 44 = {26.94 / (44 * math.exp(-1.618**2/(2*1/16))):.4e} Gyr
  
  呢個同 uniform mode 結果 (2.09e8 Gyr) 一致。
""")

# Gaussian fluctuation 計算
P_single = math.exp(-1.618**2 / (2 * 1/16))
P_44 = 44 * P_single
t_escape = 26.94 / P_44
print(f"  Gaussian 逃離:")
print(f"  P(ΔC > 1.618) = exp(-1.618²/2κ) = {P_single:.4e}")
print(f"  44-site: P = {P_44:.4e}")
print(f"  t_escape = {t_escape:.4e} Gyr")

# 對比 WKB 到 C=0
print(f"  WKB 到 C=0: t = {t_site * math.exp(44*2*S_old):.4e} Gyr")
print(f"  Gaussian 到 C=-1: t = {t_escape:.4e} Gyr")
print(f"  比值: {t_escape/(t_site * math.exp(44*2*S_old)):.2f}")

# ================================================================
# 6. 結論
# ================================================================
print(f"\n{'─'*80}")
print("  6. 結論")
print(f"{'─'*80}")

print(f"""
  兩種逃離機制:
  
  A. WKB 穿隧到 C=0 (然後映射返去 φ⁻¹, 唔夠)
     → 唔係真逃離
     
  B. WKB 穿隧到 C<-1 (繞過奇點, action 大)
     → 真逃離, 但 action 難計算
     
  C. Gaussian fluctuation 到 C<-1 (一步到位)
     → t = 7.5 × 10⁸ Gyr
     → 同 uniform mode 結果一致 (2.09 × 10⁸ Gyr)
  
  最佳估計: t_cycle ≈ 10⁸-10⁹ Gyr (機制 C)
  但機制 C 假設 fluctuation 係 Gaussian, 未考慮 WKB 修正。
  
  需要 W-field 完整量子場論才能確定。
""")