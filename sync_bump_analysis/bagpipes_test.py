#!/usr/bin/env python3
"""
Bagpipes SED fitting for CEERS z≈8.2 galaxies
=============================================
Check if P(z) posterior has secondary peak at z=6.9 (Fibonacci aliasing)

Targets: Galaxy 2859 (z=8.106) and Galaxy 13050 (z=8.137)
"""
import numpy as np
import bagpipes as pipes
import json, os, warnings, sys
warnings.filterwarnings("ignore")

print("=" * 72)
print("  Bagpipes SED Fitting — CEERS z≈8.2 Aliasing Test")
print("=" * 72)

# ══════════════════════════════════════════════════════════════════
# Check available filters
# ══════════════════════════════════════════════════════════════════
print("\n  Checking available filters...")
filter_names = []
try:
    # Try to get filter list
    import bagpipes.filters as bf
    fs = bf.filter_set
    # Check get_photometry method
    print(f"  filter_set.get_photometry: {fs.get_photometry}")
    # Try to access filter names
    for attr in dir(fs):
        if not attr.startswith('_'):
            print(f"  filter_set.{attr}")
except Exception as e:
    print(f"  Error: {e}")

# Try pipes.filters.list_available_filters 
print("\n  Trying to list filters...")
try:
    import inspect
    src = inspect.getsource(pipes.filters)
    # Find filter names
    import re
    filters_found = re.findall(r'JWST\.NIRCam\.\w+', src)
    for f in sorted(set(filters_found)):
        print(f"    {f}")
    filters_found2 = re.findall(r'HST\.\w+\.\w+', src)
    for f in sorted(set(filters_found2)):
        print(f"    {f}")
except Exception as e:
    print(f"  Error: {e}")

# Try creating a galaxy
print("\n  Trying to create galaxy object...")
try:
    # Galaxy 2859 photometry in nJy
    # Convert to uJy (1 nJy = 0.001 uJy)
    flux_2859 = {
        "F435W": 2.58 * 0.001,
        "F606W": -1.52 * 0.001,
        "F814W": 3.88 * 0.001,
        "F115W": 10.02 * 0.001,
        "F150W": 15.37 * 0.001,
        "F200W": 11.85 * 0.001,
        "F277W": 14.94 * 0.001,
        "F356W": 52.42 * 0.001,
        "F410M": 63.28 * 0.001,
        "F444W": 124.94 * 0.001,
    }
    err_2859 = {
        "F435W": 3.73 * 0.001,
        "F606W": 4.19 * 0.001,
        "F814W": 4.78 * 0.001,
        "F115W": 2.85 * 0.001,
        "F150W": 3.80 * 0.001,
        "F200W": 3.60 * 0.001,
        "F277W": 2.79 * 0.001,
        "F356W": 2.24 * 0.001,
        "F410M": 6.01 * 0.001,
        "F444W": 3.50 * 0.001,
    }
    
    # Create galaxy object
    g = pipes.input.galaxy("2859", flux_2859, 8.106, err_2859)
    print(f"  Galaxy 2859 created: {g}")
    print(f"  Filters: {g.filter_list}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 72)
print("  DONE")
print("=" * 72)