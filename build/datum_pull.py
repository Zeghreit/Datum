"""Pull Suno audio straight from the CDN, the way AssetForge pulls Gemini images.

The browser's own download path is a dead end in the AssetForge Chrome profile:
it runs with a bare --user-data-dir and no download directory, so clicking
Download never lands a file. Fetching the bytes ourselves sidesteps that
entirely and puts the file exactly where the build wants it.
"""
import os, sys, urllib.request, urllib.error

SFX = os.path.join('E:' + os.sep, 'ClaudeFiles', 'Datum', 'sfx')
os.makedirs(SFX, exist_ok=True)

# id -> the key the engine will look for
TRACKS = {
    '247d8290-901f-404e-a23f-5c9619d74008': 'music_ambient',
    '24870155-ca7b-4ef7-bc52-a2b1e015c6ed': 'music_ambient_b',
}

HOSTS = ['https://cdn1.suno.ai/{id}.mp3',
         'https://cdn1.suno.ai/{id}.m4a',
         'https://cdn-o.suno.com/{id}.mp3',
         'https://audiopipe.suno.ai/?item_id={id}']

def grab(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get('Content-Type', '')

for tid, key in TRACKS.items():
    got = False
    for pat in HOSTS:
        url = pat.format(id=tid)
        try:
            data, ctype = grab(url)
        except urllib.error.HTTPError as e:
            print('  %-46s HTTP %s' % (url[-46:], e.code)); continue
        except Exception as e:
            print('  %-46s %s' % (url[-46:], type(e).__name__)); continue
        if len(data) < 50_000:
            print('  %-46s too small (%d B)' % (url[-46:], len(data))); continue
        ext = '.m4a' if 'mp4' in ctype or url.endswith('.m4a') else '.mp3'
        dst = os.path.join(SFX, key + ext)
        open(dst, 'wb').write(data)
        print('OK  %-18s %6.2f MB  %s' % (key, len(data) / 1048576, ctype))
        got = True
        break
    if not got:
        print('FAILED', key, tid)

print('\nsfx/ now holds:')
for f in sorted(os.listdir(SFX)):
    p = os.path.join(SFX, f)
    print('   %-30s %6.2f MB' % (f, os.path.getsize(p) / 1048576))
