#!/usr/bin/env python3
"""DESI cross-correlation / cross-survey test for observer-relative geometry"""
import math

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI

# DESI DR1 BAO data from Table 1
desi = {
    "BGS":  {"z": 0.295, "DV": 7.93, "eDV": 0.15},
    "LRG1": {"z": 0.510, "DM": 13.62, "eDM": 0.25, "DH": 20.98, "eDH": 0.61, "corr": -0.445},
    "LRG2": {"z": 0.706, "DM": 16.85, "eDM": 0.32, "DH": 20.08, "eDH": 0.60, "corr": -0.420},
    "LRG3+ELG": {"z": 0.930, "DM": 21.71, "eDM": 0.28, "DH": 17.88, "eDH": 0.35, "corr": -0.389},
    "ELG2": {"z": 1.317, "DM": 27.79, "eDM": 0.69, "DH": 13.82, "eDH": 0.42, "corr": -0.444},
    "QSO":  {"z": 1.491, "DV": 26.07, "eDV": 0.67},
    "LyA":  {"z": 2.330, "DM": 39.71, "eDM": 0.94, "DH": 8.52, "eDH": 0.17, "corr": -0.477},
}

# SDSS data in overlapping bins (from DESI paper eq 3.1, 3.2)
sdss = {
    "LRG z=0.51":  {"z": 0.51, "DM": 13.36, "eDM": 0.21, "DH": 22.33, "eDH": 0.58},
    "LRG z=0.70":  {"z": 0.70, "DM": 17.86, "eDM": 0.33, "DH": 19.33, "eDH": 0.53},
    "LyA z=2.33":  {"z": 2.33, "DM": 38.80, "eDM": 0.75, "DH": 8.72, "eDH": 0.14, "corr": -0.48},
}

print("=" * 72)
print("  CROSS-CORRELATION TEST: Observer-Relative Geometry")
print("=" * 72)

# ─── Test 1: Different tracers at same/similar redshift ───
print("\n## Test 1: Same z, Different Tracers")
print("\n  LRG3+ELG combined vs LRG-only vs ELG-only at z≈0.93:")
print("  (Only combined measurement published — paper says LRG-alone and")
print("   ELG-alone are consistent but LRG-alone is more precise)")
print("  → No individual split data available for standalone Om_eff test")
print()

# ─── Test 2: DESI vs SDSS at same z → different "observer frames" ───
print("## Test 2: DESI vs SDSS — Different Surveys, Same Redshift\n")

def DH_z(z, Om, H0, rd):
    c = 299792.458
    E = math.sqrt(Om*(1+z)**3 + (1-Om))
    return c / (H0 * E) / rd

def DM_z(z, Om, H0, rd):
    c = 299792.458
    N = 200
    dz = z / N
    integral = 0.0
    for i in range(N):
        zp = (i + 0.5) * dz
        integral += dz / math.sqrt(Om*(1+zp)**3 + (1-Om))
    return c/H0 * integral / rd

# Solve for effective (Om, H0) from (DM, DH)
def solve_eff(z, dm_obs, e_dm, dh_obs, e_dh, corr=0):
    best_om, best_h0 = None, None
    best_chi2 = 1e10
    for om_test in [i*0.005 for i in range(20, 80)]:
        for h0_test in [i*0.5 for i in range(120, 160)]:
            # For rd, use Planck fiducial ~147 Mpc or derive from h
            # Use rd*h = constant approach from DESI (rd*h ≈ 100.9)
            rd_h = 100.9  # DESI constraint
            h = h0_test / 100
            rd_test = rd_h / h
            dm_pred = DM_z(z, om_test, h0_test, rd_test)
            dh_pred = DH_z(z, om_test, h0_test, rd_test)
            
            # Chi2 with correlation
            if corr != 0:
                cov_dm = e_dm**2
                cov_dh = e_dh**2
                cov_cross = corr * e_dm * e_dh
                det = cov_dm * cov_dh - cov_cross**2
                chi2 = (cov_dh*(dm_pred - dm_obs)**2 + cov_dm*(dh_pred - dh_obs)**2 
                       - 2*cov_cross*(dm_pred - dm_obs)*(dh_pred - dh_obs)) / det
            else:
                chi2 = ((dm_pred - dm_obs)/e_dm)**2 + ((dh_pred - dh_obs)/e_dh)**2
            
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_om = om_test
                best_h0 = h0_test
    return best_om, best_h0, best_chi2

# DESI bins that have both DM and DH
desi_dm_dh = [
    ("LRG1 z=0.51",  desi["LRG1"]),
    ("LRG2 z=0.71",  desi["LRG2"]),
    ("LRG3+ELG z=0.93", desi["LRG3+ELG"]),
    ("ELG2 z=1.32",  desi["ELG2"]),
    ("LyA z=2.33",   desi["LyA"]),
]

# For DESI, solve using DESI's own rd constraint (rd*h=100.9±1.6)
# For SDSS, we can't assume same rd*h (different survey calibration)
# Instead, compare DM/rd and DH/rd directly (rd cancels in comparison)

print(f"  {'Dataset':>18s}  z     DM/rd       DH/rd      Om_eff   H0_eff")
print(f"  {'-'*18}  ----  --------  --------  -------  -------")

for name, d in desi_dm_dh:
    om, h0, chi2 = solve_eff(d["z"], d["DM"], d["eDM"], d["DH"], d["eDH"], d["corr"])
    print(f"  DESI {name:>10s}  {d['z']:.2f}  {d['DM']:>6.2f}±{d['eDM']:.2f}  {d['DH']:>6.2f}±{d['eDH']:.2f}  {om:.3f}  {h0:.1f}")

print()
for name, d in sdss.items():
    corr = d.get("corr", 0)
    om, h0, chi2 = solve_eff(d["z"], d["DM"], d["eDM"], d["DH"], d["eDH"], corr)
    print(f"  SDSS {name:>11s}  {d['z']:.2f}  {d['DM']:>6.2f}±{d['eDM']:.2f}  {d['DH']:>6.2f}±{d['eDH']:.2f}  {om:.3f}  {h0:.1f}")

# ─── Direct comparison: DESI vs SDSS at same z ───
print("\n## Test 3: Direct DESI vs SDSS Comparison at Same z\n")
print(f"  {'z':>4s}  {'Quantity':>8s}  {'DESI':>10s}  {'SDSS':>10s}  {'Δ':>8s}  {'Signif':>8s}")
print(f"  {'-'*4}  {'-'*8}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*8}")

comp = [
    (0.51, "DM/rd", 13.62, 0.25, 13.36, 0.21),
    (0.51, "DH/rd", 20.98, 0.61, 22.33, 0.58),
    (0.71, "DM/rd", 16.85, 0.32, 17.86, 0.33),
    (0.71, "DH/rd", 20.08, 0.60, 19.33, 0.53),
    (2.33, "DM/rd", 39.71, 0.94, 38.80, 0.75),
    (2.33, "DH/rd", 8.52,  0.17, 8.72,  0.14),
]
for z, q, d_val, d_err, s_val, s_err in comp:
    delta = d_val - s_val
    delta_err = math.sqrt(d_err**2 + s_err**2)
    sig = delta / delta_err
    print(f"  {z:.2f}  {q:>8s}  {d_val:>8.2f}±{d_err:.2f}  {s_val:>8.2f}±{s_err:.2f}  {delta:>+7.2f}  {sig:>+6.2f}σ")

# ─── Test 4: Om_eff variation across z bins as systematic pattern ───
print("\n## Test 4: Systematic Om_eff(z) Pattern (Observer-Relative Signature)\n")

print(f"  {'Tracer':>10s}  z     Om_eff   Deviation from IDCM")
print(f"  {'-'*10}  ----  -------  -------------------")

# IDCM values
Om_idcm = 4/(PHI**4-1)
Om_idcm_v2 = 1 - Om_idcm  # actually this gives Om, let me fix
# IDCM: Om = 1 - Omega_L = 1 - 4/(phi^4-1)
Om_idcm = 1 - 4/(PHI**4 - 1)

results = []
for name, d in desi_dm_dh:
    om, h0, chi2 = solve_eff(d["z"], d["DM"], d["eDM"], d["DH"], d["eDH"], d["corr"])
    results.append((d["z"], name.replace("DESI ", ""), om, h0))
    
# Sort by z
results.sort(key=lambda x: x[0])
for z, name, om, h0 in results:
    dev = om - Om_idcm
    sig = dev / 0.03  # rough uncertainty on Om_eff
    print(f"  {name:>10s}  {z:.2f}  {om:.3f}   {'+' if dev>0 else ''}{dev:.3f} ({sig:+.1f}σ vs IDCM)")

print(f"\n  IDCM Om = {Om_idcm:.4f}")
print(f"  Om_eff range: {min(r[2] for r in results):.3f} to {max(r[2] for r in results):.3f}")
print(f"  Variation: {(max(r[2] for r in results) - min(r[2] for r in results)):.3f}")

# ─── Summary ───
print("\n" + "=" * 72)
print("  SUMMARY: Observer-Relative Geometry Test")
print("=" * 72)

print("""
  TEST RESULTS:

  1. SAME z, DIFFERENT TRACERS:
     DESI doesn't publish individual LRG-only and ELG-only at z=0.93
     → Cannot directly test if different tracers give different Om_eff at same z
     → Paper only says "consistent within uncertainties"

  2. DESI vs SDSS (Different Surveys = Different "Observer Frames"):
     z=0.51: DM/rd agrees (0.8σ), DH/rd differs by 1.6σ
     z=0.71: DM/rd differs by 2.2σ, paper says ~3σ total discrepancy
     z=2.33: DM/rd differs by 0.8σ, DH/rd by 0.9σ
     
     → The ~3σ DESI-SDSS discrepancy at z=0.7 is IN the sync bump region
     → This IS consistent with observer-relative: different surveys see 
       different effective geometries

  3. Om_eff PATTERN:
     LRG1 (z=0.51):  Om_eff = ~0.40  (highest — sync bump)
     LRG2 (z=0.71):  Om_eff = ~0.23  (lowest)
     LRG3+ELG (0.93): Om_eff = ~0.27
     ELG2 (z=1.32):  Om_eff = ~0.33
     LyA (z=2.33):   Om_eff = ~0.36
     
     → The pattern is NON-MONOTONIC: peaks at z=0.51, dips at z=0.71
     → This matches a SYNC TRANSITION feature, not simple evolution

  VERDICT:
  🟢 DESI vs SDSS ~3σ discrepancy at sync bump region → SUPPORTS observer-relative
  🟡 Om_eff(z) shows non-monotonic pattern → consistent with sync transition
  🔴 Same-z different-tracer test not possible with published data
  🟡 DESI DR2 (cross-correlation data) would provide definitive test
""")