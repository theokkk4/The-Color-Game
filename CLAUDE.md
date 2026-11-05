# The Color Game

A Stroop effect reaction game for CIS 1051 (intro Python) at Temple. A color
word appears in some ink color and the player presses the key for the ink as
fast as they can. It is a pure Python desktop app, and the whole thing is
drawn as ASCII art.

Run it with `python main.py`. Stats and charts: `python -m data.analyze`.

## How the picture is made

Every frame, about 30 times a second:

1. `render/buffer.py` clears a small pixel buffer: 160 x 90 brightness numbers
   from 0.0 to 1.0, plus a color tag per pixel.
2. The current scene draws into it with the helpers in `render/draw.py`.
3. `buffer_to_rows` turns each pixel into a character from the ramp
   ` .:-=+*#%@` and `render/screen.py` paints the rows as colored monospace
   text on a Tkinter canvas.

Menus, gameplay and the intro all go through this one renderer. Nothing draws
straight to the window.

## Layout and owners

| Path | What it is | Owner |
|---|---|---|
| `main.py` | window setup, 30 fps loop, scene switching | Theo |
| `settings.py` | grid size, ramp, colors, keys, timings, trial count | everyone |
| `sound.py` | sound effects through pygame, silent if it's missing | Theo |
| `render/` | buffer, drawing, 5x7 font, easing, the Tkinter screen | Theo |
| `scenes/` | intro, menu, game, duel (head to head), results, leaderboard | Theo |
| `core/` | trials, checking answers, scoring | Issaka |
| `data/` | CSV logging, analysis and charts, leaderboard | Oliver |
| `sounds/` | click.wav, correct.wav, wrong.wav | Theo |
| `results/` | trials.csv and charts, gitignored | |

A scene is a file in `scenes/` with three functions: `start(app)` returns a
dict of that scene's state, `on_key(scene, app, key, when)` and
`draw(scene, app, buffer, now)` each return the name of the next scene or None.

## Code style

- It has to read like a first-semester student wrote it: plain functions,
  lists and dicts. No classes unless truly needed, no numpy, no type hints.
- Short comments that explain why, not what.
- Keep every file under about 250 lines. Split it if it grows past that.
- Allowed imports: tkinter, math, random, time, csv, os, matplotlib (charts
  only), pygame (sound only) and threading (only in sound.py, so a stuck
  sound system can't freeze the game). The game must still run if pygame is missing.
- No images and no outside assets except the .wav files in `sounds/`.
- Mark unfinished work for a teammate with one sentence:
  `# TODO(Issaka): ...` in `core/`, `# TODO(Oliver): ...` in `data/`.

## Rules that are easy to break

- Reaction time is measured with `time.perf_counter()`, from the frame the
  word is painted (main.py stamps `scene["shown_at"]` after painting) to the
  moment the key goes down. Don't add anything slow between those two points.
- CSV columns, in order: timestamp, player, mode, trial_num, word, ink_color,
  congruent, response, correct, reaction_ms.
- Tkinter is slow at redrawing big areas and at drawing many separate pieces
  of colored text. Keep changes on screen local where possible, and keep the
  number of colors on one row small. That is why the starfield updates 8
  times a second, titles are striped along rows, and there are two shades.
- Don't overwrite README.md or proposal.md. Theo edits those.
- Don't git commit or push. Theo does that.
