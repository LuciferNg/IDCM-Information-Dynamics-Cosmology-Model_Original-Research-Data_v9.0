#!/usr/bin/env python3
"""攞 BOSS 光譜正確 SAS 路徑：查 specObj 攞 run2d + survey，測試候選 URL"""
import subprocess, re

def get_token():
    subprocess.run("curl -s --max-time 30 -A 'Mozilla/5.0' 'https://skyserver.sdss.org/dr18/en/tools/search/sql.aspx' -o /tmp/sqlpage2.html", shell=True)
    with open('/tmp/sqlpage2.html') as fh:
        html = fh.read()
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]*)"', html)
    return m.group(1) if m else None

def query(token, cmd):
    r = subprocess.run(['curl', '-s', '--max-time', '40', '-A', 'Mozilla/5.0',
        '-X', 'POST', 'https://skyserver.sdss.org/dr18/SearchTools/sql',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '--data-urlencode', f'cmd={cmd}',
        '--data-urlencode', 'format=csv',
        '--data-urlencode', 'searchtool=SQL',
        '--data-urlencode', f'__RequestVerificationToken={token}'],
        capture_output=True, text=True)
    return r.stdout

token = get_token()
print(f"token: {token[:20]}...")

# 攞 specObj 嘅 run2d + survey for BOSS galaxies
out = query(token, "SELECT TOP 5 plate,mjd,fiberid,z,survey,run2d FROM specObj WHERE survey='boss' AND z BETWEEN 0.3 AND 0.5")
print("BOSS specObj:")
print(out[:500])