#!/usr/bin/env python3
"""試 BOSS 光譜 v5_10_0 路徑（boss/ 同 eboss/ 子目錄）"""
import subprocess

candidates = [
    "https://data.sdss.org/sas/dr18/spectro/boss/redux/v5_10_0/spectra/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr18/spectro/boss/redux/v5_10_0/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr18/spectro/eboss/redux/v5_10_0/spectra/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v5_10_0/spectra/3586/spec-3586-55181-0628.fits",
    # 可能 plate 目錄用 4 位
    "https://data.sdss.org/sas/dr18/spectro/boss/redux/v5_10_0/spectra/3586/spec-3586-55181-628.fits",
]

for url in candidates:
    r = subprocess.run(['curl', '-sIL', '--max-time', '12', '-A', 'Mozilla/5.0', url, '-o', '/dev/null', '-w', '%{http_code}'],
                       capture_output=True, text=True)
    print(f"{r.stdout.strip()} {url}")