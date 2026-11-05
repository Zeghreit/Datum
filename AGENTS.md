# AGENTS — DATUM

Перед началом сессии:
1. Прочитай `PROJECT.md`, `README.md` и `docs/DATUM-handover.md`.
2. Если есть `STATE.md`/`HANDOFF.md` — прочитай их.
3. Дизайн-ядро — `gdd/datum-gdd.md` и `gdd/datum-gates.md`. `docs/DATUM-design.md` устарел (v1).

В конце сессии:
- Обнови `STATE.md`/`HANDOFF.md`, если они есть; не создавай и не перезаписывай их без разрешения.
- Если менялся статус — обнови `PROJECT.md`.

Правила:
- Прототип — `datum-prototype.html`; сборка — `py build\make.py` → `dist/DATUM.html`.
- Проверка сборки — `py build\datum_smoke.py` (headless Chrome, код возврата 1 = игра не открылась).
- `dist` должен оставаться автономным: three.js вшивается из `build/vendor/`, внешних ссылок в сборке нет.
- Дизайн: решения автора дописывать с датой в `gdd/` (документ + журнал в `datum-gates.md`), предложения помечать **[предложение]**.
- Звук — `docs/DATUM-sound-brief.md`.
- Не перезаписывай `dist/` вручную: пересобирай.
