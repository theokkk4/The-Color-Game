# scenes/trails.py - the lines of light at the start of the intro.  (Theo)
#
# One line wanders around the dark, unfolds into a ribbon of the five game
# colors, then bursts into a swarm of sparks that settle onto the outline of
# an eye and keep flowing around it.
#
# Nothing is remembered between frames. Every position is worked out from the
# time t, so a trail is just the same spark drawn at a few earlier times,
# each one a little dimmer.

import math
import random

import settings
from render.buffer import blend
from render.easing import progress, smoothstep, ease_out, ease_in_out, lerp

CX = settings.GRID_W / 2
CY = settings.GRID_H / 2
STEP = 0.016                 # seconds between two points of a trail
RIBBON_AT = 1.4              # when the single line starts to unfold
BURST_AT = 2.7               # when the ribbon breaks into sparks


def wander(t):
    """Where the line of light is at time t: big lazy loops around the screen."""
    x = CX + 54 * math.sin(t * 2.1 + 0.6) * math.cos(t * 0.7)
    y = CY + 27 * math.sin(t * 3.3 + 0.4)
    return x, y


def draw_ribbon(buffer, t, alpha):
    """The line, and later the five strands it splits into, each with a fading tail."""
    for k in range(48):
        then = t - k * STEP                       # an earlier moment = further down the tail
        if then < 0:
            break
        if then > BURST_AT:
            continue                              # the ribbon stops where it burst
        glow = alpha * (1 - k / 48) ** 1.5
        x, y = wander(then)
        unfold = smoothstep(progress(then, RIBBON_AT, 0.7))
        if unfold < 0.05:
            blend(buffer, x, y, glow, "white")
            continue

        # Strands sit side by side across the direction of travel. The sin()
        # makes them cross over each other, so the ribbon twists as it flies.
        ahead_x, ahead_y = wander(then + 0.01)
        length = math.hypot(ahead_x - x, ahead_y - y) or 1
        side_x = -(ahead_y - y) / length
        side_y = (ahead_x - x) / length
        spread = 3.4 * unfold * math.sin(then * 4.2)
        for number, color in enumerate(settings.COLORS):
            offset = (number - 2) * spread
            blend(buffer, x + side_x * offset, y + side_y * offset, glow, color)


def make_sparks(count):
    sparks = []
    for i in range(count):
        sparks.append({
            "color": settings.COLORS[i % len(settings.COLORS)],
            "angle": random.random() * 2 * math.pi,
            "spin": random.choice([-1, 1]) * (2.5 + random.random() * 3),
            "reach": 10 + random.random() * 30,          # how far the burst throws it
            "place": random.random(),                    # where on the outline it lands, 0 to 1
            "flow": random.choice([-1, 1]) * (0.05 + random.random() * 0.1),
            "on_iris": i % 3 == 0,                       # a third of them circle the iris
        })
    return sparks


def eye_point(spark, t, openness):
    """A point on the outline of the eye, moving steadily around it."""
    along = (spark["place"] + spark["flow"] * t) % 1
    if spark["on_iris"]:
        angle = along * 2 * math.pi
        return (CX + math.cos(angle) * settings.IRIS,
                CY + math.sin(angle) * settings.IRIS * openness)
    if along < 0.5:
        across = -1 + 4 * along                          # left to right along the top lid
        height = -settings.LID_HEIGHT * openness
    else:
        across = 3 - 4 * along                           # and back along the bottom one
        height = settings.LID_HEIGHT * 0.75 * openness
    return (CX + across * settings.EYE_HALF_WIDTH, CY + height * (1 - across * across))


def spark_point(spark, t, openness):
    since = t - BURST_AT
    # 1. thrown outward from where the ribbon ended, spinning as it goes
    grow = ease_out(progress(since, 0, 0.7))
    start_x, start_y = wander(BURST_AT)
    angle = spark["angle"] + spark["spin"] * since
    swirl_x = lerp(start_x, CX, grow) + math.cos(angle) * spark["reach"] * grow * 1.6
    swirl_y = lerp(start_y, CY, grow) + math.sin(angle) * spark["reach"] * grow * 0.8
    # 2. pulled onto the outline of the eye
    eye_x, eye_y = eye_point(spark, t, openness)
    pull = ease_in_out(progress(since, 0.35, 0.9))
    return lerp(swirl_x, eye_x, pull), lerp(swirl_y, eye_y, pull)


def draw_sparks(buffer, sparks, t, openness, alpha):
    for spark in sparks:
        for k in range(12):
            then = t - k * STEP * 1.5
            if then < BURST_AT:
                break
            x, y = spark_point(spark, then, openness)
            blend(buffer, x, y, alpha * (1 - k / 12), spark["color"])
