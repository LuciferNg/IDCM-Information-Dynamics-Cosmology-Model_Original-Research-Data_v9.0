#!/usr/bin/env python3
"""試 SAS 直接路徑（lite/）— 可能比 API endpoint 快好多"""
import subprocess

# 用已確認嘅 lite 路徑格式：plate 3586 應該存在
candidates = [
    "https://dr18.sdss.org/sas/dr18/spectro/boss/redux/v6_0_4/spectra/lite/3586/spec-3586-55181-0628.fits",
    "http://dr18.sdss.org/sas/dr18/spectro/boss/redux/v6_0_4/spectra/lite/3586/spec-3586-55181-0628.fits",
    "https://data.sdss.org/sas/dr18/spectro/boss/redux/v6_0_4/spectra/lite/3586/spec-3586-55181-0628.fits",
]
for url in candidates:
    r = subprocess.run(['curl', '-sIL', '--max-time', '12', '-A', 'Mozilla/5.0', url, '-o', '/dev/null', '-w', '%{http_code}'],
                       capture_output=True, text=True)
    print(f"{r.stdout.strip()} {url}")