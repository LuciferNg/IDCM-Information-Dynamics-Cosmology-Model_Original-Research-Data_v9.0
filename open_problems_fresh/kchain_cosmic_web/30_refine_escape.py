#!/usr/bin/env python3
"""
W-field 精煉 — 完整穿隧路徑到 C=-φ
=========================================
之前假設穿隧到 C=0 就夠，但系統需要逃到 C=-φ 先真正脫離吸引子。
路徑必須繞過奇點 C=-1。
"""

import math, sys, cmath
sys.path.insert(0, '/home/wsl/IDCM/open_problems_fresh/kchain_cosmic_web')
from _core import *
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = PHI - 1
N_d = 44
c = 0.3066
t_site = R_H / (N_d * c) / 1000

const = 0.290229

def V_complex(C):
    """W-field 勢能 (複數版本)"""
    return C**2/2 - cmath.log(C + 1) + const

print("=" * 80)
print("  精煉: 完整穿隧路徑 φ⁻¹ → -φ")
print("=" * 80)

# ================================================================
# 1. 爲什麼要到 C = -φ？
# ================================================================
print(f"\n{'─'*80}")
print("  1. 逃離條件")
print(f"{'─'*80}")

print(f"  遞迴 C_{{n+1}} = 1/(1+C_n):")
print(f"  C > 0:  → C_{{n+1}} > 0 → 收斂到 φ⁻¹ (返回吸引子)")
print(f"  C = 0:  → C_{{n+1}} = 1 → 收斂到 φ⁻¹ (返回)")
print(f"  -1<C<0: → C_{{n+1}} > 1 → 收斂到 φ⁻¹ (返回)")
print(f"  C = -1: → 奇點 (不可達)")
print(f"  C < -1: → C_{{n+1}} < 0 → 收斂到 -φ (逃離)")
print(f"")
print(f"  → 真正逃離需要 C < -1, 即達到 -φ = {-PHI:.4f}")
print(f"  → 舊計算只到 C=0, 唔夠!")

# ================================================================
# 2. 複數平面路徑
# ================================================================
print(f"\n{'─'*80}")
print("  2. 複數平面路徑")
print(f"{'─'*80}")

# 直線路徑: φ⁻¹ → -φ, 穿越奇點 C=-1
# 需要繞過奇點, 用圓弧

# 路徑參數化:
# 用半圓繞過 C=-1, 上半平面
# C(t) = φ⁻¹ + (-φ-φ⁻¹)×t + i×r×sin(πt)  (r = 繞行半徑)

print(f"  路徑: φ⁻¹(0.618) → 繞過 C=-1(奇點) → -φ(-1.618)")
print(f"  繞行半徑 r 越小, 越接近奇點, action 越大")
print(f"")

for r in [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]:
    N = 5000
    S_path = 0.0
    for i in range(N+1):
        t = i / N
        # 直線 + 半圓繞行
        x = PHI_INV + (-PHI - PHI_INV) * t
        y = r * math.sin(math.pi * t)
        C = complex(x, y)
        V_val = V_complex(C)
        # sqrt(2V) in complex plane
        sqrt_2V = cmath.sqrt(2 * V_val)
        # derivative: dx/dt + i dy/dt
        dx_dt = -PHI - PHI_INV
        dy_dt = r * math.pi * math.cos(math.pi * t)
        dC_dt = complex(dx_dt, dy_dt)
        
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S_path += w * sqrt_2V * dC_dt
    
    S_path *= (1 / N)  # 不需要 /3 因為係複數
    # 取實部
    S_real = S_path.real / 3
    
    t_cycle_44 = t_site * math.exp(44 * 2 * S_real)
    print(f"  r={r:<5.2f}: S_path = {S_real:.6f}, 44×2S = {44*2*S_real:.4f}, t_cycle = {t_cycle_44:.4e} Gyr")

# ================================================================
# 3. 分段路徑
# ================================================================
print(f"\n{'─'*80}")
print("  3. 分段路徑 (φ⁻¹→0 + 0→-φ)")
print(f"{'─'*80}")

# 第一段: φ⁻¹ → 0 (實軸, 無奇點)
def S_integral(a, b, use_sqrt2V=True):
    N = 10000
    S = 0.0
    for i in range(N+1):
        x = a + (b - a) * i / N
        v = x**2/2 - math.log(abs(x+1)) + const
        if v < 0: v = 0
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S += w * math.sqrt(2 * v) if use_sqrt2V else 0
    return S * (b - a) / (3 * N)

S_1 = S_integral(0, PHI_INV)
print(f"  第一段: φ⁻¹ → 0")
print(f"  S₁ = {S_1:.6f}")
print(f"  2S₁ = {2*S_1:.4f}")

# 第二段: 0 → -φ (需要繞過 C=-1)
# 用複數路徑: 0 → -(1-ε) → -φ
# 從 0 到 -(1-ε) 沿實軸, 然後從 -(1-ε) 到 -φ 沿實軸

# 實際上, 0 到 -1 之間嘅勢能:
print(f"\n  第二段: 0 → -1 (實軸, 接近奇點)")
for x in [0, -0.2, -0.5, -0.8, -0.9, -0.95, -0.99]:
    v = x**2/2 - math.log(abs(x+1)) + const
    print(f"  V({x:6.2f}) = {v:.4f}")

print(f"  勢能在 C=-1 處發散到 ∞")
print(f"  必須繞過奇點")

# 複數路徑: 0 → -φ, 繞過 C=-1 上半平面
# 參數化: C(t) = -t×φ + (1-t)×0, 但繞過 C=-1
# 路徑: 0 → -0.5 (實軸) → 繞過 -1 上半圓 → -1.5 (實軸) → -1.618 (實軸)

def path_segment(t, r=0.1):
    """分段路徑: 0 → -φ, 繞過 C=-1"""
    # t: 0 → 1
    # 0 → -0.9: 實軸
    if t < 0.55:
        t2 = t / 0.55
        x = -0.9 * t2
        return complex(x, 0)
    # -0.9 → -1.1: 半圓繞過 -1
    elif t < 0.65:
        t2 = (t - 0.55) / 0.1
        angle = math.pi * t2
        x = -1 + r * math.cos(angle)
        y = r * math.sin(angle)
        return complex(x, y)
    # -1.1 → -φ: 實軸
    else:
        t2 = (t - 0.65) / 0.35
        x = -1.1 + (-PHI + 1.1) * t2
        return complex(x, 0)

# 計算 action
print(f"\n  複數路徑 action (繞過奇點):")
for r in [0.01, 0.05, 0.1, 0.2, 0.5]:
    N = 10000
    S_path = 0.0
    for i in range(N+1):
        t = i / N
        C = path_segment(t, r)
        V_val = V_complex(C)
        sqrt_2V = cmath.sqrt(2 * V_val)
        # 數值微分
        dt = 1/N
        C_next = path_segment(t + dt, r) if t < 1 else C
        dC_dt = (C_next - C) / dt
        
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S_path += w * sqrt_2V * dC_dt
    
    S_real = (S_path * (1/N) / 3).real
    
    # 總 action = S₁ + S₂
    S_total = S_1 + S_real
    t_cycle_44 = t_site * math.exp(44 * 2 * S_total)
    print(f"  r={r:<5.2f}: S₂={S_real:.6f}, S_total={S_total:.6f}, 44×2S={44*2*S_total:.4f}, t_cycle={t_cycle_44:.4e} Gyr")

# ================================================================
# 4. 直接穿隧到 -φ (完整路徑)
# ================================================================
print(f"\n{'─'*80}")
print("  4. 完整路徑 φ⁻¹ → -φ (單一路徑)")
print(f"{'─'*80}")

# 完整路徑: φ⁻¹ → 0 (實軸) → 繞過 -1 → -φ (實軸)
# 用單一參數化

def full_path(t, r=0.1):
    """完整路徑: φ⁻¹ → -φ, 繞過 C=-1"""
    # 先歸一化到 [0,1]
    # φ⁻¹ → 0: t 0→0.35
    # 0 → 繞過 -1: t 0.35→0.45
    # 繞過 → -φ: t 0.45→1.0
    
    # 重新映射
    # 實際距離: φ⁻¹到0 = 0.618, 0到-φ = 1.618
    # 繞過部分佔 0.1
    
    # 第一段: φ⁻¹ → 0 (實軸)
    if t < 0.35:
        t2 = t / 0.35
        x = PHI_INV * (1 - t2)
        return complex(x, 0)
    # 第二段: 0 → -0.9 (實軸, 接近奇點)
    elif t < 0.45:
        t2 = (t - 0.35) / 0.1
        x = -0.9 * t2
        return complex(x, 0)
    # 第三段: 繞過 -1 (半圓)
    elif t < 0.55:
        t2 = (t - 0.45) / 0.1
        angle = math.pi * t2
        x = -1 + r * math.cos(angle)
        y = r * math.sin(angle)
        return complex(x, y)
    # 第四段: -1.1 → -φ (實軸)
    else:
        t2 = (t - 0.55) / 0.45
        x = -1.1 + (-PHI + 1.1) * t2
        return complex(x, 0)

print(f"  完整路徑 φ⁻¹ → -φ:")
for r in [0.01, 0.05, 0.1, 0.2, 0.5]:
    N = 20000
    S_path = 0.0
    for i in range(N+1):
        t = i / N
        C = full_path(t, r)
        V_val = V_complex(C)
        if abs(V_val) < 1e-15: V_val = complex(0, 0)
        sqrt_2V = cmath.sqrt(2 * V_val)
        
        dt = 1/N
        C_next = full_path(min(t + dt, 1.0), r)
        dC_dt = (C_next - C) / dt
        
        w = 1 if i == 0 or i == N else (4 if i % 2 == 1 else 2)
        S_path += w * sqrt_2V * dC_dt
    
    S_real = (S_path * (1/N) / 3).real
    
    t_cycle_44 = t_site * math.exp(44 * 2 * S_real)
    print(f"  r={r:<5.2f}: S_total={S_real:.6f}, 44×2S={44*2*S_real:.4f}, t_cycle={t_cycle_44:.4e} Gyr")

# ================================================================
# 5. 結論
# ================================================================
print(f"\n{'─'*80}")
print("  5. 結論")
print(f"{'─'*80}")

print(f"""
  舊計算 (只到 C=0): 2S = 20.34, t = 2.09 × 10⁸ Gyr
  新計算 (到 C=-φ):  2S >> 20.34, t >> 2.09 × 10⁸ Gyr
  
  關鍵: 逃離吸引子需要 C < -1, 唔係 C = 0
  路徑必須繞過奇點 C=-1, action 大幅增加
  
  但複數路徑積分有數值不穩定性 (奇點附近)
  需要更精確嘅 instanton 計算
  
  粗略估計:
  S_φ⁻¹→-φ ≈ S_φ⁻¹→0 + S_0→-φ
  S_0→-φ > S_φ⁻¹→0 因為勢壘高 6 倍
  總 action 可能 ~2-3× S_φ⁻¹→0
  
  44-site 集體穿隧到 C=-φ:
  t_cycle ≈ τ₀ × exp(44 × 2 × 3 × S_single)
          = τ₀ × exp(44 × 2 × 3 × 0.231)
          = τ₀ × exp(61.0)
          = 0.306 × 1.3 × 10²⁶
          = 4.0 × 10²⁵ Gyr
  
  但呢個估算好粗糙, 需要完整 instanton 解。
""")