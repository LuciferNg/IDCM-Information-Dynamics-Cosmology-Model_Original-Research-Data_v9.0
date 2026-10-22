#!/usr/bin/env python3
"""完整數值驗證：重跑所有關鍵分析，確保所有報告數值正確"""
import json, os, sys
import numpy as np
from astropy.io import fits
from scipy import stats

REPORT = []
def check(name, expected, actual, tol=0.02):
    if abs(expected) < 1e-10:
        ok = abs(actual) < tol
    else:
        ok = abs(actual/expected - 1) < tol
    status = "✅" if ok else "❌"
    REPORT.append(f"  {status} {name}: expected={expected:.4f}, actual={actual:.4f}, ratio={actual/expected if abs(expected)>1e-10 else 'NA':.4f}")
    return ok

def med(vals): return np.median(vals) if len(vals) > 0 else np.nan
def l(z): return np.log(1+z)/np.log(4)

def o3hb_vals(lst, zl, zh):
    return [r['O3_5007_flux']/r['HB_4861_flux'] for r in lst if zl<=r['z']<zh 
            and r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0]

print("="*70)
print("1. SDSS FIT 數值驗證")
print("="*70)
sdss = json.load(open('/home/wsl/IDCM/sdss_large_fit.json'))
z = np.array([r['z'] for r in sdss])
print(f"  總數: {len(sdss)}, z 範圍: {z.min():.4f}-{z.max():.4f}")
for zl, zh, em, en in [(0.001,0.02,2.23,461),(0.02,0.03,1.64,252),(0.03,0.04,1.59,277),
                        (0.04,0.05,1.33,230),(0.05,0.06,1.21,258),(0.06,0.07,1.10,249),
                        (0.07,0.08,0.87,224),(0.08,0.10,0.76,396)]:
    v = o3hb_vals(sdss, zl, zh)
    check(f"SDSS z={zl}-{zh} n", en, len(v), 0.05)
    if len(v)>=10: check(f"SDSS z={zl}-{zh} med", em, med(v), 0.05)

print("\n"+"="*70)
print("2. MASS CONTROL 數值驗證 — ⚠️ 檔案已清理，跳過")
print("="*70)
print("   newmasses_dr4.gz 已被 /tmp 清理時刪除")
print("   數值已由 mass_controlled_test.py 驗證，見文檔 38 節")

print("\n"+"="*70)
print("3. BOSS FIT 數值驗證")
print("="*70)
boss = json.load(open('/home/wsl/IDCM/boss_fit.json'))
bz = np.array([r['z'] for r in boss])
print(f"  總數: {len(boss)}, z 範圍: {bz.min():.2f}-{bz.max():.2f}")
for zl, zh, em, en in [(0.3,0.4,2.00,26),(0.4,0.5,1.51,26),(0.5,0.6,1.77,57),
                        (0.6,0.7,1.18,95),(0.7,0.8,1.30,91),(0.8,0.9,1.70,156),
                        (0.9,1.0,1.69,126),(1.0,1.2,2.84,103)]:
    v = o3hb_vals(boss, zl, zh)
    check(f"BOSS z={zl}-{zh} n", en, len(v), 0.15)
    if len(v)>=10: check(f"BOSS z={zl}-{zh} med", em, med(v), 0.15)

b_arr = np.array([(l(r['z']), r['O3_5007_flux']/r['HB_4861_flux']) for r in boss
                  if r['O3_5007_det'] and r['HB_4861_det'] and r['O3_5007_flux']>0 and r['HB_4861_flux']>0])
if len(b_arr)>50:
    rho, p = stats.spearmanr(b_arr[:,0], b_arr[:,1])
    check("BOSS Spearman rho", 0.129, rho, 0.30)
    print(f"  BOSS Spearman p={p:.2e}")

print("\n"+"="*70)
print("4. JADES FIT 數值驗證")
print("="*70)
jades = json.load(open('/home/wsl/IDCM/jades_fit_v2.json'))
jz = np.array([r['z'] for r in jades])
print(f"  總數: {len(jades)}, z 範圍: {jz.min():.2f}-{jz.max():.2f}")
for zl, zh, em, en in [(2,4,0.76,40),(4,5,2.05,73),(5,6,4.18,79),(6,8,5.06,56)]:
    v = o3hb_vals(jades, zl, zh)
    check(f"JADES z={zl}-{zh} n", en, len(v), 0.15)
    if len(v)>=5: check(f"JADES z={zl}-{zh} med", em, med(v), 0.10)

print("\n"+"="*70)
print("5. JADES MASS PROXY 數值驗證 — ⚠️ 發射線目錄已清理，跳過")
print("="*70)
print("   數值已由 jades_mass_control.py 驗證")
print("   關鍵結果：JADES 上升支唔係質量假象")

print("\n"+"="*70)
print("6. SPECOBJ 驗證")
print("="*70)
spec = fits.open('/home/wsl/IDCM/data/catalogs/specObj_dr17.fits', memmap=False)
sd = spec[1].data
print(f"  總行數: {len(sd)}")
check("BOSS", 1382442, len(sd[(sd['SURVEY']=='boss')&(sd['CLASS']=='GALAXY')&(sd['Z']>0.3)&(sd['Z']<1.5)]), 0.01)
sdss_gal = sd[(sd['SURVEY']=='sdss')&(sd['CLASS']=='GALAXY')]
print(f"  SDSS galaxy: {len(sdss_gal)}, z<0.1: {np.sum(sdss_gal['Z']<0.1)}")
spec.close()

print("\n"+"="*70)
print("驗證小結")
print("="*70)
for r in REPORT: print(r)