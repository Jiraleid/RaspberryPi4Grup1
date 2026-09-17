"""
books.py
--------
Mòdul de llibres (.pdf, .epub) i còmics (.cbz, .cbr).
De moment obre el fitxer amb el lector extern del sistema; es pot
ampliar per fer un visor de PDF/EPUB integrat amb PyMuPDF (fitz).
"""

import os
import subprocess
import sys
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

BOOK_EXTENSIONS = (".pdf", ".epub", ".cbz", ".cbr")


class BooksModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.files = []
        self.selected = 0
        self.error_message = None

    def on_enter(self):
        self.scan_folders()
        self.selected = 0

    def scan_folders(self):
        self.files = []
        self.error_message = None

        folders = [config.BOOKS_DIR, config.COMICS_DIR]
        found_any_folder = False

        for folder in folders:
            if os.path.isdir(folder):
                found_any_folder = True
                for entry in sorted(os.listdir(folder)):
                    if entry.lower().endswith(BOOK_EXTENSIONS):
                        self.files.append(os.path.join(folder, entry))

        if not found_any_folder:
            self.error_message = (
                f"Crea les carpetes:\n{config.BOOKS_DIR}\n{config.COMICS_DIR}"
            )
        elif not self.files:
            self.error_message = "No s'ha trobat cap llibre ni còmic."

    def open_selected(self):
        if not self.files:
            return
        path = self.files[self.selected]
        try:
            if sys.platform.startswith("linux"):
                subprocess.run(["xdg-open", path])
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            elif sys.platform.startswith("win"):
                os.startfile(path)  # noqa: only on Windows
        except Exception as exc:
            self.error_message = f"Error en obrir: {exc}"

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
            self.open_selected()
        elif event.key == pygame.K_F5:
            self.scan_folders()

    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        draw_text(surface, "Llibres i còmics", (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        if self.error_message:
            draw_text(surface, self.error_message, (40, 120),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
        else:
            y = 130
            for i, path in enumerate(self.files):
                is_selected = (i == self.selected)
                color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
                prefix = "\u25b6  " if is_selected else "    "
                draw_text(surface, prefix + os.path.basename(path), (60, y),
                          size=config.FONT_SIZE_TEXT, color=color)
                y += 36

        draw_text(
            surface,
            "\u2191 \u2193 Navegar   Enter: Obrir   F5: Refrescar   Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 40),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
