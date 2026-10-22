#!/usr/bin/env python3
"""試 BOSS 光譜正確下載路徑（多個候選）"""
import subprocess

candidates = [
    # BOSS DR18
    "https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr18/spectro/sdss/redux/103/spectra/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v6_0_4/spectra/3586/spec-3586-55181-0628.fits",
    # eBOSS DR17
    "https://data.sdss.org/sas/dr17/eboss/spectro/redux/26/spectra/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr17/eboss/spectro/redux/fix/spectra/3586/spec-3586-55181-0628.fits",
    # DR16 BOSS
    "https://data.sdss.org/sas/dr16/eboss/spectro/redux/26/spectra/3586/spec-3586-55181-0628.fits",
    # DR12
    "https://data.sdss.org/sas/dr12/boss/spectro/redux/26/spectra/3586/spec-3586-55181-0628.fits",
    # DR18 optical spectra path used by explore
    "https://data.sdss.org/sas/dr18/spectro/eboss/redux/26/spectra/3586/spec-3586-55181-0628.fits",
]

for url in candidates:
    r = subprocess.run(['curl', '-sIL', '--max-time', '12', '-A', 'Mozilla/5.0', url, '-o', '/dev/null', '-w', '%{http_code}'],
                       capture_output=True, text=True)
    code = r.stdout.strip()
    print(f"{code} {url}")