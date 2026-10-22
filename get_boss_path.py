#!/usr/bin/env python3
"""攞 BOSS 光譜正確 SAS 路徑：用 skyserver 光譜下載 API"""
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

# 攞 BOSS 光譜個 run2d + sciencePrimary
query(token,
      "SELECT TOP 5 s.plate,s.mjd,s.fiberid,s.z,s.run2d,s.survey,s.sciencePrimary FROM specObj s WHERE s.plate=3586 AND s.fiberid=628",
      '/tmp/boss_info.csv')
with open('/tmp/boss_info.csv') as fh:
    print("BOSS 3586/55181/628:", fh.read())