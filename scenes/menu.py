# scenes/menu.py - the title, the list of modes, and the name box.  (Theo)
#
# Up and Down move through the list, Enter picks. Letters and numbers go
# straight into the name, so there's no separate "edit name" step.

import math

import settings
from render.buffer import bloom
from render.draw import draw_text, draw_text_centered, draw_label_centered, text_width
from render.easing import progress, ease_out
from scenes import backdrop
import sound

# (where Enter goes, what the list says, the small print under the title)
ITEMS = [
    ("classic", "CLASSIC", "press the key for the INK color, not the word"),
    ("reverse", "REVERSE", "press the key for the WORD, ignore the ink"),
    ("speed", "SPEED", "like classic, but the word hides after 0.7 seconds"),
    ("head_to_head", "HEAD TO HEAD", "two players, one keyboard:  A S D F G  against  H J K L ;"),
    ("leaderboard", "LEADERBOARD", "the best runs so far"),
    ("intro", "REPLAY INTRO", "watch the opening again"),
]
CREDIT = "Made for CIS 1051 Rosen Final Project - Oliver, Theo, Issaka"
MAX_NAME = 10
CX = settings.GRID_W / 2


def start(app):
    return {
        "t0": None,
        "choice": app["menu_choice"],
        "moved_at": 0,               # when the selection last changed, for the little slide
        "stars": backdrop.make_stars(70),
        "comets": backdrop.make_comets(3),
    }


def on_key(scene, app, key, when):
    if key == "up" or key == "down":
        step = -1 if key == "up" else 1
        scene["choice"] = (scene["choice"] + step) % len(ITEMS)
        scene["moved_at"] = when
        app["menu_choice"] = scene["choice"]
        sound.play("click")
    elif key == "enter":
        target = ITEMS[scene["choice"]][0]
        if app["player"] == "":
            app["player"] = "PLAYER"
        if target == "leaderboard" or target == "intro":
            return target
        app["mode"] = target
        if target == "head_to_head":
            return "duel"
        return "game"
    elif key == "backspace":
        app["player"] = app["player"][:-1]
    elif len(key) == 1 and key.isalnum() and len(app["player"]) < MAX_NAME:
        app["player"] += key.upper()
    return None


def draw(scene, app, buffer, now):
    if scene["t0"] is None:
        scene["t0"] = now
    age = now - scene["t0"]

    backdrop.draw_stars(buffer, scene["stars"], now, 0.6)
    backdrop.draw_comets(buffer, scene["comets"], now, 0.7)

    # the title drops in from above when the menu opens
    drop = ease_out(progress(age, 0, 0.5))
    backdrop.draw_rainbow_text(buffer, CX, 6 - (1 - drop) * 20, "THE COLOR GAME", 2, 1.0, now)
    bloom(buffer, 0.65, 0.25)        # glow the title only: small text is drawn after, so it stays sharp
    draw_label_centered(buffer, CX, 23, ITEMS[scene["choice"]][2], "white")

    y = 27
    for number, item in enumerate(ITEMS):
        label = item[1]
        # each line slides in from the side, one after the other
        slide = (1 - ease_out(progress(age, 0.1 + number * 0.06, 0.4))) * 40
        if number == scene["choice"]:
            nudge = 3 * ease_out(progress(now, scene["moved_at"], 0.15))
            x = CX - text_width(label) / 2 + slide + nudge
            draw_text(buffer, x, y, label, 1.0, "accent")
            bob = math.sin(now * 6) * 1.5                      # the arrow bobs left and right
            draw_text(buffer, x - 10 + bob, y, ">", 1.0, "accent")
        else:
            draw_text_centered(buffer, CX + slide, y, label, 1, 0.8, "gray")
        y += 8

    # the name, with a blinking cursor
    name = "NAME " + app["player"]
    x = CX - text_width(name + "_") / 2
    draw_text(buffer, x, 77, name, 0.8)
    if int(now * 2) % 2 == 0:
        draw_text(buffer, x + text_width(name) + 1, 77, "_", 0.8, "accent")
    draw_label_centered(buffer, CX, 86, CREDIT, "accent")
    draw_label_centered(buffer, CX, 88, "UP / DOWN  choose      ENTER  start      type to change your name", "white")
    return None
