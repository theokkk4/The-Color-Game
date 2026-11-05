# sound.py - plays the sound effects, if it can.  (Theo)
#
# pygame is only used for sound. If pygame isn't installed, or a .wav file
# is missing from sounds/, the game just stays quiet instead of crashing.

import os
import threading

import settings

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"      # don't print pygame's hello message
try:
    import pygame
except ImportError:
    pygame = None

SOUNDS = {}                  # "click" -> a loaded pygame sound


def load_sounds():
    """Start loading the sounds without making the game wait for them.

    Setting up audio is usually instant, but if the computer's sound system
    is stuck it can take forever. Doing it on a second thread means the
    window opens either way, and the sounds just start working once loaded.
    """
    if pygame is None:
        return
    threading.Thread(target=load_in_background, daemon=True).start()


def load_in_background():
    try:
        pygame.mixer.init()
    except pygame.error:
        return               # no speakers / no audio device
    for name in ["click", "correct", "wrong"]:
        path = os.path.join(settings.SOUNDS_DIR, name + ".wav")
        if os.path.exists(path):
            try:
                SOUNDS[name] = pygame.mixer.Sound(path)
            except pygame.error:
                pass         # not a real .wav file, skip it


def play(name):
    if name in SOUNDS:
        SOUNDS[name].play()
