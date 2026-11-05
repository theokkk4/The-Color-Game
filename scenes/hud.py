# scenes/hud.py - pieces of the play screen shared by solo and head to head.  (Theo)

import settings
from render.buffer import set_pixel, add_label, shimmer
from render.draw import draw_big_text, draw_text, draw_rect, draw_circle, text_width
from render.easing import ease_out
import sound


def draw_progress(buffer, done, total):
    """A thin bar of characters along the top. done can be a fraction, for smooth filling."""
    left = 10
    right = buffer["w"] - 24
    filled = left + (right - left) * done / total
    for x in range(left, right):
        if x < filled:
            set_pixel(buffer, x, 2, 0.95, "accent")
        else:
            set_pixel(buffer, x, 2, 0.15, "white")
    add_label(buffer, right + 3, 2, "%d/%d" % (int(done), total), "accent")


def draw_word(buffer, center_x, center_y, trial, scale, now):
    """The color word, in its ink color, centered on a point."""
    text = trial["word"].upper()
    width = text_width(text, scale)
    x = center_x - width / 2
    y = center_y - 7 * scale / 2
    draw_big_text(buffer, x, y, text, scale, 1.0, trial["ink_color"])
    shimmer(buffer, x, y, x + width, y + 7 * scale, now)


def draw_key_boxes(buffer, center_x, y, keys, brightness=1.0):
    """One little box per key, each in the color that key answers."""
    letters = list(keys)
    x = center_x - (len(letters) * 14 - 3) / 2
    for letter in letters:
        color = keys[letter]
        draw_rect(buffer, x, y, 11, 11, 0.55 * brightness, color)
        draw_text(buffer, x + 3, y + 2, letter, brightness, color)
        x += 14


def add_ripple(ripples, x, y, color, now, stretch=3.0):
    ripples.append({"x": x, "y": y, "color": color, "start": now, "stretch": stretch})


def draw_ripples(buffer, ripples, now):
    """Flat rings that spread out and fade. Finished ones are dropped from the list.

    They're wide ovals instead of circles so they only cross a few rows:
    the fewer rows change, the less of the window has to be redrawn.
    """
    for ripple in ripples[:]:                 # loop over a copy so we can remove as we go
        age = now - ripple["start"]
        if age > 0.4:
            ripples.remove(ripple)
            continue
        draw_circle(buffer, ripple["x"], ripple["y"], 6 + age * 40,
                    0.6 * (1 - age / 0.4), ripple["color"], stretch=ripple["stretch"])


def draw_countdown(buffer, scene, elapsed, center_x, now):
    """3, 2, 1. Each number punches in big and settles. Returns True when it's over."""
    if elapsed >= settings.COUNTDOWN_SECONDS:
        return True
    number = settings.COUNTDOWN_SECONDS - int(elapsed)
    part = elapsed - int(elapsed)                 # 0 to 1 within this number's second
    if scene["last_tick"] != number:              # first frame of a new number
        scene["last_tick"] = number
        sound.play("click")
        add_ripple(scene["ripples"], center_x, 36, "accent", now)
    scale = 6 + 3 * (1 - ease_out(part * 5))
    brightness = 1.0
    if part > 0.75:
        brightness = 1 - (part - 0.75) / 0.25 * 0.7
    text = str(number)
    draw_big_text(buffer, center_x - text_width(text, scale) / 2, 36 - 3.5 * scale,
                  text, scale, brightness, "accent")
    return False
