"""Pull the audio Gemini just generated out of the AssetForge Chrome and into sfx/.

Gemini renders generated music as a <video> node whose src is a plain signed
https URL on contribution.usercontent.google.com. So there is nothing to
"download" through the browser at all — we ask the page's own request context
(same cookies) for the bytes and write them ourselves. The AssetForge download
rake is sidestepped completely.

    py build\\datum_gemini_audio.py music_boss
    py build\\datum_gemini_audio.py music_boss --chat https://gemini.google.com/app/<id>
    py build\\datum_gemini_audio.py music_boss --index -1      # which player on the page

Run it with the AssetForge venv python, it has playwright:
    C:\\Users\\a.bodrov\\Projects\\assetforge\\.venv\\Scripts\\python.exe
"""
import argparse
import os
import sys

from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9333"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(HERE, "sfx")

FIND = r"""
() => {
  const out = [];
  const walk = (root) => {
    for (const el of root.querySelectorAll('audio, video, source, *')) {
      const t = el.tagName.toLowerCase();
      if (t === 'audio' || t === 'video' || t === 'source') {
        const s = el.currentSrc || el.src || '';
        if (s) out.push(s);
      }
      if (el.shadowRoot) walk(el.shadowRoot);
    }
  };
  walk(document);
  return [...new Set(out)];
}
"""

EXT = {"audio/mpeg": ".mp3", "audio/mp4": ".m4a", "audio/ogg": ".ogg",
       "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/flac": ".flac",
       "video/mp4": ".m4a"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key", help="sound key, e.g. music_boss — becomes the file name")
    ap.add_argument("--chat", default=None, help="open this Gemini chat url first")
    ap.add_argument("--index", type=int, default=-1, help="which player (default: last)")
    ap.add_argument("--out", default=SFX, help="destination folder (default: sfx/)")
    a = ap.parse_args()

    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp(CDP)
        pages = [pg for ctx in br.contexts for pg in ctx.pages]
        gem = [pg for pg in pages if "gemini.google.com" in pg.url]
        if not gem:
            sys.exit("no gemini page open in the AssetForge Chrome")
        pg = gem[0]
        if a.chat:
            pg.goto(a.chat, wait_until="domcontentloaded")
            pg.wait_for_timeout(4000)

        srcs = pg.evaluate(FIND)
        srcs = [s for s in srcs if s.startswith("http")]
        if not srcs:
            sys.exit("no fetchable media on the page (blob/MSE only?) — %d nodes" % len(srcs))
        url = srcs[a.index]

        r = pg.request.get(url)
        if not r.ok:
            sys.exit("fetch failed: %s" % r.status)
        data = r.body()
        ext = EXT.get((r.headers.get("content-type") or "").split(";")[0].strip(), ".m4a")

        os.makedirs(a.out, exist_ok=True)
        path = os.path.join(a.out, a.key + ext)
        with open(path, "wb") as f:
            f.write(data)
        print("saved %s  %.1f kb  (of %d players)" % (path, len(data) / 1024, len(srcs)))


if __name__ == "__main__":
    main()
