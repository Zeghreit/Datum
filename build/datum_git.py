"""Keep spare takes out of the build, then wire up the GitHub remote."""
import os, shutil, glob, subprocess

DEST = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum')
SFX = os.path.join(DEST, 'sfx')
SPARE = os.path.join(SFX, 'spare')
REMOTE = 'https://github.com/Zeghreit/Datum.git'

# spare takes live in sfx/spare/ — the baker only scans sfx/ itself
os.makedirs(SPARE, exist_ok=True)
for f in glob.glob(os.path.join(SFX, '*_alt.*')) + glob.glob(os.path.join(SFX, '*_b.*')):
    dst = os.path.join(SPARE, os.path.basename(f))
    if os.path.exists(dst):
        os.remove(dst)
    shutil.move(f, dst)
    print('spare  ', os.path.basename(f))

print('\nbaked into the build:')
for f in sorted(glob.glob(os.path.join(SFX, '*.*'))):
    print('   %-26s %6.2f MB' % (os.path.basename(f), os.path.getsize(f) / 1048576))

# ── git ──
def git(*a):
    r = subprocess.run(['git'] + list(a), cwd=DEST, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

# audio is large and regenerable from the service; keep it out of the repo
ign = os.path.join(DEST, '.gitignore')
txt = open(ign, encoding='utf-8').read()
for line in ['sfx/*.mp3', 'sfx/*.wav', 'sfx/*.m4a', 'sfx/spare/']:
    if line not in txt:
        txt += line + '\n'
open(ign, 'w', encoding='utf-8').write(txt)

code, out = git('remote', 'get-url', 'origin')
if code == 0:
    print('\nremote already set:', out)
    git('remote', 'set-url', 'origin', REMOTE)
else:
    print('\n' + git('remote', 'add', 'origin', REMOTE)[1] or 'remote added')
print('origin ->', git('remote', 'get-url', 'origin')[1])

git('add', '-A')
code, out = git('-c', 'user.name=Datum', '-c', 'user.email=datum@local',
                'commit', '-m', 'Move to E:, sound pipeline, first ambient loop')
print(out[:400] if out else 'nothing to commit')
print('\nbranch:', git('rev-parse', '--abbrev-ref', 'HEAD')[1])
print('log:\n' + git('log', '--oneline', '-n', '4')[1])
print('\nrepo size:')
code, out = git('count-objects', '-vH')
print(out)
