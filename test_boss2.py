#!/usr/bin/env python3
"""用 skyserver SQL 攞 BOSS 光譜下載連結（specObj has RELATION to spectra）"""
import subprocess, re

def get_token():
    subprocess.run("curl -s --max-time 30 -A 'Mozilla/5.0' 'https://skyserver.sdss.org/dr18/en/tools/search/sql.aspx' -o /tmp/sqlpage3.html", shell=True)
    with open('/tmp/sqlpage3.html') as fh:
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
print(f"token: {token[:16]}...")

# 攞 plate 3586 光譜嘅 specObj + 光譜表資訊
out = query(token, "SELECT TOP 5 s.plate,s.mjd,s.fiberid,s.z,s.run2d,s.survey,p.plateid FROM specObj s JOIN platex p ON s.plate=p.plate WHERE s.plate=3586")
print("specObj join platex:")
print(out[:600])