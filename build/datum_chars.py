"""Build the party portrait strip and the full-body menu strip.

Sources are now one file per character, so no segmentation is needed — just
key the magenta, trim, and place each into its cell at a shared scale.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from datum_lib import OUT, WORK, key_magenta, trim, place, common_scale, punch

ORDER = ['ballast', 'breach', 'vector', 'conduit']   # must match LOADOUT

def load(fn):
    im = punch(trim(key_magenta(os.path.join(OUT, fn), bite=2, inset=10)))
    print('   %-26s %dx%d' % (fn, im.width, im.height))
    return im

def strip(files, cw, ch, out_name, shared=True, fill=0.94):
    """shared=True keeps one scale across the set, so relative height survives —
    right for full-body, wrong for portraits. Busts are all framed the same way,
    so each should simply fill its own cell; a shared scale just makes whoever
    was rendered on the biggest canvas look closer to the camera."""
    ims = [load(f) for f in files]
    sheet = Image.new('RGBA', (cw * len(ims), ch), (0, 0, 0, 0))
    sc = common_scale(ims, cw, ch, fill) if shared else None
    for i, im in enumerate(ims):
        s = sc if shared else min(cw * fill / im.width, ch * fill / im.height)
        place(sheet, im, i * cw, 0, cw, ch, s)
    p = os.path.join(WORK, out_name)
    sheet.save(p)
    print('%s  %s  %.1f kb' % (out_name, sheet.size, os.path.getsize(p) / 1024))
    return sheet

print('portraits:')
port = strip(['datum_port_%s.png' % n for n in ORDER], 288, 352,
             'datum_portrait_strip.png', shared=False, fill=0.99)
print('full body:')
full = strip(['datum_%s_v2.png' % n for n in ORDER], 320, 600,
             'datum_party_full.png', shared=True)

pv = Image.new('RGB', (max(port.width, full.width), port.height + full.height + 12),
               (40, 40, 38))
pv.paste(port, (0, 0), port)
pv.paste(full, (0, port.height + 12), full)
pv.resize((pv.width // 2, pv.height // 2), Image.NEAREST).save(
    os.path.join(WORK, '_pv_chars.png'))
