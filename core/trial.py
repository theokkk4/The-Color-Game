# core/trial.py - builds the trials (word + ink color) for one run.  (Issaka)
#
# A trial is a plain dict:
#     {"trial_num": 1, "word": "red", "ink_color": "blue",
#      "congruent": False, "mode": "classic", "answer": "blue"}
#
# "answer" is the color the player has to press.

import random

from settings import COLORS, CONGRUENT_RATIO, TRIALS_PER_RUN


def make_trial(mode, trial_num=1):
    """Return one random trial dict for the given mode."""
    word = random.choice(COLORS)

    # Roughly half the trials are congruent (word and ink match).
    if random.random() < CONGRUENT_RATIO:
        ink_color = word
    else:
        other_colors = [c for c in COLORS if c != word]
        ink_color = random.choice(other_colors)

    # "reverse" asks for the word; every other mode asks for the ink color.
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
    """Return a list of n trials. In head to head both players get this same list."""
    return [make_trial(mode, i + 1) for i in range(n)]

# TODO(Issaka): stop the same word + ink pair from coming up twice in a row, which makes the second one too easy.
