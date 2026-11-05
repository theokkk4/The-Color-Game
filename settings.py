# settings.py - every number and color the game uses, in one place.
#
# Change something here and the whole game follows.

import os

# ---- the picture
GRID_W = 160                 # the pixel buffer is this many cells wide
GRID_H = 90                  # ... and this many tall (16:9, like a monitor)
FPS = 30
STAR_FPS = 8                 # the starfield updates less often than everything else
WINDOW_SIZE = "1024x576"     # bigger windows look great but take longer to redraw
RAMP = " .:-=+*#%@"          # dark to bright: a pixel's brightness picks one of these
BACKGROUND = "#0A0C16"
SHOW_FRAME_TIME = False      # True prints how long each frame took, top left

# A pixel can carry a color tag. These are the real colors behind the tags.
COLOR_HEX = {
    "white":  "#EEF0FF",
    "gray":   "#8A91B8",
    "accent": "#8C3DFF",
    "red":    "#FF2A2A",
    "green":  "#1FFF6B",
    "blue":   "#2D7BFF",
    "yellow": "#FFE600",
    "purple": "#B22BFF",
}

# ---- the game
COLORS = ["red", "green", "blue", "yellow", "purple"]
MODES = ["classic", "reverse", "speed", "head_to_head"]

KEYS = {"r": "red", "g": "green", "b": "blue", "y": "yellow", "p": "purple"}
# head to head: two players share the keyboard, same color order for both
LEFT_KEYS = {"a": "red", "s": "green", "d": "blue", "f": "yellow", "g": "purple"}
RIGHT_KEYS = {"h": "red", "j": "green", "k": "blue", "l": "yellow", ";": "purple"}

TRIALS_PER_RUN = 30
CONGRUENT_RATIO = 0.5        # about half the words match their ink color
COUNTDOWN_SECONDS = 3
SPEED_HIDE_MS = 700          # speed mode: the word disappears after this long
FEEDBACK_MS = 250            # pause after an answer before the next word
DUEL_TIMEOUT_MS = 3000       # head to head: a player who waits this long gets no point

# ---- files
RESULTS_DIR = "results"
TRIALS_CSV = os.path.join(RESULTS_DIR, "trials.csv")
CSV_COLUMNS = ["timestamp", "player", "mode", "trial_num", "word", "ink_color",
               "congruent", "response", "correct", "reaction_ms"]
SOUNDS_DIR = "sounds"

# ---- the eye in the intro (shared by scenes/intro.py and scenes/trails.py)
EYE_HALF_WIDTH = 58
LID_HEIGHT = 24              # how far the top lid lifts when the eye is fully open
IRIS = 19                    # radius
PUPIL = 7
