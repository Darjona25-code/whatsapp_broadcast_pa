"""Normalización de nombres y de números de teléfono panameños."""

from __future__ import annotations

import re


class PhoneNormalizer:
    """Convierte números de teléfono al formato internacional +507XXXXXXXX."""

    # Prefijos de país de Panamá que pueden aparecer incluidos.
    COUNTRY_PREFIXES = ("507", "00507")

    # Inicios de los móviles panameños de 8 dígitos: 6 y 7.
    MOBILE_STARTS = ("6", "7")

    @classmethod
    def normalize(cls, raw: str) -> tuple[str, bool, str]:
        """Normaliza un número de teléfono.

        Retorna la tupla (numero_normalizado, es_valido, nota):
        - numero_normalizado: "+507" + 8 dígitos, o "" si no se pudo.
        - es_valido: True si parece un móvil panameño válido.
        - nota: descripción breve del resultado.
        """
        digits = cls._digits_only(raw)
        if not digits:
            return "", False, "No se detectó un número de teléfono"

        # Si viene con prefijo de país, se elimina para quedarnos
        # solo con el número local de 8 dígitos.
        local = digits
        for prefix in cls.COUNTRY_PREFIXES:
            if digits.startswith(prefix) and len(digits) == len(prefix) + 8:
                local = digits[len(prefix):]
                break

        if len(local) == 8:
            number = f"+507{local}"
            if local.startswith(cls.MOBILE_STARTS):
                return number, True, "Móvil panameño válido"
            return number, False, "Número fijo panameño: verificar"

        return "", False, f"Formato inesperado ({len(digits)} dígitos)"

    @staticmethod
    def _digits_only(raw: str) -> str:
        """Devuelve solo los dígitos del texto dado."""
        return re.sub(r"\D", "", raw or "")


class NameNormalizer:
    """Limpia y capitaliza nombres de forma consistente."""

    # Palabras que normalmente se mantienen en minúscula dentro de un nombre.
    LOWERCASE_WORDS = {"de", "del", "la", "las", "los", "y", "e", "o", "u"}

    @classmethod
    def normalize(cls, raw: str) -> str:
        """Limpia espacios, separadores y capitaliza el nombre."""
        if not raw:
            return ""

        text = raw.strip()

        # Separadores típicos entre campos (|, ;, :, tabulaciones).
        text = re.sub(r"[\t;:|]+", " ", text)

        # Guiones sueltos usados como separadores (no toca "García-López").
        text = re.sub(r"\s+[-–—]+\s+", " ", text)

        # Colapsar espacios y quitar separadores sobrantes en los extremos.
        text = re.sub(r"\s+", " ", text).strip(" -–—")
        if not text:
            return ""

        # Capitalizar cada palabra, respetando partículas en minúscula.
        words = []
        for word in text.split():
            lower = word.lower()
            if lower in cls.LOWERCASE_WORDS and words:
                words.append(lower)
            else:
                # Mantener el resto del texto tal cual (acentos, apóstrofes).
                words.append(word[:1].upper() + word[1:])
        return " ".join(words)
