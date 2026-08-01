"""Generación de reportes de salida para WhatsApp Business."""

from __future__ import annotations

from .models import Contact, ContactStatus


class ReportGenerator:
    """Construye la lista para broadcast y el reporte completo de texto."""

    @staticmethod
    def build_broadcast_list(contacts: list[Contact]) -> str:
        """Devuelve los teléfonos +507 normalizados, uno por línea.

        Se excluyen los contactos cuyo teléfono está marcado para revisión.
        """
        numbers = []
        for contact in contacts:
            if contact.status is ContactStatus.REVISAR_TELEFONO:
                continue
            if contact.phone:
                numbers.append(contact.phone)
        return "\n".join(numbers)

    @staticmethod
    def build_full_report(contacts: list[Contact]) -> str:
        """Devuelve una línea 'Nombre | Teléfono | Correo' por contacto."""
        lines = []
        for contact in contacts:
            name = contact.name or "Sin nombre"
            phone = contact.phone or "-"
            email = contact.email or "-"
            lines.append(f"{name} | {phone} | {email}")
        return "\n".join(lines)
