# scenes/backdrop.py - the starfield, comets and rainbow title.  (Theo)
#
# Shared by the intro, the menu and the results screen so they all sit in
# front of the same moving sky.

import math
import random

import settings
from render.buffer import set_pixel, shimmer
from render.draw import draw_line, draw_big_text, text_width


def make_stars(count):
    stars = []
    for i in range(count):
        stars.append({
            "x": random.random() * settings.GRID_W,
            "y": random.random() * settings.GRID_H,
            "glow": 0.15 + random.random() * 0.6,
            "phase": random.random() * 6.28,          # so they don't all twinkle together
            "twinkle": 1 + random.random() * 3,
            "drift": 0.5 + random.random() * 2.5,     # pixels per second, to the left
        })
    return stars


def draw_stars(buffer, stars, now, alpha):
    """alpha is 0 to 1, for fading the whole sky in.

    The stars only move a few times a second. They're spread over the whole
    screen, so every time one changes the window has to redraw everything.
    Holding them still in between keeps most frames cheap.
    """
    now = int(now * settings.STAR_FPS) / settings.STAR_FPS
    for star in stars:
        twinkle = 0.65 + 0.35 * math.sin(now * star["twinkle"] + star["phase"])
        x = (star["x"] - now * star["drift"]) % settings.GRID_W
        set_pixel(buffer, x, star["y"], star["glow"] * twinkle * alpha)


def make_comets(count):
    comets = []
    for i in range(count):
        comets.append({
            "number": i,
            "wait": 2.5 + random.random() * 4,        # seconds between this comet's flights
            "offset": random.random() * 5,
        })
    return comets


def draw_comets(buffer, comets, now, alpha):
    """Each comet flies across, then waits out the rest of its cycle."""
    for comet in comets:
        clock = now + comet["offset"]
        flight = int(clock / comet["wait"])           # which flight this is: 0, 1, 2...
        age = clock - flight * comet["wait"]          # seconds since it set off
        if age > 1.4:
            continue                                  # still waiting for the next one

        # Every flight starts somewhere different. Multiplying by odd numbers
        # and taking the remainder is a cheap way to scatter them around.
        start_x = (flight * 73 + comet["number"] * 41) % settings.GRID_W
        start_y = (flight * 37 + comet["number"] * 17) % (settings.GRID_H // 2)
        speed_x = 80 if (flight + comet["number"]) % 2 == 0 else -80
        speed_y = 28
        color = settings.COLORS[(flight + comet["number"]) % len(settings.COLORS)]

        head_x = start_x + speed_x * age
        head_y = start_y + speed_y * age
        fade = alpha * (1 - age / 1.4)
        # the tail is a line that fades to nothing behind the head
        draw_line(buffer, head_x, head_y, head_x - speed_x * 0.16, head_y - speed_y * 0.16,
                  fade, color, 0.0)
        set_pixel(buffer, head_x, head_y, fade, "white")


def draw_rainbow_text(buffer, center_x, y, string, scale, brightness, now):
    """Big text striped in the five game colors, with the stripes sliding upward.

    Stripes run along the rows on purpose: a row that is all one color is a
    single piece of text for the window to draw, which keeps this cheap.
    """
    width = text_width(string, scale)
    x = int(center_x - width / 2)
    y = int(y)
    draw_big_text(buffer, x, y, string, scale, brightness)
    shimmer(buffer, x, y, x + width, y + 7 * scale, now)

    stripe = max(1, round(7 * scale / len(settings.COLORS)))    # rows per stripe
    slide = int(now * 6)                                         # stripes move up 6 rows a second
    for row in range(max(0, y), min(buffer["h"], int(y + 7 * scale))):
        color = settings.COLORS[((row - y + slide) // stripe) % len(settings.COLORS)]
        tags = buffer["color"][row]
        lit = buffer["bright"][row]
        for column in range(max(0, x), min(buffer["w"], int(x + width))):
            if lit[column] > 0:
                tags[column] = color
