#!/usr/bin/env python3
"""
P2 extended: Bagpipes on remaining CEERS z>8 galaxies
======================================================
Galaxies: 14924 (z=8.831), 35300 (z=9.077)
"""
import numpy as np, bagpipes as pipes, json, os, warnings, sys, glob, h5py
warnings.filterwarnings("ignore")

targets = [14924, 35300]

galaxy_data = {
    14924: {
        "z": 8.831, "zlo": 8.741, "zhi": 8.999,
        "phot": {"f435w":[None,None], "f606w":[-2.96,3.75], "f814w":[1.00,4.61],
                 "f115w":[9.55,3.16], "f150w":[33.90,4.04], "f200w":[35.03,3.28],
                 "f277w":[46.17,2.33], "f356w":[62.95,1.77], "f410m":[116.84,5.17],
                 "f444w":[183.00,2.11]}
    },
    35300: {
        "z": 9.077, "zlo": 8.696, "zhi": 9.384,
        "phot": {"f435w":[None,None], "f606w":[-4.15,3.27], "f814w":[3.78,5.21],
                 "f115w":[0.65,2.89], "f150w":[14.70,3.77], "f200w":[12.75,3.51],
                 "f277w":[18.35,2.46], "f356w":[38.04,1.88], "f410m":[71.82,6.57],
                 "f444w":[89.74,2.98]}
    }
}

filter_dir = os.path.expanduser("~/IDCM/sync_bump_analysis/filters")
filter_names = ["F435W","F606W","F814W","F115W","F150W","F200W","F277W","F356W","F410M","F444W"]
filt_list = [os.path.join(filter_dir, f"{fn}.dat") for fn in filter_names]

print("=" * 72)
print("  P2 Extended: z=8.8-9.1 CEERS galaxies")
print("=" * 72)

results = {}

for gid in targets:
    gd = galaxy_data[gid]
    z_cat = gd["z"]
    print(f"\n  ── Galaxy {gid} (z={z_cat:.3f}) ──")
    
    # Build photometry array
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
    
    def loader(ID):
        return phot_arr
    
    try:
        g = pipes.galaxy(str(gid), loader, phot_units="mujy",
                          spectrum_exists=False, filt_list=filt_list)
        print(f"  Galaxy created: {len(g.photometry)} pts")
    except Exception as e:
        print(f"  ❌ Galaxy creation failed: {e}")
        continue
    
    fit_instructions = {
        "redshift": (5.0, 12.0),
        "delayed": {
            "age": (0.01, 1.0), "tau": (0.1, 5.0),
            "massformed": (7.0, 12.0), "metallicity": (0.01, 2.5),
        },
        "dust": {"Av": (0.0, 2.0), "type": "Calzetti"},
        "nebular": {"logU": -3.0},
    }
    
    run_name = f"p2x_{gid}"
    print(f"  Running Nautilus MCMC...")
    sys.stdout.flush()
    
    try:
        f = pipes.fit(g, fit_instructions, run=run_name, n_posterior=500)
        f.fit(verbose=True, n_live=200, n_eff=100)
        print(f"  ✅ Fit completed!")
    except Exception as e:
        print(f"  ❌ Fit failed: {e}")
        continue
    
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
        
        hist, edges = np.histogram(z_s, bins=50, range=(5, 12))
        peak_z = float((edges[np.argmax(hist)] + edges[np.argmax(hist)+1]) / 2)
        
        r = {
            "catalog_z": z_cat, "bagpipes_median_z": round(z_med, 3),
            "bagpipes_z_range": [round(z_min,3), round(z_max,3)],
            "pz_peak_z": round(peak_z, 2),
            "fraction_at_z77": round(f77, 3), "fraction_at_z82": round(f82, 3),
            "fraction_at_z85": round(f85, 3), "n_samples": len(z_s),
        }
        results[gid] = r
        
        print(f"  P(z) median: {z_med:.3f}, peak: {peak_z:.2f}")
        print(f"  z=8.2: {f82:.1%}, z=7.7: {f77:.1%}, z=8.5: {f85:.1%}")

# Summary
print(f"\n{'='*72}\n  P2 EXTENDED RESULTS\n{'='*72}")
for gid, r in results.items():
    print(f"  Galaxy {gid} (z={r['catalog_z']:.3f}): median z={r['bagpipes_median_z']}, z=8.2 frac={r.get('fraction_at_z82','N/A')}")

with open("verification/p2x_highz_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Saved to verification/p2x_highz_results.json")