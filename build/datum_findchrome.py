"""Read Chrome's configured download folder from every profile it can find."""
import os, json, glob

def prefs_paths():
    home = os.path.expanduser('~')
    roots = [
        os.path.join(home, 'AppData', 'Local', 'Google', 'Chrome', 'User Data'),
        os.path.join(home, 'AppData', 'Local', 'Chromium', 'User Data'),
        os.path.join('C:' + os.sep, 'Users', 'a.bodrov', 'Projects', 'assetforge'),
        os.path.join('E:' + os.sep, 'ClaudeFiles'),
    ]
    out = []
    for r in roots:
        if not os.path.isdir(r):
            continue
        for depth in ('Preferences', os.path.join('*', 'Preferences'),
                      os.path.join('*', '*', 'Preferences')):
            out += glob.glob(os.path.join(r, depth))
    return out

seen = set()
for p in prefs_paths():
    if p in seen:
        continue
    seen.add(p)
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        print('skip', p, type(e).__name__); continue
    dl = d.get('download', {})
    dirpath = dl.get('default_directory')
    if dirpath:
        exists = os.path.isdir(dirpath)
        print('%-70s -> %s %s' % (p[-70:], dirpath, '' if exists else '(MISSING)'))
        if exists:
            fs = sorted(glob.glob(os.path.join(dirpath, '*')),
                        key=os.path.getmtime)[-8:]
            for f in fs:
                print('      ', os.path.basename(f)[:56],
                      round(os.path.getsize(f) / 1048576, 2), 'MB')
    else:
        print('%-70s -> (no default_directory set)' % p[-70:])

if not seen:
    print('no Chrome Preferences files found')
