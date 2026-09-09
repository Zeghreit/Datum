"""Find the Suno mp3s wherever Chrome put them, and stage them into sfx/."""
import os, glob, time, shutil

SFX = os.path.join('E:', os.sep, 'ClaudeFiles', 'Datum', 'sfx')
os.makedirs(SFX, exist_ok=True)
home = os.path.expanduser('~')

roots = [os.path.join(home, d) for d in
         ['Downloads', 'Desktop', 'Documents', 'Music', 'OneDrive',
          os.path.join('OneDrive', 'Desktop'), os.path.join('OneDrive', 'Downloads')]]
roots += [os.path.join('E:' + os.sep, 'ClaudeFiles'), 'E:' + os.sep,
          os.path.join('D:' + os.sep), os.path.join('C:' + os.sep, 'Downloads')]

cutoff = time.time() - 3 * 3600          # anything touched in the last three hours
found = []

for root in roots:
    if not os.path.isdir(root):
        continue
    for depth in ('*', os.path.join('*', '*')):
        for ext in ('mp3', 'wav', 'm4a'):
            for f in glob.glob(os.path.join(root, depth + '.' + ext)):
                try:
                    if os.path.getmtime(f) > cutoff:
                        found.append(f)
                except OSError:
                    pass

found = sorted(set(found), key=os.path.getmtime)
if not found:
    print('nothing recent found in:')
    for r in roots:
        print('   ', r, '' if os.path.isdir(r) else '(missing)')
else:
    print('recent audio:')
    for f in found:
        print('  %-58s %6.2f MB  %.0f min ago' %
              (f[-58:], os.path.getsize(f) / 1048576,
               (time.time() - os.path.getmtime(f)) / 60))
