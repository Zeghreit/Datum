"""Build the audition page for everything sitting in sfx/_raw/.

I cannot hear any of these, so the choosing has to be yours, and choosing is
only cheap if it is fast: one page, every candidate for every key, keyboard
driven, and a line of text at the end that tells the cutter what won.

    py build\\datum_audition.py
    start E:\\ClaudeFiles\\Datum\\sfx\\_raw\\audition.html

J and K move through the list, Space plays, Enter picks. The bar at the bottom
says how many keys are still undecided. "Скопировать выбор" puts the whole
result on the clipboard as one line to paste back into the chat.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "sfx", "_raw")
OUT = os.path.join(RAW, "audition.html")

# what the key is supposed to be, so the ear knows what it is judging
WANT = {
    "step":      "шаг бронированного сапога по стальной плите, глухо и с крошкой",
    "turn":      "разворот на месте, короткое шарканье по железу",
    "bump":      "плечом в стену: глухой заблокированный удар, без звона",
    "swap":      "переключение реле, жёсткий щелчок",
    "print":     "фабрикатор: шипение, вой сервы, тяжёлый замок",
    "cut":       "резак прожигает лист, шипение и плевки металла",
    "slam":      "таранная плита в металл, низкий удар с гулом конструкции",
    "thrust":    "тонкий щуп протыкает лист, один точный укол",
    "pulse":     "ремонтный разряд: мягкий электрический гул, тёплый и чистый",
    "clank":     "удар по толстой броне, металлический с коротким звоном",
    "crit":      "броня раскалывается: резкий треск, потом рвущийся металл",
    "hurt":      "попали по тебе: глухой хруст с дребезгом пластин",
    "crush":     "зажим медленно смыкается, сталь стонет под давлением",
    "kill":      "машина рушится: взрыв внутри, падают плиты, оседает щебень",
    "seam":      "сварочный дрон под нагрузкой: механический стон, вой сервы",
    "dray":      "равнодушный мотор на холостых, ритмичный стук, неторопливо",
    "tally":     "прибор сканирует: быстрая череда щелчков и писков",
    "seal":      "зажим сбрасывает давление и защёлкивается",
    "brk":       "пневморам набирает давление, глубокий выдох перед ударом",
    "roar":      "Кадавр просыпается: скрежет, глубокий искажённый рёв машины",
    "amb_drone": "бесконечный низкий гул мегаструктуры, петля",
    "amb_wind":  "сквозняк в огромном пустом объёме, петля",
    "hammer":    "далёкий копёр бьёт по конструкции, один удар",
    "saw":       "отрезной диск раскручивается и врезается в металл, вдалеке",
}

ORDER = ["step", "clank", "hurt", "seam", "kill", "crush", "swap", "roar",
         "amb_drone", "turn", "bump", "print", "cut", "slam", "thrust",
         "pulse", "crit", "dray", "tally", "seal", "brk", "amb_wind",
         "hammer", "saw"]

CSS = """
:root { --bg:#0b0c0e; --fg:#c8ccd2; --dim:#6a6f78; --hot:#e8a33d; --bad:#d4553f;
        --line:#1c1f24; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:14px/1.5 ui-monospace,
       Menlo, Consolas, monospace; padding:0 0 92px; }
header { padding:26px 28px 14px; border-bottom:1px solid var(--line); }
h1 { font-size:15px; letter-spacing:.34em; margin:0 0 6px; color:var(--hot);
     font-weight:400; }
.sub { color:var(--dim); font-size:12px; }
.key { border-bottom:1px solid var(--line); padding:16px 28px; }
.key.done { opacity:.55; }
.kh { display:flex; align-items:baseline; gap:14px; margin-bottom:8px; }
.kn { color:var(--hot); letter-spacing:.2em; font-size:13px; min-width:104px; }
.kw { color:var(--dim); font-size:12px; }
.row { display:flex; align-items:center; gap:12px; padding:5px 8px; cursor:pointer;
       border-left:2px solid transparent; }
.row:hover { background:#111318; }
.row.cur { border-left-color:var(--hot); background:#12151b; }
.row.pick { background:#1a1408; }
.row.pick .nm { color:var(--hot); }
.mark { width:14px; color:var(--hot); }
.sec { color:var(--dim); width:56px; text-align:right; font-size:12px; }
.nm { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.id { color:#454a53; font-size:11px; }
footer { position:fixed; left:0; right:0; bottom:0; background:#0e1014;
         border-top:1px solid var(--line); padding:14px 28px; display:flex;
         align-items:center; gap:18px; }
button { background:#171a20; color:var(--fg); border:1px solid #2a2f38;
         padding:8px 16px; font:inherit; cursor:pointer; letter-spacing:.1em; }
button:hover { border-color:var(--hot); color:var(--hot); }
.count { color:var(--dim); font-size:12px; }
kbd { background:#171a20; border:1px solid #2a2f38; padding:1px 6px; font-size:11px;
      color:var(--dim); }
"""

JS = """
const rows = [...document.querySelectorAll('.row')];
const picks = {};
let cur = 0;
let audio = new Audio();

function paint() {
  rows.forEach((r, i) => r.classList.toggle('cur', i === cur));
  rows.forEach(r => r.classList.toggle('pick', picks[r.dataset.key] === r.dataset.id));
  document.querySelectorAll('.key').forEach(k =>
    k.classList.toggle('done', !!picks[k.dataset.key]));
  const n = Object.keys(picks).length, total = document.querySelectorAll('.key').length;
  document.querySelector('.count').textContent =
    n + ' из ' + total + ' выбрано' + (n < total ? ' · осталось ' + (total - n) : '');
  rows[cur] && rows[cur].scrollIntoView({block:'center', behavior:'smooth'});
}

function play(i) {
  const r = rows[i]; if (!r) return;
  audio.pause(); audio = new Audio(r.dataset.src); audio.play().catch(()=>{});
}

function pick(i) {
  const r = rows[i]; if (!r) return;
  picks[r.dataset.key] = picks[r.dataset.key] === r.dataset.id ? undefined : r.dataset.id;
  if (!picks[r.dataset.key]) delete picks[r.dataset.key];
  paint();
}

rows.forEach((r, i) => {
  r.onclick = () => { cur = i; play(i); paint(); };
  r.querySelector('.mark').onclick = e => { e.stopPropagation(); cur = i; pick(i); };
});

document.onkeydown = e => {
  if (e.key === 'j' || e.key === 'ArrowDown') { cur = Math.min(cur+1, rows.length-1); play(cur); paint(); }
  else if (e.key === 'k' || e.key === 'ArrowUp') { cur = Math.max(cur-1, 0); play(cur); paint(); }
  else if (e.key === ' ') { play(cur); }
  else if (e.key === 'Enter') { pick(cur); }
  else return;
  e.preventDefault();
};

document.querySelector('#copy').onclick = () => {
  const line = Object.entries(picks).map(([k, v]) => k + '=' + v).join(' ');
  navigator.clipboard.writeText(line);
  const b = document.querySelector('#copy');
  b.textContent = 'скопировано'; setTimeout(() => b.textContent = 'Скопировать выбор', 1400);
};

paint();
"""


def main():
    if not os.path.isdir(RAW):
        raise SystemExit("nothing in sfx/_raw — run datum_freesound.py first")

    keys = [k for k in ORDER if os.path.isdir(os.path.join(RAW, k))]
    keys += sorted(k for k in os.listdir(RAW)
                   if os.path.isdir(os.path.join(RAW, k)) and k not in keys)

    parts = ["<!doctype html><meta charset='utf-8'><title>DATUM · прослушивание</title>",
             "<style>%s</style>" % CSS,
             "<header><h1>DATUM · ПРОСЛУШИВАНИЕ</h1><div class='sub'>"
             "<kbd>J</kbd> <kbd>K</kbd> ходить · <kbd>Space</kbd> играть · "
             "<kbd>Enter</kbd> выбрать · клик по кружку тоже выбирает"
             "</div></header>"]

    total = 0
    for key in keys:
        files = sorted(f for f in os.listdir(os.path.join(RAW, key))
                       if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac")))
        if not files:
            continue
        parts.append("<section class='key' data-key='%s'><div class='kh'>"
                     "<span class='kn'>%s</span><span class='kw'>%s</span></div>"
                     % (key, key, html.escape(WANT.get(key, ""))))
        for fn in files:
            sid = fn.rsplit("__", 1)[-1].rsplit(".", 1)[0]
            src = "./%s/%s" % (key, fn)
            parts.append(
                "<div class='row' data-key='%s' data-id='%s' data-src='%s'>"
                "<span class='mark'>○</span><span class='sec'></span>"
                "<span class='nm'>%s</span><span class='id'>%s</span></div>"
                % (key, sid, html.escape(src), html.escape(fn), sid))
            total += 1
        parts.append("</section>")

    parts.append("<footer><button id='copy'>Скопировать выбор</button>"
                 "<span class='count'></span></footer>")
    parts.append("<script>%s</script>" % JS)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote %s — %d keys, %d candidates" % (OUT, len(keys), total))


if __name__ == "__main__":
    main()
