# scenes/results.py - how the run went: three tiles and a chart of bars.  (Theo)
#
# The numbers count up and the bars grow when the screen opens.
# R plays the same mode again, M goes back to the menu.

import settings
from core import scoring
from render.buffer import set_pixel, bloom
from render.draw import draw_rect, draw_text_centered, draw_label_centered, text_width
from render.easing import progress, ease_out
from scenes import backdrop

CX = settings.GRID_W / 2
TILE_W = 48
TILE_H = 24
TILE_Y = 26
BARS_BOTTOM = 74


def start(app):
    return {
        "t0": None,
        "summary": scoring.summarize(app["last_run"]["results"]),
        "stars": backdrop.make_stars(60),
        "comets": backdrop.make_comets(2),
    }


def on_key(scene, app, key, when):
    if key == "r":
        return "game"
    if key in ("m", "escape", "enter"):
        return "menu"
    return None


def draw(scene, app, buffer, now):
    if scene["t0"] is None:
        scene["t0"] = now
    grow = ease_out(progress(now - scene["t0"], 0.2, 0.9))     # 0 to 1 as the screen opens
    summary = scene["summary"]
    run = app["last_run"]

    backdrop.draw_stars(buffer, scene["stars"], now, 0.5)
    backdrop.draw_comets(buffer, scene["comets"], now, 0.6)
    backdrop.draw_rainbow_text(buffer, CX, 4, "RESULTS", 2, 1.0, now)
    bloom(buffer, 0.65, 0.25)        # glow the title only
    draw_label_centered(buffer, CX, 21, "%s   -   %s   -   %d / %d correct" % (
        run["player"], run["mode"].replace("_", " "), summary["correct"], summary["trials"]))

    tiles = [
        ("%d" % (summary["mean_rt"] * grow), "MEAN REACTION TIME (MS)"),
        ("%d" % (summary["accuracy"] * 100 * grow), "ACCURACY (%)"),
        ("%+d" % (summary["stroop_effect_ms"] * grow), "STROOP EFFECT (MS)"),
    ]
    x = 4
    for number, label in tiles:
        draw_tile(buffer, x, number, label)
        x += TILE_W + 4
    draw_label_centered(buffer, CX, 52,
                        "the Stroop effect is how much slower you were when the word and the ink didn't match")

    draw_bars(buffer, summary["reaction_times"], summary["correct_flags"], grow)
    draw_label_centered(buffer, CX, 77, "reaction time for each word, first to last (red = wrong)")
    draw_text_centered(buffer, CX, 81, "R AGAIN    M MENU", 1, 1.0, "accent")
    return None


def draw_tile(buffer, x, number, label):
    """A box with a big number in it and small print underneath."""
    draw_rect(buffer, x, TILE_Y, TILE_W, TILE_H, 0.5, "accent")
    scale = 2
    if text_width(number, 2) > TILE_W - 4:        # too long for the box: use small digits
        scale = 1
    draw_text_centered(buffer, x + TILE_W / 2, TILE_Y + 11 - 3.5 * scale, number, scale, 1.0)
    draw_label_centered(buffer, x + TILE_W / 2, TILE_Y + TILE_H - 4, label)


def draw_bars(buffer, times, correct_flags, grow):
    """A sparkline you can read from across the room: one bar per word, taller = slower."""
    if len(times) == 0:
        return
    slowest = max(max(times), 1)
    step = min(4, 150 // len(times))              # 3 pixels of bar, 1 of gap, if they fit
    left = CX - len(times) * step / 2
    for i in range(len(times)):
        height = int((2 + 15 * times[i] / slowest) * grow)
        color = "accent" if correct_flags[i] else "red"
        for dy in range(height):
            # brighter toward the top, so each bar is a little gradient of characters
            glow = 0.5 + 0.5 * dy / 17
            for dx in range(max(1, step - 1)):
                set_pixel(buffer, left + i * step + dx, BARS_BOTTOM - dy, glow, color)
