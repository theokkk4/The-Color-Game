# core/session.py - checks one answer against one trial.  (Issaka)
#
# The game scene measures the reaction time and hands it to us. We only
# decide whether the key was right and build the result row that gets logged.

from settings import KEYS


def record_answer(trial, key, reaction_ms, keys=KEYS):
    """
    Return a result dict for this trial.

    key         - the key the player pressed, or None if they ran out of time
    reaction_ms - milliseconds from the word being drawn to the keypress
    keys        - which key means which color (head to head passes its own)
    """
    key = (key or "").lower()
    response = keys.get(key, "none")     # "none" means an unknown key or a timeout
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

# TODO(Issaka): throw out answers faster than about 150 ms, since nobody can read a color that quickly and it means a held or mashed key.


# ---------------------------------------------------------------------------
# Tiny terminal demo, run from the project folder:   python -m core.session
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
