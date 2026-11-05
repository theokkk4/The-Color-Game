# render/easing.py - small math helpers that make motion look smooth.  (Theo)
#
# Most of these take t, a number from 0 (start) to 1 (end), and bend it so
# things speed up and slow down instead of moving at one constant speed.


def clamp(t):
    """Keep t between 0 and 1."""
    if t < 0:
        return 0.0
    if t > 1:
        return 1.0
    return t


def lerp(a, b, t):
    """The value t of the way from a to b. lerp(10, 20, 0.5) is 15."""
    return a + (b - a) * t


def progress(now, start, duration):
    """How far through an animation we are, 0 to 1."""
    return clamp((now - start) / duration)


def smoothstep(t):
    """Starts slow, ends slow. Good for fades."""
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    """Like smoothstep but with a stronger push in the middle. Good for movement."""
    t = clamp(t)
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):
    """Starts fast, then settles. Good for things that pop in."""
    t = clamp(t)
    return 1 - (1 - t) ** 3
