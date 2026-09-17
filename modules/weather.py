"""
weather.py
----------
Mòdul de meteorologia. Consulta l'API gratuïta d'OpenWeatherMap
(cal una API key pròpia a config.OPENWEATHER_API_KEY) i mostra la
temperatura actual, la sensació tèrmica, la humitat i una descripció.

La petició de xarxa es fa en un fil (thread) a part perquè no bloquegi
el bucle principal de Pygame mentre s'espera la resposta del servidor.
"""

import threading
import time
import urllib.request
import urllib.parse
import json

import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

WEATHER_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
    "?q={city}&appid={key}&units={units}&lang={lang}"
)

REFRESH_INTERVAL = 10 * 60  # segons (10 minuts)


class WeatherModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.data = None
        self.error_message = None
        self.loading = False
        self.last_fetch = 0

    def on_enter(self):
        # Només torna a consultar si fa temps que no ho fem
        if time.time() - self.last_fetch > REFRESH_INTERVAL:
            self.fetch_weather()

    def fetch_weather(self):
        if self.loading:
            return
        self.loading = True
        self.error_message = None
        thread = threading.Thread(target=self._fetch_worker, daemon=True)
        thread.start()

    def _fetch_worker(self):
        url = WEATHER_URL.format(
            city=urllib.parse.quote(config.WEATHER_CITY),
            key=config.OPENWEATHER_API_KEY,
            units=config.WEATHER_UNITS,
            lang=config.WEATHER_LANG,
        )
        try:
            with urllib.request.urlopen(url, timeout=6) as response:
                raw = response.read()
                self.data = json.loads(raw)
                self.last_fetch = time.time()
        except Exception as exc:
            self.error_message = f"No s'ha pogut obtenir la meteorologia:\n{exc}"
        finally:
            self.loading = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.manager.go_to("home")
        elif event.key == pygame.K_F5:
            self.fetch_weather()

    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        draw_text(surface, "Meteorologia", (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        if self.loading:
            draw_text(surface, "Consultant...", (40, 130),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)
        elif self.error_message:
            draw_text(surface, self.error_message, (40, 130),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
        elif self.data:
            self._draw_weather_data(surface)
        else:
            draw_text(surface, "Prem F5 per consultar la meteorologia.",
                      (40, 130), size=config.FONT_SIZE_TEXT,
                      color=config.COLOR_TEXT_MUTED)

        draw_text(
            surface, "F5: Refrescar   Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )

    def _draw_weather_data(self, surface):
        d = self.data
        city_name = d.get("name", config.WEATHER_CITY)
        temp = d["main"]["temp"]
        feels_like = d["main"]["feels_like"]
        humidity = d["main"]["humidity"]
        description = d["weather"][0]["description"].capitalize()

        draw_text(surface, city_name, (40, 120),
                  size=config.FONT_SIZE_MENU, color=config.COLOR_TEXT)
        draw_text(surface, f"{temp:.1f}\u00b0C", (40, 170),
                  size=72, color=config.COLOR_PRIMARY)
        draw_text(surface, description, (40, 250),
                  size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT)
        draw_text(surface, f"Sensació tèrmica: {feels_like:.1f}\u00b0C",
                  (40, 300), size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)
        draw_text(surface, f"Humitat: {humidity}%",
                  (40, 335), size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)
