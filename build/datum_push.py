"""Merge whatever GitHub created on init, then push."""
import subprocess, os

DEST = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum')
ID = ['-c', 'user.name=Datum', '-c', 'user.email=datum@local']

def git(*a, quiet=False):
    r = subprocess.run(['git'] + list(a), cwd=DEST, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if not quiet:
        print('$ git', ' '.join(a))
        print(out[:900] if out else '  (ok)')
        print()
    return r.returncode, out

git('fetch', 'origin')
code, out = git(*ID, 'merge', 'origin/main', '--allow-unrelated-histories',
                '--no-edit')
if code != 0 and 'CONFLICT' in out:
    # the only likely clash is a README or .gitignore GitHub made for us
    for f in ['README.md', '.gitignore', 'LICENSE']:
        git('checkout', '--ours', f, quiet=True)
        git('add', f, quiet=True)
    git(*ID, 'commit', '--no-edit')

code, out = git('push', '-u', 'origin', 'main')
if code == 0:
    print('PUSHED')
    git('log', '--oneline', '-n', '4')
else:
    print('push still failing — see above')
