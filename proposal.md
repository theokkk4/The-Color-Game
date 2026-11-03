# Proposal

## What will (likely) be the title of your project?

The Color Game

## In just a sentence or two, summarize your project. (E.g., "A website that lets you buy and sell stocks.")

A web game based on the Stroop effect: the word says RED but it's printed in blue, and you have to hit the key for the ink color as fast as you can. Solo mode plus online head-to-head where two people race live.

## In a paragraph or more, detail your project. What will your software do? What features will it have? How will it be executed?

It's a Flask app with Flask-SocketIO so the browser and server can talk live, hosted on Render so anyone can play from a link. The page is HTML/CSS with a little JavaScript to show the word, catch keypresses, and time how fast you reacted. All the actual game logic is Python on the server: picking the words and colors, deciding if a trial is congruent or not, scoring, and running the multiplayer rooms.

Modes: Classic (answer the ink color), Reverse (answer the word), Speed (word vanishes after 700 ms), and Head-to-Head, where one person makes a room, gets a 4-letter code, the other joins, and the server sends them both the same trials at the same time with a live score bar and a winner screen.

Every trial gets logged to a CSV (player, mode, word, ink color, congruent, correct, reaction time). A separate Python script reads that and spits out each player's average reaction time, accuracy, and Stroop effect (how much slower you are on mismatched trials), plus charts with matplotlib and a shareable results card.

## If planning to combine 1051's final project with another course's final project, with which other course? And which aspect(s) of your proposed project would relate to 1051, and which aspect(s) would relate to the other course?

N/A

## If planning to collaborate with 1 or 2 classmates for the final project, list their names, email addresses, and the names of their assigned TAs below.

- Theodore King IV, theok1384@gmail.com, TA: Bao Huynh
- Issaka Coulibaly, issaka.coulibaly@temple.edu, TA: Bao Huynh
- Oliver Sims, oliver.sims@temple.edu, TA: Bao Huynh

## In the world of software, most everything takes longer to implement than you expect. And so it's not uncommon to accomplish less in a fixed amount of time than you hope.

### In a sentence (or list of features), define a GOOD outcome for your final project. I.e., what WILL you accomplish no matter what?

- Classic solo mode playable in the browser: menu, countdown, 30 trials, results with reaction time, accuracy, Stroop effect
- Flask server running locally with the game logic in Python
- Trials logged to CSV and a script that prints stats per player

### In a sentence (or list of features), define a BETTER outcome for your final project. I.e., what do you THINK you can accomplish before the final project's deadline?

- Live on Render with a public link
- Online head-to-head with room codes, live score bar, winner screen
- Reverse and Speed modes
- Clean dark UI with animations and sound
- Charts and a shareable results card image
- Leaderboard

### In a sentence (or list of features), define a BEST outcome for your final project. I.e., what do you HOPE to accomplish before the final project's deadline?

- Tournament mode, up to 4 players in a room
- Run 20+ students through it and answer one real question with the data (like: is the Stroop effect bigger after you've been studying for 30 minutes?) with a chart in a FINDINGS.md
- Emotional Stroop variant (neutral vs loaded words)

## In a paragraph or more, outline your next steps. What new skills will you need to acquire? What topics will you need to research? If working with one of two classmates, who will do what?

Week 1 we set up the repo and each build our own piece so nobody's blocked. Theo does the frontend (pages, CSS, animations, sound, the JS that talks to the server). Issaka does the engine (Flask server, trial generation, timing, scoring, head-to-head rooms). Oliver does the data side (CSV logging, analysis, charts, leaderboard). Week 2 we hook the pieces together and get solo mode working locally. Week 3 is head-to-head, the other modes, deploying to Render, and polish. Week 4 is the experiment, video, and README.

Stuff we need to learn: Flask and Flask-SocketIO, enough HTML/CSS/JS for the game screen, deploying Python on Render, timing reaction in the browser so network lag doesn't mess up the numbers, matplotlib, and the actual Stroop effect (Stroop, 1935) so our modes make sense. We'll use GitHub Desktop, everyone committing their own files, and meet in lab to merge and test.
