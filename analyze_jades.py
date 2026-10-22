#!/usr/bin/env python3
"""Analyze JADES H-beta detections at high z"""
import numpy as np
from astropy.io import fits

p = fits.open('/tmp/jades_prism_line.fits')[1].data
g = fits.open('/tmp/jades_grating_line.fits')[1].data

print('=== JADES PRISM ===')
print(f'Total: {len(p)}')
zspec = p['z_Spec']
hb = p['HB_4861_flux']
hb_err = p['HB_4861_err']
good = (zspec > 0) & (hb > 0) & (hb_err > 0) & ((hb/hb_err) > 3)
print(f'z_Spec>0: {np.sum(zspec>0)}')
print(f'Hb S/N>3: {np.sum(good)}')
if np.sum(good) > 0:
    print(f'z range: {zspec[good].min():.2f} - {zspec[good].max():.2f}')
    print(f'median z: {np.median(zspec[good]):.2f}')
    print()
    print('Hb detections by redshift:')
    for z_lo, z_hi in [(0,2),(2,4),(4,5),(5,6),(6,8),(8,12)]:
        sel = good & (zspec>=z_lo) & (zspec<z_hi)
        if np.sum(sel)>0:
            print(f'  z={z_lo}-{z_hi}: n={np.sum(sel)}, median Hb flux={np.median(hb[sel]):.1f}')

print()
print('=== JADES GRATING ===')
print(f'Total: {len(g)}')
gz = g['z_Spec']
ghb = g['HB_4861_flux']
ghb_err = g['HB_4861_err']
good_g = (gz > 0) & (ghb > 0) & (ghb_err > 0) & ((ghb/ghb_err) > 3)
print(f'z_Spec>0: {np.sum(gz>0)}')
print(f'Hb S/N>3: {np.sum(good_g)}')
if np.sum(good_g) > 0:
    print(f'z range: {gz[good_g].min():.2f} - {gz[good_g].max():.2f}')
    print(f'median z: {np.median(gz[good_g]):.2f}')
    print()
    print('Hb detections by redshift:')
    for z_lo, z_hi in [(0,2),(2,4),(4,5),(5,6),(6,8),(8,12)]:
        sel = good_g & (gz>=z_lo) & (gz<z_hi)
        if np.sum(sel)>0:
            print(f'  z={z_lo}-{z_hi}: n={np.sum(sel)}, median Hb flux={np.median(ghb[sel]):.1f}')