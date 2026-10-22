#!/usr/bin/env python3
"""BOSS 光譜獨立擬合 — 用 COADD，同 SDSS 相同方法"""
import os, json
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

LINES = {
    'O2_3727': 0.37270, 'HB_4861': 0.48610, 'O3_4959': 0.49590,
    'O3_5007': 0.50070, 'HA_6563': 0.65630, 'N2_6584': 0.65840,
}

def fit_line(wl, flux, err, z, line_rest, half_width=0.005):
    line_obs = line_rest * (1 + z)
    m = (wl > line_obs - half_width) & (wl < line_obs + half_width)
    if np.sum(m) < 10:
        return np.nan, np.nan, False
    x, y, e = wl[m], flux[m], err[m]
    left = (wl > line_obs - 3*half_width) & (wl < line_obs - half_width)
    right = (wl > line_obs + half_width) & (wl < line_obs + 3*half_width)
    cont_vals = np.concatenate([flux[left], flux[right]])
    if len(cont_vals) < 10:
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
    sigma0 = max(0.0005, min(0.002, np.abs(x[peak_idx] - line_obs)))
    try:
        def gauss_fixed(xx, a, s, c):
            return c + a * np.exp(-(xx - line_obs)**2 / (2*s**2))
        popt, _ = curve_fit(gauss_fixed, x, y, p0=[amp0, sigma0, cont],
                            sigma=e, bounds=([-np.inf, 0.0002, -np.inf], [np.inf, 0.005, np.inf]),
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
        # BOSS lite 光譜可能用 COADD 或 FLUX/LOGLAM columns
        names = [h.name for h in f]
        if 'COADD' in names:
            d = f['COADD'].data
            lam = 10**d['loglam']
            flux = d['flux']
            ivar = d['ivar']
        else:
            d = f[1].data
            cols = d.columns.names
            if 'loglam' in cols:
                lam = 10**d['loglam']
                flux = d['flux']
                ivar = d['ivar']
            else:
                return None
        f.close()
    except Exception:
        return None
    wl = lam / 10000.0
    err = np.where(ivar > 0, 1.0/np.sqrt(ivar), np.nan)
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
    outdir = '/home/wsl/IDCM/data/boss_spec'
    manifest = {}
    with open('/tmp/boss_download_manifest.txt') as fh:
        for line in fh:
            p = line.strip().split('\t')
            if len(p) == 5:
                manifest[f"spec-{p[0]}-{p[1]}-{int(p[2]):04d}.fits"] = float(p[3])

    files = sorted([f for f in os.listdir(outdir) if f.endswith('.fits')])
    print(f"Found {len(files)} BOSS spectra")

    results = []
    for i, fname in enumerate(files):
        z = manifest.get(fname, np.nan)
        if np.isnan(z):
            continue
        r = process_spectrum(os.path.join(outdir, fname), z)
        if r:
            results.append(r)
        if (i+1) % 500 == 0:
            print(f"  {i+1}/{len(files)} ({len(results)} ok)", flush=True)

    print(f"\nProcessed {len(results)}")
    for ln in ['HB_4861', 'O3_5007', 'HA_6563', 'N2_6584']:
        n = sum(1 for r in results if r[ln + '_det'])
        print(f"  {ln}: {n}/{len(results)}")

    with open('/home/wsl/IDCM/boss_fit.json', 'w') as fh:
        json.dump(results, fh, indent=1, default=str)
    print("Saved /home/wsl/IDCM/boss_fit.json")

if __name__ == '__main__':
    main()