"""
settings.py - one place for every number and color the game uses.
Owner: Issaka

Change values here, not in the game logic, so the whole team stays in sync.
"""

# The five colors, the key you press for each, and the CSS color shown on screen.
COLORS = ["red", "green", "blue", "yellow", "purple"]

KEYS = {
    "r": "red",
    "g": "green",
    "b": "blue",
    "y": "yellow",
    "p": "purple",
}

# Hex values used by the browser so every color is bright on the dark theme.
COLOR_HEX = {
    "red": "#FF4D4D",
    "green": "#3DDC84",
    "blue": "#4D8DFF",
    "yellow": "#FFD93D",
    "purple": "#B57CFF",
}

# Game modes the server knows about. "head-to-head" is not a mode,
# it is just a room with two players playing one of these modes.
MODES = ["classic", "reverse", "speed"]

TRIALS_PER_RUN = 30
CONGRUENT_RATIO = 0.5       # about half the trials have word == ink color

COUNTDOWN_SECONDS = 3       # the 3-2-1 before the first word
SPEED_HIDE_MS = 700         # speed mode: word disappears after this long
MAX_PLAYERS_PER_ROOM = 2
MAX_NAME_LENGTH = 20

RESULTS_DIR = "results"
TRIALS_CSV = "results/trials.csv"

# Column order for results/trials.csv. Do not reorder without telling Oliver.
CSV_COLUMNS = [
    "timestamp", "player", "mode", "room", "trial_num",
    "word", "ink_color", "congruent", "response", "correct", "reaction_ms",
]
