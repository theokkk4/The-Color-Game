# render/buffer.py - the pixel buffer that every scene draws into.  (Theo)
#
# The buffer is a small picture: a grid of brightness numbers from 0.0 (black)
# to 1.0 (brightest), plus a color tag for every pixel. Nothing here knows
# about the window. buffer_to_rows() at the bottom turns the picture into
# lines of text, and render/screen.py paints those.

import math
import random

import settings

# ramp level 0-9 -> which shade of the color to use: 0 is dim, 1 is full.
# The two faintest characters are drawn dim, so glows and far stars sit back.
# (More shades would look smoother, but every extra shade on a row is one
# more piece of text for Tkinter to draw, and that's the slow part.)
SHADE_OF_LEVEL = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1]


def make_buffer(w, h):
    buffer = {"w": w, "h": h}
    clear(buffer)
    return buffer


def clear(buffer):
    """Back to black. Called at the start of every frame."""
    w = buffer["w"]
    buffer["bright"] = [[0.0] * w for row in range(buffer["h"])]
    buffer["color"] = [["white"] * w for row in range(buffer["h"])]
    buffer["labels"] = []        # small real text drawn on top, see add_label


def set_pixel(buffer, x, y, brightness, color="white"):
    """Set one pixel. Anything off the edge is quietly ignored."""
    x = int(x)
    y = int(y)
    if 0 <= x < buffer["w"] and 0 <= y < buffer["h"]:
        buffer["bright"][y][x] = brightness
        buffer["color"][y][x] = color


def blend(buffer, x, y, brightness, color="white"):
    """Like set_pixel, but never makes a pixel darker: the brighter light wins."""
    x = int(x)
    y = int(y)
    if 0 <= x < buffer["w"] and 0 <= y < buffer["h"]:
        if brightness > buffer["bright"][y][x]:
            buffer["bright"][y][x] = brightness
            buffer["color"][y][x] = color


def add_label(buffer, x, y, text, color="white"):
    """Small print: put real letters straight into the cells, one per cell."""
    buffer["labels"].append((int(x), int(y), text, color))


def bloom(buffer, threshold, amount):
    """A cheap glow: every bright pixel leaks some light into its neighbors."""
    w = buffer["w"]
    h = buffer["h"]
    bright = buffer["bright"]
    color = buffer["color"]

    # Collect the bright pixels first, so the glow can't feed on itself.
    sources = []
    for y in range(h):
        row = bright[y]
        if max(row) < threshold:
            continue
        for x in range(w):
            if row[x] >= threshold:
                sources.append((x, y, row[x] * amount, color[y][x]))

    for x, y, glow, tag in sources:
        # the four touching neighbors get the full glow, the corners a bit less
        for nx, ny, share in ((x - 1, y, 1), (x + 1, y, 1), (x, y - 1, 1), (x, y + 1, 1),
                              (x - 1, y - 1, 0.6), (x + 1, y - 1, 0.6),
                              (x - 1, y + 1, 0.6), (x + 1, y + 1, 0.6)):
            if 0 <= nx < w and 0 <= ny < h and bright[ny][nx] < glow * share:
                bright[ny][nx] = glow * share
                color[ny][nx] = tag


def flash(buffer, amount, color):
    """Make the whole picture a little brighter. Dark pixels light up in the color."""
    for y in range(buffer["h"]):
        row = buffer["bright"][y]
        tags = buffer["color"][y]
        for x in range(buffer["w"]):
            if row[x] < amount:
                row[x] = amount
                tags[x] = color
            else:
                row[x] = min(1.0, row[x] + amount)


def jitter(buffer, strength):
    """Shove every row sideways by a random amount, like a TV losing signal."""
    for y in range(buffer["h"]):
        shift = random.randint(-strength, strength)
        row = buffer["bright"][y]
        tags = buffer["color"][y]
        if shift > 0:
            buffer["bright"][y] = [0.0] * shift + row[:-shift]
            buffer["color"][y] = ["white"] * shift + tags[:-shift]
        elif shift < 0:
            buffer["bright"][y] = row[-shift:] + [0.0] * -shift
            buffer["color"][y] = tags[-shift:] + ["white"] * -shift


def shimmer(buffer, x0, y0, x1, y1, now):
    """A band of light sweeps across the lit pixels in a box, so big text isn't flat."""
    x0 = max(0, int(x0))
    x1 = min(buffer["w"], int(x1))
    for y in range(max(0, int(y0)), min(buffer["h"], int(y1))):
        row = buffer["bright"][y]
        for x in range(x0, x1):
            if row[x] > 0:
                row[x] *= 0.85 + 0.15 * math.sin(x * 0.3 + y * 0.25 - now * 5)


def buffer_to_rows(buffer):
    """Turn the picture into text.

    Each row comes back as a dict of layers: {(color, shade): "  ..@@#  "}.
    A layer is a full line of text with spaces wherever another layer has its
    characters, so the screen can stack them to get one line in many colors.
    """
    ramp = settings.RAMP
    top = len(ramp) - 0.001
    w = buffer["w"]
    rows = []
    for y in range(buffer["h"]):
        bright = buffer["bright"][y]
        layers = {}
        if max(bright) >= 0.1:                   # skip rows that are all black
            tags = buffer["color"][y]
            for x in range(w):
                value = bright[x]
                if value < 0.1:
                    continue
                if value > 1:
                    value = 1
                level = int(value * top)         # which character of the ramp
                key = (tags[x], SHADE_OF_LEVEL[level])
                if key not in layers:
                    layers[key] = [" "] * w
                layers[key][x] = ramp[level]
        rows.append(layers)

    # Labels go on top: clear whatever was under each letter, then write it.
    for x, y, text, color in buffer["labels"]:
        if not 0 <= y < buffer["h"]:
            continue
        layers = rows[y]
        key = (color, 1)
        if key not in layers:
            layers[key] = [" "] * w
        for i, letter in enumerate(text):
            if 0 <= x + i < w:
                for chars in layers.values():
                    chars[x + i] = " "
                layers[key][x + i] = letter

    return [{key: "".join(chars) for key, chars in layers.items()} for layers in rows]
