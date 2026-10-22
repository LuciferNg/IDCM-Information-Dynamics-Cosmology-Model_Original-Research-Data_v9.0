"""Additional checks for the φ-ratio analysis."""
from astropy.io import fits
import numpy as np

with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    data = hdul[2].data

z = data['z_PRISM']
mask = np.isfinite(z) & (z > 0) & (z < 15)
z = z[mask]

# Check wider bins around the φ-ratio pair
print("=== WIDER BIN INTEGRATION ===")
# Check various window widths around 5.6 and 6.9
for half_width in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5]:
    mask56 = np.abs(z - 5.6) < half_width
    mask69 = np.abs(z - 6.9) < half_width
    n56 = mask56.sum()
    n69 = mask69.sum()
    ratio = n69 / n56 if n56 > 0 else 0
    print(f"  ±{half_width:.2f}: N(5.6)={n56:>4d}, N(6.9)={n69:>4d}, ratio={ratio:.4f}")

# Check the peak regions (nearest peaks)
print(f"\n=== PEAK REGION INTEGRATION ===")
# z=5.55 peak: count=32, check the range around it
for half_width in [0.05, 0.1, 0.15, 0.2, 0.25]:
    mask55 = np.abs(z - 5.55) < half_width
    mask67 = np.abs(z - 6.75) < half_width
    n55 = mask55.sum()
    n67 = mask67.sum()
    ratio = n67 / n55 if n55 > 0 else 0
    # Also check z=5.95 peak (next one)
    mask60 = np.abs(z - 5.95) < half_width
    n60 = mask60.sum()
    print(f"  ±{half_width:.2f}: N(5.55)={n55:>4d}, N(6.75)={n67:>4d}, N(5.95)={n60:>4d}, "
          f"ratio(6.75/5.55)={ratio:.4f}")

# Check the specific φ-ratio claim: 6.9/5.6 = 1.232, not 1.685
# But 1.685 = 5.6 * 0.301 ... no
# Let's check: what z-values give a ratio of 1.685?
print(f"\n=== φ-RATIO INVESTIGATION ===")
print(f"6.9/5.6 = {6.9/5.6:.6f}")
print(f"φ = 1.618034")
print(f"Deviation: {(6.9/5.6 - 1.618034)/1.618034*100:.2f}%")

# Check if the ratio 1.685 refers to something else
# Maybe it's the cumulative count ratio in a wider window?
for half_width in [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1.0]:
    mask56 = np.abs(z - 5.6) < half_width
    mask69 = np.abs(z - 6.9) < half_width
    n56 = mask56.sum()
    n69 = mask69.sum()
    # Check if ratio is close to 1.685
    if n56 > 0:
        ratio = n69 / n56
        ratio_inv = n56 / n69 if n69 > 0 else 0
        print(f"  ±{half_width:.2f}: N(5.6)={n56:>4d}, N(6.9)={n69:>4d}, "
              f"r=N(6.9)/N(5.6)={ratio:.4f}, N(5.6)/N(6.9)={ratio_inv:.4f}")

# Check 1.685 possibility: is it (1+z) ratio?
print(f"\n(1+6.9)/(1+5.6) = {(1+6.9)/(1+5.6):.6f}")
print(f"(1+6.9)/(1+5.6) vs φ: {(1+6.9)/(1+5.6)/1.618034:.4f}")

# Check if 1.685 is the ratio of dV/dz volumes
print(f"\n=== VOLUME RATIO CHECK ===")
from scipy.integrate import quad
Omega_m = 0.315
Omega_L = 0.685
H0 = 67.4
c = 3e5

def dV_dz(z):
    dc, _ = quad(lambda zp: c / (H0 * np.sqrt(Omega_m*(1+zp)**3 + Omega_L)), 0, z)
    E_z = np.sqrt(Omega_m * (1+z)**3 + Omega_L)
    return c / H0 * dc**2 / E_z

v56 = dV_dz(5.6)
v69 = dV_dz(6.9)
print(f"dV/dz(5.6) = {v56:.2e}")
print(f"dV/dz(6.9) = {v69:.2e}")
print(f"dV/dz(6.9)/dV/dz(5.6) = {v69/v56:.4f}")
print(f"dV/dz(5.6)/dV/dz(6.9) = {v56/v69:.4f}")

# What about comoving volume integrated from z=0 to z?
def V_comoving(z_max):
    V, _ = quad(lambda zp: dV_dz(zp), 0, z_max)
    return V

V56 = V_comoving(5.6)
V69 = V_comoving(6.9)
print(f"\nIntegral V(0-5.6) = {V56:.2e}")
print(f"Integral V(0-6.9) = {V69:.2e}")
print(f"V(0-6.9)/V(0-5.6) = {V69/V56:.4f}")

# What about the ratio of the actual number counts?
print(f"\n=== ACTUAL NUMBER COUNTS ===")
# Total counts z>5.5 vs z>6.8
n_gt_55 = (z > 5.5).sum()
n_gt_68 = (z > 6.8).sum()
print(f"z > 5.5: {n_gt_55}")
print(f"z > 6.8: {n_gt_68}")
print(f"Ratio: {n_gt_68/n_gt_55:.4f}")

# Maybe the φ-ratio refers to z=4.1 and z=6.9?
# 6.9/4.1 = 1.683
print(f"\n=== CHECK: 6.9/4.1 = {6.9/4.1:.6f} vs φ = {1.618034:.6f} ===")
# Check if z=4.1 is a peak
mask41 = np.abs(z - 4.1) < 0.05
print(f"Count at z=4.1±0.05: {mask41.sum()}")

# What about 5.6 * φ = 9.06?
print(f"\n5.6 * φ = {5.6*1.618034:.4f}")
# Check if there's a peak there
mask906 = np.abs(z - 9.06) < 0.1
print(f"Count at z=9.06±0.1: {mask906.sum()}")

# Maybe the φ-ratio is about the ratio of two different peaks in the distribution?
# Let me list all pairs of peaks that are close to φ
from scipy.signal import find_peaks
bins = np.arange(0, 15.1, 0.1)
counts, _ = np.histogram(z, bins=bins)
bin_centers = (bins[:-1] + bins[1:]) / 2
peaks, _ = find_peaks(counts, prominence=1, width=1)
peak_zs = bin_centers[peaks]
peak_counts = counts[peaks]

print(f"\n=== PEAK PAIRS NEAR φ RATIO ===")
for i, z1 in enumerate(peak_zs):
    for j, z2 in enumerate(peak_zs):
        if j > i and z2 > 0 and z1 > 0:
            ratio = z2 / z1 if z2 > z1 else z1 / z2
            if abs(ratio / 1.618034 - 1) < 0.05:
                print(f"  z={z1:.2f} ({peak_counts[i]:>4d}) and z={z2:.2f} ({peak_counts[j]:>4d}): "
                      f"ratio={ratio:.4f} vs φ={1.618034:.4f} ({abs(ratio/1.618034-1)*100:.2f}% diff)")

# Final check: the actual φ-ratio claim
# Let me check if the number 1.685 appears in the HDU 1 (Obs_info) data
print(f"\n=== CHECKING OBS_INFO FOR φ-RELATED DATA ===")
with fits.open('jades_dr4_spectroscopic.fits') as hdul:
    if len(hdul) > 1:
        obs = hdul[1].data
        print(f"Obs_info columns: {obs.columns.names}")
        # Check z_phot, z_Spec, z_paper
        if 'z_phot' in obs.columns.names:
            zp = obs['z_phot']
            mask_zp = np.isfinite(zp) & (zp > 0) & (zp < 15)
            print(f"z_phot valid: {mask_zp.sum()}")
            zp_bins = np.arange(0, 15.1, 0.1)
            zp_counts, _ = np.histogram(zp[mask_zp], bins=zp_bins)
            zp_peaks, _ = find_peaks(zp_counts, prominence=1, width=1)
            print(f"z_phot peaks: {len(zp_peaks)}")
            for pz in sorted(bin_centers[zp_peaks]):
                if pz > 4:
                    pi = np.where(bin_centers == pz)[0][0]
                    print(f"  z={pz:.2f} (count={zp_counts[pi]})")