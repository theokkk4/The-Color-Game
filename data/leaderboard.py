"""
data/leaderboard.py - picks the best runs out of the trial rows.
Owner: Oliver

A "run" is one player finishing one game in one room. Runs are ranked by
number correct, then by faster mean reaction time to break ties.
"""

from settings import TRIALS_PER_RUN
from core.scoring import summarize


def top_scores(trials, mode="classic", n=10):
    """
    Return up to n dicts like
        {"player": "Theo", "mode": "classic", "correct": 28, "mean_rt": 612,
         "accuracy": 0.93, "stroop_effect_ms": 85}
    sorted best first. Only complete runs of the given mode are counted.
    """
    runs = {}
    for t in trials:
        if t["mode"] != mode:
            continue
        key = (t["player"], t["room"])
        runs.setdefault(key, []).append(t)

    entries = []
    for (player, room), rows in runs.items():
        if len(rows) < TRIALS_PER_RUN:
            continue        # skip games the player did not finish
        s = summarize(rows)
        entries.append({
            "player": player,
            "mode": mode,
            "correct": s["correct"],
            "mean_rt": s["mean_rt"],
            "accuracy": s["accuracy"],
            "stroop_effect_ms": s["stroop_effect_ms"],
        })

    # Most correct first; among equal scores the faster player wins.
    entries.sort(key=lambda e: (-e["correct"], e["mean_rt"]))
    return entries[:n]

# TODO(Oliver): a room code can be reused on a later day, so group runs by (player, room, date) to keep separate games apart.
