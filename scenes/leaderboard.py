# scenes/leaderboard.py - the ten best finished runs for each mode.  (Theo)
#
# Left and Right switch between modes. The rows come from results/trials.csv,
# read once when the screen opens.

import settings
from data.analyze import load_trials
from data.leaderboard import top_scores
from render.draw import draw_text_centered, draw_label_centered
from render.buffer import add_label, bloom
from render.easing import progress, ease_out
from scenes import backdrop

CX = settings.GRID_W / 2
TABLE_X = 48                     # left edge of the table, in cells


def start(app):
    return {
        "t0": None,
        "trials": load_trials(),
        "mode_index": settings.MODES.index(app["mode"]),
        "stars": backdrop.make_stars(60),
        "comets": backdrop.make_comets(2),
    }


def on_key(scene, app, key, when):
    if key == "left" or key == "right":
        step = -1 if key == "left" else 1
        scene["mode_index"] = (scene["mode_index"] + step) % len(settings.MODES)
        scene["t0"] = when           # replay the rows sliding in
    elif key in ("m", "escape", "enter"):
        return "menu"
    return None


def draw(scene, app, buffer, now):
    if scene["t0"] is None:
        scene["t0"] = now
    age = now - scene["t0"]
    mode = settings.MODES[scene["mode_index"]]

    backdrop.draw_stars(buffer, scene["stars"], now, 0.5)
    backdrop.draw_comets(buffer, scene["comets"], now, 0.6)
    backdrop.draw_rainbow_text(buffer, CX, 4, "LEADERBOARD", 2, 1.0, now)
    bloom(buffer, 0.65, 0.25)        # glow the title only
    draw_text_centered(buffer, CX, 22, "< " + mode.replace("_", " ") + " >", 1, 1.0, "accent")

    best = top_scores(scene["trials"], mode, 10)
    add_label(buffer, TABLE_X, 34, " #   PLAYER        CORRECT     MEAN TIME     STROOP EFFECT", "accent")
    if len(best) == 0:
        draw_label_centered(buffer, CX, 40, "no finished runs in this mode yet - go play one")
    for place, entry in enumerate(best):
        # rows slide in from the right, one after another
        slide = int((1 - ease_out(progress(age, place * 0.04, 0.3))) * 30)
        line = "%2d   %-10s    %2d / %-2d     %5d ms      %+6d ms" % (
            place + 1, entry["player"], entry["correct"], settings.TRIALS_PER_RUN,
            entry["mean_rt"], entry["stroop_effect_ms"])
        color = "yellow" if place == 0 else "white"
        add_label(buffer, TABLE_X + slide, 38 + place * 4, line, color)

    draw_label_centered(buffer, CX, 86, "LEFT / RIGHT  change mode        M  back to the menu")
    return None
