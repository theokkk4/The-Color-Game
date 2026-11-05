# Proposal

## What will (likely) be the title of your project?

The Color Game

## In just a sentence or two, summarize your project. (E.g., "A website that lets you buy and sell stocks.")

A Stroop effect reaction game rendered entirely in ASCII art. The word says RED but it's printed in blue, and you have to hit the key for the ink color as fast as you can. Solo modes plus head-to-head on one keyboard.

## In a paragraph or more, detail your project. What will your software do? What features will it have? How will it be executed?

It's a pure Python desktop app. Tkinter makes the window, and every frame we draw into a small pixel buffer in Python, then turn each pixel into a text character (like ` .:-=+*#%@`) and paint it as colored monospace text. Menus, gameplay, and the intro all go through that one renderer so the whole game has a single look. pygame is only used for sound.

It opens with a short cinematic intro: an eye drawn out of characters opens, blinks, looks around, the iris cycles through the game's colors, then the camera dives through the pupil into a starfield where the title fades in.

Modes: Classic (answer the ink color), Reverse (answer the word), Speed (word disappears after 700 ms), and Head-to-Head, where two players share a keyboard and race through the same trials with a split screen and a live score bar.

Every trial gets logged to a CSV (player, mode, word, ink color, congruent, correct, reaction time). A separate script reads that and gives each player's average reaction time, accuracy, and Stroop effect (how much slower you are on mismatched trials), plus charts with matplotlib.

## If planning to combine 1051's final project with another course's final project, with which other course? And which aspect(s) of your proposed project would relate to 1051, and which aspect(s) would relate to the other course?

N/A

## If planning to collaborate with 1 or 2 classmates for the final project, list their names, email addresses, and the names of their assigned TAs below.

- Theodore King IV, theok1384@gmail.com, TA: Bao Huynh
- Issaka Coulibaly, issaka.coulibaly@temple.edu, TA: Bao Huynh
- Oliver Sims, oliver.sims@temple.edu, TA: Bao Huynh

## In the world of software, most everything takes longer to implement than you expect. And so it's not uncommon to accomplish less in a fixed amount of time than you hope.

### In a sentence (or list of features), define a GOOD outcome for your final project. I.e., what WILL you accomplish no matter what?

- The ASCII renderer works: pixel buffer to characters in a Tkinter window
- Classic solo mode playable: menu, countdown, 30 trials, results with reaction time, accuracy, Stroop effect
- Trials logged to CSV and a script that prints stats per player

### In a sentence (or list of features), define a BETTER outcome for your final project. I.e., what do you THINK you can accomplish before the final project's deadline?

- The cinematic eye intro
- Head-to-Head split screen on one keyboard
- Reverse and Speed modes
- Sound, screen flash and shake on correct/wrong
- Charts from the CSV and a leaderboard

### In a sentence (or list of features), define a BEST outcome for your final project. I.e., what do you HOPE to accomplish before the final project's deadline?

- Run 20+ students through it and answer one real question with the data (like: is the Stroop effect bigger after you've been studying for 30 minutes?) with a chart in a FINDINGS.md
- Emotional Stroop variant (neutral vs loaded words)
- A shareable results card image

## In a paragraph or more, outline your next steps. What new skills will you need to acquire? What topics will you need to research? If working with one of two classmates, who will do what?

Week 1 we set up the repo and each build our own piece so nobody's blocked. Theo does the renderer and UI (pixel buffer, character ramp, the Tkinter window, the intro animation, menus, screens). Issaka does the game engine (trial generation, timing, scoring, head-to-head rules). Oliver does the data side (CSV logging, analysis, charts, leaderboard). Week 2 we hook the pieces together and get Classic mode playable. Week 3 is head-to-head, the other modes, the intro polish. Week 4 is the experiment, video, and README.

Stuff we need to learn: Tkinter (window, text widget, key events, a timed loop), how to draw shapes and text into a 2D list and convert brightness to characters, easing functions so animation feels smooth, timing keypresses accurately with `time.perf_counter()`, matplotlib for charts, and the actual Stroop effect (Stroop, 1935) so our modes make sense. We'll use GitHub Desktop, everyone on their own branch committing their own files, PRs into main weekly, and meet in lab to merge and test.
