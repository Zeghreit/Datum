"""One command: verify the engine source, then bake dist/DATUM.html.

The old loop was: edit a copy, hand it over, download, place, bake. Now the
source lives on disk and is edited in place, so this is the only step left.
Run it after every engine change.

    py E:\\ClaudeFiles\\Datum\\build\\make.py
"""
import os, re, subprocess, sys, hashlib, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, 'datum-prototype.html')
DIST = os.path.join(ROOT, 'dist', 'DATUM.html')

# Functions the game calls at runtime. Each must exist exactly once — a
# duplicated block silently shadows half the file and is very hard to spot.
NEED = """buildZone clearWorld buildGreebles buildProps buildVista scatterLights
spawnEnemies addEnemy occupied los faceToward enemyTurn aiFighter aiHauler
aiSurveyor aiSealer aiBreaker aiCadaver wakeBoss bossRoar splitCadaver
releaseClamps explode crushHeld flankTile stepToward inReach intentOf
drawCallouts callout screenOf drawBoss drawVitals paintPortraits resetBodies
damageShell inhabit printBodies playerStrike useDoor transitZone arrivalSpot
faceOpen dispatch tryMove tryTurn drawMini updateSeen runBoot openMenu
buildMenu auInit startAmbient startMusic musicSet clank thud robo tellFor
loadSound say note zstate facing""".split()

MARKERS = ['__ENEMIES__', '__PORTRAITS__', '__TEXTURES__', '__SFX__']


def check():
    html = open(SRC, encoding='utf-8').read()
    m = re.search(r'<script>([\s\S]*?)</script>\s*</body>', html)
    if not m:
        return ['cannot find the game script block']
    js = m.group(1)
    bad = []

    # 1. every bake marker still present — baking consumes them, the source keeps them
    for k in MARKERS:
        if k not in html:
            bad.append('marker missing: ' + k)

    # 2. no function defined twice
    for fn in NEED:
        n = len(re.findall(r'function ' + fn + r'\b', js))
        if n != 1:
            bad.append('function %s defined %d times' % (fn, n))

    # 3. structural check, in pure python so the build never depends on what
    #    happens to be installed. A raw brace count would lie — braces live
    #    inside strings and regexes too — so jscheck walks the source as a small
    #    state machine. This is what catches a truncated or half-pasted edit.
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from jscheck import scan
        errs, _ = scan(js)
        bad.extend(errs)
        if not errs:
            print('structure ok')
    except Exception as e:
        print('structure check unavailable:', type(e).__name__, e)

    # 4. real parse, when node is around. Stricter than the above — it sees
    #    genuine syntax errors that are still brace-balanced. Note it does NOT
    #    replace check 2: a function pasted twice parses perfectly.
    #    Looked up directly rather than through PATH, which a shell opened
    #    before the install will not have picked up yet.
    node = shutil.which('node')
    if not node:
        for c in [r'C:\Program Files\nodejs\node.exe',
                  r'C:\Program Files (x86)\nodejs\node.exe',
                  os.path.expanduser(r'~\AppData\Roaming\npm\node.exe'),
                  os.path.expanduser(r'~\scoop\apps\nodejs\current\node.exe')]:
            if os.path.exists(c):
                node = c
                break

    probe = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_parse.mjs')
    if not node:
        print('parse    skipped (node not found)')
    else:
        try:
            with open(probe, 'w', encoding='utf-8') as f:
                f.write('import fs from "fs";\n'
                        'const h = fs.readFileSync(process.argv[2], "utf8");\n'
                        'const m = h.match(/<script>([\\s\\S]*?)<\\/script>\\s*<\\/body>/);\n'
                        'if (!m) { console.log("no script block"); process.exit(2); }\n'
                        'try { new Function(m[1]); }\n'
                        'catch (e) { console.log(e.message); process.exit(3); }\n')
            r = subprocess.run([node, probe, SRC],
                               capture_output=True, text=True, timeout=90)
            if r.returncode == 0:
                print('parse    ok (node)')
            else:
                bad.append('syntax: ' + (r.stdout + r.stderr).strip()[:200])
        except (OSError, subprocess.TimeoutExpired) as e:
            print('parse    skipped (%s)' % type(e).__name__)
        finally:
            if os.path.exists(probe):
                os.remove(probe)

    return bad


def main():
    if not os.path.exists(SRC):
        sys.exit('engine source not found: ' + SRC)

    b = open(SRC, 'rb').read()
    print('source  %s  %d bytes  sha1 %s' %
          (os.path.basename(SRC), len(b), hashlib.sha1(b).hexdigest()[:12]))

    problems = check()
    if problems:
        print('\nREFUSING TO BUILD:')
        for p in problems:
            print('  !', p)
        sys.exit(1)
    print('checks   ok (%d functions, %d markers)' % (len(NEED), len(MARKERS)))

    r = subprocess.run([sys.executable,
                        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'datum_inline.py')],
                       capture_output=True, text=True)
    print()
    print((r.stdout + r.stderr).strip())
    if r.returncode != 0:
        sys.exit(r.returncode)
    if os.path.exists(DIST):
        print('\nopen: %s  (%.1f MB)' % (DIST, os.path.getsize(DIST) / 1048576))


if __name__ == '__main__':
    main()
