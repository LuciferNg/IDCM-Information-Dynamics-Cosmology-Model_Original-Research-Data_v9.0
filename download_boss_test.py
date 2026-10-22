#!/usr/bin/env python3
"""下載 BOSS 光譜測試 — 確認係咪真光譜"""
import subprocess

r = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', 'Mozilla/5.0',
    'https://dr18.sdss.org/optical/spectrum/view/data/format=fits/spec=lite?plateid=3586&mjd=55181&fiberid=628',
    '-o', '/tmp/boss_spec_test.fits', '-w', '%{http_code} %{size_download}'],
    capture_output=True, text=True)
print("HTTP:", r.stdout)

import os
if os.path.exists('/tmp/boss_spec_test.fits'):
    size = os.path.getsize('/tmp/boss_spec_test.fits')
    print(f"Size: {size} bytes")
    # 睇前幾 bytes 確認係 fits
    with open('/tmp/boss_spec_test.fits', 'rb') as fh:
        head = fh.read(80)
    print("Header magic:", head[:20])