"""Locate AssetForge's Chrome profile and pull any recent audio out of it."""
import os, sys, json, glob, time, shutil

AF = r'C:\Users\a.bodrov\Projects\assetforge'
SFX = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum', 'sfx')
os.makedirs(SFX, exist_ok=True)

# config.json holds profile_dir; find it wherever it lives
cfgs = glob.glob(os.path.join(AF, 'config.json')) + \
       glob.glob(os.path.join(AF, 'assetforge', 'config.json')) + \
       glob.glob(os.path.join(AF, '**', 'config.json'), recursive=True)

profile = None
for c in dict.fromkeys(cfgs):
    try:
        d = json.load(open(c, encoding='utf-8'))
    except Exception:
        continue
    if 'profile_dir' in d:
        profile = os.path.expandvars(os.path.expanduser(str(d['profile_dir'])))
        print('config:', c)
        print('profile_dir:', profile, '' if os.path.isdir(profile) else '(MISSING)')
        break

if not profile:
    # config.py may hold the default instead
    for p in glob.glob(os.path.join(AF, 'assetforge', 'config.py')):
        txt = open(p, encoding='utf-8', errors='ignore').read()
        for line in txt.splitlines():
            if 'profile_dir' in line:
                print('config.py:', line.strip())

# look for the download folder inside that profile, and for loose audio
cands = []
if profile and os.path.isdir(profile):
    cands.append(profile)
    for pref in glob.glob(os.path.join(profile, '*', 'Preferences')):
        try:
            d = json.load(open(pref, encoding='utf-8'))
            dd = d.get('download', {}).get('default_directory')
            if dd:
                print('profile download dir:', dd,
                      '' if os.path.isdir(dd) else '(MISSING)')
                cands.append(dd)
        except Exception:
            pass

cutoff = time.time() - 6 * 3600
hits = []
for root in cands:
    for pat in ('**/*.mp3', '**/*.wav', '**/*.m4a'):
        for f in glob.glob(os.path.join(root, pat), recursive=True):
            try:
                if os.path.getmtime(f) > cutoff:
                    hits.append(f)
            except OSError:
                pass

hits = sorted(set(hits), key=os.path.getmtime)
if not hits:
    print('\nno recent audio inside the AssetForge profile either')
else:
    print('\nfound:')
    for f in hits:
        dst = os.path.join(SFX, os.path.basename(f))
        shutil.copy2(f, dst)
        print('  %-56s %6.2f MB  -> sfx/' %
              (os.path.basename(f)[:56], os.path.getsize(f) / 1048576))
