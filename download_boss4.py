#!/usr/bin/env python3
"""
BOSS 光譜下載 v4 — 只補缺口，輸出去 /home/wsl/IDCM/data/boss_spec
curl 加硬 timeout，防卡死
"""
import os, time, concurrent.futures as cf

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

def download(item):
    fname, url = item
    dest = os.path.join(OUTDIR, fname)
    for attempt in range(6):
        r = os.system(f'curl -sL --connect-timeout 8 --max-time 25 -A "Mozilla/5.0" -o "{dest}" "{url}"')
        if os.path.exists(dest) and os.path.getsize(dest) > 10000:
            return (fname, 'ok', os.path.getsize(dest))
        time.sleep(2 + attempt)
    return (fname, 'fail', 0)

done = 0
fail = 0
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for fname, status, size in ex.map(download, items):
        done += 1
        if status == 'fail':
            fail += 1
        if done % 100 == 0:
            print(f"  {done}/{len(items)} (fail={fail})", flush=True)
print(f"\nDONE: {done} attempts, {fail} failed")
print(f"Files: {len([f for f in os.listdir(OUTDIR) if f.endswith('.fits')])}")