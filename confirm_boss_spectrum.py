#!/usr/bin/env python3
"""確認 BOSS 光譜正確路徑 + 下載測試"""
import subprocess

# 我哋要嘅 BOSS 光譜：plate=3586, mjd=55181, fiber=628
candidates = [
    "http://dr18.sdss.org/sas/dr18/spectro/boss/redux/v6_0_4/spectra/lite/3586/spec-3586-55181-0628.fits",
    "https://dr18.sdss.org/sas/dr18/spectro/boss/redux/v6_0_4/spectra/lite/3586/spec-3586-55181-0628.fits",
    "https://dr18.sdss.org/optical/spectrum/view/data/format=fits/spec=lite?plateid=3586&mjd=55181&fiberid=628",
]

for url in candidates:
    r = subprocess.run(['curl', '-sIL', '--max-time', '15', '-A', 'Mozilla/5.0', url, '-o', '/dev/null', '-w', '%{http_code}'],
                       capture_output=True, text=True)
    print(f"{r.stdout.strip()} {url}")