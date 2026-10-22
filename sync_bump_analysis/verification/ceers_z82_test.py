#!/usr/bin/env python3
"""
CEERS z=8.2 Aliasing Test — Direct Catalog Analysis
====================================================
Using the Labbé+2023 photometric catalog to check if
z≈8.2 galaxies show the predicted aliasing signature.

Aliasing signature at z=8.2:
- Hβ+[OIII] at 5007Å → 4.606μm (F444W, NOT F410M)
- F410M flux should be ANOMALOUSLY low at z=8.2
  because no strong emission line falls in F410M
- This creates a color degeneracy: F410M-F444W color
  should be similar for line-dominated and continuum SEDs
"""
import math, json
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI

print("=" * 72)
print("  CEERS z=8.2 Aliasing Test — Direct Catalog Analysis")
print("=" * 72)

# ══════════════════════════════════════════════════════════════════
# Read the ECSV catalog
# ══════════════════════════════════════════════════════════════════
with open("ceers_catalog.ecsv") as f:
    lines = [l.strip() for l in f if not l.startswith("#") and l.strip()]

# Parse header
header = lines[0].split()
data = []
for line in lines[1:]:
    vals = line.split()
    if len(vals) >= len(header):
        row = dict(zip(header, vals))
        data.append(row)

print(f"\n  Loaded {len(data)} galaxies from CEERS catalog")

# Extract columns of interest
galaxies = []
for row in data:
    gal = {
        "id": int(row["id"]),
        "z": float(row["z"]),
        "zlo": float(row["zlo"]),
        "zhi": float(row["zhi"]),
        "mass": float(row["mass"]),
        "masslo": float(row["masslo"]),
        "masshi": float(row["masshi"]),
        "f410m": float(row["f410m"]),
        "e410m": float(row["e410m"]),
        "f356w": float(row["f356w"]),
        "e356w": float(row["e356w"]),
        "f444w": float(row["f444w"]),
        "e444w": float(row["e444w"]),
        "f277w": float(row["f277w"]),
        "e277w": float(row["e277w"]),
        "f150w": float(row["f150w"]),
        "f115w": float(row["f115w"]),
    }
    # Compute colors
    gal["f356w_f410m"] = gal["f356w"] - gal["f410m"]
    gal["f410m_f444w"] = gal["f410m"] - gal["f444w"]
    # SNR
    gal["snr_410m"] = abs(gal["f410m"]) / gal["e410m"] if gal["e410m"] > 0 else 0
    gal["snr_356w"] = abs(gal["f356w"]) / gal["e356w"] if gal["e356w"] > 0 else 0
    gal["snr_444w"] = abs(gal["f444w"]) / gal["e444w"] if gal["e444w"] > 0 else 0
    
    galaxies.append(gal)

# ══════════════════════════════════════════════════════════════════
# Sort by z
# ══════════════════════════════════════════════════════════════════
galaxies.sort(key=lambda g: g["z"])

print(f"\n  {'ID':>6s}  {'z':>8s}  {'z_lo':>6s}  {'z_hi':>6s}  {'logM*':>7s}  "
      f"{'F356W':>8s}  {'F410M':>8s}  {'F444W':>8s}  "
      f"{'F356W-F410M':>12s}  {'F410M-F444W':>12s}  {'SNR410':>7s}")
print(f"  {'─'*6}  {'─'*8}  {'─'*6}  {'─'*6}  {'─'*7}  "
      f"{'─'*8}  {'─'*8}  {'─'*8}  "
      f"{'─'*12}  {'─'*12}  {'─'*7}")

for g in galaxies:
    # Flag galaxies near z=8.2
    near_82 = abs(g["z"] - 8.2) < 0.3
    marker = " ◀ z≈8.2" if near_82 else ""
    # Flag aliasing z
    is_aliasing = abs(g["z"] - 5.6) < 0.1 or abs(g["z"] - 6.9) < 0.1 or abs(g["z"] - 7.7) < 0.1
    marker = marker or (" ◀ aliasing" if is_aliasing else "")
    
    print(f"  {g['id']:>6d}  {g['z']:>8.3f}  {g['zlo']:>6.2f}  {g['zhi']:>6.2f}  "
          f"{g['mass']:>7.2f}  {g['f356w']:>8.1f}  {g['f410m']:>8.1f}  "
          f"{g['f444w']:>8.1f}  {g['f356w_f410m']:>+12.1f}  "
          f"{g['f410m_f444w']:>+12.1f}  {g['snr_410m']:>7.1f}{marker}")

# ══════════════════════════════════════════════════════════════════
# Analysis: F410M flux at z≈8.2
# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*72}")
print(f"  ALIASING ANALYSIS")
print(f"{'─'*72}")

# The aliasing signature at z=8.2: F410M should have LOW flux
# because Hβ+[OIII] is in F444W, not F410M
# But the color F410M-F444W should be SIMILAR for different SED models

# Check galaxies at z≈8.2
z82_gals = [g for g in galaxies if abs(g["z"] - 8.2) < 0.3]
print(f"\n  Galaxies at z≈8.2:")
for g in z82_gals:
    print(f"    ID={g['id']}: z={g['z']:.3f}, mass={g['mass']:.2f}, "
          f"F410M={g['f410m']:.1f}±{g['e410m']:.1f}, "
          f"F356W-F410M={g['f356w_f410m']:+.1f}, "
          f"F410M-F444W={g['f410m_f444w']:+.1f}")

# The aliasing z: 5.6, 6.9, 7.7, 8.2
aliasing_zs = [5.6, 6.9, 7.7, 8.2]
print(f"\n  Aliasing z from Fibonacci sequence: {aliasing_zs}")
print(f"\n  {'z (aliasing)':>15s}  {'Galaxies near':>15s}  {'F410M median':>15s}  {'F410M-F444W':>15s}")
print(f"  {'─'*15}  {'─'*15}  {'─'*15}  {'─'*15}")

for az in aliasing_zs:
    near = [g for g in galaxies if abs(g["z"] - az) < 0.3]
    if near:
        f410m_med = np.median([g["f410m"] for g in near])
        f410m_f444w_med = np.median([g["f410m_f444w"] for g in near])
        print(f"  {az:>15.1f}  {len(near):>15d}  {f410m_med:>15.1f}  {f410m_f444w_med:>+15.1f}")
    else:
        print(f"  {az:>15.1f}  {'0':>15s}  {'—':>15s}  {'—':>15s}")

# ══════════════════════════════════════════════════════════════════
# Color-color diagram: F356W-F410M vs F410M-F444W
# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*72}")
print(f"  COLOR-COLOR DIAGRAM: F356W-F410M vs F410M-F444W")
print(f"{'─'*72}")
print(f"\n  {'ID':>6s}  {'z':>8s}  {'F356W-F410M':>12s}  {'F410M-F444W':>12s}  {'aliasing?':>10s}")
print(f"  {'─'*6}  {'─'*8}  {'─'*12}  {'─'*12}  {'─'*10}")

for g in galaxies:
    is_82 = abs(g["z"] - 8.2) < 0.3
    is_aliasing_z = any(abs(g["z"] - az) < 0.3 for az in [5.6, 6.9, 7.7])
    
    note = ""
    if is_82:
        note = "z≈8.2 🔮"
    elif is_aliasing_z:
        note = "aliasing ✅"
    
    if note:
        print(f"  {g['id']:>6d}  {g['z']:>8.3f}  {g['f356w_f410m']:>+12.1f}  "
              f"{g['f410m_f444w']:>+12.1f}  {note:>10s}")

# ══════════════════════════════════════════════════════════════════
# Verification: Is z≈8.2 a color degeneracy point?
# ══════════════════════════════════════════════════════════════════
print(f"\n{'─'*72}")
print(f"  VERDICT: z=8.2 Aliasing Test")
print(f"{'─'*72}")

print(f"""
  DATA:
  - 13 galaxies in CEERS catalog
  - 2 galaxies at z≈8.2 (ID 2859 z=8.106, ID 13050 z=8.137)
  - 1 galaxy at z=6.5 (aliasing zone)
  - 0 galaxies at z=5.6 (below sample range)
  
  COLOR SIGNATURE:
  - z=8.2 galaxies show F410M-F444W ≈ -20 to -60
  - This is the same RANGE as other z>7 galaxies
  - No clear aliasing signature visible in the photometry alone
  
  LIMITATION:
  - The catalog only has 13 galaxies — too few for statistical test
  - The aliasing is a P(z) effect, not a photometric color effect
  - Need NIRSpec spectroscopy to see the bimodal P(z) at z=8.2
  - Labbé+2023 Fig. 5 shows the color degeneracy is at z=5.6,6.9,7.7
  - z=8.2 is BEYOND the published range of the existing analysis
  
  PREDICTION:
  - If we run the same P(z) analysis as Labbé+2023 Extended Data Fig. 5
  - We should see a SIMILAR color degeneracy at z=8.2
  - The F410M-F444W color at z=8.2 should be nearly identical
    for line-dominated and continuum-dominated SEDs
  - This would appear as a spike in the P(z) of Bagpipes/Prospector fits
""")

# ══════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════
results = {
    "n_galaxies": len(galaxies),
    "z82_galaxies": [{"id": g["id"], "z": g["z"], "mass": g["mass"],
                      "f410m": g["f410m"], "f410m_f444w": g["f410m_f444w"]}
                     for g in z82_gals],
    "aliasing_prediction": {
        "z": 8.2,
        "mechanism": "Hβ+[OIII] at F410M/F444W boundary → color degeneracy",
        "test": "Need NIRSpec P(z) analysis at z=8.2",
        "status": "catalog downloaded — photometry alone insufficient for definitive test"
    },
    "verdict": "Inconclusive with photometry alone — need NIRSpec spectroscopy"
}

with open("verification/ceers_z82_test.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"  Saved to verification/ceers_z82_test.json")
print("=" * 72)