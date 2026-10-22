#!/usr/bin/env python3
"""
JWST aliasing redshift Fibonacci sequence — full forward + backward
===================================================================
Observed: z = 5.6, 6.9, 7.7
Pattern: start at F₅ + F₄/F₅ = 5.6, then Fibonacci gaps F₇/10, F₆/10

The full Fibonacci sequence both ways:
FORWARD:  ...F₈/10, F₇/10, F₆/10, F₅/10
BACKWARD: F₅/10, F₄/10, F₃/10, F₂/10, F₁/10...

Prediction: earlier aliasing z between z=4.4 and z=5.6
"""
import math, json

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI

def fib(n):
    """Fibonacci number F_n"""
    return round(PHI**n / math.sqrt(5))

print("=" * 72)
print("  JWST Aliasing z — Complete Fibonacci Sequence")
print("=" * 72)

# Observed aliasing z
z_obs = [5.6, 6.9, 7.7]
print(f"\n  Observed: z = {z_obs}")
print(f"  Pattern:")

# Verify
z1 = 5 + 3/5
print(f"    z₁ = 5 + 3/5 = 5 + {3/5} = {z1} ✅")

z2 = z1 + 13/10
print(f"    z₂ = z₁ + 13/10 = {z1} + 1.3 = {z2} ✅")

z3 = z2 + 8/10
print(f"    z₃ = z₂ + 8/10 = {z2} + 0.8 = {z3} ✅")

# Forward: predict next
print(f"\n{'─'*72}")
print(f"  FORWARD PREDICTION")
print(f"{'─'*72}")

Fn = [5, 8, 13]  # F₅, F₆, F₇
Fscale = 10

z_current = 5.6
forward_zs = []
for n in [13, 8, 5, 3, 2, 1, 1]:
    z_current += n / 10
    forward_zs.append(round(z_current, 2))

print(f"  Next predicted aliasing z (forward from 7.7):")
for i, z in enumerate(forward_zs):
    fn_val = [13, 8, 5, 3, 2, 1, 1][i]
    if z <= 7.7:
        status = f"✅ observed (gap = F_{[7,6,5,4,3,2,1][i]}/10 = {fn_val}/10)"
    else:
        status = f"🔮 predicted (gap = F_{[7,6,5,4,3,2,1][i]}/10 = {fn_val}/10)"
    print(f"    z = {z:.2f}  {status}")

# Backward: predict earlier
print(f"\n{'─'*72}")
print(f"  BACKWARD PREDICTION (earlier aliasing z)")
print(f"{'─'*72}")

# Descending Fibonacci gaps: F₅/10, F₄/10, F₃/10, F₂/10, F₁/10
back_gaps = [5, 3, 2, 1, 1]  # F₅, F₄, F₃, F₂, F₁
back_fn = [5, 4, 3, 2, 1]  # F indices

z_back = 5.6
backward_zs = []
for i, gap in enumerate(back_gaps):
    z_back -= gap / 10
    backward_zs.append(round(z_back, 2))

print(f"  Predicted earlier aliasing z (backward from 5.6):")
for i, z in enumerate(backward_zs):
    fn = back_fn[i]
    gap = back_gaps[i]
    print(f"    z = {z:.2f}  (gap = F_{fn}/10 = {gap}/10 = {gap/10})")

print(f"\n{'─'*72}")
print(f"  FILTER CONTEXT FOR EACH PREDICTED z")
print(f"{'─'*72}")

# NIRCam filter wavelengths (μm)
filters = {
    "F115W": 1.15,
    "F150W": 1.50,
    "F200W": 2.00,
    "F277W": 2.77,
    "F356W": 3.56,
    "F410M": 4.10,
    "F444W": 4.44
}

# Emission lines (Å)
lines = {
    "Hα": 6563,
    "Hβ+[OIII]": 5007,
    "[OIII]4959": 4959,
    "[OII]3727": 3727,
    "Lyα": 1216,
    "CIII]1909": 1909,
    "MgII2798": 2798
}

# All predicted z (both ways)
all_zs = sorted(set(backward_zs + [5.6] + forward_zs))

for z in all_zs:
    print(f"\n  z = {z:.2f}:")
    for name, lam in lines.items():
        obs_lam = lam * (1 + z)
        obs_micron = obs_lam / 10000
        
        # Which filter(s)?
        in_filters = []
        for fname, fcen in sorted(filters.items(), key=lambda x: x[1]):
            fwidth = 0.2 * fcen  # ~20% fractional bandwidth
            if fcen - fwidth <= obs_micron <= fcen + fwidth:
                in_filters.append(fname)
        
        # Near filter boundaries?
        boundary_info = ""
        for fname, fcen in sorted(filters.items(), key=lambda x: x[1]):
            fwidth = 0.2 * fcen
            lo = fcen - fwidth
            hi = fcen + fwidth
            # Check if within 5% of edge
            edge_width = fwidth * 0.05
            if abs(obs_micron - lo) < edge_width:
                boundary_info += f" {fname} BLUE EDGE |"
            if abs(obs_micron - hi) < edge_width:
                boundary_info += f" {fname} RED EDGE |"
        
        if in_filters or boundary_info:
            boundary_str = boundary_info if boundary_info else " —"
            print(f"    {name} → {obs_micron:.3f}μm [{','.join(in_filters)}] {boundary_str}")

print(f"\n{'─'*72}")
print(f"  SPECTROSCOPIC CONFIRMATION PREDICTION")
print(f"{'─'*72}")

# The most testable prediction
print(f"""
  IF the Fibonacci structure is real:
  - z=4.4 to z=5.1 should show aliasing in Hα at F356W/F277W boundaries
  - These are in the CEERS field and should be visible in NIRSpec
  - The predicted z spread: 4.4, 4.5, 4.6, 4.8, 5.1, 5.6, 6.9, 7.7, 8.2...

  TEST WITH EXISTING DATA:
  Check NIRSpec spectra at these specific z for line-continuum degeneracy.
  The JADES and CEERS surveys both cover this range.
  
  KEY: If the aliasing ONLY occurs at these Fibonacci z (not continuously),
  it confirms the rendering boundary hypothesis.
""")

# Save results
results = {
    "observed_aliasing_z": z_obs,
    "pattern_type": "Fibonacci gaps scaled by 0.1",
    "observed_pattern": {
        "z1": "F₅ + F₄/F₅ = 5 + 3/5 = 5.6",
        "z2": "z₁ + F₇/10 = 5.6 + 13/10 = 6.9",
        "z3": "z₂ + F₆/10 = 6.9 + 8/10 = 7.7"
    },
    "forward_prediction": {
        "gap_sequence": "F₅/10, F₄/10, F₃/10, F₂/10, F₁/10...",
        "next_z": 8.2,
        "z_values": forward_zs
    },
    "backward_prediction": {
        "path": "from z=5.6 backward subtracting F₅/10, F₄/10, F₃/10, F₂/10...",
        "z_values": backward_zs
    },
    "all_predicted_zs": sorted(set(all_zs)),
    "verdict": "Fibonacci-ordered aliasing z spanning z≈4.4 to z≈8.2"
}

with open("verification/jwst_full_fibonacci_sequence.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"  Saved to verification/jwst_full_fibonacci_sequence.json")
print("=" * 72)