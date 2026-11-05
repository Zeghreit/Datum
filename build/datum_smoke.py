"""Open the built game in a real browser and report what actually happened.

This replaces the old party-panel smoke test, which was pinned to a path that
no longer exists and drove a CDP browser that is not always running. It now
launches its own headless Chrome, so the only requirement is Chrome itself.

    py build\\datum_smoke.py

It prints one line of facts -- three.js revision, zone size, shells, enemies,
console errors -- and writes build/_ui.png so the HUD can be looked at. Exit
code is 1 when the page threw, when three.js did not arrive, or when the maze
did not come up: that is a build that should not be handed to anyone.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, 'dist', 'DATUM.html')
HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, '_smoke.html')
SHOT = os.path.join(HERE, '_ui.png')

CHROME = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    os.path.expanduser(r'~\AppData\Local\Google\Chrome\Application\chrome.exe'),
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
]

# Runs after the page's own script. Never edits the source: it is appended to
# a throwaway copy in build/, so the shipped dist keeps its prologue.
INJECT = """
<script>
window.__errs = [];
window.addEventListener('error', function (e) { window.__errs.push(e.message); });
function K(code) { window.dispatchEvent(new KeyboardEvent('keydown', {code: code, key: code, bubbles: true})); }
window.addEventListener('load', function () {
  setTimeout(function () {
    try { if (typeof endBoot === 'function') endBoot(); } catch (e) {}
    try { menuOpen = false; var m = document.getElementById('menu'); if (m) m.style.display = 'none'; } catch (e) {}
    var steps = [function(){K('KeyW');}, function(){K('KeyW');}, function(){K('KeyC');}];
    var i = 0;
    (function next() {
      if (i < steps.length) { try { steps[i++](); } catch (e) { window.__errs.push('act ' + e.message); } setTimeout(next, 400); }
      else setTimeout(function () {
        try {
          document.title = 'PROBE' + JSON.stringify({
            errs: window.__errs,
            three: (typeof THREE !== 'undefined') ? THREE.REVISION : null,
            zone: (typeof Z !== 'undefined' && Z) ? [Z.name, Z.w, Z.h, Z.tile] : null,
            pos: (typeof P !== 'undefined') ? [P.x, P.y] : null,
            tick: (typeof tickNo !== 'undefined') ? tickNo : null,
            seen: (typeof seen !== 'undefined' && seen) ? seen.size : null,
            status: (typeof statusOpen !== 'undefined') ? statusOpen : null,
            bodies: (typeof bodies !== 'undefined') ? bodies.map(function (b) { return b.k + ':' + Math.round(b.hp); }) : null,
            enemies: (typeof enemies !== 'undefined') ? enemies.filter(function (e) { return e.hp > 0; }).length : null
          });
        } catch (e) { document.title = 'PROBEFAIL ' + e; }
      }, 1500);
    })();
  }, 2500);
});
</script>
"""


def chrome():
    for c in CHROME:
        if os.path.exists(c):
            return c
    return None


def main():
    if not os.path.exists(DIST):
        sys.exit('dist/DATUM.html not found — run build/make.py first')
    exe = chrome()
    if not exe:
        print('skip: no Chrome or Edge found')
        return

    html = open(DIST, encoding='utf-8').read()
    open(PROBE, 'w', encoding='utf-8').write(html.replace('</body>', INJECT + '</body>', 1))

    # A stale TEMP breaks Chrome's profile and python's tempfile alike; give
    # the run a directory we know exists.
    prof = os.path.join(HERE, '_smoke_profile')
    env = dict(os.environ)
    for k in ('TEMP', 'TMP'):
        if k in env and not os.path.isdir(env[k]):
            env[k] = tempfile.gettempdir() if _temp_ok() else HERE

    url = 'file:///' + PROBE.replace('\\', '/')
    try:
        r = subprocess.run([exe, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-data-dir=' + prof, '--window-size=1280,800',
                            '--virtual-time-budget=25000', '--screenshot=' + SHOT,
                            '--dump-dom', url],
                           capture_output=True, text=True, timeout=180, env=env)
    except subprocess.TimeoutExpired:
        sys.exit('FAIL: the page did not settle in 180 s')

    dom = r.stdout
    m = re.search(r'<title>(PROBE|PROBEFAIL)(.*?)</title>', dom, re.S)
    if not m:
        print('FAIL: the probe never reported — the page did not finish loading')
        print(dom[:400])
        sys.exit(1)
    if m.group(1) == 'PROBEFAIL':
        sys.exit('FAIL: probe threw: ' + m.group(2).strip())

    d = json.loads(m.group(2))
    print('three   %s' % (d['three'] or 'MISSING'))
    print('zone    %s %sx%s tile %sm' % tuple(d['zone']) if d['zone'] else 'zone    none')
    print('walked  %s -> pos %s, tick %s, seen %s' % (d['bodies'][0] if d['bodies'] else '?',
                                                      d['pos'], d['tick'], d['seen']))
    print('shells  %s' % ', '.join(d['bodies'] or []))
    print('enemies %s alive' % d['enemies'])
    print('screen  status=%s   shot: %s' % (d['status'], SHOT))
    if d['errs']:
        print('errors  %d' % len(d['errs']))
        for e in d['errs'][:8]:
            print('   !', e[:200])
        sys.exit(1)
    if not d['three']:
        sys.exit('FAIL: three.js did not load — dist is not self-contained')
    if not d['zone']:
        sys.exit('FAIL: no zone was built')
    print('ok')


def _temp_ok():
    try:
        tempfile.gettempdir()
        return True
    except Exception:
        return False


if __name__ == '__main__':
    main()
