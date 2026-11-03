"""
data/logger.py - appends one row per trial to results/trials.csv.
Owner: Oliver

The server calls log_trial(result) right after each answer. The result dict
must contain player, mode, room, and every field from record_answer().
We add the timestamp here so the clock is always the server's.
"""

import csv
import os
from datetime import datetime

from settings import CSV_COLUMNS, RESULTS_DIR, TRIALS_CSV


def log_trial(result):
    """Append one result row to the CSV, writing the header if the file is new."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    is_new_file = not os.path.exists(TRIALS_CSV)

    row = {column: result.get(column, "") for column in CSV_COLUMNS}
    row["timestamp"] = datetime.now().isoformat(timespec="seconds")

    with open(TRIALS_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if is_new_file:
            writer.writeheader()
        writer.writerow(row)

# TODO(Oliver): decide whether to also log abandoned runs (player disconnects mid-game) or only complete ones.
