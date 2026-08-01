"""Persistencia del último estado procesado (autosave y restauración)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Contact

# Nombre del archivo que guarda el estado de la aplicación.
STATE_FILENAME = "state.json"


def _state_dir() -> Path:
    """Directorio de datos del usuario, portable para PyInstaller."""
    appdata = os.getenv("APPDATA") or str(Path.home())
    return Path(appdata) / "WhatsAppBroadcastPA"


class StateStore:
    """Guarda y restaura la última información procesada en un JSON."""

    def __init__(self, directory: Path | str | None = None) -> None:
        self.directory = Path(directory) if directory else _state_dir()
        self.filepath = self.directory / STATE_FILENAME

    def save(self, input_text: str, contacts: list[Contact]) -> None:
        """Persiste el texto de entrada y los contactos procesados."""
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            data = {
                "input_text": input_text,
                "contacts": [c.to_dict() for c in contacts],
            }
            with open(self.filepath, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
        except OSError:
            # El guardado es una comodidad: falla sin interrumpir la app.
            pass

    def load(self) -> tuple[str, list[Contact]]:
        """Restaura el último estado guardado; vacío si no existe o está dañado."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            contacts = [Contact.from_dict(c) for c in data.get("contacts", [])]
            return data.get("input_text", ""), contacts
        except (OSError, json.JSONDecodeError, ValueError):
            return "", []
