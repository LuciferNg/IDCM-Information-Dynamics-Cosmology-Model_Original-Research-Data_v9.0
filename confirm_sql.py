#!/usr/bin/env python3
"""確認 skyserver SQL API 仲 work + 攞 BOSS 光譜資訊"""
import subprocess, re, sys

def get_token():
    subprocess.run("curl -s --max-time 30 -A 'Mozilla/5.0' 'https://skyserver.sdss.org/dr18/en/tools/search/sql.aspx' -o /tmp/sp.html", shell=True)
    with open('/tmp/sp.html') as fh:
        html = fh.read()
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]*)"', html)
    return m.group(1) if m else None

def query(token, cmd, outfile=None):
    args = ['curl', '-s', '--max-time', '40', '-A', 'Mozilla/5.0',
        '-X', 'POST', 'https://skyserver.sdss.org/dr18/SearchTools/sql',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '--data-urlencode', f'cmd={cmd}',
        '--data-urlencode', 'format=csv',
        '--data-urlencode', 'searchtool=SQL',
        '--data-urlencode', f'__RequestVerificationToken={token}']
    if outfile:
        args += ['-o', outfile]
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout

token = get_token()
print(f"token: {token[:16]}...")

# 簡單 query 確認
out = query(token, "SELECT TOP 3 plate,mjd,fiberid,z FROM specObj WHERE z BETWEEN 0.3 AND 0.4", '/tmp/confirm.csv')
print("stdout:", repr(out[:100]))
import os
if os.path.exists('/tmp/confirm.csv'):
    with open('/tmp/confirm.csv') as fh:
        print("file:", fh.read()[:300])