#!/usr/bin/env python3
"""
BOSS 光譜下載 v5 — 串行 + 固定 delay，對 throttling server 最有效
一次一個 request，server 唔會 rate-limit，成功率高
"""
import os, time, subprocess

OUTDIR = '/home/wsl/IDCM/data/boss_spec'
os.makedirs(OUTDIR, exist_ok=True)

# 讀全部 manifest，過濾已成功下載
items = []
have = set()
for fn in os.listdir(OUTDIR):
    if fn.endswith('.fits') and os.path.getsize(os.path.join(OUTDIR, fn)) > 10000:
        have.add(fn)

with open('/tmp/boss_download_manifest.txt') as fh:
    for line in fh:
        p = line.strip().split('\t')
        if len(p) == 5:
            fname = f"spec-{p[0]}-{p[1]}-{int(p[2]):04d}.fits"
            if fname in have:
                continue
            url = f"https://dr18.sdss.org/optical/spectrum/view/data/format=fits/spec=lite?plateid={p[0]}&mjd={p[1]}&fiberid={p[2]}"
            items.append((fname, url))

print(f"需要補: {len(items)} 個 (已有 {len(have)})")

fail = 0
ok = 0
for idx, (fname, url) in enumerate(items):
    dest = os.path.join(OUTDIR, fname)
    r = subprocess.run(['curl', '-sL', '--connect-timeout', '8', '--max-time', '25',
                        '-A', 'Mozilla/5.0', '-o', dest, url],
                       capture_output=True, text=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        ok += 1
    else:
        fail += 1
        # 刪除壞檔
        if os.path.exists(dest):
            os.remove(dest)
    if (idx+1) % 25 == 0:
        print(f"  {idx+1}/{len(items)} (ok={ok}, fail={fail})", flush=True)
    time.sleep(0.8)  # 固定 delay 避 rate limit

print(f"\nDONE: ok={ok}, fail={fail}")
print(f"Files: {len([f for f in os.listdir(OUTDIR) if f.endswith('.fits')])}")