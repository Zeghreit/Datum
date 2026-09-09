# DATUM — звуковое задание

Каждый звук ниже заменяет синтезированный. Файл называется **ключом**, регистр не важен, расширение любое из `wav mp3 ogg m4a flac`.

Два способа поставить:

- **Проверить на лету** — перетащить файл на окно игры. Вверху мигнёт `SOUND · step`.
- **Вшить насовсем** — положить в папку `sfx/` рядом с `datum_inline.py` и пересобрать. Всё, чего нет, остаётся синтезированным, так что можно вставлять по одному.

Общее для всех: **моно, без реверберации** — она добавляется движком и зависит от помещения. Обрезать тишину в начале, иначе действие будет запаздывать.

---

## Где генерировать

| Сервис | Плюс | Минус |
|---|---|---|
| **elevenlabs.io/sound-effects** | лучшее качество, до 22 сек, коммерческие права | нужен аккаунт, бесплатный лимит |
| **gensfx.com** | без регистрации | 2 попытки за раз |
| **sunra.ai/ai-sound-effect-generator** | без регистрации и вотермарка | — |
| **overchat.ai/audio/ai-sound-effect-generator** | без аккаунта, выбор моделей | — |
| **freesound.org** | живые записи, не генерация | нужен аккаунт, разные лицензии |

Для музыки и петель лучше ElevenLabs — остальные плохо держат длину и зацикливание.

---

## Действия

| Ключ | Длина | Промпт |
|---|---|---|
| `step` | 0.3 с | heavy armoured boot stepping on a metal floor plate inside a concrete corridor, single dull impact with grit, dry, no reverb |
| `turn` | 0.2 с | armoured figure pivoting on a gritty metal floor, short scrape of boot on steel, dry |
| `bump` | 0.3 с | armoured shoulder colliding with a solid steel wall, dull blocked thud, no clang |
| `swap` | 0.2 с | industrial relay switching over, hard mechanical click with a faint electrical snap |
| `print` | 1.2 с | industrial fabricator cycling: pneumatic hiss, servo whine rising, then a heavy clamp locking shut |

## Удары отряда

| Ключ | Длина | Промпт |
|---|---|---|
| `cut` | 0.4 с | industrial cutting torch firing a short burst through steel plate, hiss and spitting metal |
| `slam` | 0.5 с | massive blunt ram plate driven into thick metal, deep low impact with structural boom |
| `thrust` | 0.2 с | thin steel probe punching cleanly through a plate, single sharp precise stab |
| `pulse` | 0.5 с | repair device discharging, soft electrical hum swelling and releasing, warm and clean |

## Попадания и урон

| Ключ | Длина | Промпт |
|---|---|---|
| `clank` | 0.3 с | hard blow landing on thick armour plating, metallic impact with short inharmonic ring |
| `crit` | 0.5 с | devastating strike splitting an armour plate open, sharp crack then tearing metal |
| `hurt` | 0.5 с | heavy impact on a worn armoured body, dull crunching thud with rattling plates |
| `crush` | 0.5 с | hydraulic clamp slowly closing on a metal body, groaning steel buckling under pressure |
| `kill` | 1.2 с | large machine collapsing: internal explosion, plates falling, debris settling on concrete |

## Голоса машин

Не животные — механизмы, у которых голос получается случайно.

| Ключ | Длина | Промпт |
|---|---|---|
| `seam` | 0.6 с | heavy welding drone straining under load, low mechanical groan with servo whine, no organic quality |
| `dray` | 0.6 с | low indifferent industrial motor idling, dull rhythmic clunking, unhurried |
| `tally` | 0.5 с | survey instrument scanning: rapid ascending series of sharp digital clicks and beeps |
| `seal` | 0.8 с | hydraulic clamp releasing pressure then snapping shut, sharp pneumatic hiss and heavy metallic lock |
| `brk` | 0.7 с | pneumatic demolition ram charging up, deep pressurised exhale before a strike |
| `roar` | 2.5 с | enormous derelict machine waking after centuries: grinding metal, deep distorted mechanical bellow, structural groan |

`roar` — это пробуждение Кадавра, самый важный звук в первом секторе. Стоит потратить на него несколько попыток.

## Фон

| Ключ | Длина | Промпт |
|---|---|---|
| `amb_drone` | 20 с, петля | endless low structural hum inside a vast abandoned concrete megastructure, distant machinery, seamless loop |
| `amb_wind` | 20 с, петля | wind moving through an enormous empty industrial space, hollow and directionless, seamless loop |
| `hammer` | 1.0 с | distant pile hammer striking structural steel once, heavy and far away with long decay |
| `saw` | 2.0 с | large cutting disc spinning up and biting into metal, distant |

## Музыка

Три петли, движок сам их сводит.

| Ключ | Длина | Промпт |
|---|---|---|
| `music_ambient` | 60 с, петля | dark ambient drone, slow unresolved minor chord, industrial and cold, no percussion, no melody, seamless loop |
| `music_approach` | 45 с, петля | tense dark ambient, one low breathing note with a semitone above it that never resolves, no drums, dread, seamless loop |
| `music_combat` | 60 с, петля | dark trance 140 bpm, four on the floor kick, acid bassline in D minor, dissonant pad, industrial, no vocals, seamless loop |

Как только появляется `music_ambient` или `music_combat`, генеративный слой под ним отключается сам.

---

## Порядок, в котором это стоит делать

Не всё сразу. Каждый файл слышен отдельно, так что имеет смысл идти от того, что звучит чаще.

1. `step` — звучит чаще всего остального вместе взятого
2. `clank`, `hurt`, `crush` — весь бой держится на них
3. `roar` — единственное событие в секторе
4. `music_combat` — вторая по заметности вещь после шага
5. `amb_drone`, `amb_wind` — фон, на котором всё лежит
6. остальное
