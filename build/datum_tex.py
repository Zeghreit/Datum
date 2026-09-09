"""Build the 4-tile texture strip: wall, floor, ceiling, structural metal.

One source file per tile now, so no segmentation. The engine wraps these with
MirroredRepeatWrapping, which makes any tile seamless regardless of how it was
authored — the mirror symmetry reads as manufactured on panel surfaces.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from datum_lib import OUT, WORK

SIZE = 512                       # texels per tile
SRC = ['datum_tex_wall.png', 'datum_tex_floor.png',
       'datum_tex_ceil.png', 'datum_tex_metal.png']

tiles = []
for fn in SRC:
    im = Image.open(os.path.join(OUT, fn)).convert('RGB')
    s = min(im.width, im.height)                       # centre square
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2,
                  (im.width - s) // 2 + s, (im.height - s) // 2 + s))
    im = im.resize((SIZE, SIZE), Image.LANCZOS)
    tiles.append(im)
    print('   %-24s %d -> %d' % (fn, s, SIZE))

strip = Image.new('RGB', (SIZE * 4, SIZE))
for i, t in enumerate(tiles):
    strip.paste(t, (i * SIZE, 0))
# palette pass: shrinks the file hard and lands closer to the era
strip = strip.convert('P', palette=Image.ADAPTIVE, colors=224)
p = os.path.join(WORK, 'datum_textures.png')
strip.save(p, optimize=True)
print('\nwrote', p, strip.size, '%.1f kb' % (os.path.getsize(p) / 1024))

strip.convert('RGB').resize((SIZE * 2, SIZE // 2), Image.NEAREST).save(
    os.path.join(WORK, '_pv_tiles.png'))
