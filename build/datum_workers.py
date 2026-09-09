"""Build the enemy sprite sheet.

Each figure FILLS its cell. Do not bake metric proportion into the sheet: the
engine already builds each sprite plane at the machine's real height in metres,
so scaling here as well applies it twice — that is what made a 2.3 m welder
render at about 1.2 m and look like a toy.

Only a front view exists, so all three view rows use it; turning still swaps
rows, it just shows the same art until side and back are drawn.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from datum_lib import OUT, WORK, key_magenta, trim, place, punch

CELL_W, CELL_H, STATES, VIEWS = 320, 440, 1, 3     # one column, higher res

# order must match ETYPE in the prototype
SRC = ['datum_seam_v3.png', 'datum_dray_v3.png', 'datum_tally_v3.png',
       'datum_seal_v6.png', 'datum_break_v4.png', 'datum_cadaver_v5.png']

sheet = Image.new('RGBA', (CELL_W * STATES, CELL_H * VIEWS * len(SRC)), (0, 0, 0, 0))
shots = []

for ti, fn in enumerate(SRC):
    im = punch(trim(key_magenta(os.path.join(OUT, fn), bite=2, inset=10)))
    sc = min(CELL_W * 0.98 / im.width, CELL_H * 0.98 / im.height)
    print('   %-24s %dx%d -> %dx%d' %
          (fn, im.width, im.height, int(im.width * sc), int(im.height * sc)))
    for vi in range(VIEWS):
        row = ti * VIEWS + vi
        for st in range(STATES):
            place(sheet, im, st * CELL_W, row * CELL_H, CELL_W, CELL_H, sc)
    shots.append((im, sc))

out = os.path.join(WORK, 'datum_enemies_sheet.png')
sheet.save(out)
print('\nwrote', out, sheet.size, '%.1f kb' % (os.path.getsize(out) / 1024))

pv = Image.new('RGB', (CELL_W * len(shots), CELL_H), (26, 26, 24))
for i, (im, sc) in enumerate(shots):
    tmp = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
    place(tmp, im, 0, 0, CELL_W, CELL_H, sc)
    pv.paste(tmp.convert('RGB'), (i * CELL_W, 0), tmp)
pv.save(os.path.join(WORK, '_pv_roster.png'))
