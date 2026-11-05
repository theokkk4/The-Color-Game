# scenes/duel.py - head to head: two players, one keyboard, the same words.  (Theo)
#
# The screen is split down the middle. Both players see the same word and
# answer with their own five keys (A S D F G on the left, H J K L ; on the
# right). Each correct answer is a point, and the bar in the middle shows
# who's ahead. A player who doesn't answer in time gets no point.

import settings
from core import scoring
from core.trial import make_trials
from core.session import record_answer
from data.logger import log_trial
from render.buffer import set_pixel, bloom
from render.draw import draw_big_text, draw_text_centered, draw_label_centered, text_width
from scenes import backdrop, hud
import sound

CX = settings.GRID_W / 2
WORD_Y = 38
BAR_TOP = 22
BAR_BOTTOM = 80


def make_side(name, keys, center_x, color):
    return {"name": name, "keys": keys, "x": center_x, "color": color,
            "results": [], "answer": None}       # answer = this trial's result, once given


def start(app):
    return {
        "trials": make_trials("head_to_head"),
        "index": 0,
        "phase": "countdown",        # then "word", "feedback", and finally "over"
        "phase_start": None,
        "shown_at": None,
        "stamp_after_paint": False,
        "last_tick": None,
        "left": make_side(app["player"], settings.LEFT_KEYS, 39, "white"),
        "right": make_side("PLAYER 2", settings.RIGHT_KEYS, 121, "accent"),
        "stars": backdrop.make_stars(50),
        "comets": backdrop.make_comets(3),
        "ripples": [],
    }


def on_key(scene, app, key, when):
    if key == "escape":
        return "menu"
    if scene["phase"] == "over":
        if key == "r":
            return "duel"
        if key in ("m", "enter"):
            return "menu"
    elif scene["phase"] == "word" and scene["shown_at"] is not None:
        for side in (scene["left"], scene["right"]):
            if key in side["keys"] and side["answer"] is None:
                give_answer(scene, side, key, (when - scene["shown_at"]) * 1000, when)
    return None


def give_answer(scene, side, key, reaction_ms, when):
    trial = scene["trials"][scene["index"]]
    result = record_answer(trial, key, reaction_ms, side["keys"])
    result["player"] = side["name"]
    log_trial(result)
    side["answer"] = result
    side["results"].append(result)
    sound.play("correct" if result["correct"] else "wrong")
    hud.add_ripple(scene["ripples"], side["x"], WORD_Y, "green" if result["correct"] else "red", when, 1.7)
    if scene["left"]["answer"] is not None and scene["right"]["answer"] is not None:
        scene["phase"] = "feedback"
        scene["phase_start"] = when


def draw(scene, app, buffer, now):
    if scene["phase_start"] is None:
        scene["phase_start"] = now
    elapsed = now - scene["phase_start"]
    sides = (scene["left"], scene["right"])

    backdrop.draw_stars(buffer, scene["stars"], now, 0.4)
    hud.draw_ripples(buffer, scene["ripples"], now)

    if scene["phase"] == "over":
        draw_winner(buffer, scene, now)
        return None

    if scene["phase"] == "countdown":
        if hud.draw_countdown(buffer, scene, elapsed, CX, now):
            scene["phase"] = "word"
    elif scene["phase"] == "word" and scene["shown_at"] is not None:
        # out of time: whoever hasn't answered gets a miss
        if (now - scene["shown_at"]) * 1000 > settings.DUEL_TIMEOUT_MS:
            for side in sides:
                if side["answer"] is None:
                    give_answer(scene, side, None, settings.DUEL_TIMEOUT_MS, now)
    elif scene["phase"] == "feedback" and elapsed > 0.5:
        scene["index"] += 1
        scene["shown_at"] = None
        scene["left"]["answer"] = None
        scene["right"]["answer"] = None
        scene["phase"] = "word"
        if scene["index"] >= len(scene["trials"]):
            scene["phase"] = "over"
            scene["phase_start"] = now
            return None

    if scene["phase"] != "countdown":
        trial = scene["trials"][scene["index"]]
        for side in sides:
            if side["answer"] is None:
                hud.draw_word(buffer, side["x"], WORD_Y, trial, 2, now)
            elif side["answer"]["correct"]:
                draw_text_centered(buffer, side["x"], WORD_Y - 7, "OK", 2, 1.0, "green")
            else:
                draw_text_centered(buffer, side["x"], WORD_Y - 7, "MISS", 2, 1.0, "red")
        if scene["phase"] == "word" and scene["shown_at"] is None:
            scene["stamp_after_paint"] = True     # start both players' clocks together

    bloom(buffer, 0.65, 0.3)         # glow the big words; the small parts below stay sharp
    for side in sides:
        draw_label_centered(buffer, side["x"], 8, side["name"], side["color"])
        hud.draw_key_boxes(buffer, side["x"], 66, side["keys"])
    draw_score_bar(buffer, scene)
    hud.draw_progress(buffer, scene["index"], len(scene["trials"]))
    draw_label_centered(buffer, CX, 86, "press the key for the INK color        ESC  menu")
    return None


def draw_score_bar(buffer, scene):
    """Two thin columns in the middle that fill from the bottom, one per player."""
    total = len(scene["trials"])
    column = CX - 2
    for side in (scene["left"], scene["right"]):
        points = scoring.score(side["results"])
        filled = (BAR_BOTTOM - BAR_TOP) * points / total
        for y in range(BAR_TOP, BAR_BOTTOM):
            glow = 0.95 if BAR_BOTTOM - y <= filled else 0.15
            set_pixel(buffer, column, y, glow, side["color"])
            set_pixel(buffer, column + 1, y, glow, side["color"])
        column += 2
    # the scores themselves, on either side of the top of the bar
    left_points = str(scoring.score(scene["left"]["results"]))
    draw_big_text(buffer, CX - 4 - text_width(left_points, 2), 5, left_points, 2, 1.0, "white")
    draw_big_text(buffer, CX + 4, 5, str(scoring.score(scene["right"]["results"])), 2, 1.0, "accent")


def draw_winner(buffer, scene, now):
    left = scene["left"]
    right = scene["right"]
    backdrop.draw_comets(buffer, scene["comets"], now, 0.8)
    # most points wins; if that's a tie, the faster player wins
    left_rank = (scoring.score(left["results"]), -scoring.mean_rt(left["results"]))
    right_rank = (scoring.score(right["results"]), -scoring.mean_rt(right["results"]))
    if left_rank == right_rank:
        backdrop.draw_rainbow_text(buffer, CX, 26, "TIE", 3, 1.0, now)
    else:
        winner = left if left_rank > right_rank else right
        backdrop.draw_rainbow_text(buffer, CX, 18, winner["name"], 2, 1.0, now)
        backdrop.draw_rainbow_text(buffer, CX, 36, "WINS", 3, 1.0, now)
    bloom(buffer, 0.65, 0.3)
    for side in (left, right):
        draw_label_centered(buffer, side["x"], 64, "%s   %d correct   %d ms average" % (
            side["name"], scoring.score(side["results"]), scoring.mean_rt(side["results"])), side["color"])
    draw_text_centered(buffer, CX, 76, "R AGAIN    M MENU", 1, 1.0, "accent")
