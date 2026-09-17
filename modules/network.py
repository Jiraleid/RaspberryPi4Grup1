"""
network.py
----------
Mòdul de configuració de xarxa. Fa servir `nmcli` (NetworkManager
CLI), que ve preinstal·lat a Raspberry Pi OS, per llistar xarxes
Wi-Fi disponibles i mostrar l'estat de connexió actual.

Nota: connectar-se a una xarxa que requereix contrasenya necessitaria
un teclat en pantalla (on-screen keyboard); aquí es mostra l'estructura
i es deixa un mètode `connect()` preparat per ampliar-ho.
"""

import subprocess
import pygame
import config
from modules.base_module import BaseModule
from ui_utils import draw_text


class NetworkModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.networks = []
        self.selected = 0
        self.error_message = None
        self.current_connection = None

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.error_message = None
        self.networks = self._scan_wifi()
        self.current_connection = self._get_current_connection()
        self.selected = 0

    def _scan_wifi(self):
        """Retorna una llista de (ssid, senyal, seguretat) via nmcli."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                capture_output=True, text=True, timeout=8,
            )
            networks = []
            seen = set()
            for line in result.stdout.splitlines():
                parts = line.split(":")
                if len(parts) >= 3 and parts[0] and parts[0] not in seen:
                    seen.add(parts[0])
                    networks.append((parts[0], parts[1], parts[2]))
            return networks
        except FileNotFoundError:
            self.error_message = "'nmcli' no està disponible en aquest sistema."
            return []
        except Exception as exc:
            self.error_message = f"Error escanejant xarxes: {exc}"
            return []

    def _get_current_connection(self):
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "active,ssid", "device", "wifi"],
                capture_output=True, text=True, timeout=8,
            )
            for line in result.stdout.splitlines():
                if line.startswith("yes:"):
                    return line.split(":", 1)[1]
        except Exception:
            pass
        return None

    def connect(self, ssid, password=None):
        """
        Connecta a la xarxa indicada. Si cal contrasenya i no se'n
        proporciona cap, aquí és on s'hauria d'obrir un teclat en
        pantalla per demanar-la a l'usuari.
        """
        try:
            cmd = ["nmcli", "device", "wifi", "connect", ssid]
            if password:
                cmd += ["password", password]
            subprocess.run(cmd, timeout=15)
            self.refresh()
        except Exception as exc:
            self.error_message = f"No s'ha pogut connectar: {exc}"

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.manager.go_to("home")
        elif event.key in (pygame.K_UP, pygame.K_w) and self.networks:
            self.selected = (self.selected - 1) % len(self.networks)
        elif event.key in (pygame.K_DOWN, pygame.K_s) and self.networks:
            self.selected = (self.selected + 1) % len(self.networks)
        elif event.key == pygame.K_F5:
            self.refresh()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.networks:
            ssid = self.networks[self.selected][0]
            # De moment només xarxes obertes; per xarxes amb contrasenya
            # caldria integrar un teclat en pantalla.
            self.connect(ssid)

    def draw(self, surface):
        surface.fill(config.COLOR_BG)
        draw_text(surface, "Xarxa", (40, 30),
                  size=config.FONT_SIZE_TITLE, color=config.COLOR_PRIMARY)

        status = self.current_connection or "Sense connexió"
        status_color = config.COLOR_OK if self.current_connection else config.COLOR_ERROR
        draw_text(surface, f"Connectat a: {status}", (40, 90),
                  size=config.FONT_SIZE_TEXT, color=status_color)

        if self.error_message:
            draw_text(surface, self.error_message, (40, 140),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_ERROR)
        elif not self.networks:
            draw_text(surface, "Cap xarxa detectada.", (40, 140),
                      size=config.FONT_SIZE_TEXT, color=config.COLOR_TEXT_MUTED)
        else:
            y = 150
            for i, (ssid, signal, security) in enumerate(self.networks):
                is_selected = (i == self.selected)
                color = config.COLOR_PRIMARY if is_selected else config.COLOR_TEXT
                lock = "\U0001f512 " if security else "   "
                prefix = "\u25b6  " if is_selected else "    "
                draw_text(surface, f"{prefix}{lock}{ssid}  ({signal}%)", (60, y),
                          size=config.FONT_SIZE_TEXT, color=color)
                y += 36

        draw_text(
            surface,
            "\u2191 \u2193 Navegar   Enter: Connectar   F5: Refrescar   Esc: Tornar",
            (surface.get_width() // 2, surface.get_height() - 30),
            size=config.FONT_SIZE_SMALL, color=config.COLOR_TEXT_MUTED,
            align="center",
        )
