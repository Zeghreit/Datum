"""Tidy the docs into docs/, then commit and push the whole session's work."""
import os, shutil, subprocess

D = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum')
DOCS = os.path.join(D, 'docs')
os.makedirs(DOCS, exist_ok=True)

for name in ['DATUM-design.md', 'DATUM-handover.md', 'DATUM-sound-brief.md']:
    src = os.path.join(D, name)
    if os.path.exists(src):
        dst = os.path.join(DOCS, name)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.move(src, dst)
        print('moved  docs/' + name)

# README points at the handover so a fresh clone knows where to start
readme = os.path.join(D, 'README.md')
txt = open(readme, encoding='utf-8').read() if os.path.exists(readme) else ''
if 'DATUM-handover' not in txt:
    txt = ('# DATUM\n\n'
           'Пошаговый данжен-кроулер от первого лица внутри самореплицирующейся '
           'мегаструктуры. Прототип — один HTML-файл, открывается в любом браузере.\n\n'
           '**Начни с [docs/DATUM-handover.md](docs/DATUM-handover.md)** — состояние '
           'проекта, устройство конвейера и список уже пройденных граблей.\n\n'
           '- Дизайн целиком: [docs/DATUM-design.md](docs/DATUM-design.md)\n'
           '- Звуковое задание: [docs/DATUM-sound-brief.md](docs/DATUM-sound-brief.md)\n\n'
           '## Сборка\n\n'
           '```\n'
           'py build/make.py\n'
           '```\n\n'
           'Проверяет исходник `datum-prototype.html` и собирает `dist/DATUM.html`.\n'
           'Пересборка арта нужна только при смене картинок: `datum_workers.py`, '
           '`datum_chars.py`, `datum_tex.py`.\n\n'
           + ('\n---\n\n' + txt if txt.strip() else ''))
    open(readme, 'w', encoding='utf-8').write(txt)
    print('README rewritten')


def git(*a, quiet=False):
    r = subprocess.run(['git'] + list(a), cwd=D, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if not quiet:
        print('\n$ git', ' '.join(a[:3]))
        print(out[:700] if out else '  (ok)')
    return r.returncode, out


git('add', '-A', quiet=True)
git('-c', 'user.name=Datum', '-c', 'user.email=datum@local', 'commit', '-m',
    'Build in place: make.py with four-layer source checks, docs, node parse')
git('push', 'origin', 'main')
git('log', '--oneline', '-n', '4')
