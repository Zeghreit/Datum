"""Prove jscheck actually catches the failures we have hit, before trusting it."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jscheck import scan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, 'datum-prototype.html'), encoding='utf-8').read()
js = re.search(r'<script>([\s\S]*?)</script>\s*</body>', html).group(1)

def expect(name, mutated, should_fail):
    errs, _ = scan(mutated)
    ok = bool(errs) == should_fail
    print('%-42s %s %s' % (name, 'PASS' if ok else 'FAIL',
                           ('- ' + errs[0]) if errs else ''))
    return ok

results = []

# the real file must stay clean
results.append(expect('untouched source', js, False))

# a truncated edit: drop the last 400 characters
results.append(expect('truncated tail', js[:-400], True))

# A duplicated block is brace-BALANCED, so jscheck cannot see it — that is
# make.py's job, via the count of function definitions. Check that division of
# labour holds, because between them the two must cover it.
i = js.index('function crushHeld')
j = js.index('function enemyTurn', i)
dup = js[:j] + js[i:j] + js[j:]
errs, _ = scan(dup)
n = len(re.findall(r'function crushHeld\b', dup))
ok = (not errs) and n == 2
print('%-42s %s %s' % ('duplicate block -> caught by count', 'PASS' if ok else 'FAIL',
                       '- jscheck silent (expected), count sees %d' % n))
results.append(ok)

# a stray closing brace
k = js.index('function drawVitals')
results.append(expect('stray closing brace', js[:k] + '}\n' + js[k:], True))

# an unterminated string
results.append(expect('unterminated string',
                      js.replace("say('clamp released', 'good');",
                                 "say('clamp released, 'good');", 1), True))

# braces inside strings and regexes must NOT be miscounted
noise = js + '\nconst _t = "a { b ( c [ d";\nconst _r = /[{(\\[]/g;\n' \
             'const _tpl = `x { y ( z`;\n'
results.append(expect('braces inside strings/regex ignored', noise, False))

print('\n%d/%d checks behaved correctly' % (sum(results), len(results)))
sys.exit(0 if all(results) else 1)
