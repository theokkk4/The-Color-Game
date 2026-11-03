"""
core/trial.py - builds the trials (word + ink color) for one run.
Owner: Issaka

A trial is a plain dict:
    {"trial_num": 1, "word": "red", "ink_color": "blue",
     "congruent": False, "mode": "classic", "answer": "blue"}

"answer" is the color name the player must press. It stays on the server;
the browser never sees it (see public_trial below).
"""

import random

from settings import COLORS, CONGRUENT_RATIO, TRIALS_PER_RUN, SPEED_HIDE_MS


def make_trial(mode, trial_num=1):
    """Return one random trial dict for the given mode."""
    word = random.choice(COLORS)

    # Roughly half the trials are congruent (word and ink match).
    if random.random() < CONGRUENT_RATIO:
        ink_color = word
    else:
        other_colors = [c for c in COLORS if c != word]
        ink_color = random.choice(other_colors)

    # "reverse" asks for the word; classic and speed ask for the ink color.
    if mode == "reverse":
        answer = word
    else:
        answer = ink_color

    return {
        "trial_num": trial_num,
        "word": word,
        "ink_color": ink_color,
        "congruent": word == ink_color,
        "mode": mode,
        "answer": answer,
    }


def make_trials(mode, n=TRIALS_PER_RUN):
    """Return a list of n trials. Both players in a room get this same list."""
    return [make_trial(mode, i + 1) for i in range(n)]


def public_trial(trial, total):
    """Copy of a trial that is safe to send to the browser (no answer)."""
    hide_after_ms = SPEED_HIDE_MS if trial["mode"] == "speed" else 0
    return {
        "trial_num": trial["trial_num"],
        "total": total,
        "word": trial["word"],
        "ink_color": trial["ink_color"],
        "mode": trial["mode"],
        "hide_after_ms": hide_after_ms,
    }
