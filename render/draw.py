# render/draw.py - shapes and text, drawn into the pixel buffer.  (Theo)
#
# Everything here just calls set_pixel() a lot. x grows to the right and
# y grows downward, and (0, 0) is the top left pixel.

import math

from render.buffer import set_pixel, add_label
from render.font import FONT
from render.easing import lerp


def letter_step(letter, scale):
    """How far to move right after a letter. A space is half as wide as a letter."""
    if letter == " ":
        return 3 * scale
    return 6 * scale             # 5 pixels of letter + 1 of gap


def text_width(string, scale=1):
    width = 0
    for letter in string:
        width += letter_step(letter, scale)
    return width - scale         # no gap after the last letter


def draw_big_text(buffer, x, y, string, scale, brightness, color="white"):
    """Draw text with every font pixel blown up to scale x scale.

    scale doesn't have to be a whole number: for each pixel on screen we look
    up which pixel of the 5x7 letter it lands on.
    """
    tall = int(7 * scale)
    wide = int(5 * scale)
    for letter in string.upper():
        shape = FONT.get(letter, FONT["?"])
        for dy in range(tall):
            row = shape[int(dy / scale)]
            if "#" not in row:
                continue
            for dx in range(wide):
                if row[int(dx / scale)] == "#":
                    set_pixel(buffer, x + dx, y + dy, brightness, color)
        x += letter_step(letter, scale)


def draw_text(buffer, x, y, string, brightness, color="white"):
    """Text at the font's real size: 5 pixels wide, 7 tall."""
    draw_big_text(buffer, x, y, string, 1, brightness, color)


def draw_text_centered(buffer, center_x, y, string, scale, brightness, color="white"):
    x = center_x - text_width(string, scale) / 2
    draw_big_text(buffer, x, y, string, scale, brightness, color)


def draw_label_centered(buffer, center_x, y, text, color="white"):
    """Small print (real letters, one per cell), centered on center_x."""
    add_label(buffer, center_x - len(text) / 2, y, text, color)


def draw_line(buffer, x0, y0, x1, y1, brightness, color="white", end_brightness=None):
    """A straight line. Give end_brightness to make it fade along its length."""
    if end_brightness is None:
        end_brightness = brightness
    steps = int(max(abs(x1 - x0), abs(y1 - y0)))
    if steps == 0:
        set_pixel(buffer, x0, y0, brightness, color)
        return
    for i in range(steps + 1):
        t = i / steps
        set_pixel(buffer, lerp(x0, x1, t), lerp(y0, y1, t),
                  lerp(brightness, end_brightness, t), color)


def draw_circle(buffer, center_x, center_y, radius, brightness, color="white", filled=False,
                stretch=1.0):
    """A circle. stretch above 1 makes it wider than it is tall (an oval)."""
    if filled:
        # one horizontal slice at a time
        for dy in range(-int(radius), int(radius) + 1):
            half = math.sqrt(radius * radius - dy * dy) * stretch
            for x in range(int(center_x - half), int(center_x + half) + 1):
                set_pixel(buffer, x, center_y + dy, brightness, color)
    else:
        # walk around the edge in small enough steps to leave no gaps
        points = int(radius * 7 * stretch) + 8
        for i in range(points):
            angle = i / points * 2 * math.pi
            set_pixel(buffer, center_x + math.cos(angle) * radius * stretch,
                      center_y + math.sin(angle) * radius, brightness, color)


def draw_rect(buffer, x, y, w, h, brightness, color="white", filled=False):
    for row in range(int(h)):
        for column in range(int(w)):
            on_edge = row == 0 or row == int(h) - 1 or column == 0 or column == int(w) - 1
            if filled or on_edge:
                set_pixel(buffer, x + column, y + row, brightness, color)
