"""
movies.py
---------
Mòdul de Pel·lícules i Sèries amb suport tàctil i reproducció de vídeo per a Raspberry Pi.
"""

import os
import subprocess
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text, draw_rounded_rect


# Directoris absoluts on cercar el contingut audiovisual
MOVIES_DIR = "/home/joviat/media_center/data/movies"
SERIES_DIR = "/home/joviat/media_center/data/series"


class MoviesModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.tab = "movies"  # "movies" o "series"

        self.movies_list = []
        self.series_dict = {}  # {"Nom_Serie": ["Episodi_1.mp4", ...]}
        self.selected_series = None  # Si s'ha entrat a explorar una sèrie

        # Paginació / Selecció
        self.selected_index = 0

        # Guardar rectangles per a clics/tocs
        self.interactive_rects = []

        # Carregar els fitxers directament al crear el mòdul
        self.scan_media()

    def on_enter(self):
        self.tab = "movies"
        self.selected_series = None
        self.selected_index = 0
        self.scan_media()

    def scan_media(self):
        """Detecta els fitxers de vídeo disponibles als directoris."""
        os.makedirs(MOVIES_DIR, exist_ok=True)
        os.makedirs(SERIES_DIR, exist_ok=True)

        valid_extensions = (".mp4", ".mkv", ".avi", ".mov")

        # Escanejar pel·lícules
        self.movies_list = [
            f for f in os.listdir(MOVIES_DIR)
            if f.lower().endswith(valid_extensions)
        ]

        # Escanejar sèries (carpetes per sèrie)
        self.series_dict = {}
        if os.path.exists(SERIES_DIR):
            for serie_name in os.listdir(SERIES_DIR):
                serie_path = os.path.join(SERIES_DIR, serie_name)
                if os.path.isdir(serie_path):
                    episodes = [
                        ep for ep in os.listdir(serie_path)
                        if ep.lower().endswith(valid_extensions)
                    ]
                    episodes.sort()
                    self.series_dict[serie_name] = episodes

    def play_video(self, video_path):
        """Reprodueix el vídeo usant MPV tancant i reobrint el display de Pygame netament."""
        if not os.path.exists(video_path):
            print(f"[ERROR] Fitxer no trobat: {video_path}")
            return

        if os.path.getsize(video_path) == 0:
            print(f"[ERROR] El fitxer està buit (0 bytes): {video_path}")
            return

        print(f"[INFO] Reproduint vídeo: {video_path}")

        # Libera temporalment el DRM Master/pantalla perquè MPV el pugui utilitzar
        pygame.display.quit()

        try:
            # Prova la reproducció amb MPV forçant el mode framebuffer o DRM
            cmd = ["mpv", "--fs", "--vo=drm,fbdev,gpu", "--ao=alsa", "--audio-device=alsa/hw:0,0", "--volume=100", video_path]
            subprocess.run(cmd, check=False)

        except Exception as e:
            print(f"[ERROR] Error en la reproducció: {e}")

        finally:
            # Reiniciar el display de Pygame netament
            pygame.display.init()
            new_screen = pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
                pygame.FULLSCREEN
            )

            # Reassignar la pantalla al gestor si existeix
            if hasattr(self.manager, 'screen'):
                self.manager.screen = new_screen

            pygame.event.clear()

            # Forçar el redibuixat
            self.draw(new_screen)
            pygame.display.flip()

    def get_current_items(self):
        """Retorna la llista d'elements actual segons la pestanya/vista."""
        if self.tab == "movies":
            return self.movies_list
        elif self.tab == "series":
            if self.selected_series is None:
                return list(self.series_dict.keys())
            else:
                return self.series_dict.get(self.selected_series, [])
        return []

    def handle_event(self, event):
        # 1. Gestió de tocs / clics
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for action_type, item_data, rect in self.interactive_rects:
                if rect.collidepoint(event.pos):
                    if action_type == "tab_movies":
                        self.tab = "movies"
                        self.selected_series = None
                        self.selected_index = 0
                    elif action_type == "tab_series":
                        self.tab = "series"
                        self.selected_series = None
                        self.selected_index = 0
                    elif action_type == "back_home":
                        self.manager.go_to("home")
                    elif action_type == "back_series":
                        self.selected_series = None
                        self.selected_index = 0
                    elif action_type == "select_item":
                        self.execute_selection(item_data)
                    return

        # 2. Gestió de teclat
        elif event.type == pygame.KEYDOWN:
            items = self.get_current_items()
            if event.key in (pygame.K_UP, pygame.K_w):
                if items:
                    self.selected_index = (self.selected_index - 1) % len(items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if items:
                    self.selected_index = (self.selected_index + 1) % len(items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if items and 0 <= self.selected_index < len(items):
                    self.execute_selection(items[self.selected_index])
            elif event.key == pygame.K_ESCAPE:
                if self.selected_series:
                    self.selected_series = None
                else:
                    self.manager.go_to("home")

    def execute_selection(self, item_name):
        """Executa l'acció segons l'element seleccionat."""
        if self.tab == "movies":
            video_path = os.path.join(MOVIES_DIR, item_name)
            self.play_video(video_path)

        elif self.tab == "series":
            if self.selected_series is None:
                # Entrar a la sèrie
                self.selected_series = item_name
                self.selected_index = 0
            else:
                # Reproduir l'episodi
                video_path = os.path.join(SERIES_DIR, self.selected_series, item_name)
                self.play_video(video_path)

    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        self.interactive_rects = []

        # --- Capçalera i Pestanyes ---
        draw_text(surface, "PEL·LÍCULES I SÈRIES", (30, 20),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        # Botó Tornar
        btn_back = pygame.Rect(surface.get_width() - 120, 20, 90, 35)
        draw_rounded_rect(surface, btn_back, config.COLOR_PRIMARY_DARK, radius=8)
        draw_text(surface, "Tornar", btn_back.center, size=config.FONT_SIZE_SMALL, align="center")

        if self.selected_series:
            self.interactive_rects.append(("back_series", None, btn_back))
        else:
            self.interactive_rects.append(("back_home", None, btn_back))

        # Pestanyes
        btn_movies = pygame.Rect(30, 70, 140, 40)
        btn_series = pygame.Rect(180, 70, 140, 40)

        col_mov = config.COLOR_PRIMARY if self.tab == "movies" else config.COLOR_BG_SECONDARY
        col_ser = config.COLOR_PRIMARY if self.tab == "series" else config.COLOR_BG_SECONDARY

        draw_rounded_rect(surface, btn_movies, col_mov, radius=8)
        draw_text(surface, "Pel·lícules", btn_movies.center, align="center")
        self.interactive_rects.append(("tab_movies", None, btn_movies))

        draw_rounded_rect(surface, btn_series, col_ser, radius=8)
        draw_text(surface, "Sèries", btn_series.center, align="center")
        self.interactive_rects.append(("tab_series", None, btn_series))

        # Llista d'elements
        start_y = 130
        items = self.get_current_items()

        if not items:
            draw_text(surface, "No s'han trobat fitxers multimèdia.", (30, start_y + 30),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)
        else:
            item_h = 45
            max_visible = 6

            for i, item in enumerate(items[:max_visible]):
                y_pos = start_y + (i * (item_h + 8))
                rect = pygame.Rect(30, y_pos, surface.get_width() - 60, item_h)

                is_selected = (i == self.selected_index)
                bg_col = config.COLOR_PRIMARY_DARK if is_selected else config.COLOR_BG_SECONDARY

                draw_rounded_rect(surface, rect, bg_col, radius=10)

                # Etiqueta text
                draw_text(surface, item, (rect.x + 20, rect.centery),
                          size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT, align="midleft")

                self.interactive_rects.append(("select_item", item, rect))

        # Peu informatiu
        draw_text(surface, "Toca un fitxer per reproduir-lo",
                  (surface.get_width() // 2, surface.get_height() - 25),
                  size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED, align="center")
