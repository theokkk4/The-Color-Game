Drop three short sounds here: `click.wav`, `correct.wav`, `wrong.wav`.
`templates/base.html` loads them with `<audio>` tags and `game.js` plays them.
If a file is missing, the play() error is swallowed and the game carries on.
