#!/usr/bin/env python3
"""檢查 BOSS 光譜結構（用 astropy 正確語法）"""
import os, subprocess

files = [f for f in os.listdir('/tmp/boss_spec') if f.endswith('.fits')]
print(f"BOSS files: {len(files)}")
if files:
    test = os.path.join('/tmp/boss_spec', files[0])
    code = '''
from astropy.io import fits
f = fits.open("''' + test + '''")
print("HDUs:", [h.name for h in f])
for h in f:
    if h.data is not None and hasattr(h, 'columns') and h.columns is not None:
        cols = list(h.columns.names)
        print(f"  {h.name}: cols={cols[:10]}")
f.close()
'''
    r = subprocess.run(['python3', '-c', code], capture_output=True, text=True,
                       env={**os.environ, 'PYTHONPATH': '/home/wsl/.local/lib/python3.13/site-packages'})
    print(r.stdout)
    if r.stderr:
        print("ERR:", r.stderr[:300])