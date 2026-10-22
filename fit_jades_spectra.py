#!/usr/bin/env python3
"""
獨立光譜擬合 v2：robust 線偵測 + 連續譜 noise 計 SNR
用 JADES x1d 原始光譜自己量發射線，同 catalog 對比 recovery rate
"""
import os, glob
import numpy as np
from astropy.io import fits
from scipy.optimize import curve_fit

LINES = {
    'O2_3727': 0.37270,
    'Ne3_3869': 0.38690,
    'HD_4102': 0.41020,
    'HG_4340': 0.43400,
    'O3_4363': 0.43630,
    'HB_4861': 0.48610,
    'O3_4959': 0.49590,
    'O3_5007': 0.50070,
    'He1_5875': 0.58750,
    'O1_6300': 0.63000,
    'HA_6563': 0.65630,
    'N2_6584': 0.65840,
    'S2_6717': 0.67170,
    'S2_6731': 0.67310,
}

def fit_line(wl, flux, err, z, line_rest, half_width=0.05):
    """fit 一條線，用連續譜 noise 計 SNR"""
    line_obs = line_rest * (1 + z)
    m = (wl > line_obs - half_width) & (wl < line_obs + half_width)
    if np.sum(m) < 10:
        return np.nan, np.nan, False
    x, y, e = wl[m], flux[m], err[m]
    # 連續譜：兩側 0.05-0.15 um
    left = (wl > line_obs - 0.15) & (wl < line_obs - 0.05)
    right = (wl > line_obs + 0.05) & (wl < line_obs + 0.15)
    cont_vals = np.concatenate([flux[left], flux[right]])
    if len(cont_vals) < 8:
        return np.nan, np.nan, False
    cont = np.median(cont_vals)
    # continuum noise = std of continuum region (robust)
    noise = 1.4826 * np.median(np.abs(cont_vals - np.median(cont_vals)))  # MAD->sigma
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
        popt, pcov = curve_fit(gauss_fixed, x, y, p0=[amp0, sigma0, cont],
                               sigma=e, bounds=([-np.inf, 0.001, -np.inf], [np.inf, 0.05, np.inf]),
                               maxfev=5000)
        a, s, c = popt
        # flux_line [erg/s/cm2] = amp[erg/s/cm2/AA] * sigma[AA] * sqrt(2pi)
        # s 係 micron，轉 Å: * 10000
        flux_line = a * (s * 10000) * np.sqrt(2*np.pi)
        # SNR using continuum noise (robust to low-SNR prism)
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
    outdir = '/tmp/jades_spec'
    manifest = {}
    with open('/tmp/jades_download_manifest.txt') as fh:
        for line in fh:
            p = line.strip().split('\t')
            if len(p) == 4:
                manifest[os.path.basename(p[3])] = float(p[1])

    files = sorted([f for f in os.listdir(outdir) if f.endswith('.fits')])
    print(f"Found {len(files)} spectra files")

    results = []
    for fname in files:
        z = manifest.get(fname, np.nan)
        if np.isnan(z):
            continue
        r = process_spectrum(os.path.join(outdir, fname), z)
        if r:
            results.append(r)

    print(f"Processed {len(results)} spectra")

    # 偵測統計
    for ln in ['HB_4861', 'O3_5007', 'HA_6563', 'O2_3727', 'O3_4959']:
        n = sum(1 for r in results if r[ln + '_det'])
        print(f"  {ln}: {n}/{len(results)} detected")

    # 線比率（同一光譜，都需要偵測）
    import json
    pairs = {
        'O3/Hb': ('O3_5007', 'HB_4861'),
        'O32': ('O3_5007', 'O2_3727'),
        'Ha/Hb': ('HA_6563', 'HB_4861'),
        'O3/Ha': ('O3_5007', 'HA_6563'),
    }
    print("\n線比率（獨立擬合）：")
    for name, (num, den) in pairs.items():
        vals = []
        for r in results:
            if r[num + '_det'] and r[den + '_det'] and r[num + '_flux'] > 0 and r[den + '_flux'] > 0:
                vals.append(r[num + '_flux'] / r[den + '_flux'])
        if vals:
            print(f"  {name}: n={len(vals)}, med={np.median(vals):.2f}, "
                  f"mean={np.mean(vals):.2f}, P25={np.percentile(vals,25):.2f}, P75={np.percentile(vals,75):.2f}")

    # 按 z bin 睇 O3/Hb
    print("\n[OIII]/Hβ 按 z bin：")
    for zl, zh in [(2,4),(4,5),(5,6),(6,8),(8,12)]:
        vals = []
        for r in results:
            if zl <= r['z'] < zh and r['O3_5007_det'] and r['HB_4861_det'] \
               and r['O3_5007_flux']>0 and r['HB_4861_flux']>0:
                vals.append(r['O3_5007_flux']/r['HB_4861_flux'])
        if vals:
            print(f"  z={zl}-{zh}: n={len(vals)}, med={np.median(vals):.2f}")

    with open('/home/wsl/IDCM/jades_fit_v2.json', 'w') as fh:
        json.dump(results, fh, indent=1, default=str)
    print("\nSaved /home/wsl/IDCM/jades_fit_v2.json")

if __name__ == '__main__':
    main()