#!/usr/bin/env python3
"""
Download NIRCam filter transmission curves from SVO Filter Profile Service
"""
import urllib.request, os, sys

filter_dir = os.path.expanduser("~/IDCM/sync_bump_analysis/filters")
os.makedirs(filter_dir, exist_ok=True)

# NIRCam filters from CEERS catalog
filters = {
    "F115W": "JWST.NIRCam.F115W",
    "F150W": "JWST.NIRCam.F150W", 
    "F200W": "JWST.NIRCam.F200W",
    "F277W": "JWST.NIRCam.F277W",
    "F356W": "JWST.NIRCam.F356W",
    "F410M": "JWST.NIRCam.F410M",
    "F444W": "JWST.NIRCam.F444W",
}

# Also HST filters
filters.update({
    "F435W": "HST.ACS.WFC.F435W",
    "F606W": "HST.ACS.WFC.F606W",
    "F814W": "HST.ACS.WFC.F814W",
})

for short, full in filters.items():
    url = f"http://svo2.cab.inta-csic.es/svo/theory/fps/getdata.php?format=ascii&id={full}"
    outpath = os.path.join(filter_dir, f"{short}.dat")
    print(f"Downloading {short} ({full})...", end=" ")
    try:
        urllib.request.urlretrieve(url, outpath)
        lines = open(outpath).read().strip().split("\n")
        # Remove header (lines starting with #)
        data_lines = [l for l in lines if not l.startswith("#") and l.strip()]
        print(f"{len(data_lines)} points")
    except Exception as e:
        print(f"FAILED: {e}")

print(f"\nDone. Filters saved to {filter_dir}/")
print("Files:", os.listdir(filter_dir))