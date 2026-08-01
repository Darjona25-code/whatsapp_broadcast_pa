"""Extracción de contactos a partir de texto pegado desde una página web."""

from __future__ import annotations

import re

from .models import Contact, ContactStatus
from .normalizer import NameNormalizer, PhoneNormalizer


class ContactParser:
    """Analiza texto libre y lo convierte en una lista de Contact.

    Reconoce nombres, teléfonos y correos sin importar el orden en que
    aparezcan, ya sea cada campo en su propia línea o separados por
    símbolos como |, - o ;.
    """

    # Expresión para correos electrónicos.
    EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

    # Expresión para números de teléfono: 8 dígitos con separadores
    # opcionales (-, ., espacio) y prefijo de país opcional (+507/507/00507).
    PHONE_RE = re.compile(
        r"(?:\+?507[\s.\-]*)?\d{3}[\s.\-]*\d{3,4}[\s.\-]*\d{1,4}"
        r"|(?:\+?507[\s.\-]*)?\d{4}[\s.\-]*\d{4}"
    )

    def parse(self, text: str) -> list[Contact]:
        """Convierte el texto pegado en una lista de Contact procesados."""
        contacts: list[Contact] = []
        current: dict | None = None  # Acumulador de la persona en construcción.

        def flush() -> None:
            """Cierra el registro en curso y lo agrega a la lista."""
            nonlocal current
            if current and (current["name"] or current["phone"] or current["email"]):
                contacts.append(self._build_contact(current))
            current = None

        for line in text.splitlines():
            line = self._clean_line(line)
            if not line:
                continue

            email = self._extract_email(line)
            phone = self._extract_phone(line)
            name = self._extract_name(line, email, phone)

            if current is None:
                current = {"name": "", "phone": "", "email": ""}

            if name:
                # Llega un nombre nuevo.
                if current["name"]:
                    # El registro actual ya tenía nombre: si además tenía
                    # datos, es una persona nueva → cerrar y empezar otra.
                    if current["phone"] or current["email"]:
                        flush()
                        current = {"name": "", "phone": "", "email": ""}
                    # Si aún no tenía datos, se reemplaza el nombre anterior
                    # (p. ej. texto suelto antes del contacto real).
                    current["name"] = name
                else:
                    # El registro en curso empezó con teléfono/correo
                    # y ahora recibe el nombre.
                    current["name"] = name

            # El teléfono y el correo pueden estar en la misma línea
            # que el nombre (o en líneas siguientes).
            if phone:
                current["phone"] = phone
            if email:
                current["email"] = email

        flush()
        return contacts

    # ------------------------------------------------------------------
    # Métodos de extracción
    # ------------------------------------------------------------------
    @classmethod
    def _extract_email(cls, line: str) -> str:
        """Devuelve el primer correo detectado en la línea."""
        match = cls.EMAIL_RE.search(line)
        return match.group(0) if match else ""

    @classmethod
    def _extract_phone(cls, line: str) -> str:
        """Devuelve el primer teléfono detectado en la línea."""
        match = cls.PHONE_RE.search(line)
        return match.group(0) if match else ""

    @classmethod
    def _extract_name(cls, line: str, email: str, phone: str) -> str:
        """Quita correo y teléfono de la línea y deja solo el nombre."""
        text = line
        if email:
            text = text.replace(email, " ")
        if phone:
            text = text.replace(phone, " ")
        return NameNormalizer.normalize(text)

    @staticmethod
    def _clean_line(line: str) -> str:
        """Elimina espacios no separadores y colapsa espacios múltiples."""
        line = line.replace("\ufeff", "").replace("\xa0", " ")
        return " ".join(line.split())

    @staticmethod
    def _build_contact(current: dict) -> Contact:
        """Construye el Contact final con teléfono normalizado y estado."""
        phone_raw = current["phone"]
        phone, phone_ok, note = "", False, ""
        if phone_raw:
            phone, phone_ok, note = PhoneNormalizer.normalize(phone_raw)

        name = current["name"]
        email = current["email"]

        status = ContactStatus.VALIDO
        if not phone_raw:
            # No se encontró ningún número en el texto.
            status = ContactStatus.INCOMPLETO
            note = "Falta número de teléfono"
        elif not phone_ok:
            # El número encontrado no parece un móvil panameño válido.
            status = ContactStatus.REVISAR_TELEFONO
        elif not email or not name:
            status = ContactStatus.INCOMPLETO
            note = "Falta nombre o correo"

        return Contact(
            name=name,
            phone_raw=phone_raw,
            phone=phone,
            email=email,
            status=status,
            note=note,
        )
