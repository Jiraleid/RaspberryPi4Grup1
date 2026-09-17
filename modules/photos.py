"""
photos.py
---------
Mòdul de galeria de fotografies. A diferència de vídeos o llibres,
Pygame sí que pot carregar i mostrar imatges directament, així que
aquí sí que implementem un visor complet integrat (amb miniatures
i pantalla completa) en lloc de llançar un programa extern.
"""

import os
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

THUMB_SIZE = (180, 135)
GRID_COLS = 5


class PhotosModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.files = []
        self.thumbnails = []   # cache de superfícies redimensionades
        self.selected = 0
        self.error_message = None
        self.fullscreen_view = False
        self.current_full_image = None

    def on_enter(self):
        self.scan_folder()
        self.selected = 0
        self.fullscreen_view = False

    def scan_folder(self):
        self.files = []
        self.thumbnails = []
        self.error_message = None

        if not os.path.isdir(config.PHOTOS_DIR):
            self.error_message = f"No s'ha trobat la carpeta:\n{config.PHOTOS_DIR}"
            return

        for entry in sorted(os.listdir(config.PHOTOS_DIR)):
            if entry.lower().endswith(IMAGE_EXTENSIONS):
                self.files.append(os.path.join(config.PHOTOS_DIR, entry))

        if not self.files:
            self.error_message = "No s'ha trobat cap imatge en aquesta carpeta."
            return

        # Genera les miniatures un cop, es reutilitzen a cada frame.
        for path in self.files:
            try:
                img = pygame.image.load(path).convert()
                thumb = pygame.transform.smoothscale(img, THUMB_SIZE)
            except Exception:
                thumb = None
            self.thumbnails.append(thumb)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.fullscreen_view:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.fullscreen_view = False
                self.current_full_image = None
            elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.files:
                self.selected = (self.selected + 1) % len(self.files)
                self._load_full_image()
            elif event.key in (pygame.K_LEFT, pygame.K_a) and self.files:
                self.selected = (self.selected - 1) % len(self.files)
                self._load_full_image()
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.go_to("home")
        elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.files:
            self.selected = (self.selected + 1) % len(self.files)
        elif event.key in (pygame.K_LEFT, pygame.K_a) and self.files:
            self.selected = (self.selected - 1) % len(self.files)
        elif event.key in (pygame.K_DOWN, pygame.K_s) and self.files:
            self.selected = (self.selected + GRID_COLS) % len(self.files)
        elif event.key in (pygame.K_UP, pygame.K_w) and self.files:
            self.selected = (self.selected - GRID_COLS) % len(self.files)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.files:
            self.fullscreen_view = True
            self._load_full_image()
        elif event.key == pygame.K_F5:
            self.scan_folder()

    def _load_full_image(self):
        path = self.files[self.selected]
        try:
            self.current_full_image = pygame.image.load(path).convert()
        except Exception:
            self.current_full_image = None
            self.error_message = f"No s'ha pogut carregar: {os.path.basename(path)}"

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        if self.fullscreen_view and self.current_full_image:
            self._draw_fullscreen(surface)
            return

        draw_text(surface, "Fotografies", (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        if self.error_message and not self.files:
            draw_text(surface, self.error_message, (40, 120),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
            return

        margin_x, start_y = 40, 110
        gap = 20
        for i, thumb in enumerate(self.thumbnails):
            col = i % GRID_COLS
            row = i // GRID_COLS
            x = margin_x + col * (THUMB_SIZE[0] + gap)
            y = start_y + row * (THUMB_SIZE[1] + gap)

            rect = pygame.Rect(x, y, *THUMB_SIZE)
            if thumb:
                surface.blit(thumb, rect)
            else:
                pygame.draw.rect(surface, config.COLOR_BG_SECONDARY, rect)

            if i == self.selected:
                pygame.draw.rect(surface, config.COLOR_PRIMARY, rect, width=4)

        draw_text(
            surface,
            "Fletxes: Navegar   Enter: Ampliar   F5: Refrescar   Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )

    def _draw_fullscreen(self, surface):
        surface.fill((0, 0, 0))
        img = self.current_full_image
        sw, sh = surface.get_size()
        iw, ih = img.get_size()
        scale = min(sw / iw, sh / ih)
        new_size = (int(iw * scale), int(ih * scale))
        scaled = pygame.transform.smoothscale(img, new_size)
        rect = scaled.get_rect(center=(sw // 2, sh // 2))
        surface.blit(scaled, rect)

        filename = os.path.basename(self.files[self.selected])
        draw_text(surface, filename, (sw // 2, sh - 30),
                  size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
                  align="center")
