"""
ui_utils.py
-----------
Funcions i classes auxiliars per dibuixar la interfície:
carrega de fonts, text amb ombra, botons seleccionables i
una petita utilitat de "fade" per a transicions entre pantalles.
"""

import os
import pygame
import config


_font_cache = {}


def get_font(size, bold=False):
    """
    Retorna (i cacheja) un objecte pygame.font.Font del tamany indicat.
    Si a config.py s'ha indicat un fitxer de font personalitzat i existeix,
    es fa servir; si no, es fa servir la font per defecte del sistema.
    """
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]

    font = None
    if config.FONT_NAME:
        path = os.path.join(config.FONTS_DIR, config.FONT_NAME)
        if os.path.isfile(path):
            font = pygame.font.Font(path, size)

    if font is None:
        font = pygame.font.SysFont(None, size, bold=bold)

    _font_cache[key] = font
    return font


def draw_text(surface, text, pos, size=config.FONT_SIZE_TEXT,
              color=config.COLOR_TEXT, align="topleft", shadow=True):
    """
    Dibuixa text a la pantalla amb una petita ombra per llegibilitat.
    `pos` és una tupla (x, y) i `align` indica quin punt del rectangle
    de text es fa coincidir amb `pos` (topleft, center, midtop, etc.).
    """
    font = get_font(size)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(**{align: pos})

    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(**{align: (pos[0] + 2, pos[1] + 2)})
        surface.blit(shadow_surf, shadow_rect)

    surface.blit(text_surf, rect)
    return rect


def draw_rounded_rect(surface, rect, color, radius=12, width=0):
    """Dibuixa un rectangle amb cantonades arrodonides."""
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


class MenuItem:
    """Representa una entrada d'un menú (icona/text + acció associada)."""

    def __init__(self, label, action=None, icon=None, data=None):
        self.label = label
        self.action = action      # funció a executar quan se selecciona
        self.icon = icon          # pygame.Surface opcional
        self.data = data          # dades extra (p.ex. ruta d'un fitxer)


def draw_horizontal_menu(surface, items, selected_index, center_y,
                       item_width=220, item_height=140, gap=30):
    """
    Dibuixa un menú horitzontal tipus "carrusel" (com el de Kodi/Netflix),
    amb l'element seleccionat ressaltat i una mica més gran.
    Retorna la llista de rectangles dibuixats (útil per detectar clics).
    """
    screen_w = surface.get_width()
    total_width = len(items) * (item_width + gap) - gap
    start_x = screen_w // 2 - total_width // 2

    rects = []
    for i, item in enumerate(items):
        x = start_x + i * (item_width + gap)
        is_selected = (i == selected_index)
        scale = 1.15 if is_selected else 1.0
        w = int(item_width * scale)
        h = int(item_height * scale)
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (x + item_width // 2, center_y)

        bg_color = config.COLOR_PRIMARY_DARK if is_selected else config.COLOR_BG_SECONDARY
        draw_rounded_rect(surface, rect, bg_color, radius=16)

        if is_selected:
            pygame.draw.rect(surface, config.COLOR_PRIMARY, rect,
                             width=3, border_radius=16)

        if item.icon:
            icon_rect = item.icon.get_rect(center=(rect.centerx, rect.centery - 15))
            surface.blit(item.icon, icon_rect)

        draw_text(
            surface, item.label,
            (rect.centerx, rect.bottom - 22),
            size=config.FONT_SIZE_SMALL if not is_selected else config.FONT_SIZE_TEXT,
            color=config.COLOR_TEXT,
            align="center",
        )
        rects.append(rect)

    return rects


def draw_grid_menu(surface, items, selected_index, start_y=140, cols=3,
                   item_width=210, item_height=120, gap_x=20, gap_y=20):
    """
    Dibuixa un menú en forma de graella (3 columnes x 2 files) amb targetes grans.
    Retorna la llista de Pygame Rects per detectar el toc o clic.
    """
    rects = []
    total_grid_width = (cols * item_width) + ((cols - 1) * gap_x)
    start_x = (surface.get_width() - total_grid_width) // 2

    for index, item in enumerate(items):
        row = index // cols
        col = index % cols

        x = start_x + col * (item_width + gap_x)
        y = start_y + row * (item_height + gap_y)

        rect = pygame.Rect(x, y, item_width, item_height)
        rects.append(rect)

        is_selected = (index == selected_index)

        bg_color = config.COLOR_PRIMARY if is_selected else config.COLOR_BG_SECONDARY
        text_color = (255, 255, 255) if is_selected else config.COLOR_TEXT

        draw_rounded_rect(surface, rect, bg_color, radius=14)

        if is_selected:
            pygame.draw.rect(surface, (255, 255, 255), rect, width=3, border_radius=14)

        if hasattr(item, 'icon') and item.icon:
            icon_rect = item.icon.get_rect(center=(rect.centerx, rect.centery - 15))
            surface.blit(item.icon, icon_rect)
            text_y = rect.bottom - 25
        else:
            text_y = rect.centery

        draw_text(
            surface, getattr(item, 'label', getattr(item, 'text', '')),
            (rect.centerx, text_y),
            size=config.FONT_SIZE_TEXT,
            color=text_color,
            align="center"
        )

    return rects


class FadeTransition:
    """Petita utilitat per fer un fade-in/fade-out en canviar de pantalla."""

    def __init__(self, duration_ms=250):
        self.duration = duration_ms
        self.alpha = 255
        self.fading_in = True
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        step = (255 / self.duration) * dt
        if self.fading_in:
            self.alpha -= step
            if self.alpha <= 0:
                self.alpha = 0
                self.active = False
        return self.alpha

    def draw(self, surface):
        if self.alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(int(self.alpha))
        surface.blit(overlay, (0, 0))
