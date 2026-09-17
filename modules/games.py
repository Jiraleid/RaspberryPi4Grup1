"""
games.py
--------
Mòdul de jocs retro. No emula res directament (això ho fan programes
com RetroArch); simplement escaneja una carpeta de ROMs i llança
l'emulador corresponent com a subprocés. Cal tenir instal·lat
RetroArch (o un altre emulador) a la Raspberry Pi.
"""

import os
import subprocess
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

# Relaciona extensions de ROM amb el "core" de RetroArch corresponent.
# Cal ajustar els noms de core segons el que hi hagi instal·lat.
ROM_CORES = {
    ".nes": "fceumm_libretro.so",
    ".sfc": "snes9x_libretro.so",
    ".smc": "snes9x_libretro.so",
    ".gba": "mgba_libretro.so",
    ".gb": "gambatte_libretro.so",
    ".gbc": "gambatte_libretro.so",
}


class GamesModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.files = []
        self.selected = 0
        self.error_message = None

    def on_enter(self):
        self.scan_folder()
        self.selected = 0

    def scan_folder(self):
        self.files = []
        self.error_message = None

        if not os.path.isdir(config.ROMS_DIR):
            self.error_message = f"No s'ha trobat la carpeta:\n{config.ROMS_DIR}"
            return

        for entry in sorted(os.listdir(config.ROMS_DIR)):
            ext = os.path.splitext(entry)[1].lower()
            if ext in ROM_CORES:
                self.files.append(entry)

        if not self.files:
            self.error_message = "No s'ha trobat cap ROM compatible."

    def launch_selected(self):
        if not self.files:
            return

        filename = self.files[self.selected]
        rom_path = os.path.join(config.ROMS_DIR, filename)
        ext = os.path.splitext(filename)[1].lower()
        core = ROM_CORES.get(ext)

        try:
            # Exemple d'ús de RetroArch en mode línia de comandes.
            # La ruta dels cores varia segons la instal·lació
            # (sol ser /usr/lib/aarch64-linux-gnu/libretro/ a Raspberry Pi OS).
            subprocess.run(["retroarch", "-L", core, rom_path])
        except FileNotFoundError:
            self.error_message = "RetroArch no està instal·lat o no és a la PATH."
        except Exception as exc:
            self.error_message = f"Error en llançar el joc: {exc}"

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
            self.launch_selected()
        elif event.key == pygame.K_F5:
            self.scan_folder()

    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        draw_text(surface, "Jocs retro", (40, 30),
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
            "\u2191 \u2193 Navegar   Enter: Jugar   F5: Refrescar   Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 40),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
