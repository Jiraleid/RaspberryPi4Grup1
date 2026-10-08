"""
main.py
-------
Punt d'entrada del Media Center.
"""

import os
import sys

# Variables de entorno para SDL2 en consola pura / kmsdrm
os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
os.environ["SDL_MOUSE_TOUCH_EVENTS"] = "1"

import pygame

import config
from modules.home import HomeModule
from modules.movies import MoviesModule
from modules.books import BooksModule
from modules.games import GamesModule
from modules.photos import PhotosModule
from modules.weather import WeatherModule
from modules.network import NetworkModule
from modules.alarms import AlarmsModule

class ModuleManager:
    MODULE_CLASSES = {
        "home": HomeModule,
        "movies": MoviesModule,
        "books": BooksModule,
        "games": GamesModule,
        "photos": PhotosModule,
        "weather": WeatherModule,
        "network": NetworkModule,
        "alarms": AlarmsModule,
    }

    def __init__(self):
        self.modules = {name: cls(self) for name, cls in self.MODULE_CLASSES.items()}
        self.current_name = "home"
        self.current = self.modules["home"]
        self.running = True
        self.current.on_enter()

    def go_to(self, name):
        if name not in self.modules:
            print(f"[Aviso] Mòdul desconegut: {name}")
            return
        self.current.on_exit()
        self.current_name = name
        self.current = self.modules[name]
        self.current.on_enter()

    def quit(self):
        self.running = False

    def handle_event(self, event):
        self.current.handle_event(event)

    def update(self, dt):
        self.current.update(dt)

    def draw(self, surface):
        self.current.draw(surface)


def create_screen():
    pygame.display.set_caption(config.WINDOW_TITLE)
    flags = pygame.FULLSCREEN if config.FULLSCREEN else 0
    screen = pygame.display.set_mode(
        (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags
    )
    return screen


def main():
    pygame.init()
    pygame.display.set_caption(config.WINDOW_TITLE)

    screen = create_screen()
    clock = pygame.time.Clock()
    manager = ModuleManager()

    while manager.running:
        dt_ms = clock.tick(config.FPS)
        dt = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                manager.quit()

            # --- TRADUCCIÓN DE EVENTOS TÁCTILES PARA EL MENÚ ---
            elif event.type == pygame.FINGERDOWN:
                # Calculamos coordenadas exactas en píxeles
                px = int(event.x * config.SCREEN_WIDTH)
                py = int(event.y * config.SCREEN_HEIGHT)

                # 1. Actualizamos la posición real del cursor de Pygame
                pygame.mouse.set_pos((px, py))

                # 2. Generamos el evento MOUSEBUTTONDOWN estándar
                down_event = pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN,
                    pos=(px, py),
                    button=1
                )
                manager.handle_event(down_event)

            elif event.type == pygame.FINGERUP:
                px = int(event.x * config.SCREEN_WIDTH)
                py = int(event.y * config.SCREEN_HEIGHT)

                pygame.mouse.set_pos((px, py))

                # Generamos el evento MOUSEBUTTONUP estándar
                up_event = pygame.event.Event(
                    pygame.MOUSEBUTTONUP,
                    pos=(px, py),
                    button=1
                )
                manager.handle_event(up_event)

            else:
                manager.handle_event(event)

        manager.update(dt)

        # Obtener dinámicamente la superficie por si la pantalla se reabre tras el video
        current_screen = pygame.display.get_surface()
        if current_screen is not None:
            manager.draw(current_screen)
            pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
