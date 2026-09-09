"""Shared helpers for the DATUM asset pipeline.

Import only — this module never builds anything on its own, so moving old
source images out of the folder can't break the scripts that use it.
"""
import os
import numpy as np
from PIL import Image

OUT  = os.path.join(os.path.dirname(os.path.dirname(
           os.path.abspath(__file__))), 'src')
WORK = os.path.join(os.path.dirname(OUT), 'assets')
os.makedirs(WORK, exist_ok=True)


def erode(alpha, n=1):
    a = alpha.copy()
    for _ in range(n):
        a = np.minimum.reduce([a, np.roll(a, 1, 0), np.roll(a, -1, 0),
                                  np.roll(a, 1, 1), np.roll(a, -1, 1)])
    return a


def key_magenta(path, bite=1, inset=0):
    """Magenta -> alpha, plus a bite off the edge to kill the purple fringe.

    `inset` trims a border off the source first: some renders come back with a
    dark frame or vignette that is not magenta, so it survives keying and welds
    itself to whichever figures touch the edge.
    """
    im = Image.open(path).convert('RGBA')
    if inset:
        im = im.crop((inset, inset, im.width - inset, im.height - inset))
    a = np.array(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    keep = ~((r > 110) & (b > 110) & (g < (r + b) // 2 - 25))
    alpha = erode(keep.astype(np.uint8) * 255, bite)
    fr = (alpha > 0) & (r > 100) & (b > 100) & (g < (r + b) // 2 - 12)
    mid = (a[..., 0] + a[..., 2]) // 2
    a[..., 1] = np.where(fr, mid, a[..., 1])
    a[..., 3] = alpha
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def bands(vis, axis, min_size, gap):
    """Runs of occupied rows/columns separated by more than `gap` empty ones."""
    occ = vis.any(axis=axis)
    out, start, run = [], None, 0
    for i, v in enumerate(occ):
        if v:
            if start is None:
                start = i
            run = 0
        elif start is not None:
            run += 1
            if run > gap:
                out.append((start, i - run)); start = None; run = 0
    if start is not None:
        out.append((start, len(occ) - 1))
    return [s for s in out if s[1] - s[0] >= min_size]


def trim(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def split_n(im, n):
    """Cut a merged run into n parts at the emptiest column near each boundary."""
    col = (np.array(im)[..., 3] > 8).sum(axis=0)
    w, win = im.width, max(4, im.width // (3 * n))
    xs = [0]
    for i in range(1, n):
        c = int(w * i / n)
        lo, hi = max(0, c - win), min(w, c + win)
        xs.append(lo + int(np.argmin(col[lo:hi])))
    xs.append(w)
    return [trim(im.crop((xs[i], 0, xs[i + 1], im.height))) for i in range(n)]


def ensure(crops, n):
    """Figures that touch come back as one blob — force them apart."""
    if len(crops) >= n:
        return crops[:n]
    widest = max(crops, key=lambda c: c.width)
    print('   merged blob %dx%d -> forcing %d' % (widest.width, widest.height, n))
    return split_n(widest, n)


def figures(fn, bite=1, inset=0):
    """Every separate figure in a turnaround sheet, in reading order."""
    im = key_magenta(os.path.join(OUT, fn), bite, inset)
    vis = np.array(im)[..., 3] > 8
    crops = []
    for y0, y1 in bands(vis, 1, 30, 10):
        strip = vis[y0:y1 + 1]
        for x0, x1 in bands(strip, 0, 25, 8):
            crops.append(trim(im.crop((x0, y0, x1 + 1, y1 + 2))))
    return crops


def place(dst, im, cx, cy, cw, ch, scale, bottom=True):
    w = max(1, int(im.width * scale)); h = max(1, int(im.height * scale))
    im = im.resize((w, h), Image.NEAREST)
    x = cx + (cw - w) // 2
    y = cy + (ch - h) if bottom else cy + (ch - h) // 2
    dst.alpha_composite(im, (x, max(cy, y)))


def common_scale(views, cw, ch, fill=0.94):
    """One scale for all views of a subject so they keep the same height."""
    return min(min(cw * fill / v.width, ch * fill / v.height) for v in views)


def punch(im, gamma=0.62, contrast=1.22, black=0.06):
    """Prepare near-black line art for heavy downscaling.

    Averaging a dark, finely hatched drawing down to ~100px turns it into one
    flat smudge: the linework and the plate seams both land in the same value.
    Lifting the midtones first, then re-deepening the blacks, keeps the seams
    alive through the resize while the figure still reads as black.
    """
    import numpy as np
    from PIL import Image as _Im
    a = np.array(im.convert('RGBA')).astype(np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3:]
    rgb = np.power(np.clip(rgb, 0, 1), gamma)                 # lift the dark end
    rgb = np.clip((rgb - 0.5) * contrast + 0.5, 0, 1)          # widen the range
    rgb = np.clip((rgb - black) / (1.0 - black), 0, 1)         # put black back
    out = np.concatenate([rgb, alpha], axis=-1)
    return _Im.fromarray((out * 255).astype(np.uint8))
