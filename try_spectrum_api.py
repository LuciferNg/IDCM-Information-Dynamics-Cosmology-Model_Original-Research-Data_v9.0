#!/usr/bin/env python3
"""用 specObjID 試多個光譜下載端點"""
import subprocess

specobjid = "4037649776186990592"
plate, mjd, fiber = 3586, 55181, 628

candidates = [
    f"https://dr18.sdss.org/optical/spectrum/view?specobjid={specobjid}",
    f"https://dr18.sdss.org/optical/spectrum/data?specobjid={specobjid}",
    f"https://dr18.sdss.org/optical/spectrum/download?specobjid={specobjid}",
    f"https://skyserver.sdss.org/dr18/spectro/optical/spectrum?specobjid={specobjid}",
    f"https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/3586/spec-3586-55181-0628.fits",
    # 試 run2d 目錄 + plate 目錄（BOSS 用 4-digit plate）
]

for url in candidates:
    r = subprocess.run(['curl', '-sIL', '--max-time', '12', '-A', 'Mozilla/5.0', url, '-o', '/dev/null', '-w', '%{http_code}'],
                       capture_output=True, text=True)
    print(f"{r.stdout.strip()} {url}")