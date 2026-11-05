# scenes/game.py - one solo run: countdown, 30 words, then off to the results.  (Theo)
#
# The scene moves through three phases:
#   "countdown"  3, 2, 1
#   "word"       a word is up and we're waiting for a key
#   "feedback"   a short pause after the answer (flash or jitter), then the next word
#
# Reaction time is measured with time.perf_counter(): main.py stamps
# scene["shown_at"] right after the frame with the new word is painted, and
# the key handler gets the time the key went down.

import settings
from core.trial import make_trials
from core.session import record_answer
from data.logger import log_trial
from render.buffer import flash, jitter, bloom
from render.draw import draw_label_centered
from scenes import backdrop, hud
import sound

CX = settings.GRID_W / 2
WORD_Y = 40
HINTS = {
    "classic": "press the key for the INK color",
    "reverse": "press the key for the WORD",
    "speed": "press the key for the INK color - the word hides fast",
}


def start(app):
    return {
        "mode": app["mode"],
        "trials": make_trials(app["mode"]),
        "index": 0,                  # which trial we're on
        "results": [],
        "phase": "countdown",
        "phase_start": None,
        "shown_at": None,            # when the current word was painted
        "stamp_after_paint": False,  # asks main.py to set shown_at after this frame
        "last_tick": None,
        "effect": None,              # "correct" or "wrong", for the flash / jitter
        "effect_start": 0,
        "bar": 0.0,                  # the progress bar glides toward the real number
        "stars": backdrop.make_stars(50),
        "ripples": [],
    }


def on_key(scene, app, key, when):
    if key == "escape":
        return "menu"
    if scene["phase"] != "word" or scene["shown_at"] is None:
        return None                  # no word on screen yet, so the key doesn't count
    if key not in settings.KEYS:
        return None

    trial = scene["trials"][scene["index"]]
    reaction_ms = (when - scene["shown_at"]) * 1000
    result = record_answer(trial, key, reaction_ms)
    result["player"] = app["player"]
    log_trial(result)
    scene["results"].append(result)

    if result["correct"]:
        scene["effect"] = "correct"
        sound.play("correct")
        hud.add_ripple(scene["ripples"], CX, WORD_Y, trial["ink_color"], when)
    else:
        scene["effect"] = "wrong"
        sound.play("wrong")
        hud.add_ripple(scene["ripples"], CX, WORD_Y, "red", when)
    scene["effect_start"] = when
    scene["phase"] = "feedback"
    scene["phase_start"] = when
    return None


def draw(scene, app, buffer, now):
    if scene["phase_start"] is None:
        scene["phase_start"] = now
    elapsed = now - scene["phase_start"]

    backdrop.draw_stars(buffer, scene["stars"], now, 0.4)
    hud.draw_ripples(buffer, scene["ripples"], now)

    if scene["phase"] == "countdown":
        if hud.draw_countdown(buffer, scene, elapsed, CX, now):
            scene["phase"] = "word"

    if scene["phase"] == "word":
        trial = scene["trials"][scene["index"]]
        hidden = (scene["mode"] == "speed" and scene["shown_at"] is not None
                  and (now - scene["shown_at"]) * 1000 > settings.SPEED_HIDE_MS)
        if not hidden:
            hud.draw_word(buffer, CX, WORD_Y, trial, 4, now)
        if scene["shown_at"] is None:
            scene["stamp_after_paint"] = True     # start the clock once this frame is up

    elif scene["phase"] == "feedback":
        # The word stays for a moment so the flash has something to hit, then
        # the screen goes blank so the next word is clearly a new one.
        if elapsed < settings.FEEDBACK_MS / 1000 * 0.6 and scene["mode"] != "speed":
            hud.draw_word(buffer, CX, WORD_Y, scene["trials"][scene["index"]], 4, now)
        if elapsed >= settings.FEEDBACK_MS / 1000:
            scene["index"] += 1
            scene["shown_at"] = None
            scene["phase"] = "word"
            if scene["index"] >= len(scene["trials"]):
                app["last_run"] = {"mode": scene["mode"], "player": app["player"],
                                   "results": scene["results"]}
                return "results"

    bloom(buffer, 0.65, 0.3)         # glow the big word; the small parts below stay sharp

    # the parts that are always there
    scene["bar"] += (len(scene["results"]) - scene["bar"]) * 0.3
    hud.draw_progress(buffer, scene["bar"], len(scene["trials"]))
    hud.draw_key_boxes(buffer, CX, 68, settings.KEYS)
    draw_label_centered(buffer, CX, 83, HINTS[scene["mode"]])
    draw_label_centered(buffer, CX, 86, "ESC  back to the menu", "accent")

    # the whole picture reacts to the last answer
    age = now - scene["effect_start"]
    if scene["effect"] == "correct" and age < 0.2:
        flash(buffer, 0.3 * (1 - age / 0.2), "green")
    elif scene["effect"] == "wrong" and age < 0.25:
        jitter(buffer, int(7 * (1 - age / 0.25)) + 1)
    return None
