"""Smoke-test the party panel: start a run, fire abilities, screenshot the HUD."""
from playwright.sync_api import sync_playwright

URL = "file:///E:/ClaudeFiles/Datum/dist/DATUM.html"
SHOT = r"E:\ClaudeFiles\Datum\build\_ui.png"

with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    pg = br.contexts[0].new_page()
    pg.set_viewport_size({"width": 1280, "height": 760})
    errs = []
    pg.on("console", lambda m: errs.append(m.type + ": " + m.text[:160])
          if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)[:250]))

    pg.goto(URL, wait_until="load", timeout=120000)
    pg.wait_for_timeout(1500)
    pg.mouse.click(640, 400)                       # end the teletype
    pg.wait_for_timeout(1200)
    # skip the shell menu — this is a mechanics check, not a menu check
    print("gate", pg.evaluate(
        "() => { try { if (typeof endBoot === 'function') endBoot(); } catch (e) {}"
        " try { menuOpen = false; } catch (e) {}"
        " try { resetBodies(); } catch (e) {}"
        " const m = document.getElementById('menu'); if (m) m.style.display = 'none';"
        " return { boot: !!bootEl, menu: menuOpen, alive: alive() }; }"))
    pg.wait_for_timeout(600)

    for key in ["Digit2", "KeyF", "Space", "KeyQ", "Digit1", "KeyF",
                "Digit3", "KeyR", "Digit4", "KeyF", "KeyF"]:
        pg.keyboard.press(key)
        pg.wait_for_timeout(450)

    pg.wait_for_timeout(900)
    print(pg.evaluate(
        "() => bodies.map(b => b.k + ' hp' + Math.round(b.hp) +"
        " ' cd' + b.cd.join('/') + ' sh' + b.shield + ' dg' + b.dodge).join(' | ')"))
    print("tick", pg.evaluate("() => tickNo"))
    pg.screenshot(path=SHOT, clip={"x": 380, "y": 480, "width": 560, "height": 280})
    for e in errs[:10]:
        print("  ", e)
    pg.close()
