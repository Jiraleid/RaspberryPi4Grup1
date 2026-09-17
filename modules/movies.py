"""
movies.py
---------
Mòdul de pel·lícules i sèries. Escaneja una carpeta local buscant
fitxers de vídeo i permet reproduir-los amb un reproductor extern
(mpv/omxplayer a la Raspberry Pi, o el reproductor per defecte al PC).

Nota: reproduir vídeo directament amb Pygame no és pràctic (no té
descodificació de vídeo integrada), així que la pràctica habitual en
projectes de media center és llançar un reproductor extern com a
subprocés i, mentre s'executa, deixar Pygame en pausa.
"""

import os
import subprocess
import sys
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".webm")


class MoviesModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.files = []
        self.selected = 0
        self.error_message = None

    def on_enter(self):
        self.scan_folder()
        self.selected = 0

    def scan_folder(self):
        """Cerca fitxers de vídeo dins de config.MOVIES_DIR."""
        self.files = []
        self.error_message = None

        if not os.path.isdir(config.MOVIES_DIR):
            self.error_message = f"No s'ha trobat la carpeta:\n{config.MOVIES_DIR}"
            return

        for entry in sorted(os.listdir(config.MOVIES_DIR)):
            if entry.lower().endswith(VIDEO_EXTENSIONS):
                self.files.append(entry)

        if not self.files:
            self.error_message = "No s'ha trobat cap vídeo en aquesta carpeta."

    def play_selected(self):
        """Llança el reproductor extern per al fitxer seleccionat."""
        if not self.files:
            return
        path = os.path.join(config.MOVIES_DIR, self.files[self.selected])

        # A la Raspberry Pi es recomana `omxplayer` o `mpv --fullscreen`.
        # A l'ordinador de desenvolupament fem servir el reproductor
        # per defecte del sistema operatiu.
        try:
            if sys.platform.startswith("linux"):
                # Prova primer mpv (més modern i disponible a la majoria
                # de distribucions); si no existeix, prova omxplayer.
                if _command_exists("mpv"):
                    subprocess.run(["mpv", "--fullscreen", path])
                elif _command_exists("omxplayer"):
                    subprocess.run(["omxplayer", path])
                else:
                    self.error_message = "Instal·la 'mpv' o 'omxplayer' per reproduir vídeo."
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            elif sys.platform.startswith("win"):
                os.startfile(path)  # noqa: only on Windows
        except Exception as exc:
            self.error_message = f"Error en reproduir: {exc}"

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.go_to("home")
        elif event.key in (pygame.K_UP, pygame.K_w) and self.files:
            self.selected = (self.selected - 1) % len(self.files)
        elif event.key in (pygame.K_DOWN, pygame.K_s) and self.files:
            self.selected = (self.selected + 1) % len(self.files)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.play_selected()
        elif event.key == pygame.K_F5:
            self.scan_folder()

    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        draw_text(surface, "Pel·lícules i sèries", (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        if self.error_message:
            draw_text(surface, self.error_message, (40, 120),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
        else:
            y = 130
            for i, filename in enumerate(self.files):
                is_selected = (i == self.selected)
                color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
                prefix = "\u25b6  " if is_selected else "    "
                draw_text(surface, prefix + filename, (60, y),
                          size=config.FONT_SIZE_TEXT, color=color)
                y += 36

        draw_text(
            surface,
            "\u2191 \u2193 Navegar   Enter: Reproduir   F5: Refrescar   Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 40),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )


def _command_exists(cmd):
    from shutil import which
    return which(cmd) is not None
