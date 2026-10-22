#!/usr/bin/env python3
"""檢查 optical/spectrum/view 返回內容 — 搵光譜數據下載方法"""
import subprocess

specobjid = "4037649776186990592"
# 下載返回內容
r = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', 'Mozilla/5.0',
    f'https://dr18.sdss.org/optical/spectrum/view?specobjid={specobjid}',
    '-o', '/tmp/spectrum_view.html', '-w', '%{http_code} %{size_download}'],
    capture_output=True, text=True)
print("HTTP:", r.stdout)

with open('/tmp/spectrum_view.html') as fh:
    content = fh.read()
print("content type check - first 300 chars:")
print(content[:300])
print("\n...\n")
# 搵 download/data/fits 連結
import re
links = re.findall(r'href="([^"]*(?:fits|download|data|spectrum)[^"]*)"', content, re.I)
print("download links:", links[:10])
# 搵 embedded JSON / data
if 'specobjid' in content or 'fits' in content.lower():
    print("\ncontains spec/fits references")