"""
main.py
-------
Punt d'entrada del Media Center.

Conté:
    - ModuleManager: gestiona quin mòdul (pantalla) està actiu i
      permet canviar-hi ("navegar") des de qualsevol mòdul.
    - El bucle principal de Pygame: gestiona esdeveniments, actualitza
      l'estat i dibuixa cada frame.

Per afegir un mòdul nou:
    1. Crea modules/el_meu_modul.py heretant de BaseModule.
    2. Importa'l aquí i registra'l a ModuleManager.MODULES.
"""

import sys
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
    """
    Registra tots els mòduls disponibles i controla quin és l'actiu.
    Fa de "router" entre pantalles: cada mòdul rep una referència al
    manager i pot cridar manager.go_to("nom_del_modul") per navegar.
    """

    # Nom -> classe del mòdul. S'instancien un sol cop (a __init__)
    # i es reutilitzen, per no perdre el seu estat intern en tornar-hi.
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

    # Les tres funcions següents simplement deleguen al mòdul actiu.
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
        dt = dt_ms / 1000.0  # segons, útil per a la lògica dels mòduls

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                manager.quit()
            else:
                manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
