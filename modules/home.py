"""
home.py
-------
Pantalla d'inici: mostra el menú principal en graella (3x2)
amb totes les seccions del media center.
"""

import os
import datetime
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text, draw_grid_menu, MenuItem


class HomeModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)

        # Cada entrada del menú apunta al nom del mòdul destí
        self.items = [
            MenuItem("Pel·lícules i sèries", data="movies"),
            MenuItem("Llibres i còmics", data="books"),
            MenuItem("Jocs retro", data="games"),
            MenuItem("Fotos", data="photos"),
            MenuItem("Meteorologia", data="weather"),
            MenuItem("Xarxa", data="network"),
        ]
        self.selected = 0
        self.item_rects = []  # Guarda els rectangles dibuixats per detectar el toc

        # Carregar el logo de SofaTV si existeix
        self.logo_img = None
        if hasattr(config, "LOGO_PATH") and os.path.exists(config.LOGO_PATH):
            try:
                img = pygame.image.load(config.LOGO_PATH).convert_alpha()
                w, h = img.get_size()
                new_w = 180
                new_h = int(h * (new_w / w))
                self.logo_img = pygame.transform.smoothscale(img, (new_w, new_h))
            except Exception as e:
                print(f"Error carregant el logo: {e}")

    def on_enter(self):
        self.selected = 0

    def handle_event(self, event):
        # 1. Suport per a pantalla tàctil i ratolí
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    target = self.items[self.selected].data
                    self.manager.go_to(target)
                    return

        # 2. Suport per a teclat amb navegació 3x2 (files i columnes)
        elif event.type == pygame.KEYDOWN:
            cols = 3
            if event.key in (pygame.K_LEFT, pygame.K_a):
                if self.selected % cols > 0:
                    self.selected -= 1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.selected % cols < cols - 1 and self.selected + 1 < len(self.items):
                    self.selected += 1
            elif event.key in (pygame.K_UP, pygame.K_w):
                if self.selected >= cols:
                    self.selected -= cols
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.selected + cols < len(self.items):
                    self.selected += cols
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                target = self.items[self.selected].data
                self.manager.go_to(target)
            elif event.key == pygame.K_ESCAPE:
                self.manager.quit()

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        # Capçalera amb rellotge i data
        now = datetime.datetime.now()
        draw_text(surface, now.strftime("%H:%M"), (40, 20),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)
        draw_text(surface, now.strftime("%A, %d %B %Y"), (40, 75),
                  size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)

        # Dibuixar el logo a la part superior dreta
        if self.logo_img:
            logo_x = surface.get_width() - self.logo_img.get_width() - 40
            surface.blit(self.logo_img, (logo_x, 20))
        else:
            draw_text(surface, "SofaTV", (surface.get_width() - 40, 30),
                      size=config.FONT_SIZE_MENU, color=config.COLOR_PRIMARY,
                      align="topright")

        # Dibuixem el menú en graella de 3 columnes (3 a dalt, 3 a baix)
        # Amb mides de targetes més grans (210x120px)
        self.item_rects = draw_grid_menu(
            surface, self.items, self.selected,
            start_y=130, cols=3, item_width=210, item_height=120, gap_x=20, gap_y=20
        )

        # Peu amb ajuda de controls
        draw_text(
            surface,
            "\u2190 \u2191 \u2192 \u2193 Navegar    Enter / Toc: Seleccionar    Esc: Sortir",
            (surface.get_width() // 2, surface.get_height() - 25),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
