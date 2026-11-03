"""
core/rooms.py - keeps track of every room and who is in it.
Owner: Issaka

A solo game is just a room with one player. All state lives in the ROOMS
dict below (no database). Each room looks like:

    ROOMS["ABCD"] = {
        "code": "ABCD",
        "mode": "classic",
        "started": False,
        "trials": [],             # filled by start_room()
        "players": {              # keyed by socket id (sid)
            "<sid>": {"name": "Theo", "ready": False, "index": 0,
                      "results": [], "done": False},
        },
    }
"""

import random

from settings import MAX_PLAYERS_PER_ROOM, MAX_NAME_LENGTH, MODES

ROOMS = {}          # code -> room dict
SID_TO_CODE = {}    # socket id -> room code, so we can find a player's room fast

# No I, O, 0, 1 so codes are easy to read out loud.
CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def new_code():
    """Return an unused 4-letter room code."""
    while True:
        code = "".join(random.choice(CODE_LETTERS) for _ in range(4))
        if code not in ROOMS:
            return code


def clean_name(name):
    name = (name or "").strip()[:MAX_NAME_LENGTH]
    return name or "Player"


def new_player(name):
    return {"name": clean_name(name), "ready": False, "index": 0,
            "results": [], "done": False}


def create_room(sid, name, mode):
    """Make a room with this player as the first member and return it."""
    if mode not in MODES:
        mode = "classic"
    room = {
        "code": new_code(),
        "mode": mode,
        "started": False,
        "trials": [],
        "players": {sid: new_player(name)},
    }
    ROOMS[room["code"]] = room
    SID_TO_CODE[sid] = room["code"]
    return room


def join_room(code, sid, name):
    """Add a player to an existing room. Returns the room, or None if it can't join."""
    room = ROOMS.get((code or "").upper())
    if room is None or room["started"]:
        return None
    if len(room["players"]) >= MAX_PLAYERS_PER_ROOM:
        return None
    room["players"][sid] = new_player(name)
    SID_TO_CODE[sid] = room["code"]
    return room


def get_room_for_sid(sid):
    code = SID_TO_CODE.get(sid)
    return ROOMS.get(code)


def mark_ready(room, sid):
    if sid in room["players"]:
        room["players"][sid]["ready"] = True


def all_ready(room):
    return all(p["ready"] for p in room["players"].values())


def start_room(room, trials):
    """Lock the room and hand every player the same trial list."""
    room["started"] = True
    room["trials"] = trials
    for player in room["players"].values():
        player["index"] = 0
        player["results"] = []
        player["done"] = False


def all_done(room):
    return all(p["done"] for p in room["players"].values())


def remove_player(sid):
    """Drop a player when their socket disconnects. Deletes empty rooms."""
    code = SID_TO_CODE.pop(sid, None)
    room = ROOMS.get(code)
    if room is None:
        return None
    room["players"].pop(sid, None)
    if not room["players"]:
        del ROOMS[code]
        return None
    return room


def public_state(room):
    """The part of a room that is safe and useful to send to browsers."""
    from core.scoring import score   # imported here to avoid a circular import

    players = []
    for sid, p in room["players"].items():
        players.append({
            "sid": sid,
            "name": p["name"],
            "ready": p["ready"],
            "score": score(p["results"]),
            "trial_num": p["index"],
            "done": p["done"],
        })
    return {
        "code": room["code"],
        "mode": room["mode"],
        "started": room["started"],
        "total": len(room["trials"]),
        "players": players,
    }

# TODO(Issaka): add a rematch() that resets a finished room so both players can play again without re-joining.
# TODO(Issaka): when one player disconnects mid-game, tell the other player instead of silently ending the game.
