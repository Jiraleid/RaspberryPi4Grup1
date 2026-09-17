"""
base_module.py
--------------
Classe abstracta que defineix la interfície comuna de tots els mòduls
(pantalles) del media center: Inici, Pel·lícules, Llibres, Jocs, Fotos,
Meteorologia, Xarxa i Alarmes.

Cada mòdul nou només ha de:
    1. Heretar de BaseModule.
    2. Implementar handle_event(event) i update(dt) si cal.
    3. Implementar draw(surface).
    4. Registrar-se al ModuleManager (veure main.py).

Això permet afegir funcionalitats noves sense tocar el nucli de
l'aplicació (obert/tancat - principi Open/Closed).
"""


class BaseModule:
    def __init__(self, manager):
        # `manager` és la instància de ModuleManager: permet canviar
        # de pantalla (manager.go_to("home")) des de qualsevol mòdul.
        self.manager = manager

    def on_enter(self):
        """Es crida cada vegada que s'entra en aquest mòdul."""
        pass

    def on_exit(self):
        """Es crida cada vegada que se surt d'aquest mòdul."""
        pass

    def handle_event(self, event):
        """Rep els esdeveniments de Pygame (teclat, ratolí, comandament)."""
        pass

    def update(self, dt):
        """Lògica que cal actualitzar cada frame. `dt` en segons."""
        pass

    def draw(self, surface):
        """Dibuixa el contingut del mòdul a la superfície principal."""
        raise NotImplementedError("Cada mòdul ha d'implementar draw()")
