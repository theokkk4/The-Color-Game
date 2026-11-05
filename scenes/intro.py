# scenes/intro.py - the opening cinematic.  (Theo)
#
# About nine seconds, and any key skips it:
#   1. a line of light wanders in the dark       (scenes/trails.py)
#   2. it unfolds into a ribbon of five colors
#   3. the ribbon bursts into sparks that settle into a line across the middle
#   4. the line opens into an eye, with the sparks riding the eyelids
#   5. the eye blinks, looks left and right, and its iris cycles the game colors
#   6. we fall into the pupil, to black
#   7. stars, comets and the title
#
# Everything is worked out from t, the seconds since the intro began, so
# there's nothing to keep track of between frames.

import math
import random

import settings
from render.buffer import set_pixel, bloom
from render.draw import draw_line, draw_circle, draw_text_centered
from render.easing import progress, smoothstep, ease_in_out
from scenes import backdrop, trails

CX = settings.GRID_W / 2         # the eye sits in the middle of the screen
CY = settings.GRID_H / 2
FIBERS = 96                      # the iris is cut into this many thin slices

# when each part starts, in seconds
OPEN_AT = 3.9
BLINK_AT = 5.0
COLOR_AT = 5.2
GAZE_AT = 5.4
DIVE_AT = 6.7
TITLE_AT = 7.5
READY_AT = 8.8


def start(app):
    return {
        "t0": None,
        # one random brightness per slice of the iris, which makes it look fibrous
        "fibers": [random.random() for i in range(FIBERS)],
        "sparks": trails.make_sparks(42),
        "stars": backdrop.make_stars(110),
        "comets": backdrop.make_comets(4),
    }


def on_key(scene, app, key, when):
    return "menu"                # any key skips


def draw(scene, app, buffer, now):
    if scene["t0"] is None:
        scene["t0"] = now
    t = now - scene["t0"]
    if t >= TITLE_AT:
        draw_title_part(scene, buffer, t, now)
        return None

    openness = ease_in_out(progress(t, OPEN_AT, 0.9))          # 4. the lids part
    if t >= OPEN_AT:
        draw_eye_part(scene, buffer, t, openness)

    if t < trails.BURST_AT + 0.4:                              # 1 and 2. the line, then the ribbon
        fade_in = smoothstep(progress(t, 0, 0.5))
        fade_out = 1 - progress(t, trails.BURST_AT, 0.4)
        trails.draw_ribbon(buffer, t, fade_in * fade_out)
    if trails.BURST_AT <= t < BLINK_AT:                        # 3. sparks, fading as the eye fills in
        alpha = 1 - progress(t, OPEN_AT + 0.3, BLINK_AT - OPEN_AT - 0.3)
        trails.draw_sparks(buffer, scene["sparks"], t, openness, alpha)
    bloom(buffer, 0.8, 0.3)
    return None


def draw_eye_part(scene, buffer, t, openness):
    fade = smoothstep(progress(t, OPEN_AT + 0.1, 0.7))         # the solid eye fades in

    blink = progress(t, BLINK_AT, 0.35)                        # 5. one quick blink
    if 0 < blink < 1:
        openness *= 1 - math.sin(blink * math.pi)
    look = smoothstep(progress(t, GAZE_AT, 1.2))               # ... then left, then right
    gaze = -9 * math.sin(look * 2 * math.pi)

    dive = progress(t, DIVE_AT, TITLE_AT - DIVE_AT)            # 6. zoom until the pupil is everything
    zoom = 1 + 14 * dive ** 3

    draw_eye(buffer, scene["fibers"], fade, openness, gaze, zoom, t - COLOR_AT)
    lash_glow = 0.75 * progress(t, OPEN_AT + 0.3, 0.4)
    if lash_glow > 0:
        draw_lashes(buffer, lash_glow, openness, zoom)
    if openness > 0.6:
        # the small bright highlight, up and to the left on the iris
        iris = settings.IRIS * zoom
        draw_circle(buffer, CX + gaze * zoom - iris * 0.4, CY - iris * 0.4,
                    max(1, iris * 0.14), fade, "white", filled=True)


def draw_eye(buffer, fibers, fade, openness, gaze, zoom, color_clock):
    """Fill in every pixel between the two eyelids."""
    half_width = settings.EYE_HALF_WIDTH * zoom
    top_height = settings.LID_HEIGHT * openness * zoom
    bottom_height = top_height * 0.75
    iris = settings.IRIS * zoom
    pupil = settings.PUPIL * zoom
    iris_x = CX + gaze * zoom
    lid_glow = (0.4 + 0.5 * openness) * fade
    bright = buffer["bright"]
    color = buffer["color"]

    for x in range(max(0, int(CX - half_width)), min(buffer["w"], int(CX + half_width) + 1)):
        across = (x - CX) / half_width            # -1 at the left corner, +1 at the right
        arch = 1 - across * across                # lids are tallest in the middle
        y_top = CY - top_height * arch
        y_bottom = CY + bottom_height * arch

        for y in range(max(0, int(y_top) + 1), min(buffer["h"], int(y_bottom))):
            dx = x - iris_x
            dy = y - CY
            far = dx * dx + dy * dy               # distance from the iris center, squared
            if far < pupil * pupil:
                continue                          # the pupil stays black
            if far < iris * iris:
                far = math.sqrt(far)
                rim = far / iris                  # 0 at the center, 1 at the edge
                # which slice of the iris this pixel is in, from its angle
                slice_number = int((math.atan2(dy, dx) / math.pi + 1) * FIBERS / 2) % FIBERS
                ring = int(far / zoom * 2)
                glow = (0.3 + 0.4 * fibers[slice_number]
                        + 0.25 * fibers[(slice_number * 5 + ring) % FIBERS])
                if rim > 0.88:
                    glow *= 0.5                   # the dark ring around the edge
                # colors spread outward from the pupil, one after another
                wave = color_clock * 2.2 - rim * 0.9
                if wave >= 0:
                    color[y][x] = settings.COLORS[int(wave) % len(settings.COLORS)]
            else:
                glow = 0.3 - 0.15 * abs(across)   # the white of the eye, darker in the corners
                if y - y_top < 3 * zoom:
                    glow *= 0.6                   # shadow under the top lid
            bright[y][x] = glow * fade

        set_pixel(buffer, x, y_top, lid_glow)
        set_pixel(buffer, x, y_bottom, lid_glow * 0.8)


def draw_lashes(buffer, glow, openness, zoom):
    """Short strokes along the lids. They lean outward, and droop when the eye shuts."""
    half_width = settings.EYE_HALF_WIDTH * zoom
    top_height = settings.LID_HEIGHT * openness * zoom
    for step in range(-9, 10):
        across = step / 10
        arch = 1 - across * across
        x = CX + across * half_width
        y = CY - top_height * arch
        rise = (6 * openness - 2 * (1 - openness)) * (0.6 + 0.4 * arch) * zoom
        draw_line(buffer, x, y, x + across * 5 * zoom, y - rise, glow, "white", glow * 0.4)
    for step in range(-6, 7, 2):                  # fewer, shorter ones underneath
        across = step / 8
        x = CX + across * half_width
        y = CY + top_height * 0.75 * (1 - across * across)
        draw_line(buffer, x, y, x + across * 2 * zoom, y + 2.5 * openness * zoom, glow * 0.7)


def draw_title_part(scene, buffer, t, now):
    """7. Out of the black: stars, comets, and the name of the game."""
    sky = smoothstep(progress(t, TITLE_AT, 1.0))
    backdrop.draw_stars(buffer, scene["stars"], now, sky)
    backdrop.draw_comets(buffer, scene["comets"], now, sky)

    title = smoothstep(progress(t, TITLE_AT + 0.3, 1.0))
    if title > 0:
        backdrop.draw_rainbow_text(buffer, CX, 19, "THE COLOR", 3, title, now)
        backdrop.draw_rainbow_text(buffer, CX, 45, "GAME", 3, title, now)
        bloom(buffer, 0.6, 0.28 * title)

    if t > READY_AT:
        pulse = 0.86 + 0.14 * math.sin(now * 5)
        draw_text_centered(buffer, CX, 77, "PRESS ANY KEY", 1, pulse)
