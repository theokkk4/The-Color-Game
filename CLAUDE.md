# The Color Game - team conventions

Stroop effect web game for CIS 1051 (intro Python). Team of three, each
owns a folder. Read this before changing anything.

## Stack (do not add to it)
- Python 3, Flask, Flask-SocketIO with eventlet.
- HTML / CSS / vanilla JS. No React, no bundler, no build step, no npm.
- No database, no ORM. State lives in Python dicts; results go to a CSV.
- Allowed libraries: flask, flask-socketio, eventlet, matplotlib, pillow, standard library.

## Code style (readable by a first-semester student)
- Plain functions, dicts and lists. Clear names. Short comments that say *why*.
- No classes unless truly needed. No type hints. No decorators beyond Flask's.
- All game logic lives in Python on the server. JS only draws the screen,
  captures keys, times the reaction, and sends/receives socket events.
- Stubs a teammate must replace are marked `# TODO(Issaka)` or `# TODO(Oliver)`
  with one sentence saying what the function should do.

## Who owns what
| Path | Owner |
|---|---|
| `app.py`, `settings.py`, `core/` | Issaka |
| `data/` | Oliver |
| `templates/`, `static/` | Theo |

Change files outside your folder only after talking to the owner.

## Game rules
- Modes: `classic` (answer ink color), `reverse` (answer the word),
  `speed` (classic, word hides after 700 ms).
- Colors red, green, blue, yellow, purple. Keys r g b y p.
- 30 trials per run, about 50% congruent (word == ink).
- Solo = a room with one player. Head-to-head = two players in one room,
  both get the identical trial list.
- Reaction time is measured in the browser with `performance.now()` from
  word shown to keypress and sent in the `answer` event. **Never time it on
  the server.**

## Socket events (exact names, do not rename)
| Direction | Event | Payload |
|---|---|---|
| browser -> server | `join_room` | `{name, mode}` to create, `{name, code}` to join |
| server -> browser | `room_update` | room state: `{code, mode, started, total, players[]}` or `{error}` |
| browser -> server | `start_game` | `{}` (marks the player ready) |
| server -> browser | `start_game` | `{countdown, total}` sent to the whole room |
| server -> browser | `trial` | `{trial_num, total, word, ink_color, mode, hide_after_ms}` |
| browser -> server | `answer` | `{trial_num, key, reaction_ms}` |
| server -> browser | `score_update` | room state plus `last: {sid, trial_num, correct, reaction_ms}` |
| server -> browser | `game_over` | `{code, mode, players: [{sid, name, summary}], winner}` |

## CSV (results/trials.csv, gitignored)
Columns, in order: `timestamp, player, mode, room, trial_num, word, ink_color,
congruent, response, correct, reaction_ms`. One row per answered trial.

## UI
- Dark theme via CSS variables: `--bg #0F1117`, `--surface #1A1D27`,
  `--text #E6E8EF`, `--muted #8B90A5`, `--accent #7C5CFF`.
- Font Inter, self-hosted with `@font-face` (drop the .woff2 in `static/fonts/`),
  fallback `system-ui`.
- Cards: 16px radius, 1px border, soft shadow. Screens fade in over 200 ms.
  Buttons scale 1.05 on hover. Word size uses `clamp()`.
- Sounds through `<audio>` tags: `click.wav`, `correct.wav`, `wrong.wav`.
  Missing files must never break the game.

## Running
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
python core/session.py   # 5-trial terminal demo
python -m data.analyze   # charts + report cards from results/trials.csv
```
`app.py` reads `PORT` from the environment so Render can set it.
Do not commit `results/`.
