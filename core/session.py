"""
core/session.py - checks one answer against one trial.
Owner: Issaka

The browser measures reaction time and sends it to us. We only decide
whether the key was right and build the result row that gets logged.
"""

import os
import sys

# When run as a plain script (python core/session.py), Python only sees the
# core/ folder. Add the project root so "settings" and "core.*" import.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import KEYS


def record_answer(trial, key, reaction_ms):
    """
    Return a result dict for this trial.

    key         - the letter the player pressed ("r", "g", "b", "y", "p")
    reaction_ms - milliseconds from word shown to keypress, measured in the browser
    """
    key = (key or "").lower()
    response = KEYS.get(key, "none")     # "none" means an unknown key or a timeout
    correct = response == trial["answer"]

    try:
        reaction_ms = int(round(float(reaction_ms)))
    except (TypeError, ValueError):
        reaction_ms = 0

    return {
        "trial_num": trial["trial_num"],
        "mode": trial["mode"],
        "word": trial["word"],
        "ink_color": trial["ink_color"],
        "congruent": trial["congruent"],
        "response": response,
        "correct": correct,
        "reaction_ms": reaction_ms,
    }


# ---------------------------------------------------------------------------
# Tiny terminal demo:  python core/session.py   (or: python -m core.session)
# Plays 5 classic trials in the terminal using ANSI colors for the ink.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import time

    from core.trial import make_trials
    from core.scoring import summarize

    ANSI = {
        "red": "\033[91m", "green": "\033[92m", "blue": "\033[94m",
        "yellow": "\033[93m", "purple": "\033[95m",
    }
    RESET = "\033[0m"

    print("Stroop demo - type the first letter of the INK color (r g b y p) and press Enter.\n")
    results = []
    for trial in make_trials("classic", 5):
        colored_word = ANSI[trial["ink_color"]] + trial["word"].upper() + RESET
        started = time.perf_counter()
        key = input("Trial %d:  %s  > " % (trial["trial_num"], colored_word))
        reaction_ms = (time.perf_counter() - started) * 1000
        result = record_answer(trial, key.strip()[:1], reaction_ms)
        results.append(result)
        print("   %s  (%d ms)\n" % ("correct" if result["correct"] else "wrong", result["reaction_ms"]))

    print("Summary:", summarize(results))
