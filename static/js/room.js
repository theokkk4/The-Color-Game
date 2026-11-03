/* room.js - lobby for head-to-head: create/join a room, Ready, split score bar. Owner: Theo
 * Runs after game.js, which owns the socket and the game board.
 */

var socket = window.Board.socket;
var mySid = null;
var opponentSid = null;
var totalTrials = 30;

var lobby = {
  screen: document.getElementById("screen-lobby"),
  setup: document.getElementById("lobby-setup"),
  room: document.getElementById("lobby-room"),
  modeSelect: document.getElementById("room-mode"),
  create: document.getElementById("btn-create"),
  join: document.getElementById("btn-join"),
  joinCode: document.getElementById("join-code"),
  joinError: document.getElementById("join-error"),
  code: document.getElementById("room-code"),
  modeLabel: document.getElementById("room-mode-label"),
  players: document.getElementById("player-list"),
  ready: document.getElementById("btn-ready"),
  status: document.getElementById("lobby-status")
};
var bar = {
  wrap: document.getElementById("score-bar"),
  leftName: document.getElementById("score-left-name"),
  leftVal: document.getElementById("score-left-val"),
  rightName: document.getElementById("score-right-name"),
  rightVal: document.getElementById("score-right-val"),
  fillLeft: document.getElementById("score-fill-left"),
  fillRight: document.getElementById("score-fill-right")
};

var playerName = document.body.dataset.name || localStorage.getItem("playerName") || "Player";

socket.on("connect", function () {
  mySid = socket.id;
  // Arriving with ?code=ABCD in the URL joins straight away.
  var urlCode = document.body.dataset.code;
  if (urlCode) socket.emit("join_room", { name: playerName, code: urlCode });
});

lobby.create.addEventListener("click", function () {
  socket.emit("join_room", { name: playerName, mode: lobby.modeSelect.value });
});

lobby.join.addEventListener("click", function () {
  var code = lobby.joinCode.value.trim().toUpperCase();
  if (code.length !== 4) { lobby.joinError.textContent = "Codes are 4 letters."; return; }
  socket.emit("join_room", { name: playerName, code: code });
});

lobby.ready.addEventListener("click", function () {
  socket.emit("start_game", {});
  lobby.ready.disabled = true;
  lobby.status.textContent = "Waiting for the other player to be ready...";
});

function renderLobby(state) {
  lobby.setup.classList.add("hidden");
  lobby.room.classList.remove("hidden");
  lobby.code.textContent = state.code;
  lobby.modeLabel.textContent = "mode: " + state.mode;

  lobby.players.innerHTML = "";
  state.players.forEach(function (p) {
    var chip = document.createElement("div");
    chip.className = "player-chip" + (p.ready ? " ready" : "");
    chip.textContent = p.name + (p.sid === mySid ? " (you)" : "") + (p.ready ? " - ready" : "");
    lobby.players.appendChild(chip);
    if (p.sid !== mySid) opponentSid = p.sid;
  });

  if (state.players.length < 2) {
    lobby.status.textContent = "Waiting for a second player...";
  } else if (!lobby.ready.disabled) {
    lobby.status.textContent = "Both here. Press Ready!";
  }
}

function renderScoreBar(state) {
  var me = null, other = null;
  state.players.forEach(function (p) { if (p.sid === mySid) me = p; else other = p; });
  if (!me) return;
  bar.wrap.classList.remove("hidden");
  bar.leftName.textContent = me.name;
  bar.leftVal.textContent = me.score;
  bar.fillLeft.style.width = (me.score / totalTrials * 50) + "%";
  if (other) {
    bar.rightName.textContent = other.name;
    bar.rightVal.textContent = other.score;
    bar.fillRight.style.width = (other.score / totalTrials * 50) + "%";
  }
}

socket.on("room_update", function (state) {
  if (state.error) { lobby.joinError.textContent = state.error; return; }
  lobby.joinError.textContent = "";
  renderLobby(state);
});

socket.on("start_game", function (data) {
  totalTrials = data.total || totalTrials;
  lobby.screen.classList.add("hidden");
  bar.wrap.classList.remove("hidden");
});

socket.on("score_update", renderScoreBar);

