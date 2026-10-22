from astropy.io import fits
import numpy as np

with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    data = hdul[2].data

z_flag = data['Z_FLAG']
z = data['z_PRISM']

# Show unique values
unique = np.unique(z_flag)
print(f"Z_FLAG unique values: {unique}")
print(f"Z_FLAG dtype: {z_flag.dtype}")
print(f"Z_FLAG sample: {z_flag[:10]}")

# Also check Unique_ID examples
uid = data['Unique_ID']
print(f"\nUnique_ID examples (first 5):")
for i in range(5):
    print(f"  {uid[i]}")

# Check z_PRISM stats
mask = np.isfinite(z) & (z > 0) & (z < 15)
print(f"\nz_PRISM valid range: {z[mask].min():.4f} to {z[mask].max():.4f}")
print(f"NaN count: {np.isnan(z).sum()}")

# Check what Z_FLAG values look like as strings
print(f"\nZ_FLAG as strings: {[str(x).strip() for x in z_flag[:20]]}")