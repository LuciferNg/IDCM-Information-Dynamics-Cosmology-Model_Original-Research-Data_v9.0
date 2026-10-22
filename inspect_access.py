#!/usr/bin/env python3
"""檢查 optical/spectrum/view/data/access 端點 — 搵光譜 FITS 下載"""
import subprocess, re

specobjid = "4037649776186990592"

# data/access 網頁
r = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', 'Mozilla/5.0',
    f'https://dr18.sdss.org/optical/spectrum/view/data/access?specobjid={specobjid}',
    '-o', '/tmp/access.html', '-w', '%{http_code} %{size_download}'],
    capture_output=True, text=True)
print("HTTP:", r.stdout)

with open('/tmp/access.html') as fh:
    content = fh.read()
# 搵 fits 下載連結
fits_links = re.findall(r'href="([^"]*\.fits[^"]*)"', content)
print("fits links:", fits_links[:10])
# 全部連結
all_links = re.findall(r'href="([^"]*)"', content)
print("\nall links:", [l for l in all_links if 'fits' in l.lower() or 'download' in l.lower() or 'coadd' in l.lower()][:15])