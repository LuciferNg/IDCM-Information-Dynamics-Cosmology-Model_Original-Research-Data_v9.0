#!/usr/bin/env python3
"""Check Bagpipes filter API"""
import bagpipes as pipes
import warnings
warnings.filterwarnings("ignore")

# List filter-related attributes
filt_attrs = [a for a in dir(pipes.filters) if not a.startswith('_')]
print("filter attributes:", filt_attrs)

# Check if there's a filter reader
try:
    f = pipes.filters.Filter("JWST.NIRCam.F444W")
    print(f"\nF444W filter: {f.transmission_table}")
except Exception as e:
    print(f"\nFilter error: {e}")

# Try to list filters
try:
    flist = pipes.filters.list_filters()
    print(f"\nlist_filters: {flist[:10]}...")
except Exception as e:
    print(f"\nlist_filters error: {e}")

# Try different filter naming
for name in ["JWST.NIRCam.F444W", "jwst_nircam_f444w", "nircam_f444w", "nircam_f444w"]:
    try:
        f = pipes.filters.Filter(name)
        print(f"\n'{name}' works!")
        break
    except:
        pass