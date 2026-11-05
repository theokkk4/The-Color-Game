# data/analyze.py - reads results/trials.csv and turns it into stats and charts.  (Oliver)
#
# Run from the project folder:   python -m data.analyze
# Charts are written to results/charts/. matplotlib is imported inside
# make_charts, so the game itself never has to load it.

import csv
import os

from settings import TRIALS_CSV, RESULTS_DIR
from core import scoring


def load_trials(path=TRIALS_CSV):
    """Return every CSV row as a dict with real numbers and booleans."""
    if not os.path.exists(path):
        return []
    trials = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row["trial_num"] = int(row["trial_num"])
            row["reaction_ms"] = int(row["reaction_ms"])
            row["congruent"] = row["congruent"] == "True"
            row["correct"] = row["correct"] == "True"
            trials.append(row)
    return trials


def split_runs(trials):
    """Split the rows into runs (one player playing one game).

    Rows are in the order they were played, so a player's run starts every
    time their trial_num goes back to 1.
    """
    open_runs = {}               # (player, mode) -> the run that player is in the middle of
    runs = []
    for t in trials:
        key = (t["player"], t["mode"])
        if t["trial_num"] == 1 or key not in open_runs:
            open_runs[key] = []
            runs.append(open_runs[key])
        open_runs[key].append(t)
    return runs


def summarize(trials):
    """Stats per player across all of their runs, as {player: summary_dict}."""
    by_player = {}
    for t in trials:
        by_player.setdefault(t["player"], []).append(t)
    return {name: scoring.summarize(rows) for name, rows in by_player.items()}


def make_charts(trials, out_dir=os.path.join(RESULTS_DIR, "charts")):
    """Save two dark-style charts and return their file paths."""
    import matplotlib
    matplotlib.use("Agg")            # draw to files, no window needed
    import matplotlib.pyplot as plt

    stats = summarize(trials)
    if not stats:
        return []
    os.makedirs(out_dir, exist_ok=True)
    plt.style.use("dark_background")
    paths = []

    # 1. congruent vs incongruent mean reaction time, one pair of bars per player
    names = list(stats.keys())
    congruent = [stats[n]["congruent_rt"] for n in names]
    incongruent = [stats[n]["incongruent_rt"] for n in names]
    x = range(len(names))
    plt.figure(figsize=(8, 4))
    plt.bar([i - 0.2 for i in x], congruent, width=0.4, label="word matches ink", color="#1FFF6B")
    plt.bar([i + 0.2 for i in x], incongruent, width=0.4, label="word differs from ink", color="#FF2A2A")
    plt.xticks(list(x), names)
    plt.ylabel("mean reaction time (ms)")
    plt.title("Stroop effect per player")
    plt.legend()
    paths.append(os.path.join(out_dir, "stroop_by_player.png"))
    plt.savefig(paths[-1], bbox_inches="tight")
    plt.close()

    # 2. how the correct reaction times are spread out
    plt.figure(figsize=(8, 4))
    same = [t["reaction_ms"] for t in trials if t["correct"] and t["congruent"]]
    different = [t["reaction_ms"] for t in trials if t["correct"] and not t["congruent"]]
    plt.hist([same, different], bins=20, label=["word matches ink", "word differs from ink"],
             color=["#1FFF6B", "#FF2A2A"])
    plt.xlabel("reaction time (ms)")
    plt.ylabel("number of answers")
    plt.title("Reaction times, correct answers only")
    plt.legend()
    paths.append(os.path.join(out_dir, "reaction_times.png"))
    plt.savefig(paths[-1], bbox_inches="tight")
    plt.close()
    return paths

# TODO(Oliver): add a chart of reaction time over trial number (1 to 30) to see whether players speed up or get tired during a run.


if __name__ == "__main__":
    rows = load_trials()
    print("Loaded %d trial rows in %d runs" % (len(rows), len(split_runs(rows))))
    for name, s in summarize(rows).items():
        print("%-12s mean RT %4d ms   accuracy %3d%%   stroop %+d ms" % (
            name, s["mean_rt"], round(s["accuracy"] * 100), s["stroop_effect_ms"]))
    for path in make_charts(rows):
        print("Chart saved to", path)
