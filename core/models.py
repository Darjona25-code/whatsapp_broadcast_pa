"""Modelos de datos de la aplicación.

Define la estructura de un contacto procesado y los estados
que puede tener según la información detectada en el texto.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class ContactStatus(str, Enum):
    """Estados posibles de un contacto procesado."""

    VALIDO = "Válido"
    REVISAR_TELEFONO = "Revisar teléfono"
    INCOMPLETO = "Información incompleta"


@dataclass
class Contact:
    """Representa un contacto detectado en el texto pegado.

    Atributos:
        name: Nombre normalizado de la persona.
        phone_raw: Número tal como apareció en el texto original.
        phone: Número normalizado al formato +507XXXXXXXX (si aplica).
        email: Correo electrónico detectado.
        status: Estado calculado del contacto.
        note: Detalle adicional del porqué del estado.
    """

    name: str = ""
    phone_raw: str = ""
    phone: str = ""
    email: str = ""
    status: ContactStatus = ContactStatus.INCOMPLETO
    note: str = ""

    def to_dict(self) -> dict:
        """Convierte el contacto a diccionario (para persistencia)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        """Reconstruye un contacto desde un diccionario (JSON)."""
        return cls(
            name=data.get("name", ""),
            phone_raw=data.get("phone_raw", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            status=ContactStatus(data.get("status", ContactStatus.INCOMPLETO.value)),
            note=data.get("note", ""),
        )
