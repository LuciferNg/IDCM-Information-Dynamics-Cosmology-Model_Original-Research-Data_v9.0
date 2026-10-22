#!/usr/bin/env python3
"""Check Bagpipes filter_set to find NIRCam filters"""
import bagpipes as pipes
import warnings
warnings.filterwarnings("ignore")

# Check filter_set
fs = pipes.filters.filter_set
print(f"filter_set type: {type(fs)}")

# Try to access as dict
try:
    keys = list(fs.keys())
    print(f"Total filters: {len(keys)}")
    # Search for NIRCam
    for k in keys:
        if 'nircam' in k.lower() or 'f444' in k.lower() or 'f356' in k.lower() or 'f410' in k.lower() or 'f277' in k.lower() or 'f200' in k.lower() or 'f150' in k.lower() or 'f115' in k.lower():
            print(f"  {k}")
except Exception as e:
    print(f"Keys error: {e}")
    # Try dir
    print(f"dir: {[a for a in dir(fs) if not a.startswith('_')][:20]}")