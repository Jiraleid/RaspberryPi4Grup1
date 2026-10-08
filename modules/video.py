"""
modules/video.py
----------------
Reproductor de vídeo en Pygame con barra de botones táctiles en la capa superior.
"""

import os
import cv2
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".webm")


class VideoModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.videos = []
        self.selected = 0
        self.error_message = None
        self.thumb_cache = {}

        self.item_rects = []
        self.btn_back_home_rect = None
        self.btn_play_rect = None

    def on_enter(self):
        self.scan_folder()
        self.selected = 0

    def scan_folder(self):
        self.videos = []
        self.thumb_cache = {}
        self.error_message = None

        videos_dir = getattr(config, "VIDEOS_DIR", os.path.expanduser("~/media_center/videos"))

        if not os.path.isdir(videos_dir):
            self.error_message = f"No s'ha trobat la carpeta:\n{videos_dir}"
            return

        for entry in sorted(os.listdir(videos_dir)):
            ext = os.path.splitext(entry)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                full_path = os.path.join(videos_dir, entry)
                base_name = os.path.splitext(entry)[0]

                thumb_path = None
                for img_ext in (".png", ".jpg", ".jpeg"):
                    potential_thumb = os.path.join(videos_dir, base_name + img_ext)
                    if os.path.isfile(potential_thumb):
                        thumb_path = potential_thumb
                        break

                self.videos.append({
                    "name": base_name,
                    "filename": entry,
                    "video_path": full_path,
                    "thumb_path": thumb_path,
                    "ext": ext
                })

        if not self.videos:
            self.error_message = "No s'han trobat fitxers de vídeo."

    def load_thumb(self, path, max_w=280, max_h=200):
        if not path or not os.path.isfile(path):
            return None
        if path in self.thumb_cache:
            return self.thumb_cache[path]

        try:
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            scale = min(max_w / w, max_h / h)
            new_size = (int(w * scale), int(h * scale))
            img = pygame.transform.smoothscale(img, new_size)
            self.thumb_cache[path] = img
            return img
        except Exception:
            return None

    def play_selected(self):
        if not self.videos:
            return

        video = self.videos[self.selected]
        video_path = video["video_path"]

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.error_message = "Error en obrir el vídeo."
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or fps > 120:
            fps = 30

        clock = pygame.time.Clock()
        screen = pygame.display.get_surface()
        screen_w, screen_h = screen.get_size()

        bar_h = 90
        video_h = screen_h - bar_h

        # Botones
        btn_w = (screen_w // 4) - 20
        btn_h = 60
        btn_y = video_h + ((bar_h - btn_h) // 2)

        btn_rewind = pygame.Rect(10, btn_y, btn_w, btn_h)
        btn_play_pause = pygame.Rect(10 + btn_w + 15, btn_y, btn_w, btn_h)
        btn_forward = pygame.Rect(10 + (btn_w + 15) * 2, btn_y, btn_w, btn_h)
        btn_exit = pygame.Rect(10 + (btn_w + 15) * 3, btn_y, btn_w, btn_h)

        pygame.font.init()
        font_btn = pygame.font.SysFont(None, 32)

        is_playing = True
        paused = False
        frame_surface = None

        while is_playing:
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_playing = False

                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                    pos = getattr(event, "pos", None)
                    if pos is None and hasattr(event, "x"):
                        pos = (int(event.x * screen_w), int(event.y * screen_h))

                    if pos:
                        if btn_rewind.collidepoint(pos):
                            curr = cap.get(cv2.CAP_PROP_POS_FRAMES)
                            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, curr - (5 * fps)))
                        elif btn_play_pause.collidepoint(pos):
                            paused = not paused
                        elif btn_forward.collidepoint(pos):
                            curr = cap.get(cv2.CAP_PROP_POS_FRAMES)
                            total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                            cap.set(cv2.CAP_PROP_POS_FRAMES, min(total - 1, curr + (5 * fps)))
                        elif btn_exit.collidepoint(pos):
                            is_playing = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        is_playing = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused

            # Vídeo
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (screen_w, video_h))
                frame_surface = pygame.image.frombuffer(frame.tobytes(), (screen_w, video_h), "RGB")

            # Dibujar fondo y vídeo
            screen.fill((0, 0, 0))
            if frame_surface:
                screen.blit(frame_surface, (0, 0))

            # Dibujar barra inferior (Capa superior)
            overlay = pygame.Surface((screen_w, bar_h))
            overlay.fill((20, 20, 20))
            screen.blit(overlay, (0, video_h))

            # Dibujar botones sobre la barra
            pygame.draw.rect(screen, (70, 70, 70), btn_rewind, border_radius=8)
            txt_rew = font_btn.render("-5s", True, (255, 255, 255))
            screen.blit(txt_rew, txt_rew.get_rect(center=btn_rewind.center))

            color_pp = (220, 130, 0) if paused else (40, 160, 40)
            txt_pp_str = "PLAY" if paused else "PAUSA"
            pygame.draw.rect(screen, color_pp, btn_play_pause, border_radius=8)
            txt_pp = font_btn.render(txt_pp_str, True, (255, 255, 255))
            screen.blit(txt_pp, txt_pp.get_rect(center=btn_play_pause.center))

            pygame.draw.rect(screen, (70, 70, 70), btn_forward, border_radius=8)
            txt_fwd = font_btn.render("+5s", True, (255, 255, 255))
            screen.blit(txt_fwd, txt_fwd.get_rect(center=btn_forward.center))

            pygame.draw.rect(screen, (200, 40, 40), btn_exit, border_radius=8)
            txt_exit = font_btn.render("SORTIR", True, (255, 255, 255))
            screen.blit(txt_exit, txt_exit.get_rect(center=btn_exit.center))

            pygame.display.update()
            clock.tick(fps)

        cap.release()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.go_to("home")
            elif event.key in (pygame.K_UP, pygame.K_w) and self.videos:
                self.selected = (self.selected - 1) % len(self.videos)
            elif event.key in (pygame.K_DOWN, pygame.K_s) and self.videos:
                self.selected = (self.selected + 1) % len(self.videos)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.play_selected()
            elif event.key == pygame.K_F5:
                self.scan_folder()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.btn_back_home_rect and self.btn_back_home_rect.collidepoint(pos):
                self.manager.go_to("home")
                return

            if self.btn_play_rect and self.btn_play_rect.collidepoint(pos):
                self.play_selected()
                return

            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(pos):
                    if self.selected == i:
                        self.play_selected()
                    else:
                        self.selected = i
                    break

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        draw_text(surface, "Vídeos", (40, 25),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        self.btn_back_home_rect = pygame.Rect(surface.get_width() - 150, 20, 110, 40)
        pygame.draw.rect(surface, (180, 50, 50), self.btn_back_home_rect, border_radius=8)
        draw_text(surface, "Tornar", self.btn_back_home_rect.center,
                  size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")

        self.item_rects = []

        if self.error_message:
            draw_text(surface, self.error_message, (40, 120),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
            return

        list_w = surface.get_width() // 2 - 20
        y = 100
        for i, vid in enumerate(self.videos):
            is_selected = (i == self.selected)
            color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
            prefix = "▶  " if is_selected else "    "

            draw_text(surface, prefix + vid["name"], (50, y),
                      size=config.FONT_SIZE_TEXT, color=color)

            rect = pygame.Rect(40, y - 5, list_w, 35)
            self.item_rects.append(rect)
            y += 40

        if self.videos:
            current_video = self.videos[self.selected]
            right_x = surface.get_width() // 2 + 40

            subtitle_size = getattr(config, "FONT_SIZE_SUBTITLE", config.FONT_SIZE_TITLE - 4)
            draw_text(surface, current_video["name"], (right_x, 100),
                      size=subtitle_size, color=config.COLOR_PRIMARY)

            thumb_img = self.load_thumb(current_video["thumb_path"])
            if thumb_img:
                surface.blit(thumb_img, (right_x, 140))
            else:
                no_thumb_rect = pygame.Rect(right_x, 140, 240, 150)
                pygame.draw.rect(surface, (40, 40, 40), no_thumb_rect, border_radius=8)
                draw_text(surface, "Sense Vista Prèvia", no_thumb_rect.center,
                          size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED, align="center")

            self.btn_play_rect = pygame.Rect(right_x, 320, 180, 45)
            pygame.draw.rect(surface, config.COLOR_PRIMARY, self.btn_play_rect, border_radius=8)
            draw_text(surface, "REPRODUIR", self.btn_play_rect.center,
                      size=config.FONT_SIZE_TEXT, color=(255, 255, 255), align="center")
