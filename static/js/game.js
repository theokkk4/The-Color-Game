/* game.js - draws the board, times reactions, talks to the server. Owner: Theo
 *
 * The browser never decides whether an answer is right. It only:
 *   1. shows the word the server sent,
 *   2. measures performance.now() from "word shown" to "key pressed",
 *   3. sends {key, reaction_ms} and waits for the server to reply.
 *
 * This file runs on both the solo page (game.html) and the room page
 * (room.html). room.js adds the lobby on top and reuses window.Board.
 */

var COLOR_HEX = { red: "#FF4D4D", green: "#3DDC84", blue: "#4D8DFF", yellow: "#FFD93D", purple: "#B57CFF" };
var VALID_KEYS = ["r", "g", "b", "y", "p"];

var socket = io();                      // shared with room.js
var body = document.body;
var myName = body.dataset.name || localStorage.getItem("playerName") || "Player";
var myMode = body.dataset.mode || "classic";
var autoStart = body.dataset.autoStart === "1";   // solo page starts as soon as the room exists

var roomCode = null;
var currentTrial = null;                // the trial on screen, or null while waiting
var shownAt = 0;                        // performance.now() when the word appeared
var hideTimer = null;
var countingDown = false;
var pendingTrial = null;                // a trial that arrived during the countdown

var el = {
  countdown: document.getElementById("screen-countdown"),
  countdownNumber: document.getElementById("countdown-number"),
  countdownHint: document.getElementById("countdown-hint"),
  play: document.getElementById("screen-play"),
  results: document.getElementById("screen-results"),
  word: document.getElementById("word"),
  progress: document.getElementById("progress-fill"),
  resultsTitle: document.getElementById("results-title"),
  tileRt: document.getElementById("tile-rt"),
  tileAcc: document.getElementById("tile-acc"),
  tileStroop: document.getElementById("tile-stroop"),
  sparkline: document.getElementById("sparkline"),
  again: document.getElementById("btn-again")
};

// ---------------------------------------------------------------- helpers

function show(screen) {
  [el.countdown, el.play, el.results].forEach(function (s) { s.classList.add("hidden"); });
  screen.classList.remove("hidden");
  // re-trigger the fade-in animation
  screen.style.animation = "none";
  void screen.offsetWidth;
  screen.style.animation = "";
}

function playSound(id) {
  var audio = document.getElementById(id);
  if (!audio) return;
  try {
    audio.currentTime = 0;
    var p = audio.play();
    if (p && p.catch) p.catch(function () {});   // missing file or autoplay block: ignore
  } catch (e) {}
}

function flash(correct) {
  var cls = correct ? "flash-correct" : "flash-wrong";
  body.classList.remove("flash-correct", "flash-wrong");
  void body.offsetWidth;
  body.classList.add(cls);
  setTimeout(function () { body.classList.remove(cls); }, 300);
}

function modeHint(mode) {
  if (mode === "reverse") return "Press the key for the WORD, ignore the ink.";
  if (mode === "speed") return "Ink color. Quick, the word disappears!";
  return "Press the key for the INK COLOR of the word.";
}

// ---------------------------------------------------------------- countdown

function runCountdown(seconds, onDone) {
  countingDown = true;
  show(el.countdown);
  el.countdownHint.textContent = modeHint(myMode);
  var n = seconds;
  el.countdownNumber.textContent = n;
  playSound("snd-click");
  var timer = setInterval(function () {
    n -= 1;
    if (n <= 0) {
      clearInterval(timer);
      countingDown = false;
      onDone();
      return;
    }
    el.countdownNumber.textContent = n;
    el.countdownNumber.style.animation = "none";
    void el.countdownNumber.offsetWidth;
    el.countdownNumber.style.animation = "";
    playSound("snd-click");
  }, 1000);
}

// ---------------------------------------------------------------- trials

function showTrial(trial) {
  currentTrial = trial;
  show(el.play);
  el.progress.style.width = ((trial.trial_num - 1) / trial.total * 100) + "%";
  el.word.textContent = trial.word;
  el.word.style.color = COLOR_HEX[trial.ink_color] || "#fff";
  el.word.style.visibility = "visible";

  // Start the clock the moment the word is on screen.
  shownAt = performance.now();

  if (hideTimer) clearTimeout(hideTimer);
  if (trial.hide_after_ms > 0) {
    hideTimer = setTimeout(function () { el.word.style.visibility = "hidden"; }, trial.hide_after_ms);
  }
}

function onKey(event) {
  if (!currentTrial) return;
  var key = event.key.toLowerCase();
  if (VALID_KEYS.indexOf(key) === -1) return;

  var reactionMs = Math.round(performance.now() - shownAt);
  var trial = currentTrial;
  currentTrial = null;                  // ignore more keys until the next trial arrives
  el.progress.style.width = (trial.trial_num / trial.total * 100) + "%";

  socket.emit("answer", { code: roomCode, trial_num: trial.trial_num, key: key, reaction_ms: reactionMs });
}
document.addEventListener("keydown", onKey);

// ---------------------------------------------------------------- results

function drawSparkline(canvas, times, flags) {
  var ctx = canvas.getContext("2d");
  var w = canvas.width, h = canvas.height, pad = 10;
  ctx.clearRect(0, 0, w, h);
  if (!times.length) return;

  var max = Math.max.apply(null, times) || 1;
  var stepX = (w - pad * 2) / Math.max(times.length - 1, 1);
  function x(i) { return pad + i * stepX; }
  function y(v) { return h - pad - (v / max) * (h - pad * 2); }

  ctx.strokeStyle = "#7C5CFF";
  ctx.lineWidth = 2;
  ctx.beginPath();
  times.forEach(function (t, i) { i === 0 ? ctx.moveTo(x(i), y(t)) : ctx.lineTo(x(i), y(t)); });
  ctx.stroke();

  // a dot per trial, red if that answer was wrong
  times.forEach(function (t, i) {
    ctx.fillStyle = flags[i] ? "#E6E8EF" : "#FF4D4D";
    ctx.beginPath();
    ctx.arc(x(i), y(t), 3, 0, Math.PI * 2);
    ctx.fill();
  });
}

function showResults(data) {
  var me = null;
  data.players.forEach(function (p) { if (p.sid === socket.id) me = p; });
  if (!me) me = data.players[0];
  var s = me.summary;

  if (data.winner) {
    el.resultsTitle.textContent = data.winner === me.name ? "You win!" : data.winner + " wins";
  } else {
    el.resultsTitle.textContent = "Results";
  }
  el.tileRt.textContent = s.mean_rt + " ms";
  el.tileAcc.textContent = Math.round(s.accuracy * 100) + "%";
  el.tileStroop.textContent = (s.stroop_effect_ms >= 0 ? "+" : "") + s.stroop_effect_ms + " ms";
  drawSparkline(el.sparkline, s.reaction_times, s.correct_flags);
  show(el.results);
}

el.again.addEventListener("click", function (e) { e.preventDefault(); window.location.reload(); });

// ---------------------------------------------------------------- socket events

socket.on("connect", function () {
  if (autoStart) socket.emit("join_room", { name: myName, mode: myMode });
});

socket.on("room_update", function (state) {
  if (state.error) return;              // room.js shows errors on the lobby
  roomCode = state.code;
  myMode = state.mode;
  if (autoStart && !state.started) socket.emit("start_game", { code: roomCode });
});

socket.on("start_game", function (data) {
  pendingTrial = null;
  runCountdown(data.countdown, function () {
    if (pendingTrial) { showTrial(pendingTrial); pendingTrial = null; }
  });
});

socket.on("trial", function (trial) {
  if (countingDown) { pendingTrial = trial; return; }
  showTrial(trial);
});

socket.on("score_update", function (state) {
  if (state.last && state.last.sid === socket.id) {
    flash(state.last.correct);
    playSound(state.last.correct ? "snd-correct" : "snd-wrong");
  }
});

socket.on("game_over", function (data) {
  currentTrial = null;
  showResults(data);
});

// Small public surface so room.js can reuse the board.
window.Board = { socket: socket, show: show, playSound: playSound, setRoom: function (c) { roomCode = c; } };
