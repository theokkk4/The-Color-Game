# data/leaderboard.py - picks the best runs out of the trial rows.  (Oliver)
#
# A "run" is one player finishing one game. Runs are ranked by number
# correct, then by faster mean reaction time to break ties.

from settings import TRIALS_PER_RUN
from core.scoring import summarize
from data.analyze import split_runs


def top_scores(trials, mode="classic", n=10):
    """
    Return up to n dicts like
        {"player": "Theo", "mode": "classic", "correct": 28, "mean_rt": 612,
         "accuracy": 0.93, "stroop_effect_ms": 85}
    sorted best first. Only complete runs of the given mode are counted.
    """
    entries = []
    for rows in split_runs(trials):
        if rows[0]["mode"] != mode:
            continue
        if len(rows) < TRIALS_PER_RUN:
            continue        # skip games the player did not finish
        s = summarize(rows)
        entries.append({
            "player": rows[0]["player"],
            "mode": mode,
            "correct": s["correct"],
            "mean_rt": s["mean_rt"],
            "accuracy": s["accuracy"],
            "stroop_effect_ms": s["stroop_effect_ms"],
        })

    # Most correct first; among equal scores the faster player wins.
    entries.sort(key=lambda e: (-e["correct"], e["mean_rt"]))
    return entries[:n]

# TODO(Oliver): show only each player's best run, so one person can't fill the whole board.
