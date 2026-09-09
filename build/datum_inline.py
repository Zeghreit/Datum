import base64, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(HERE, 'datum-prototype.html')
DST  = os.path.join(HERE, 'dist', 'DATUM.html')
SFX  = os.path.join(HERE, 'sfx')          # drop audio files here

ASSETS = {
    '__ENEMIES__':   'datum_enemies_sheet.png',
    '__PORTRAITS__': 'datum_portrait_strip.png',
    '__TEXTURES__':  'datum_textures.png',
}

MIME = {'.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4', '.flac': 'audio/flac'}

if not os.path.exists(SRC):
    sys.exit('Put datum-prototype.html next to this script first: ' + SRC)

html = open(SRC, encoding='utf-8').read()

for marker, fn in ASSETS.items():
    path = os.path.join(HERE, 'assets', fn)
    if not os.path.exists(path):
        print('skip (missing):', fn)
        continue
    data = base64.b64encode(open(path, 'rb').read()).decode('ascii')
    html = html.replace(marker, 'data:image/png;base64,' + data)
    print('baked %-28s %8.1f kb' % (fn, len(data) / 1024))

# ── sound: every file in sfx/ becomes a key named after the file ──
sounds = {}
if os.path.isdir(SFX):
    for fn in sorted(os.listdir(SFX)):
        ext = os.path.splitext(fn)[1].lower()
        if ext not in MIME:
            continue
        key = os.path.splitext(fn)[0].lower()
        raw = open(os.path.join(SFX, fn), 'rb').read()
        sounds[key] = 'data:%s;base64,%s' % (MIME[ext],
                                             base64.b64encode(raw).decode('ascii'))
        print('baked sound %-22s %8.1f kb' % (key, len(raw) / 1024))
else:
    print('no sfx/ folder — keeping the synthesised bank')

# JSON goes in as a JS string literal, so escape the quotes it sits inside
payload = json.dumps(sounds).replace('\\', '\\\\').replace('"', '\\"')
html = html.replace('__SFX__', payload)

open(DST, 'w', encoding='utf-8').write(html)
print('\nwrote %s  %.1f kb  (%d sounds)' %
      (DST, os.path.getsize(DST) / 1024, len(sounds)))
