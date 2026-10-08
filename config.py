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

# Carpetes on l'usuari pot desar el seu contingut multimèdia.
# Es poden canviar per rutes reals de la Raspberry Pi (USB, NAS, etc.)
MOVIES_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Pelicules")
SERIES_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Series")
BOOKS_DIR = os.path.expanduser("~/media_center/data/books/Libros")
COMICS_DIR = os.path.expanduser("~/media_center/data/books/Comics")
PHOTOS_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Fotos")
ROMS_DIR = os.path.join(os.path.expanduser("~"), "MediaCenter", "Roms")

# ---------------------------------------------------------------------------
# Pantalla
# ---------------------------------------------------------------------------
# A la Raspberry Pi normalment voldrem pantalla completa (FULLSCREEN = True).
# Durant el desenvolupament a l'ordinador és més còmode una finestra.
FULLSCREEN = True
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30

WINDOW_TITLE = "Media Center"

# ---------------------------------------------------------------------------
# Colors (paleta fosca, estil "media center")
# ---------------------------------------------------------------------------
COLOR_BG = (18, 18, 24)
COLOR_BG_SECONDARY = (28, 28, 36)
COLOR_PRIMARY = (0, 200, 180)          # accent turquesa
COLOR_PRIMARY_DARK = (0, 140, 130)
COLOR_TEXT = (235, 235, 240)
COLOR_TEXT_MUTED = (150, 150, 160)
COLOR_SELECTED_BG = (0, 200, 180, 60)  # amb alfa, per superposar
COLOR_ERROR = (220, 80, 80)
COLOR_OK = (100, 200, 120)

# ---------------------------------------------------------------------------
# Tipografia
# ---------------------------------------------------------------------------
# Si no es troba cap fitxer .ttf a ASSETS/fonts, es farà servir la
# tipografia per defecte de Pygame (pygame.font.get_default_font()).
FONT_NAME = None       # p.ex. "Roboto-Regular.ttf" dins de FONTS_DIR
FONT_SIZE_TITLE = 48
FONT_SIZE_MENU = 32
FONT_SIZE_TEXT = 22
FONT_SIZE_SMALL = 16

# ---------------------------------------------------------------------------
# Xarxa / APIs
# ---------------------------------------------------------------------------
# Clau gratuïta d'OpenWeatherMap (cal que l'usuari en generi una pròpia a
# https://openweathermap.org/api)
OPENWEATHER_API_KEY = "POSA_AQUI_LA_TEVA_API_KEY"
WEATHER_CITY = "Barcelona,ES"
WEATHER_UNITS = "metric"
WEATHER_LANG = "ca"

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------
# Pensat perquè funcioni tant amb teclat com amb un comandament
# (mapejat com a teclat mitjançant eines com `xboxdrv` o `antimicrox`).
KEY_UP = "up"
KEY_DOWN = "down"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_SELECT = "select"
KEY_BACK = "back"

# Repetició de tecla (per navegar ràpid mantenint premut)
KEY_REPEAT_DELAY = 400   # ms abans de començar a repetir
KEY_REPEAT_INTERVAL = 120  # ms entre repeticions
