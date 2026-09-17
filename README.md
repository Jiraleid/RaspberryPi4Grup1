# Media Center (Fase 1)

Interfície gràfica pròpia per a un centre multimèdia sobre Raspberry Pi,
feta amb Python i Pygame, sense utilitzar cap interfície multimèdia
existent (Kodi, Plex, etc.).

## Estructura del projecte

```
media_center/
├── main.py                # Bucle principal i gestor de mòduls (ModuleManager)
├── config.py               # Colors, rutes, mides de pantalla, claus d'API...
├── ui_utils.py              # Funcions de dibuix reutilitzables (text, menús, fade)
├── requirements.txt
├── modules/
│   ├── base_module.py       # Classe base que ha d'heretar cada pantalla
│   ├── home.py               # Menú principal (carrusel de seccions)
│   ├── movies.py              # Pel·lícules i sèries (llança mpv/omxplayer)
│   ├── books.py               # Llibres i còmics (obre amb el lector del sistema)
│   ├── games.py               # Jocs retro (llança RetroArch)
│   ├── photos.py               # Galeria de fotografies (visor integrat)
│   ├── weather.py              # Meteorologia (API OpenWeatherMap)
│   ├── network.py              # Xarxa Wi-Fi (via nmcli)
│   └── alarms.py                # Alarmes amb persistència en JSON
├── data/
│   └── alarms.json           # Es genera automàticament
└── assets/
    ├── icons/                 # Icones dels mòduls (opcional)
    └── fonts/                  # Tipografies personalitzades (opcional)
```

## Instal·lació

### A l'ordinador (desenvolupament)

```bash
python3 -m venv venv
source venv/bin/activate        # a Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### A la Raspberry Pi

```bash
sudo apt update
sudo apt install python3-pip python3-pygame mpv network-manager
pip3 install -r requirements.txt

# Per fer que arrenqui a pantalla completa en engegar la Pi,
# posa FULLSCREEN = True a config.py i afegeix una entrada
# a l'autostart (~/.config/autostart/mediacenter.desktop) o
# a l'arxiu /etc/xdg/lxsession/LXDE-pi/autostart
python3 main.py
```

## Configuració abans d'utilitzar-lo

1. **Carpetes de contingut**: edita `config.py` i ajusta les rutes
   `MOVIES_DIR`, `BOOKS_DIR`, `COMICS_DIR`, `PHOTOS_DIR`, `ROMS_DIR`
   perquè apuntin a les teves carpetes reals (per exemple, un disc USB
   muntat a `/media/pi/USB`).
2. **Meteorologia**: crea un compte gratuït a
   [OpenWeatherMap](https://openweathermap.org/api), genera una API key
   i posa-la a `config.OPENWEATHER_API_KEY`.
3. **Jocs retro**: instal·la [RetroArch](https://www.retroarch.com/) i
   revisa que els noms dels "cores" a `modules/games.py`
   (`ROM_CORES`) coincideixin amb els que tens instal·lats.
4. **Xarxa**: el mòdul fa servir `nmcli`, que ja ve instal·lat a
   Raspberry Pi OS per defecte.

## Controls (teclat)

| Tecla                | Acció                                   |
|-----------------------|------------------------------------------|
| ← → ↑ ↓               | Navegar pel menú / llistes               |
| Enter / Espai         | Seleccionar / Reproduir / Obrir          |
| Esc                   | Tornar enrere / Sortir des de l'inici    |
| F5                    | Refrescar (llistes de fitxers, xarxa...) |
| N (dins d'Alarmes)    | Crear una alarma nova                    |

Es poden mapejar els mateixos controls a un comandament de joc amb
eines com `antimicrox` (que tradueix botons a pulsacions de teclat),
de manera que el codi no necessita canvis addicionals.

## Arquitectura pensada per créixer

Cada pantalla (mòdul) hereta de `BaseModule` i només ha d'implementar
`handle_event()`, `update()` i `draw()`. El `ModuleManager` de
`main.py` s'encarrega d'instanciar-los i de canviar entre ells amb
`manager.go_to("nom_modul")`. Això permet ampliar el projecte en
fases posteriors (per exemple, un teclat en pantalla, perfils
d'usuari, control remot per xarxa, etc.) sense haver de reescriure el
nucli de l'aplicació.

## Limitacions conegudes d'aquesta primera fase

- La reproducció de vídeo es delega a un reproductor extern (`mpv` /
  `omxplayer`), ja que Pygame no descodifica vídeo nativament.
- La connexió a xarxes Wi-Fi amb contrasenya necessita un teclat en
  pantalla que encara no està implementat (el mètode `connect()` ja
  accepta un paràmetre `password` per quan s'afegeixi).
- Els llibres/còmics s'obren amb el lector per defecte del sistema;
  un visor de PDF/EPUB integrat es podria afegir amb `PyMuPDF`.
