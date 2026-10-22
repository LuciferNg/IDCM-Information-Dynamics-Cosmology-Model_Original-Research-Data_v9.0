#!/usr/bin/env python3
"""檢查已下載 BOSS 光譜結構"""
import os, subprocess
files = [f for f in os.listdir('/tmp/boss_spec') if f.endswith('.fits')]
print(f"BOSS files: {len(files)}")
if files:
    # 用 astropy 睇結構
    import sys
    test = os.path.join('/tmp/boss_spec', files[0])
    code = subprocess.run(['python3', '-c', f'''
from astropy.io import fits
f = fits.open("{test}")
print("HDUs:", [h.name for h in f])
for h in f[1:]:
    if h.data is not None:
        cols = list(h.columns.names)
        print(f"  {h.name}: {cols[:8]}")
'''], capture_output=True, text=True, env={**os.environ, 'PYTHONPATH':'/home/wsl/.local/lib/python3.13/site-packages'})
    print(code.stdout)
    if code.stderr: print("ERR:", code.stderr[:200])