#!/usr/bin/env python3
"""
Bagpipes SED fitting for CEERS z≈8.2 galaxies
=============================================
Check if P(z) posterior has secondary peak at z=6.9 (Fibonacci aliasing)

Targets: Galaxy 2859 (z=8.106) and Galaxy 13050 (z=8.137)
"""
import numpy as np
import bagpipes as pipes
import json, os, warnings
warnings.filterwarnings("ignore")

print("=" * 72)
print("  Bagpipes SED Fitting — CEERS z≈8.2 Aliasing Test")
print("=" * 72)

# ══════════════════════════════════════════════════════════════════
# Check available filters
# ══════════════════════════════════════════════════════════════════
print("\n  Checking available filters...")
try:
    filter_set = pipes.filters.filter_set
    print(f"  Available filter sets: {len(filter_set)}")
    # List NIRCam filters
    for f in sorted(filter_set.keys()):
        if any(x in f.lower() for x in ['f435', 'f606', 'f814', 'f115', 'f150', 'f200', 'f277', 'f356', 'f410', 'f444', 'acs', 'wfc3', 'wasp']):
            print(f"    {f}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 72)
print("  DONE")
print("=" * 72)