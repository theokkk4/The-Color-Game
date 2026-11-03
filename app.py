"""
app.py - the Flask + Socket.IO server for The Color Game.
Owner: Issaka

Run it:        python app.py
Then open:     http://localhost:5000

Pages are plain HTML (templates/). The game itself talks over Socket.IO.
Socket event names, both directions, are fixed and shared with the JS:
    browser -> server:  join_room, start_game, answer
    server -> browser:  room_update, start_game, trial, score_update, game_over
"""

import eventlet
eventlet.monkey_patch()     # must run before Flask is imported, so sockets are cooperative

import os

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_socketio import join_room as socket_join_room

import settings
from core import rooms
from core.trial import make_trials, public_trial
from core.session import record_answer
from core.scoring import summarize
from data.logger import log_trial
from data.analyze import load_trials
from data.leaderboard import top_scores

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def page_context():
    """Values every template can use."""
    return {
        "color_hex": settings.COLOR_HEX,
        "keys": settings.KEYS,
        "modes": settings.MODES,
    }


@app.route("/")
def index():
    return render_template("index.html", **page_context())


@app.route("/game")
def game():
    mode = request.args.get("mode", "classic")
    if mode not in settings.MODES:
        mode = "classic"
    name = request.args.get("name", "")
    return render_template("game.html", mode=mode, name=name, **page_context())


@app.route("/room")
def room():
    name = request.args.get("name", "")
    code = request.args.get("code", "").upper()
    return render_template("room.html", name=name, code=code, **page_context())


@app.route("/leaderboard")
def leaderboard():
    mode = request.args.get("mode", "classic")
    if mode not in settings.MODES:
        mode = "classic"
    entries = top_scores(load_trials(), mode=mode, n=10)
    return render_template("leaderboard.html", mode=mode, entries=entries, **page_context())


# --------------------------------------------------------------------------
# Socket events
# --------------------------------------------------------------------------

def send_trial(room, sid):
    """Send this player's next trial to only their browser."""
    player = room["players"][sid]
    trial = room["trials"][player["index"]]
    emit("trial", public_trial(trial, len(room["trials"])), to=sid)


@socketio.on("join_room")
def on_join_room(data):
    """Create a room (no code given) or join one (code given)."""
    data = data or {}
    name = data.get("name", "")
    code = (data.get("code") or "").strip().upper()
    mode = data.get("mode", "classic")

    if code:
        room = rooms.join_room(code, request.sid, name)
        if room is None:
            emit("room_update", {"error": "Room %s is full or does not exist." % code})
            return
    else:
        room = rooms.create_room(request.sid, name, mode)

    socket_join_room(room["code"])
    emit("room_update", rooms.public_state(room), to=room["code"])


@socketio.on("start_game")
def on_start_game(data):
    """A player pressed Ready. When everyone is ready the game begins."""
    room = rooms.get_room_for_sid(request.sid)
    if room is None or room["started"]:
        return

    rooms.mark_ready(room, request.sid)
    emit("room_update", rooms.public_state(room), to=room["code"])
    if not rooms.all_ready(room):
        return

    rooms.start_room(room, make_trials(room["mode"], settings.TRIALS_PER_RUN))

    # Everyone runs the same countdown, then the first word appears together.
    emit("start_game", {"countdown": settings.COUNTDOWN_SECONDS,
                        "total": settings.TRIALS_PER_RUN}, to=room["code"])
    socketio.sleep(settings.COUNTDOWN_SECONDS)
    for sid in list(room["players"].keys()):
        send_trial(room, sid)


@socketio.on("answer")
def on_answer(data):
    """Check a keypress, log it, send the score and the next trial."""
    data = data or {}
    room = rooms.get_room_for_sid(request.sid)
    if room is None or not room["started"]:
        return
    player = room["players"][request.sid]
    if player["done"]:
        return

    trial = room["trials"][player["index"]]
    if data.get("trial_num") != trial["trial_num"]:
        return      # stale or duplicate answer, ignore it

    result = record_answer(trial, data.get("key"), data.get("reaction_ms"))
    player["results"].append(result)
    player["index"] += 1

    # Add who/where before logging so the CSV row is complete.
    log_row = dict(result)
    log_row["player"] = player["name"]
    log_row["room"] = room["code"]
    log_trial(log_row)

    state = rooms.public_state(room)
    state["last"] = {"sid": request.sid, "trial_num": result["trial_num"],
                     "correct": result["correct"], "reaction_ms": result["reaction_ms"]}
    emit("score_update", state, to=room["code"])

    if player["index"] < len(room["trials"]):
        send_trial(room, request.sid)
        return

    player["done"] = True
    if rooms.all_done(room):
        finish_room(room)


def finish_room(room):
    """Send every player's summary so the results screen can draw itself."""
    players = []
    for sid, p in room["players"].items():
        players.append({"sid": sid, "name": p["name"], "summary": summarize(p["results"])})

    winner = None
    if len(players) > 1:
        best = max(players, key=lambda p: (p["summary"]["correct"], -p["summary"]["mean_rt"]))
        winner = best["name"]

    emit("game_over", {"code": room["code"], "mode": room["mode"],
                       "players": players, "winner": winner}, to=room["code"])


@socketio.on("disconnect")
def on_disconnect():
    room = rooms.remove_player(request.sid)
    if room is not None:
        emit("room_update", rooms.public_state(room), to=room["code"])
    # TODO(Issaka): if the game had started, finish_room() for the player left behind instead of leaving them waiting.


if __name__ == "__main__":
    # Render sets PORT; locally we default to 5000.
    port = int(os.environ.get("PORT", 5000))
    print("The Color Game running on http://localhost:%d" % port)
    try:
        socketio.run(app, host="0.0.0.0", port=port, debug=False)
    except OSError:
        # On macOS, AirPlay Receiver also listens on 5000. Pick another port:
        #   PORT=5001 python app.py
        print("Port %d is already in use. Try:  PORT=5001 python app.py" % port)
