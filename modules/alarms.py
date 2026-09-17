"""
alarms.py
---------
Mòdul d'alarmes. Permet crear alarmes (hora:minut), desar-les en un
fitxer JSON perquè persisteixin entre execucions, i llança un so
d'avís quan arriba l'hora. La comprovació es fa a `update()`, que es
crida cada frame des del bucle principal.
"""

import os
import json
import datetime
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text

ALARMS_FILE = os.path.join(config.DATA_DIR, "alarms.json")


class Alarm:
    def __init__(self, hour, minute, label="Alarma", enabled=True):
        self.hour = hour
        self.minute = minute
        self.label = label
        self.enabled = enabled
        self.triggered_today = False

    def to_dict(self):
        return {
            "hour": self.hour, "minute": self.minute,
            "label": self.label, "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(d):
        return Alarm(d["hour"], d["minute"], d.get("label", "Alarma"),
                      d.get("enabled", True))


class AlarmsModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.alarms = []
        self.selected = 0
        self.ringing_alarm = None
        self._load()

        # Modo edició per crear una alarma nova amb les fletxes
        self.editing_new = False
        self.new_hour = 8
        self.new_minute = 0

    def _load(self):
        os.makedirs(config.DATA_DIR, exist_ok=True)
        if os.path.isfile(ALARMS_FILE):
            try:
                with open(ALARMS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.alarms = [Alarm.from_dict(d) for d in data]
            except Exception:
                self.alarms = []

    def _save(self):
        os.makedirs(config.DATA_DIR, exist_ok=True)
        with open(ALARMS_FILE, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in self.alarms], f, indent=2)

    def update(self, dt):
        """Es crida cada frame: comprova si alguna alarma ha de sonar."""
        now = datetime.datetime.now()

        # Reinicia el flag `triggered_today` a mitjanit
        for alarm in self.alarms:
            if now.hour == 0 and now.minute == 0:
                alarm.triggered_today = False

            if (alarm.enabled and not alarm.triggered_today
                    and alarm.hour == now.hour and alarm.minute == now.minute):
                alarm.triggered_today = True
                self.ringing_alarm = alarm

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Si sona una alarma, qualsevol tecla la para
        if self.ringing_alarm:
            self.ringing_alarm = None
            return

        if self.editing_new:
            self._handle_edit_event(event)
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.go_to("home")
        elif event.key in (pygame.K_UP, pygame.K_w) and self.alarms:
            self.selected = (self.selected - 1) % len(self.alarms)
        elif event.key in (pygame.K_DOWN, pygame.K_s) and self.alarms:
            self.selected = (self.selected + 1) % len(self.alarms)
        elif event.key == pygame.K_n:
            self.editing_new = True
            self.new_hour, self.new_minute = 8, 0
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.alarms:
            self.alarms[self.selected].enabled = not self.alarms[self.selected].enabled
            self._save()
        elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE) and self.alarms:
            del self.alarms[self.selected]
            self.selected = max(0, self.selected - 1)
            self._save()

    def _handle_edit_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.editing_new = False
        elif event.key == pygame.K_UP:
            self.new_hour = (self.new_hour + 1) % 24
        elif event.key == pygame.K_DOWN:
            self.new_hour = (self.new_hour - 1) % 24
        elif event.key == pygame.K_RIGHT:
            self.new_minute = (self.new_minute + 5) % 60
        elif event.key == pygame.K_LEFT:
            self.new_minute = (self.new_minute - 5) % 60
        elif event.key == pygame.K_RETURN:
            self.alarms.append(Alarm(self.new_hour, self.new_minute))
            self._save()
            self.editing_new = False

    def draw(self, surface):
        surface.fill(config.COLOR_BG)

        if self.ringing_alarm:
            self._draw_ringing(surface)
            return

        draw_text(surface, "Alarmes", (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        if self.editing_new:
            self._draw_editor(surface)
            return

        if not self.alarms:
            draw_text(surface, "Cap alarma configurada. Prem 'N' per crear-ne una.",
                      (40, 130), size=config.FONT_SIZE_TEXT,
                      color=config.COLOR_TEXT_MUTED)
        else:
            y = 130
            for i, alarm in enumerate(self.alarms):
                is_selected = (i == self.selected)
                color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
                state = "ON " if alarm.enabled else "OFF"
                prefix = "\u25b6  " if is_selected else "    "
                text = f"{prefix}[{state}]  {alarm.hour:02d}:{alarm.minute:02d}  {alarm.label}"
                draw_text(surface, text, (60, y),
                          size=config.FONT_SIZE_TEXT, color=color)
                y += 40

        draw_text(
            surface,
            "\u2191\u2193 Navegar  Enter: Act/Desact  N: Nova  Supr: Esborrar  Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )

    def _draw_editor(self, surface):
        draw_text(surface, "Nova alarma", (40, 120),
                  size=config.FONT_SIZE_MENU, color=config.COLOR_TEXT)
        time_str = f"{self.new_hour:02d}:{self.new_minute:02d}"
        draw_text(surface, time_str, (surface.get_width() // 2, 260),
                  size=90, color=config.COLOR_PRIMARY, align="center")
        draw_text(
            surface,
            "\u2191\u2193 Hora   \u2190\u2192 Minuts (x5)   Enter: Desar   Esc: Cancel·lar",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )

    def _draw_ringing(self, surface):
        surface.fill(config.COLOR_ERROR)
        alarm = self.ringing_alarm
        draw_text(surface, "\u23f0 ALARMA", (surface.get_width() // 2, 200),
                  size=64, color=config.COLOR_TEXT, align="center")
        draw_text(surface, f"{alarm.hour:02d}:{alarm.minute:02d}  {alarm.label}",
                  (surface.get_width() // 2, 300),
                  size=config.FONT_SIZE_MENU, color=config.COLOR_TEXT, align="center")
        draw_text(surface, "Prem qualsevol tecla per aturar-la",
                  (surface.get_width() // 2, 400),
                  size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT, align="center")
