"""Rename whatever landed in sfx/ onto the keys the engine looks for.

The engine matches by filename stem, so 'Cold Caverns.mp3' does nothing until
it becomes 'music_ambient.mp3'. Anything already correctly named is left alone.
"""
import os, glob, sys

SFX = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum', 'sfx')

# what came out of Suno -> what the engine wants
MAP = {
    'cold caverns':     'music_ambient',
    'cold caverns (1)': 'music_ambient_alt',
}

KEYS = {'step','turn','bump','swap','print','cut','slam','thrust','pulse','clank',
        'crit','crush','hurt','kill','seam','dray','tally','seal','brk','roar',
        'hammer','saw','amb_drone','amb_wind',
        'music_ambient','music_approach','music_combat','music_ambient_alt'}

for f in sorted(glob.glob(os.path.join(SFX, '*'))):
    stem, ext = os.path.splitext(os.path.basename(f))
    low = stem.lower()
    if low in KEYS:
        print('keep   ', os.path.basename(f)); continue
    key = MAP.get(low)
    if not key:
        print('UNKNOWN', os.path.basename(f), '- name it after a key'); continue
    dst = os.path.join(SFX, key + ext.lower())
    if os.path.exists(dst) and os.path.abspath(dst) != os.path.abspath(f):
        os.remove(dst)
    os.rename(f, dst)
    print('rename ', os.path.basename(f), '->', os.path.basename(dst))

print('\nsfx/ now:')
for f in sorted(glob.glob(os.path.join(SFX, '*'))):
    print('   %-28s %6.2f MB' % (os.path.basename(f), os.path.getsize(f) / 1048576))
