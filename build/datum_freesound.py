"""Harvest CC0 sounds from Freesound without an account.

The search page carries a preview mp3 url for every hit, and the previews are
served straight off the CDN, so a query plus a download is the whole story — no
API key, no login, no waiting on a generator's free tier. Only Creative Commons
Zero is asked for, so nothing here needs attribution or comes with strings.

    py build\\datum_freesound.py search "heavy metal impact" -n 8
    py build\\datum_freesound.py grab step "boot step metal floor" -n 5

`search` just prints what is out there — id, length, name — so a human can read
the list before anything is fetched. `grab` downloads the candidates into
sfx/_raw/<key>/ named <key>__<rank>__<id>.mp3, ready to audition and cut.
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "sfx", "_raw")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")
CC0 = 'license:"Creative Commons 0"'


PACE = 4.0      # seconds between searches — freesound answers 429 if you rush


def get(url, tries=4):
    """Fetch, backing off politely when the site says slow down."""
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "en"})
    wait = 6.0
    for n in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or n == tries - 1:
                raise
            time.sleep(wait)
            wait *= 2
    raise RuntimeError("unreachable")


def search(query, want=10, page=1, extra=""):
    """Every hit on the page: id, seconds, preview url, name."""
    f = CC0 + ((" " + extra) if extra else "")
    url = ("https://freesound.org/search/?q=" + urllib.parse.quote(query) +
           "&f=" + urllib.parse.quote(f) + "&s=score+desc&page=%d" % page)
    doc = get(url).decode("utf-8", "replace")

    out = []
    # every result carries its player as a bundle of data- attributes
    for m in re.finditer(r'data-mp3="([^"]+)"([^>]*)', doc):
        blob = m.group(0)
        mp3 = html.unescape(m.group(1))
        sid = re.search(r"/(\d+)_[\d-]+-[lh]q\.mp3", mp3)
        dur = re.search(r'data-duration="([\d.]+)"', blob)
        name = re.search(r'data-title="([^"]*)"', blob)
        if not sid:
            continue
        out.append({
            "id": sid.group(1),
            "sec": float(dur.group(1)) if dur else 0.0,
            "mp3": mp3.replace("-lq.mp3", "-hq.mp3"),
            "name": html.unescape(name.group(1)) if name else "",
        })
        if len(out) >= want:
            break

    if not out:
        empty = ("nothing found" in doc.lower() or "no results" in doc.lower()
                 or 'id="search-results"' not in doc)
        print("  (no hits — %s)" % ("query too narrow" if empty
                                    else "page markup may have moved"))
    return out


def grab(key, query, want=5, extra=""):
    hits = search(query, want, extra=extra)
    dst = os.path.join(RAW, key)
    os.makedirs(dst, exist_ok=True)
    for i, h in enumerate(hits, 1):
        path = os.path.join(dst, "%s__%d__%s.mp3" % (key, i, h["id"]))
        try:
            data = get(h["mp3"])
        except Exception as e:
            print("  %2d. %-9s FAILED %s" % (i, h["id"], str(e)[:60]))
            continue
        with open(path, "wb") as f:
            f.write(data)
        print("  %2d. %-9s %6.2fs %6.0f kb  %s"
              % (i, h["id"], h["sec"], len(data) / 1024, h["name"][:56]))
    return hits


# One query per key, with a length filter so the results are already the right
# shape. The wording is what a field recordist would have typed into the file
# name, not what the design document calls the thing — "servo motor groan" finds
# SEAM's voice, "SEAM" finds nothing.
KEYS = [
    ("step",      "footstep metal",      "duration:[0 TO 3]"),
    ("turn",      "scuff metal",         "duration:[0 TO 3]"),
    ("bump",      "dull thud",           "duration:[0 TO 3]"),
    ("swap",      "relay click",         "duration:[0 TO 2]"),
    ("print",     "pneumatic servo",     "duration:[0 TO 5]"),
    ("cut",       "cutting torch",       "duration:[0 TO 5]"),
    ("slam",      "impact boom",         "duration:[0 TO 4]"),
    ("thrust",    "metal stab",          "duration:[0 TO 3]"),
    ("pulse",     "electric hum",        "duration:[0 TO 4]"),
    ("clank",     "metal clang",         "duration:[0 TO 3]"),
    ("crit",      "metal crack",         "duration:[0 TO 4]"),
    ("hurt",      "impact crunch",       "duration:[0 TO 3]"),
    ("crush",     "metal groan",         "duration:[0 TO 6]"),
    ("kill",      "metal crash",         "duration:[0 TO 6]"),
    ("seam",      "servo groan",         "duration:[0 TO 4]"),
    ("dray",      "motor idle",          "duration:[0 TO 8]"),
    ("tally",     "digital beeps",       "duration:[0 TO 4]"),
    ("seal",      "hydraulic hiss",      "duration:[0 TO 5]"),
    ("brk",       "pneumatic exhaust",   "duration:[0 TO 5]"),
    ("roar",      "machine roar",        "duration:[1 TO 8]"),
    ("amb_drone", "industrial hum",      "duration:[15 TO 120]"),
    ("amb_wind",  "wind interior",       "duration:[15 TO 120]"),
    ("hammer",    "pile driver",         "duration:[0 TO 6]"),
    ("saw",       "circular saw",        "duration:[0 TO 6]"),
]


def main():
    try:                       # sound names are full of unicode; cp1251 chokes
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a_ = sub.add_parser("all", help="grab candidates for every key in KEYS")
    a_.add_argument("-n", type=int, default=5)
    a_.add_argument("--only", default="", help="comma-separated keys")

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--extra", default="", help='more filters, e.g. "duration:[0 TO 2]"')

    g = sub.add_parser("grab")
    g.add_argument("key")
    g.add_argument("query")
    g.add_argument("-n", type=int, default=5)
    g.add_argument("--extra", default="")

    a = ap.parse_args()
    if a.cmd == "all":
        only = [k.strip() for k in a.only.split(",") if k.strip()]
        for key, query, extra in KEYS:
            if only and key not in only:
                continue
            done = os.path.join(RAW, key)
            if os.path.isdir(done) and os.listdir(done):
                print("%s — already have %d, skipping"
                      % (key, len(os.listdir(done))))
                continue
            print("%s <- %s" % (key, query))
            try:
                grab(key, query, a.n, extra)
            except Exception as e:
                print("  search failed: %s" % str(e)[:80])
            time.sleep(PACE)
        return
    if a.cmd == "search":
        for i, h in enumerate(search(a.query, a.n, extra=a.extra), 1):
            print("  %2d. %-9s %6.2fs  %s" % (i, h["id"], h["sec"], h["name"][:70]))
    else:
        print("%s <- %s" % (a.key, a.query))
        grab(a.key, a.query, a.n, a.extra)


if __name__ == "__main__":
    main()
