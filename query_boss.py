#!/usr/bin/env python3
"""
攞 BOSS galaxy (z=0.3-2.0) plate/mjd/fiber 清單 — 用 skyserver SQL API
分段查詢避免 timeout，拼合成大樣本
"""
import subprocess, re, time, sys

TOKEN_CMD = "curl -s --max-time 30 -A 'Mozilla/5.0' 'https://skyserver.sdss.org/dr18/en/tools/search/sql.aspx' -o /tmp/sqlpage.html && grep -oE 'name=\"__RequestVerificationToken\"[^>]*value=\"[^\"]*\"' /tmp/sqlpage.html | grep -oE 'value=\"[^\"]*\"' | sed 's/value=\"//;s/\"//'"

def get_token():
    r = subprocess.run(TOKEN_CMD, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def run_query(token, query, outfile):
    """POST SQL query, 存 CSV"""
    cmd = ['curl', '-s', '--max-time', '90', '-A', 'Mozilla/5.0',
           '-X', 'POST', 'https://skyserver.sdss.org/dr18/SearchTools/sql',
           '-H', 'Content-Type: application/x-www-form-urlencoded',
           '--data-urlencode', f'cmd={query}',
           '--data-urlencode', 'format=csv',
           '--data-urlencode', 'searchtool=SQL',
           '--data-urlencode', f'__RequestVerificationToken={token}',
           '-o', outfile]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode

token = get_token()
print(f"Token: {token[:20]}...")

# 分段查詢：z bins，每段 TOP 50000
all_data = []
z_bins = [(0.3,0.5),(0.5,0.7),(0.7,0.9),(0.9,1.1),(1.1,1.3),(1.3,1.5),(1.5,1.7),(1.7,2.0)]

for i,(zlo,zhi) in enumerate(z_bins):
    out = f'/tmp/boss_z_{i}.csv'
    query = (f"SELECT TOP 50000 plate,mjd,fiberid,z,class "
             f"FROM specObj WHERE class='GALAXY' AND z BETWEEN {zlo} AND {zhi} "
             f"AND plate > 3000 AND survey='boss'")
    rc = run_query(token, query, out)
    # 讀行數
    try:
        with open(out) as fh:
            lines = [l for l in fh if l.strip() and not l.startswith('#')]
        n = len(lines) - 1  # minus header
        print(f"z={zlo}-{zhi}: {n} galaxies")
        all_data.extend(lines[1:])
    except Exception as e:
        print(f"z={zlo}-{zhi}: FAIL {e}")
    time.sleep(1)

print(f"\nTotal BOSS galaxies: {len(all_data)}")

# 寫合併 manifest（plate mjd fiber z）
with open('/tmp/boss_galaxies.txt', 'w') as fh:
    fh.write("plate,mjd,fiberid,z\n")
    for l in all_data:
        fh.write(l)

# 統計
z_vals = [float(l.split(',')[3]) for l in all_data if len(l.split(','))==4]
print(f"z 範圍: {min(z_vals):.2f} - {max(z_vals):.2f}")