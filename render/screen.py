# render/screen.py - the window. Paints rows of colored characters.  (Theo)
#
# The picture arrives as text (see buffer_to_rows in render/buffer.py). Each
# row is a few "layers", one per color, and every layer is one text item on a
# Tkinter canvas. Stacking the layers gives a line with many colors in it.
# A canvas is used instead of a Text widget because we can choose exactly how
# far apart the rows are: the same distance as the characters, so one cell is
# a square pixel and circles come out round.

import tkinter
import tkinter.font

import settings

FONT_CHOICES = ["Menlo", "Consolas", "DejaVu Sans Mono", "Courier New", "Courier"]
SHADES = [0.5, 1.0]              # how much of the color a dim / bright cell gets
FLUSH_GAP = 8                    # this many unchanged rows in between is "far apart"


def open_window():
    root = tkinter.Tk()
    root.title("The Color Game")
    root.geometry(settings.WINDOW_SIZE)
    root.minsize(640, 360)
    root.configure(bg=settings.BACKGROUND)
    canvas = tkinter.Canvas(root, bg=settings.BACKGROUND, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # the first monospace font this computer actually has
    family = "Courier"
    available = tkinter.font.families()
    for choice in FONT_CHOICES:
        if choice in available:
            family = choice
            break

    screen = {
        "root": root,
        "canvas": canvas,
        "font": tkinter.font.Font(family=family, size=-12),
        "items": {},             # (row, layer) -> canvas text item
        "texts": {},             # (row, layer) -> what that item says right now
        "starts": {},            # (row, layer) -> which column that item starts at
        "shown": [{} for row in range(settings.GRID_H)],  # what each row looked like last frame
        "colors": {},            # layer -> "#rrggbb"
        "cell": 8.0, "left": 0.0, "top": 0.0, "lift": 0.0,
    }
    root.update()                # so the canvas knows its real size
    fit(screen)
    canvas.bind("<Configure>", lambda event: fit(screen))
    return screen


def fit(screen):
    """Pick the biggest font where the whole grid still fits in the window."""
    canvas = screen["canvas"]
    font = screen["font"]
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # how wide one character is compared to the font size (about 0.6)
    font.configure(size=-100)
    ratio = font.measure("@" * 100) / 100 / 100
    size = int(min(width / settings.GRID_W, height / settings.GRID_H) / ratio)
    size = max(4, size)
    font.configure(size=-size)

    cell = font.measure("@" * settings.GRID_W) / settings.GRID_W
    screen["cell"] = cell
    screen["left"] = (width - cell * settings.GRID_W) / 2      # center the picture
    screen["top"] = (height - cell * settings.GRID_H) / 2
    # A text item is placed by the top of its line, but a character sits lower
    # than that. Lift each row so characters land in the middle of their cell.
    screen["lift"] = font.metrics("ascent") - size * 0.33 - cell / 2

    for name, item in screen["items"].items():
        canvas.coords(item, screen["left"] + screen["starts"][name] * cell, row_y(screen, name[0]))


def row_y(screen, row):
    return screen["top"] + row * screen["cell"] - screen["lift"]


def layer_color(screen, layer):
    """(color tag, shade) -> a real color, mixed toward the background when dim."""
    if layer not in screen["colors"]:
        tag, shade = layer
        strength = SHADES[shade]
        full = settings.COLOR_HEX[tag]
        back = settings.BACKGROUND
        mixed = "#"
        for i in (1, 3, 5):                       # red, green, blue
            a = int(full[i:i + 2], 16)
            b = int(back[i:i + 2], 16)
            mixed += "%02x" % int(b + (a - b) * strength)
        screen["colors"][layer] = mixed
    return screen["colors"][layer]


def paint(screen, rows):
    """Show one frame. Only rows that changed since the last frame are touched.

    Tkinter redraws one rectangle that covers everything that changed, and
    the bigger the rectangle the slower it is. If the changes are in two
    places far apart (the title at the top, a comet at the bottom) we tell it
    to redraw after the first one, so it never has to redraw the gap between.
    """
    canvas = screen["canvas"]
    waiting = False              # are there changes Tkinter hasn't redrawn yet?
    last_changed = 0

    for row, layers in enumerate(rows):
        if layers == screen["shown"][row]:
            if waiting and row - last_changed >= FLUSH_GAP:
                canvas.update_idletasks()
                waiting = False
            continue
        paint_row(screen, row, layers)
        screen["shown"][row] = layers
        waiting = True
        last_changed = row
    if waiting:
        canvas.update_idletasks()


def paint_row(screen, row, layers):
    canvas = screen["canvas"]
    items = screen["items"]
    texts = screen["texts"]
    starts = screen["starts"]

    for layer, line in layers.items():
        # A layer is mostly spaces. Cut them off both ends and move the text
        # item to where the first character is, so there's less to draw.
        text = line.rstrip()
        start = len(text)
        text = text.lstrip()
        start -= len(text)

        name = (row, layer)
        if name not in items:
            items[name] = canvas.create_text(
                screen["left"] + start * screen["cell"], row_y(screen, row), text=text,
                anchor="nw", font=screen["font"], fill=layer_color(screen, layer))
            texts[name] = text
            starts[name] = start
            continue
        if texts[name] != text:
            canvas.itemconfigure(items[name], text=text)
            texts[name] = text
        if starts[name] != start:
            canvas.coords(items[name], screen["left"] + start * screen["cell"], row_y(screen, row))
            starts[name] = start

    # a layer this row had last frame but not this one has to be emptied
    for layer in screen["shown"][row]:
        if layer not in layers and texts[(row, layer)] != "":
            canvas.itemconfigure(items[(row, layer)], text="")
            texts[(row, layer)] = ""


def key_name(event):
    """A short, lowercase name for the key in a Tkinter key event."""
    name = event.keysym.lower()
    renames = {"semicolon": ";", "return": "enter", "kp_enter": "enter", "space": " "}
    return renames.get(name, name)
