"""
core/scoring.py - turns a list of result dicts into stats.
Owner: Issaka

Every function takes a list of results from record_answer() and never
changes it. Reaction-time stats only count correct answers, because a
wrong keypress tells us nothing about how fast the player read the color.
"""


def mean_rt(results):
    """Average reaction time in ms over correct answers (0 if none)."""
    times = [r["reaction_ms"] for r in results if r["correct"]]
    if not times:
        return 0
    return round(sum(times) / len(times))


def accuracy(results):
    """Fraction correct, 0.0 to 1.0."""
    if not results:
        return 0.0
    correct = sum(1 for r in results if r["correct"])
    return round(correct / len(results), 3)


def congruent_rt(results):
    """Mean RT on trials where the word matched the ink color."""
    return mean_rt([r for r in results if r["congruent"]])


def incongruent_rt(results):
    """Mean RT on trials where the word and ink color differed."""
    return mean_rt([r for r in results if not r["congruent"]])


def stroop_effect_ms(results):
    """How much slower incongruent trials were. Bigger = stronger Stroop effect."""
    return incongruent_rt(results) - congruent_rt(results)


def score(results):
    """Head-to-head score: one point per correct answer."""
    return sum(1 for r in results if r["correct"])


def summarize(results):
    """One dict with everything the results screen needs."""
    return {
        "trials": len(results),
        "correct": score(results),
        "accuracy": accuracy(results),
        "mean_rt": mean_rt(results),
        "congruent_rt": congruent_rt(results),
        "incongruent_rt": incongruent_rt(results),
        "stroop_effect_ms": stroop_effect_ms(results),
        "reaction_times": [r["reaction_ms"] for r in results],
        "correct_flags": [r["correct"] for r in results],
    }
