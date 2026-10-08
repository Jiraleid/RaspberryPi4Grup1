"""
games.py
--------
Mòdul de consola retro. Escanea la carpeta de ROMs, mostra la llista de jocs,
el nom, la caràtula i un botó de jugar. Executa la ROM amb RetroArch i el nucli
de DeSmuME (.nds) u altres consoles, tornant automàticament al Media Center.
"""

import os
import subprocess
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

# Mapeig d'extensions amb el seu nucli de RetroArch corresponent
ROM_CORES = {
    ".nds": "desmume_libretro.so",
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
        self.games = []
        self.selected = 0
        self.error_message = None
        self.cover_cache = {}

        # Rectangles de col·lisió tàctil
        self.item_rects = []
        self.btn_back_home_rect = None
        self.btn_play_rect = None

    def on_enter(self):
        self.scan_folder()
        self.selected = 0

    def scan_folder(self):
        self.games = []
        self.cover_cache = {}
        self.error_message = None

        roms_dir = getattr(config, "ROMS_DIR", os.path.expanduser("~/media_center/roms"))

        if not os.path.isdir(roms_dir):
            self.error_message = f"No s'ha trobat la carpeta:\n{roms_dir}"
            return

        for entry in sorted(os.listdir(roms_dir)):
            ext = os.path.splitext(entry)[1].lower()
            if ext in ROM_CORES:
                full_path = os.path.join(roms_dir, entry)
                base_name = os.path.splitext(entry)[0]

                # Cerca de caràtula amb el mateix nom
                cover_path = None
                for img_ext in (".png", ".jpg", ".jpeg"):
                    potential_cover = os.path.join(roms_dir, base_name + img_ext)
                    if os.path.isfile(potential_cover):
                        cover_path = potential_cover
                        break

                self.games.append({
                    "name": base_name,
                    "filename": entry,
                    "rom_path": full_path,
                    "cover_path": cover_path,
                    "ext": ext
                })

        if not self.games:
            self.error_message = "No s'ha trobat cap ROM compatible."

    def load_cover(self, path, max_w=220, max_h=280):
        if not path or not os.path.isfile(path):
            return None
        if path in self.cover_cache:
            return self.cover_cache[path]

        try:
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            scale = min(max_w / w, max_h / h)
            new_size = (int(w * scale), int(h * scale))
            img = pygame.transform.smoothscale(img, new_size)
            self.cover_cache[path] = img
            return img
        except Exception:
            return None

    def launch_selected(self):
        if not self.games:
            return

        game = self.games[self.selected]
        rom_path = game["rom_path"]
        core_filename = ROM_CORES.get(game["ext"])

        # Cerca dinàmica del nucli
        possible_base_paths = [
            "/usr/lib/aarch64-linux-gnu/libretro/",
            "/usr/lib/arm-linux-gnueabihf/libretro/",
            "/usr/lib/libretro/",
            "/usr/local/lib/libretro/"
        ]

        core_path = None
        if core_filename:
            for base in possible_base_paths:
                full_core = os.path.join(base, core_filename)
                if os.path.isfile(full_core):
                    core_path = full_core
                    break

        # Tancar la pantalla de Pygame per alliberar el controlador gràfic KMS/DRM
        pygame.display.quit()

        try:
            cmd = ["retroarch"]
            if core_path:
                cmd.extend(["-L", core_path])
            cmd.append(rom_path)

            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            self.error_message = "RetroArch no està instal·lat o no és al PATH."
        except Exception as exc:
            self.error_message = f"Error en llançar el joc: {exc}"
        finally:
            # Recrear la pantalla de Pygame en tancar el joc
            pygame.display.init()
            if hasattr(config, "SCREEN_WIDTH") and hasattr(config, "SCREEN_HEIGHT"):
                flags = pygame.FULLSCREEN if getattr(config, "FULLSCREEN", True) else 0
                self.manager.screen = pygame.display.set_mode(
                    (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags
                )

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.go_to("home")
            elif event.key in (pygame.K_UP, pygame.K_w) and self.games:
                self.selected = (self.selected - 1) % len(self.games)
            elif event.key in (pygame.K_DOWN, pygame.K_s) and self.games:
                self.selected = (self.selected + 1) % len(self.games)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.launch_selected()
            elif event.key == pygame.K_F5:
                self.scan_folder()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Botó "Tornar"
            if self.btn_back_home_rect and self.btn_back_home_rect.collidepoint(pos):
                self.manager.go_to("home")
                return

            # Botó "Jugar"
            if self.btn_play_rect and self.btn_play_rect.collidepoint(pos):
                self.launch_selected()
                return

            # Llista d'elements
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(pos):
                    if self.selected == i:
                        self.launch_selected()
                    else:
                        self.selected = i
                    break

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        # Títol
        draw_text(surface, "Jocs retro", (40, 25),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        # Botó "Tornar"
        self.btn_back_home_rect = pygame.Rect(surface.get_width() - 150, 20, 110, 40)
        pygame.draw.rect(surface, (180, 50, 50), self.btn_back_home_rect, border_radius=8)
        draw_text(surface, "Tornar", self.btn_back_home_rect.center,
                  size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

        self.item_rects = []

        if self.error_message:
            draw_text(surface, self.error_message, (40, 120),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
            return

        # Columna esquerra: Llista de ROMs
        list_w = surface.get_width() // 2 - 20
        y = 100
        for i, game in enumerate(self.games):
            is_selected = (i == self.selected)
            color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
            prefix = "▶  " if is_selected else "    "

            draw_text(surface, prefix + game["name"], (50, y),
                      size=config.FONT_SIZE_TEXT, color=color)

            rect = pygame.Rect(40, y - 5, list_w, 35)
            self.item_rects.append(rect)
            y += 40

        # Columna dreta: Caràtula i Botó de Jugar
        if self.games:
            current_game = self.games[self.selected]
            right_x = surface.get_width() // 2 + 40

            subtitle_size = getattr(config, "FONT_SIZE_SUBTITLE", config.FONT_SIZE_TITLE - 4)
            draw_text(surface, current_game["name"], (right_x, 100),
                      size=subtitle_size, color=config.COLOR_PRIMARY)

            # Caràtula
            cover_img = self.load_cover(current_game["cover_path"])
            if cover_img:
                surface.blit(cover_img, (right_x, 140))
            else:
                no_cover_rect = pygame.Rect(right_x, 140, 200, 200)
                pygame.draw.rect(surface, (40, 40, 40), no_cover_rect, border_radius=8)
                draw_text(surface, "Sense Caràtula", no_cover_rect.center,
                          size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED, align="center")

            # Botó Jugar
            self.btn_play_rect = pygame.Rect(right_x, 380, 160, 45)
            pygame.draw.rect(surface, config.COLOR_PRIMARY, self.btn_play_rect, border_radius=8)
            draw_text(surface, "JUGAR", self.btn_play_rect.center,
                      size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

        # Barra inferior
        draw_text(
            surface,
            "Navegar: Toc / ↑↓    Obrir: Enter / Toc 'JUGAR'    Tornar: Esc / Toc 'Tornar'",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
