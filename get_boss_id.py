#!/usr/bin/env python3
"""攞 BOSS 光譜 specObjID，用 skyserver optical spectrum API 下載"""
import subprocess, re

def get_token():
    subprocess.run("curl -s --max-time 30 -A 'Mozilla/5.0' 'https://skyserver.sdss.org/dr18/en/tools/search/sql.aspx' -o /tmp/sp.html", shell=True)
    with open('/tmp/sp.html') as fh:
        html = fh.read()
    m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]*)"', html)
    return m.group(1) if m else None

def query(token, cmd, outfile):
    subprocess.run(['curl', '-s', '--max-time', '40', '-A', 'Mozilla/5.0',
        '-X', 'POST', 'https://skyserver.sdss.org/dr18/SearchTools/sql',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '--data-urlencode', f'cmd={cmd}',
        '--data-urlencode', 'format=csv',
        '--data-urlencode', 'searchtool=SQL',
        '--data-urlencode', f'__RequestVerificationToken={token}',
        '-o', outfile], capture_output=True)

token = get_token()
query(token, "SELECT TOP 3 specObjID,plate,mjd,fiberid FROM specObj WHERE plate=3586 AND fiberid=628", '/tmp/boss_id.csv')
with open('/tmp/boss_id.csv') as fh:
    print("BOSS specObjID:", fh.read())