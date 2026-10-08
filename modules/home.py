"""
home.py
-------
Pantalla d'inici: mostra el menú principal en forma de carrusel
horitzontal amb totes les seccions del media center.
"""

import datetime
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text, draw_horizontal_menu, MenuItem


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
            MenuItem("Alarmes", data="alarms"),
        ]
        self.selected = 0
        self.item_rects = []  # Guarda els rectangles dibuixats per detectar el toc

    def on_enter(self):
        self.selected = 0

    def handle_event(self, event):
        # 1. Suport per a pantalla táctil i ratolí (MOUSEBUTTONDOWN)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(event.pos):
                    self.selected = i
                    target = self.items[self.selected].data
                    self.manager.go_to(target)
                    return

        # 2. Suport per a teclat (KEYDOWN)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(self.items)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(self.items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                target = self.items[self.selected].data
                self.manager.go_to(target)
            elif event.key == pygame.K_ESCAPE:
                self.manager.quit()

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        # Capçalera amb rellotge i data
        now = datetime.datetime.now()
        draw_text(surface, now.strftime("%H:%M"), (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)
        draw_text(surface, now.strftime("%A, %d %B %Y"), (40, 90),
                  size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)

        draw_text(surface, "MEDIA CENTER", (surface.get_width() - 40, 40),
                  size=config.FONT_SIZE_MENU, color=config.COLOR_TEXT,
                  align="topright")

        # Dibuixem el menú i guardem les posicions dels botons
        self.item_rects = draw_horizontal_menu(
            surface, self.items, self.selected,
            center_y=surface.get_height() // 2, item_width=90, item_height=70, gap=10,
        )

        # Peu amb ajuda de controls
        draw_text(
            surface,
            "\u2190 \u2192 Navegar    Enter / Toc: Seleccionar    Esc: Sortir",
            (surface.get_width() // 2, surface.get_height() - 40),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
