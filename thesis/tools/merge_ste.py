#!/usr/bin/env python3
"""Copy every STE-edited file that passes tools/check_ste.py over the live source,
after backing up the live source to thesis/backup-pre-ste/."""
import subprocess, shutil, sys, os
from pathlib import Path
T = Path(__file__).resolve().parent.parent
bk = T / 'backup-pre-ste'
for sub in ('chapters', 'frontmatter'):
    (bk / sub).mkdir(parents=True, exist_ok=True)
    for f in (T / sub).glob('*.tex'):
        if not (bk / sub / f.name).exists(): shutil.copy2(f, bk / sub / f.name)
merged, rejected, missing = [], [], []
for sub in ('chapters', 'frontmatter'):
    for live in sorted((T / sub).glob('*.tex')):
        ste = T / 'ste' / sub / live.name
        if not ste.exists(): missing.append(f'{sub}/{live.name}'); continue
        r = subprocess.run([sys.executable, str(T / 'tools' / 'check_ste.py'), str(bk / sub / live.name), str(ste)], capture_output=True, text=True)
        if r.returncode == 0:
            shutil.copy2(ste, live); merged.append(f'{sub}/{live.name}')
        else:
            rejected.append(f'{sub}/{live.name}: ' + ' | '.join(l for l in r.stdout.splitlines() if l.startswith('FAIL')))
print('MERGED:', merged); print('REJECTED:', rejected); print('NO STE VERSION:', missing)
