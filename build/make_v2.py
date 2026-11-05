"""Build datum-v2.html into dist/DATUM-v2.html.

Same rule as the v1 build: the source keeps its markers so it can be read and
edited, and this script substitutes them. The two differences are that v2 has
one art strip (the texture sheet) instead of four, and that its own smoke test
is separate.

    py build\\make_v2.py
"""
import base64
import hashlib
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'datum-v2.html')
DST = os.path.join(ROOT, 'dist', 'DATUM-v2.html')
TEX = os.path.join(ROOT, 'assets', 'datum_textures.png')
THREE = os.path.join(ROOT, 'build', 'vendor', 'three.min.js')
CDN = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/'
       'r128/three.min.js"></script>')


def parse_check(html):
    # The built file has two script blocks: three.js, then the game. Take the
    # LAST one — a regex from the first '<script>' runs through the closing tag
    # of the library and dies on '<'.
    i = html.rfind('<script>')
    j = html.find('</script>', i)
    if i < 0 or j < 0:
        print('parse    FAILED: no game script block')
        return False
    code = html[i + len('<script>'):j]

    probe = os.path.join(ROOT, 'build', '_parse_v2.js')
    node = None
    from shutil import which
    for c in ['node', r'C:\Program Files\nodejs\node.exe']:
        if c == 'node':
            node = which(c)
        elif os.path.exists(c):
            node = c
        if node:
            break
    if not node:
        print('parse    skipped (node not found)')
        return True
    try:
        open(probe, 'w', encoding='utf-8').write(code)
        r = subprocess.run([node, '--check', probe], capture_output=True, text=True, timeout=90)
        if r.returncode == 0:
            print('parse    ok (node)')
            return True
        print('parse    FAILED: ' + (r.stdout + r.stderr).strip()[:300])
        return False
    finally:
        if os.path.exists(probe):
            os.remove(probe)


def main():
    if not os.path.exists(SRC):
        sys.exit('missing ' + SRC)
    html = open(SRC, encoding='utf-8').read()

    stamp = '%s %s' % (time.strftime('%d.%m %H:%M'),
                       hashlib.sha1(html.encode('utf-8')).hexdigest()[:7])
    if "const BUILD = 'dev';" not in html:
        sys.exit("BUILD marker missing from datum-v2.html")
    html = html.replace("const BUILD = 'dev';", "const BUILD = '%s';" % stamp)
    print('build    %s' % stamp)

    if CDN not in html:
        sys.exit('<script src=...three.js...> tag not found — the bake needs it')
    if not os.path.exists(THREE):
        sys.exit('missing build/vendor/three.min.js')
    lib = open(THREE, encoding='utf-8').read()
    if '</script>' in lib:
        sys.exit('three.min.js contains </script> — cannot inline safely')

    # room art: one picture per room type, keyed by file name
    art_script = ''
    roomdir = os.path.join(ROOT, 'assets', 'roomart')
    if os.path.isdir(roomdir):
        arts = {}
        for fn in sorted(os.listdir(roomdir)):
            base, ext = os.path.splitext(fn)
            ext = ext.lower()
            if ext not in ('.png', '.jpg', '.jpeg', '.webp'):
                continue
            mime = {'.png': 'image/png', '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg', '.webp': 'image/webp'}[ext]
            data = base64.b64encode(open(os.path.join(roomdir, fn), 'rb').read()).decode('ascii')
            arts[base] = 'data:%s;base64,%s' % (mime, data)
            print('baked    %-28s %8.1f kb  (room art: %s)' % (fn, len(data) / 1024, base))
        if arts:
            art_script = '<script>window.__ROOMART__=' + json.dumps(arts) + ';</script>\n'
        else:
            print('room art none — cards will show glyphs')
    else:
        print('room art none — cards will show glyphs')

    html = html.replace(CDN, art_script + '<script>\n' + lib + '\n</script>')
    print('baked    %-28s %8.1f kb  (offline)' % ('three.min.js', len(lib) / 1024))

    if os.path.exists(TEX):
        data = base64.b64encode(open(TEX, 'rb').read()).decode('ascii')
        html = html.replace('"__TEXTURES__"', '"data:image/png;base64,' + data + '"')
        print('baked    %-28s %8.1f kb' % ('datum_textures.png', len(data) / 1024))
    else:
        print('skip     assets/datum_textures.png missing — procedural panels only')

    if '"__TEXTURES__"' in html:
        sys.exit('texture marker survived the bake')

    if not parse_check(html):
        sys.exit('REFUSING: the built file does not parse')
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    open(DST, 'w', encoding='utf-8').write(html)
    print('\nwrote %s  (%.1f MB)' % (DST, os.path.getsize(DST) / 1048576))


if __name__ == '__main__':
    main()
