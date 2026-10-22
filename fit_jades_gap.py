#!/usr/bin/env python3
"""JADES 低 z (0.5-3) 光譜獨立擬合 — 填 gap 用"""
import os, glob, json
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

LINES = {
    'O2_3727': 0.37270, 'Ne3_3869': 0.38690, 'HB_4861': 0.48610,
    'O3_4959': 0.49590, 'O3_5007': 0.50070, 'HA_6563': 0.65630,
    'N2_6584': 0.65840, 'S2_6717': 0.67170, 'S2_6731': 0.67310,
}

def fit_line(wl, flux, err, z, line_rest, half_width=0.05):
    line_obs = line_rest * (1 + z)
    m = (wl > line_obs - half_width) & (wl < line_obs + half_width)
    if np.sum(m) < 10:
        return np.nan, np.nan, False
    x, y, e = wl[m], flux[m], err[m]
    left = (wl > line_obs - 0.15) & (wl < line_obs - 0.05)
    right = (wl > line_obs + 0.05) & (wl < line_obs + 0.15)
    cont_vals = np.concatenate([flux[left], flux[right]])
    if len(cont_vals) < 8:
        return np.nan, np.nan, False
    cont = np.median(cont_vals)
    noise = 1.4826 * np.median(np.abs(cont_vals - np.median(cont_vals)))
    if noise <= 0:
        noise = np.std(cont_vals)
    y_sub = y - cont
    peak_idx = np.argmax(y_sub)
    if y_sub[peak_idx] <= 0:
        return np.nan, cont, False
    amp0 = y_sub[peak_idx]
    sigma0 = max(0.002, min(0.01, np.abs(x[peak_idx] - line_obs)))
    try:
        def gauss_fixed(xx, a, s, c):
            return c + a * np.exp(-(xx - line_obs)**2 / (2*s**2))
        popt, _ = curve_fit(gauss_fixed, x, y, p0=[amp0, sigma0, cont],
                            sigma=e, bounds=([-np.inf, 0.001, -np.inf], [np.inf, 0.05, np.inf]),
                            maxfev=5000)
        a, s, c = popt
        flux_line = a * (s * 10000) * np.sqrt(2*np.pi)
        snr = a / noise
        det = (snr > 3) and (a > 0)
        return flux_line, cont, det
    except Exception:
        return np.nan, cont, False

def process_spectrum(path, z):
    try:
        f = fits.open(path)
        d = f['EXTRACT1D'].data
        wl, flux, err = d['WAVELENGTH'], d['FLUX'], d['FLUX_ERR']
        f.close()
    except Exception:
        return None
    if wl is None or len(wl) < 100:
        return None
    g = np.isfinite(flux) & np.isfinite(err) & (err > 0)
    if np.sum(g) < 200:
        return None
    wl, flux, err = wl[g], flux[g], err[g]
    result = {'z': z, 'path': os.path.basename(path)}
    for name, rest in LINES.items():
        fl, cont, det = fit_line(wl, flux, err, z, rest)
        result[name + '_flux'] = fl
        result[name + '_cont'] = cont
        result[name + '_det'] = det
    return result

def main():
    outdir = '/tmp/jades_gap_spec'
    manifest = {}
    with open('/tmp/jades_gap_manifest.txt') as fh:
        for line in fh:
            p = line.strip().split('\t')
            if len(p) == 3:
                manifest[os.path.basename(p[2])] = float(p[1])

    files = sorted([f for f in os.listdir(outdir) if f.endswith('.fits')])
    print(f"Found {len(files)} JADES gap spectra")

    results = []
    for fname in files:
        z = manifest.get(fname, np.nan)
        if np.isnan(z):
            continue
        r = process_spectrum(os.path.join(outdir, fname), z)
        if r:
            results.append(r)

    print(f"Processed {len(results)}")
    for ln in ['HB_4861', 'O3_5007', 'HA_6563', 'O2_3727']:
        n = sum(1 for r in results if r[ln + '_det'])
        print(f"  {ln}: {n}/{len(results)}")

    with open('/home/wsl/IDCM/jades_gap_fit.json', 'w') as fh:
        json.dump(results, fh, indent=1, default=str)
    print("Saved /home/wsl/IDCM/jades_gap_fit.json")

if __name__ == '__main__':
    main()