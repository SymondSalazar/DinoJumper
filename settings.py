import pygame
import os
from random import randint

# Dimensiones y Pantalla
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
FPS = 60

# Rutas
SPRITE_SHEET_PATH = os.path.join("sprites", "offline-sprite-2x.png")

# Colores
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (32, 32, 32)

# Físicas
GRAVITY = 0.6
SPEED_START = 6.0
MAX_SPEED = 13.0
ACCELERATION = 0.001

JUMP_VELOCITY = -13.0
DROP_VELOCITY = -5.0
MIN_JUMP_HEIGHT = -4.0

# Posiciones
DINO_X_POS = 50
GROUND_Y_POS = 380

# Dificultad
SCORE_DIVISOR = 10


def get_day_night_distance():
    return randint(400, 600)
