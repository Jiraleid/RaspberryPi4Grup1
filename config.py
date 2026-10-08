"""
config.py
---------
Configuració global del Media Center.
Centralitza colors, mides, rutes i paràmetres perquè tots els
mòduls comparteixin el mateix aspecte visual i comportament.
"""

import os

# ---------------------------------------------------------------------------
# Rutes base
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ruta del logo
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

# Carpetes de contingut multimèdia
MOVIES_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Pelicules")
SERIES_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Series")
BOOKS_DIR = os.path.expanduser("~/media_center/data/books/Libros")
COMICS_DIR = os.path.expanduser("~/media_center/data/books/Comics")
PHOTOS_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Fotos")
ROMS_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Roms")

# ---------------------------------------------------------------------------
# Pantalla
# ---------------------------------------------------------------------------
FULLSCREEN = True
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30

WINDOW_TITLE = "SofaTV Media Center"

# ---------------------------------------------------------------------------
# Colors (Paleta fosca i elegant basada en SofaTV)
# ---------------------------------------------------------------------------
COLOR_BG = (15, 22, 33)               # Blau fosc nit (molt fosc per a fons)
COLOR_BG_SECONDARY = (27, 38, 54)     # Blau fosc mitjà per a targes/botons
COLOR_PRIMARY = (217, 130, 43)        # Taronja SofaTV (per a elements principals/rellotge)
COLOR_PRIMARY_DARK = (175, 98, 25)    # Taronja més fosc per a botons premuts
COLOR_ACCENT = (58, 122, 189)         # Blau viu SofaTV
COLOR_TEXT = (255, 255, 255)          # Text blanc pur (alta llegibilitat)
COLOR_TEXT_MUTED = (160, 175, 195)    # Text secundari gris-blau clar
COLOR_SELECTED_BG = (217, 130, 43, 80)# Fons seleccionat en taronja amb transparència
COLOR_ERROR = (230, 70, 70)
COLOR_OK = (80, 200, 120)

# ---------------------------------------------------------------------------
# Tipografia
# ---------------------------------------------------------------------------
FONT_NAME = None
FONT_SIZE_TITLE = 48
FONT_SIZE_MENU = 32
FONT_SIZE_TEXT = 22
FONT_SIZE_SMALL = 16

# ---------------------------------------------------------------------------
# Xarxa / APIs
# ---------------------------------------------------------------------------
OPENWEATHER_API_KEY = "POSA_AQUI_LA_TEVA_API_KEY"
WEATHER_CITY = "Barcelona,ES"
WEATHER_UNITS = "metric"
WEATHER_LANG = "ca"

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------
KEY_UP = "up"
KEY_DOWN = "down"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_SELECT = "select"
KEY_BACK = "back"

KEY_REPEAT_DELAY = 400
KEY_REPEAT_INTERVAL = 120
