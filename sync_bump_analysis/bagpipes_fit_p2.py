#!/usr/bin/env python3
"""
P2: Bagpipes SED fitting for z≈8.5 CEERS galaxies
==================================================
Check if P(z) posterior peaks at z=8.2 (aliasing point)
"""
import numpy as np
import bagpipes as pipes
import json, os, warnings, sys, glob, h5py
warnings.filterwarnings("ignore")

targets = [16624, 21834, 39575]

galaxy_data = {
    16624: {
        "z": 8.517, "zlo": 8.299, "zhi": 8.711,
        "phot": {"f435w": [None,None], "f606w":[1.15,4.07], "f814w":[None,None],
                 "f115w":[21.90,3.68], "f150w":[62.56,4.85], "f200w":[56.96,3.98],
                 "f277w":[74.98,2.99], "f356w":[88.69,2.32], "f410m":[117.30,6.56],
                 "f444w":[212.37,3.50]}
    },
    21834: {
        "z": 8.543, "zlo": 8.030, "zhi": 8.861,
        "phot": {"f435w":[3.35,4.40], "f606w":[-1.11,3.66], "f814w":[1.66,5.55],
                 "f115w":[3.84,2.88], "f150w":[13.94,3.65], "f200w":[16.53,3.23],
                 "f277w":[17.61,2.10], "f356w":[32.60,1.69], "f410m":[45.18,4.89],
                 "f444w":[82.95,2.74]}
    },
    39575: {
        "z": 8.616, "zlo": 8.049, "zhi": 8.959,
        "phot": {"f435w":[3.01,8.32], "f606w":[4.11,6.40], "f814w":[None,None],
                 "f115w":[0.003,5.94], "f150w":[33.19,8.33], "f200w":[25.17,7.50],
                 "f277w":[28.37,4.48], "f356w":[53.25,3.53], "f410m":[52.84,10.62],
                 "f444w":[94.36,5.51]}
    }
}

filter_dir = os.path.expanduser("~/IDCM/sync_bump_analysis/filters")
filter_names = ["F435W","F606W","F814W","F115W","F150W","F200W","F277W","F356W","F410M","F444W"]
filt_list = [os.path.join(filter_dir, f"{fn}.dat") for fn in filter_names]

print("=" * 72)
print("  P2: z=8.5 Aliasing — Bagpipes SED Fitting")
print("=" * 72)

results = {}

for gid in targets:
    gd = galaxy_data[gid]
    z_cat = gd["z"]
    print(f"\n  ── Galaxy {gid} (z={z_cat:.3f}) ──")
    
    # Build photometry array: shape (n_filters, 2) = [flux, error]
    phot_arr = []
    valid = 0
    for fn in filter_names:
        fval, ferr = gd["phot"].get(fn.lower(), [None, None])
        if fval is not None and ferr is not None:
            phot_arr.append([max(fval, 0.001), ferr])
            valid += 1
        else:
            phot_arr.append([0.001, 100.0])
    phot_arr = np.array(phot_arr)
    print(f"  Valid photometry: {valid}/{len(filter_names)} filters")
    
    if valid < 4:
        print(f"  ❌ Skipping")
        results[gid] = {"status": "skipped"}
        continue
    
    # Galaxy data loader
    def loader(ID):
        return phot_arr
    
    # Create galaxy
    try:
        g = pipes.galaxy(str(gid), loader, phot_units="mujy",
                          spectrum_exists=False, filt_list=filt_list)
        print(f"  Galaxy created: {len(g.photometry)} pts")
    except Exception as e:
        print(f"  ❌ Galaxy creation failed: {e}")
        continue
    
    # Fit instructions
    fit_instructions = {
        "redshift": (5.0, 10.0),
        "delayed": {
            "age": (0.01, 1.0), "tau": (0.1, 5.0),
            "massformed": (7.0, 12.0), "metallicity": (0.01, 2.5),
        },
        "dust": {"Av": (0.0, 2.0), "type": "Calzetti"},
        "nebular": {"logU": -3.0},
    }
    
    # Run fit
    run_name = f"p2_{gid}"
    print(f"  Running Nautilus MCMC...")
    sys.stdout.flush()
    
    try:
        f = pipes.fit(g, fit_instructions, run=run_name, n_posterior=500)
        f.fit(verbose=True, n_live=400)
        print(f"  ✅ Fit completed!")
    except Exception as e:
        print(f"  ❌ Fit failed: {e}")
        continue
    
    # Read posterior
    h5_files = glob.glob(f"pipes/posterior/{run_name}/*.h5")
    if not h5_files:
        print(f"  ❌ No HDF5 file found")
        continue
    
    with h5py.File(h5_files[0], 'r') as hf:
        samples = hf['samples2d'][()]
        z_s = samples[:, 5]
        
        z_med = float(np.median(z_s))
        z_min, z_max = float(z_s.min()), float(z_s.max())
        f82 = float(np.sum(np.abs(z_s - 8.2) < 0.2) / len(z_s))
        f77 = float(np.sum(np.abs(z_s - 7.7) < 0.2) / len(z_s))
        f85 = float(np.sum(np.abs(z_s - 8.5) < 0.2) / len(z_s))
        
        hist, edges = np.histogram(z_s, bins=50, range=(5, 10))
        peak_z = float((edges[np.argmax(hist)] + edges[np.argmax(hist)+1]) / 2)
        
        # Verdict
        if abs(z_med - 8.2) < 0.3:
            verdict = "CONFIRMED: z=8.5 catalog is aliasing artifact, true z≈8.2"
            status = "PASS"
        elif abs(z_med - z_cat) < 0.3:
            verdict = "NOT aliasing: P(z) consistent with catalog z"
            status = "FAIL"
        else:
            verdict = f"AMBIGUOUS: P(z) median at {z_med:.2f}"
            status = "UNCLEAR"
        
        r = {
            "catalog_z": z_cat, "bagpipes_median_z": round(z_med, 3),
            "bagpipes_z_range": [round(z_min,3), round(z_max,3)],
            "pz_peak_z": round(peak_z, 2),
            "fraction_at_z77": round(f77, 3), "fraction_at_z82": round(f82, 3),
            "fraction_at_z85": round(f85, 3), "n_samples": len(z_s),
            "verdict": verdict, "status": status
        }
        results[gid] = r
        
        print(f"  P(z) median: {z_med:.3f}, peak: {peak_z:.2f}")
        print(f"  z=8.2: {f82:.1%}, z=7.7: {f77:.1%}, z=8.5: {f85:.1%}")
        print(f"  Verdict: {verdict}")

# Summary
print(f"\n{'='*72}\n  P2 RESULTS\n{'='*72}")
for gid, r in results.items():
    s = r.get('status','?')
    print(f"  Galaxy {gid} (z={r['catalog_z']:.3f}): {s}")
    print(f"    Bagpipes median z = {r.get('bagpipes_median_z','N/A')}, z=8.2 frac = {r.get('fraction_at_z82','N/A'):.1%}")

with open("verification/p2_z85_aliasing_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Saved to verification/p2_z85_aliasing_results.json")