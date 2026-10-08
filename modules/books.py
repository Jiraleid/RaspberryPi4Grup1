"""
books.py
--------
Mòdul de llibres (.pdf, .epub) i còmics (.cbz, .cbr).
Organitzat en dues seccions: Llibres i Còmics.
Inclou lector integrat amb suport tàctil complet, zoom, arrossegament (pan)
compatible amb pantalla tàctil, botó de "Sortir" i "Tornar".
"""

import os
import pygame
import fitz  # PyMuPDF
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
        self.current_section = "books"

        # Hitboxes tàctils
        self.item_rects = []
        self.tab_books_rect = None
        self.tab_comics_rect = None
        self.btn_exit_reader_rect = None
        self.btn_back_home_rect = None

        # Botons tàctils de Zoom
        self.btn_zoom_in_rect = None
        self.btn_zoom_out_rect = None
        self.btn_zoom_reset_rect = None

        # Estat del lector integrat
        self.is_reading = False
        self.current_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.page_surface = None
        self.zoom_level = 1.0

        # Posició i desplaçament (Pan / Drag)
        self.offset_x = 0
        self.offset_y = 0
        self.is_dragging = False
        self.drag_start_pos = (0, 0)
        self.drag_start_offset = (0, 0)

    def on_enter(self):
        self.scan_folders()
        self.selected = 0
        self.close_reader()

    def scan_folders(self):
        self.files = []
        self.error_message = None
        target_dir = config.BOOKS_DIR if self.current_section == "books" else config.COMICS_DIR

        if os.path.isdir(target_dir):
            for entry in sorted(os.listdir(target_dir)):
                if entry.lower().endswith(BOOK_EXTENSIONS):
                    self.files.append(os.path.join(target_dir, entry))
            if not self.files:
                cat_name = "llibre" if self.current_section == "books" else "còmic"
                self.error_message = f"No s'ha trobat cap {cat_name} a la carpeta."
        else:
            self.error_message = f"No existeix la carpeta:\n{target_dir}"

    def open_selected(self):
        if not self.files:
            return
        path = self.files[self.selected]
        try:
            self.current_doc = fitz.open(path)
            self.total_pages = len(self.current_doc)
            self.current_page = 0
            self.reset_view()
            self.is_reading = True
            self.render_current_page()
        except Exception as exc:
            self.error_message = f"Error en obrir: {exc}"

    def close_reader(self):
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None
        self.is_reading = False
        self.page_surface = None
        self.reset_view()

    def reset_view(self):
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def change_zoom(self, amount):
        self.zoom_level = max(0.5, min(3.0, self.zoom_level + amount))
        if self.zoom_level == 1.0:
            self.offset_x = 0
            self.offset_y = 0
        self.render_current_page()

    def render_current_page(self):
        if not self.current_doc or self.total_pages == 0:
            return

        page = self.current_doc[self.current_page]

        screen_w = config.SCREEN_WIDTH
        screen_h = config.SCREEN_HEIGHT - 70

        rect = page.rect
        zoom_x = screen_w / rect.width
        zoom_y = screen_h / rect.height
        base_zoom = min(zoom_x, zoom_y)

        final_zoom = base_zoom * self.zoom_level

        mat = fitz.Matrix(final_zoom, final_zoom)
        pix = page.get_pixmap(matrix=mat)

        mode = "RGBA" if pix.alpha else "RGB"
        img = pygame.image.fromstring(pix.samples, (pix.width, pix.height), mode)
        self.page_surface = img

    def _get_event_pos(self, event):
        """Obté coordenades de posició en píxels tant per ratolí com per pantalla tàctil."""
        if hasattr(event, "pos"):
            return event.pos
        elif hasattr(event, "x") and hasattr(event, "y"):
            return (int(event.x * config.SCREEN_WIDTH), int(event.y * config.SCREEN_HEIGHT))
        return None

    def handle_event(self, event):
        # --- MODO LECTOR ---
        if self.is_reading:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.close_reader()
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_PAGEDOWN, pygame.K_SPACE):
                    if self.current_page < self.total_pages - 1:
                        self.current_page += 1
                        self.reset_view()
                        self.render_current_page()
                elif event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_PAGEUP):
                    if self.current_page > 0:
                        self.current_page -= 1
                        self.reset_view()
                        self.render_current_page()
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                    self.change_zoom(0.2)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.change_zoom(-0.2)

            # INICI DE TOC O CLIC
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button != 1:
                    return

                pos = self._get_event_pos(event)
                if not pos:
                    return

                # Comprovar botons inferiors
                if self.btn_exit_reader_rect and self.btn_exit_reader_rect.collidepoint(pos):
                    self.close_reader()
                    return

                if self.btn_zoom_out_rect and self.btn_zoom_out_rect.collidepoint(pos):
                    self.change_zoom(-0.2)
                    return
                elif self.btn_zoom_reset_rect and self.btn_zoom_reset_rect.collidepoint(pos):
                    self.reset_view()
                    self.render_current_page()
                    return
                elif self.btn_zoom_in_rect and self.btn_zoom_in_rect.collidepoint(pos):
                    self.change_zoom(0.2)
                    return

                # Si es toca la zona de lectura (fóra de la barra inferior)
                if pos[1] < config.SCREEN_HEIGHT - 70:
                    self.is_dragging = True
                    self.drag_start_pos = pos
                    self.drag_start_offset = (self.offset_x, self.offset_y)

            # MOVIMENT EN ARROSSEGAR
            elif event.type in (pygame.MOUSEMOTION, pygame.FINGERMOTION) and self.is_dragging:
                pos = self._get_event_pos(event)
                if pos:
                    dx = pos[0] - self.drag_start_pos[0]
                    dy = pos[1] - self.drag_start_pos[1]
                    self.offset_x = self.drag_start_offset[0] + dx
                    self.offset_y = self.drag_start_offset[1] + dy

            # FINAL DE TOC O CLIC
            elif event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                if self.is_dragging:
                    self.is_dragging = False
                    pos = self._get_event_pos(event) or self.drag_start_pos
                    
                    # Si ha estat un toc ràpid/curt, passa de pàgina
                    dx = abs(pos[0] - self.drag_start_pos[0])
                    dy = abs(pos[1] - self.drag_start_pos[1])
                    if dx < 15 and dy < 15 and pos[1] < config.SCREEN_HEIGHT - 70:
                        if pos[0] > config.SCREEN_WIDTH // 2:
                            if self.current_page < self.total_pages - 1:
                                self.current_page += 1
                                self.reset_view()
                                self.render_current_page()
                        else:
                            if self.current_page > 0:
                                self.current_page -= 1
                                self.reset_view()
                                self.render_current_page()
            return

        # --- MODO LLISTA / NAVEGACIÓ ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.go_to("home")
            elif event.key == pygame.K_TAB:
                self.current_section = "comics" if self.current_section == "books" else "books"
                self.scan_folders()
                self.selected = 0
            elif event.key in (pygame.K_UP, pygame.K_w) and self.files:
                self.selected = (self.selected - 1) % len(self.files)
            elif event.key in (pygame.K_DOWN, pygame.K_s) and self.files:
                self.selected = (self.selected + 1) % len(self.files)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.open_selected()
            elif event.key == pygame.K_F5:
                self.scan_folders()

        elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
            pos = self._get_event_pos(event)
            if not pos:
                return

            if self.btn_back_home_rect and self.btn_back_home_rect.collidepoint(pos):
                self.manager.go_to("home")
                return

            if self.tab_books_rect and self.tab_books_rect.collidepoint(pos):
                if self.current_section != "books":
                    self.current_section = "books"
                    self.scan_folders()
                    self.selected = 0
                return

            if self.tab_comics_rect and self.tab_comics_rect.collidepoint(pos):
                if self.current_section != "comics":
                    self.current_section = "comics"
                    self.scan_folders()
                    self.selected = 0
                return

            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(pos):
                    if self.selected == i:
                        self.open_selected()
                    else:
                        self.selected = i
                    break

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        # ----------------------------------------------------
        # 1. PANTALLA DE LECTURA (Lector Obert)
        # ----------------------------------------------------
        if self.is_reading:
            if self.page_surface:
                base_x = (surface.get_width() - self.page_surface.get_width()) // 2
                base_y = (surface.get_height() - 70 - self.page_surface.get_height()) // 2
                x = base_x + self.offset_x
                y = base_y + self.offset_y
                surface.blit(self.page_surface, (x, y))

            # Botó tàctil "Sortir"
            self.btn_exit_reader_rect = pygame.Rect(20, surface.get_height() - 55, 110, 40)
            pygame.draw.rect(surface, config.COLOR_PRIMARY, self.btn_exit_reader_rect, border_radius=8)
            draw_text(surface, "Sortir", self.btn_exit_reader_rect.center,
                      size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

            # Botons de ZOOM tàctils
            self.btn_zoom_out_rect = pygame.Rect(140, surface.get_height() - 55, 80, 40)
            pygame.draw.rect(surface, (70, 70, 70), self.btn_zoom_out_rect, border_radius=8)
            draw_text(surface, "Zoom -", self.btn_zoom_out_rect.center,
                      size=config.FONT_SIZE_SMALL, color=(255, 255, 255), align="center")

            self.btn_zoom_reset_rect = pygame.Rect(228, surface.get_height() - 55, 80, 40)
            pygame.draw.rect(surface, (50, 50, 80), self.btn_zoom_reset_rect, border_radius=8)
            zoom_str = f"{int(self.zoom_level * 100)}%"
            draw_text(surface, zoom_str, self.btn_zoom_reset_rect.center,
                      size=config.FONT_SIZE_SMALL, color=(255, 255, 255), align="center")

            self.btn_zoom_in_rect = pygame.Rect(316, surface.get_height() - 55, 80, 40)
            pygame.draw.rect(surface, (70, 70, 70), self.btn_zoom_in_rect, border_radius=8)
            draw_text(surface, "Zoom +", self.btn_zoom_in_rect.center,
                      size=config.FONT_SIZE_SMALL, color=(255, 255, 255), align="center")

            # Informació de pàgina
            info_str = f"Pàgina {self.current_page + 1} / {self.total_pages}"
            draw_text(
                surface, info_str,
                (surface.get_width() - 150, surface.get_height() - 35),
                size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
                align="center",
            )
            return

        # ----------------------------------------------------
        # 2. PANTALLA PRINCIPAL (Llista i Pestanyes)
        # ----------------------------------------------------
        draw_text(surface, "Llibres i còmics", (40, 25),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        # Botó "Tornar" al menú principal
        self.btn_back_home_rect = pygame.Rect(surface.get_width() - 150, 20, 110, 40)
        pygame.draw.rect(surface, (180, 50, 50), self.btn_back_home_rect, border_radius=8)
        draw_text(surface, "Tornar", self.btn_back_home_rect.center,
                  size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

        # Pestanyes "Llibres" i "Còmics"
        color_books = config.COLOR_PRIMARY if self.current_section == "books" else (80, 80, 80)
        color_comics = config.COLOR_PRIMARY if self.current_section == "comics" else (80, 80, 80)

        self.tab_books_rect = pygame.Rect(40, 85, 120, 35)
        pygame.draw.rect(surface, color_books, self.tab_books_rect, border_radius=6)
        draw_text(surface, "Llibres", self.tab_books_rect.center,
                  size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

        self.tab_comics_rect = pygame.Rect(170, 85, 120, 35)
        pygame.draw.rect(surface, color_comics, self.tab_comics_rect, border_radius=6)
        draw_text(surface, "Còmics", self.tab_comics_rect.center,
                  size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

        self.item_rects = []

        if self.error_message:
            draw_text(surface, self.error_message, (40, 150),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
        else:
            y = 140
            for i, path in enumerate(self.files):
                is_selected = (i == self.selected)
                color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
                prefix = "\u25b6  " if is_selected else "    "

                filename = os.path.basename(path)
                text_str = prefix + filename

                draw_text(surface, text_str, (60, y),
                          size=config.FONT_SIZE_TEXT, color=color)

                rect = pygame.Rect(40, y - 5, surface.get_width() - 80, 35)
                self.item_rects.append(rect)

                y += 38

        draw_text(
            surface,
            "Pestanyes: Toc / Tab    Navegar: Toc / \u2191\u2193    Obrir: Enter / Toc    Tornar: Esc / Toc 'Tornar'",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
