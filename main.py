# main.py - opens the window and runs the game loop.  (Theo)
#
# The Color Game: a Stroop effect reaction game for CIS 1051. The whole thing
# is drawn as ASCII art. About 30 times a second we:
#   1. clear a small pixel buffer (160 x 90 brightness numbers)
#   2. let the current scene draw into it
#   3. turn every pixel into a character and paint the rows in the window
#
# A scene is a file in scenes/ with three functions:
#   start(app)                      -> a dict holding that scene's state
#   on_key(scene, app, key, when)   -> the name of the next scene, or None
#   draw(scene, app, buffer, now)   -> the name of the next scene, or None
#
# Run:  python main.py

import time

import settings
import sound
from render import screen as window
from render.buffer import make_buffer, clear, add_label, buffer_to_rows
from scenes import intro, menu, game, duel, results, leaderboard

SCENES = {"intro": intro, "menu": menu, "game": game, "duel": duel,
          "results": results, "leaderboard": leaderboard}

# Things every scene can see and change.
app = {
    "player": "",
    "mode": "classic",
    "menu_choice": 0,            # so the menu remembers which line you were on
    "last_run": None,            # the results screen reads the finished run from here
    "scene_name": "",
    "scene": None,
    "held": {},                  # keys that are down right now
    "frame_ms": 0,
    "next_frame": 0,             # when the next frame is due
}


def switch(name):
    app["scene_name"] = name
    app["scene"] = SCENES[name].start(app)


def key_down(event):
    when = time.perf_counter()   # note the time first, before anything slower happens
    key = window.key_name(event)
    if key in app["held"]:
        return                   # a held key repeats itself; only the first press counts
    app["held"][key] = True
    next_scene = SCENES[app["scene_name"]].on_key(app["scene"], app, key, when)
    if next_scene:
        switch(next_scene)


def key_up(event):
    app["held"].pop(window.key_name(event), None)


def frame():
    started = time.perf_counter()
    buffer = app["buffer"]
    scene = app["scene"]
    root = app["screen"]["root"]

    clear(buffer)
    next_scene = SCENES[app["scene_name"]].draw(scene, app, buffer, started)
    if settings.SHOW_FRAME_TIME:
        add_label(buffer, 0, 0, "%d ms" % app["frame_ms"])
    window.paint(app["screen"], buffer_to_rows(buffer))

    # Reaction time starts when the word is really on screen, so push the
    # frame out to the window before starting the clock.
    root.update_idletasks()
    if scene.get("stamp_after_paint"):
        scene["shown_at"] = time.perf_counter()
        scene["stamp_after_paint"] = False

    if next_scene:
        switch(next_scene)

    # Frames are due every 1/30 of a second. If this one ran long, the next
    # one starts sooner to make up for it, so the game keeps its pace.
    now = time.perf_counter()
    app["frame_ms"] = (now - started) * 1000
    app["next_frame"] += 1 / settings.FPS
    if app["next_frame"] < now - 0.1:
        app["next_frame"] = now              # way behind (the window was dragged?): start over
    root.after(max(1, int((app["next_frame"] - now) * 1000)), frame)


def open_game():
    sound.load_sounds()
    app["screen"] = window.open_window()
    app["buffer"] = make_buffer(settings.GRID_W, settings.GRID_H)
    root = app["screen"]["root"]
    root.bind("<KeyPress>", key_down)
    root.bind("<KeyRelease>", key_up)
    root.bind("<FocusOut>", lambda event: app["held"].clear())

    # bring the window to the front so the keyboard works without clicking it first
    root.lift()
    root.attributes("-topmost", True)
    root.after(300, lambda: root.attributes("-topmost", False))
    root.focus_force()

    switch("intro")
    app["next_frame"] = time.perf_counter()
    frame()


if __name__ == "__main__":
    open_game()
    app["screen"]["root"].mainloop()
