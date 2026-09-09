"""Post for sfx/ — makes generated audio fit to be baked into the game.

Generators hand back studio-weight files that start with silence, sit at random
loudness and do not loop. This turns them into what the engine wants: mono,
44.1k, ogg, level-matched, and — for the music and the ambience beds — actually
seamless.

    py build\\datum_audio.py info
    py build\\datum_audio.py loop music_boss music_combat --xfade 4
    py build\\datum_audio.py trim step clank hurt

The seam: a loop is cut to D-X seconds, and the last X seconds of the source are
faded in over the first X of the result while those fade out. The end of the file
then runs into its own start, because the material either side of the join is
the same material. Equal-power curves, so the level does not dip in the middle.

The original is never destroyed — it moves to sfx/spare/ and the .ogg takes its
place. ffmpeg comes from the imageio-ffmpeg wheel, so there is nothing on PATH
to install or keep in sync.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(HERE, "sfx")
SPARE = os.path.join(SFX, "spare")
EXTS = (".wav", ".mp3", ".ogg", ".m4a", ".flac", ".webm", ".aac", ".opus")

# mono, one rate, one format — every later filter can then assume all three
HEAD = "aresample=44100,aformat=sample_fmts=fltp:channel_layouts=mono"


def find(key):
    """The file currently standing for this key, whatever extension it wears."""
    for fn in sorted(os.listdir(SFX)):
        stem, ext = os.path.splitext(fn)
        if stem.lower() == key.lower() and ext.lower() in EXTS:
            return os.path.join(SFX, fn)
    return None


def probe(path):
    """Duration in seconds and peak level in dBFS, from ffmpeg's own report."""
    p = subprocess.run([FF, "-hide_banner", "-i", path, "-af", "volumedetect",
                        "-f", "null", "-"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    err = p.stderr
    dur = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", err)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    peak = None
    m = re.search(r"max_volume:\s*(-?\d+\.?\d*) dB", err)
    if m:
        peak = float(m.group(1))
    return dur, peak


def encode(src, dst, chain, q):
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
           "-filter_complex", chain, "-map", "[out]",
           "-c:a", "libvorbis", "-q:a", str(q), dst]
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode:
        sys.exit("ffmpeg failed on %s\n%s" % (os.path.basename(src), p.stderr[-1500:]))


def install(src, tmp, key):
    """Put the .ogg in place and retire the source into spare/."""
    out = os.path.join(SFX, key + ".ogg")
    os.makedirs(SPARE, exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(out):
        shutil.move(src, os.path.join(SPARE, os.path.basename(src)))
    elif os.path.exists(out):
        os.remove(out)
    shutil.move(tmp, out)
    return out


def do_loop(key, xfade, lufs, q):
    src = find(key)
    if not src:
        print("  %-16s no file" % key)
        return
    dur, _ = probe(src)
    if dur <= 0:
        print("  %-16s unreadable" % key)
        return
    x = min(xfade, dur / 3.0)
    body_end = dur - x
    chain = (
        "[0:a]{h},asplit=3[a][b][c];"
        "[a]atrim=0:{x:.3f},asetpts=PTS-STARTPTS,"
        "afade=t=out:st=0:d={x:.3f}:curve=qsin[head];"
        "[b]atrim={e:.3f}:{d:.3f},asetpts=PTS-STARTPTS,"
        "afade=t=in:st=0:d={x:.3f}:curve=qsin[tail];"
        "[head][tail]amix=inputs=2:normalize=0[join];"
        "[c]atrim={x:.3f}:{e:.3f},asetpts=PTS-STARTPTS[body];"
        "[join][body]concat=n=2:v=0:a=1,"
        "loudnorm=I={l}:TP=-1.5:LRA=11,{h}[out]"
    ).format(h=HEAD, x=x, e=body_end, d=dur, l=lufs)
    tmp = os.path.join(SFX, key + ".tmp.ogg")
    encode(src, tmp, chain, q)
    out = install(src, tmp, key)
    print("  %-16s %5.1fs -> %5.1fs loop, xfade %.1fs, %6.0f kb (was %5.0f kb)"
          % (key, dur, dur - x, x, os.path.getsize(out) / 1024,
             os.path.getsize(os.path.join(SPARE, os.path.basename(src))) / 1024))


def do_trim(key, headroom, q):
    """One-shots: drop the leading silence, bring the peak up to a common level."""
    src = find(key)
    if not src:
        print("  %-16s no file" % key)
        return
    dur, peak = probe(src)
    gain = 0.0 if peak is None else (headroom - peak)
    chain = ("[0:a]{h},"
             "silenceremove=start_periods=1:start_silence=0:start_threshold=-55dB,"
             "volume={g:.2f}dB,{h}[out]").format(h=HEAD, g=gain)
    tmp = os.path.join(SFX, key + ".tmp.ogg")
    encode(src, tmp, chain, q)
    out = install(src, tmp, key)
    new_dur, new_peak = probe(out)
    print("  %-16s %5.2fs -> %5.2fs, peak %+.1f -> %+.1f dB, %5.0f kb"
          % (key, dur, new_dur, peak or 0.0, new_peak or 0.0,
             os.path.getsize(out) / 1024))


# How long each cue is allowed to be. A one-shot that outlasts the turn it
# belongs to smears into the next one, and the brief's timings are what the
# engine's own synthesis was written against.
TARGET = {
    "step": 0.35, "turn": 0.25, "bump": 0.35, "swap": 0.25, "print": 1.2,
    "cut": 0.45, "slam": 0.60, "thrust": 0.25, "pulse": 0.50, "clank": 0.35,
    "crit": 0.60, "hurt": 0.55, "crush": 0.70, "kill": 1.40, "seam": 0.70,
    "dray": 0.80, "tally": 0.60, "seal": 0.90, "brk": 0.80, "roar": 3.00,
    "hammer": 1.20, "saw": 2.00,
}
LOOPS = ("amb_drone", "amb_wind")
RAW = os.path.join(SFX, "_raw")


def raw_for(key, sid):
    d = os.path.join(RAW, key)
    if not os.path.isdir(d):
        return None
    for fn in sorted(os.listdir(d)):
        if fn.rsplit("__", 1)[-1].rsplit(".", 1)[0] == sid:
            return os.path.join(d, fn)
    return None


def do_pick(key, sid, start, q):
    """Take one audition candidate and make it the key, at the right length."""
    src = raw_for(key, sid)
    if not src:
        print("  %-10s no candidate %s in _raw" % (key, sid))
        return
    dur, peak = probe(src)
    gain = 0.0 if peak is None else (-1.0 - peak)
    out = os.path.join(SFX, key + ".ogg")

    if key in LOOPS:
        x = min(2.5, dur / 3.0)
        e = dur - x
        chain = ("[0:a]{h},asplit=3[a][b][c];"
                 "[a]atrim=0:{x:.3f},asetpts=PTS-STARTPTS,"
                 "afade=t=out:st=0:d={x:.3f}:curve=qsin[head];"
                 "[b]atrim={e:.3f}:{d:.3f},asetpts=PTS-STARTPTS,"
                 "afade=t=in:st=0:d={x:.3f}:curve=qsin[tail];"
                 "[head][tail]amix=inputs=2:normalize=0[join];"
                 "[c]atrim={x:.3f}:{e:.3f},asetpts=PTS-STARTPTS[body];"
                 "[join][body]concat=n=2:v=0:a=1,"
                 "loudnorm=I=-22:TP=-2:LRA=11,{h}[out]").format(h=HEAD, x=x, e=e, d=dur)
        note = "loop %.1fs" % (dur - x)
    else:
        want = TARGET.get(key, 1.0)
        fade = min(0.06, want / 4)
        chain = ("[0:a]{h},atrim=start={s:.3f},asetpts=PTS-STARTPTS,"
                 "silenceremove=start_periods=1:start_silence=0:start_threshold=-55dB,"
                 "atrim=0:{w:.3f},asetpts=PTS-STARTPTS,"
                 "afade=t=out:st={fo:.3f}:d={f:.3f}:curve=qsin,"
                 "volume={g:.2f}dB,{h}[out]"
                 ).format(h=HEAD, s=start, w=want, fo=max(0.0, want - fade),
                          f=fade, g=gain)
        note = "%.2fs" % want

    tmp = out + ".tmp.ogg"
    encode(src, tmp, chain, q)
    if os.path.exists(out):
        os.remove(out)
    shutil.move(tmp, out)
    print("  %-10s <- %-9s %s, %5.0f kb   %s"
          % (key, sid, note, os.path.getsize(out) / 1024,
             os.path.basename(src)[:40]))


def do_info():
    print("  %-18s %8s %8s %8s" % ("key", "sec", "peak dB", "kb"))
    for fn in sorted(os.listdir(SFX)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in EXTS:
            continue
        path = os.path.join(SFX, fn)
        d, p = probe(path)
        print("  %-18s %8.2f %8.1f %8.0f"
              % (stem, d, p if p is not None else 0.0,
                 os.path.getsize(path) / 1024))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("loop", help="seamless loop + level match (music, ambience)")
    s.add_argument("keys", nargs="+")
    s.add_argument("--xfade", type=float, default=4.0, help="crossfade seconds")
    s.add_argument("--lufs", type=float, default=-19.0, help="target loudness")
    s.add_argument("-q", type=int, default=2, help="vorbis quality (0..10)")

    s = sub.add_parser("trim", help="cut leading silence + peak match (one-shots)")
    s.add_argument("keys", nargs="+")
    s.add_argument("--peak", type=float, default=-1.0, help="target peak dBFS")
    s.add_argument("-q", type=int, default=4, help="vorbis quality (0..10)")

    s = sub.add_parser("pick", help='apply audition picks: "step=815039 clank=842171"')
    s.add_argument("picks", nargs="+")
    s.add_argument("--start", type=float, default=0.0,
                   help="skip this many seconds into the source first")
    s.add_argument("-q", type=int, default=4)

    sub.add_parser("info", help="what is in sfx/ right now")

    a = ap.parse_args()
    if a.cmd == "info":
        return do_info()
    if a.cmd == "pick":
        print("ffmpeg %s" % os.path.basename(FF))
        for token in " ".join(a.picks).replace(",", " ").split():
            if "=" not in token:
                print("  skipping %r — expected key=id" % token)
                continue
            key, sid = token.split("=", 1)
            do_pick(key.strip(), sid.strip(), a.start, a.q)
        return
    print("ffmpeg %s" % os.path.basename(FF))
    for k in a.keys:
        if a.cmd == "loop":
            do_loop(k, a.xfade, a.lufs, a.q)
        else:
            do_trim(k, a.peak, a.q)


if __name__ == "__main__":
    main()
