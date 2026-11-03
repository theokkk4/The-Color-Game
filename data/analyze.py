"""
data/analyze.py - reads results/trials.csv and turns it into stats and pictures.
Owner: Oliver

Run from the project root:   python -m data.analyze
Charts are written to results/charts/, report cards to results/cards/.
matplotlib and pillow are imported inside the functions that need them, so
the web server never has to load them.
"""

import csv
import os

from settings import TRIALS_CSV, RESULTS_DIR


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


def group_runs(trials):
    """Split rows into runs. One run = one player in one room in one mode."""
    runs = {}
    for t in trials:
        key = (t["player"], t["room"], t["mode"])
        runs.setdefault(key, []).append(t)
    return runs


def summarize(trials):
    """Stats per player across all of their runs, as {player: summary_dict}."""
    by_player = {}
    for t in trials:
        by_player.setdefault(t["player"], []).append(t)
    # core.scoring.summarize already knows how to do the math on a list of rows.
    from core import scoring
    return {name: scoring.summarize(rows) for name, rows in by_player.items()}


def make_charts(trials, out_dir=os.path.join(RESULTS_DIR, "charts")):
    """Save a bar chart of congruent vs incongruent mean RT per player."""
    import matplotlib
    matplotlib.use("Agg")            # draw to files, no window needed
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    stats = summarize(trials)
    if not stats:
        return None

    names = list(stats.keys())
    congruent = [stats[n]["congruent_rt"] for n in names]
    incongruent = [stats[n]["incongruent_rt"] for n in names]
    x = range(len(names))

    plt.figure(figsize=(8, 4))
    plt.bar([i - 0.2 for i in x], congruent, width=0.4, label="congruent")
    plt.bar([i + 0.2 for i in x], incongruent, width=0.4, label="incongruent")
    plt.xticks(list(x), names)
    plt.ylabel("mean reaction time (ms)")
    plt.title("Stroop effect per player")
    plt.legend()
    path = os.path.join(out_dir, "stroop_by_player.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path

# TODO(Oliver): make_charts should also draw a histogram of reaction times and an RT-over-trial line per run.


def make_report_card(player, summary, out_dir=os.path.join(RESULTS_DIR, "cards")):
    """Save a small PNG 'report card' image for one player using Pillow."""
    from PIL import Image, ImageDraw

    os.makedirs(out_dir, exist_ok=True)
    img = Image.new("RGB", (480, 260), "#1A1D27")
    draw = ImageDraw.Draw(img)
    lines = [
        "THE COLOR GAME - report card",
        "Player: %s" % player,
        "Mean RT: %d ms" % summary["mean_rt"],
        "Accuracy: %d%%" % round(summary["accuracy"] * 100),
        "Stroop effect: %d ms" % summary["stroop_effect_ms"],
    ]
    y = 30
    for line in lines:
        draw.text((30, y), line, fill="#E6E8EF")
        y += 40
    path = os.path.join(out_dir, "%s.png" % player.replace(" ", "_"))
    img.save(path)
    return path

# TODO(Oliver): make_report_card should use the Inter font from static/fonts and the accent color, and look like the results screen.


if __name__ == "__main__":
    rows = load_trials()
    print("Loaded %d trial rows" % len(rows))
    for name, s in summarize(rows).items():
        print("%-12s mean RT %4d ms   accuracy %3d%%   stroop %+d ms" % (
            name, s["mean_rt"], round(s["accuracy"] * 100), s["stroop_effect_ms"]))
    if rows:
        print("Chart saved to", make_charts(rows))
        for name, s in summarize(rows).items():
            print("Card saved to", make_report_card(name, s))
