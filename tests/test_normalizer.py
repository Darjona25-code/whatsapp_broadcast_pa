"""Pruebas del normalizador de teléfonos y nombres."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Permite ejecutar las pruebas desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.normalizer import NameNormalizer, PhoneNormalizer  # noqa: E402


class TestPhoneNormalizer(unittest.TestCase):
    """Casos para la normalización de teléfonos panameños."""

    def test_movil_con_guion(self):
        numero, valido, nota = PhoneNormalizer.normalize("6673-2629")
        self.assertEqual(numero, "+50766732629")
        self.assertTrue(valido)

    def test_movil_sin_guion(self):
        numero, valido, _ = PhoneNormalizer.normalize("60001111")
        self.assertEqual(numero, "+50760001111")
        self.assertTrue(valido)

    def test_con_prefijo_507(self):
        numero, valido, _ = PhoneNormalizer.normalize("+507 6673-2629")
        self.assertEqual(numero, "+50766732629")
        self.assertTrue(valido)

    def test_con_prefijo_00507(self):
        numero, valido, _ = PhoneNormalizer.normalize("00507 6673-2629")
        self.assertEqual(numero, "+50766732629")
        self.assertTrue(valido)

    def test_numero_fijo_es_convertido_pero_marcado(self):
        numero, valido, _ = PhoneNormalizer.normalize("222-3333")
        self.assertEqual(numero, "+5072223333")
        self.assertFalse(valido)

    def test_numero_corto_invalido(self):
        numero, valido, _ = PhoneNormalizer.normalize("12345")
        self.assertEqual(numero, "")
        self.assertFalse(valido)

    def test_sin_digitos(self):
        numero, valido, _ = PhoneNormalizer.normalize("sin numero")
        self.assertEqual(numero, "")
        self.assertFalse(valido)

    def test_letras_mezcladas(self):
        numero, valido, _ = PhoneNormalizer.normalize("66a73-26b29")
        self.assertEqual(numero, "+50766732629")
        self.assertTrue(valido)


class TestNameNormalizer(unittest.TestCase):
    """Casos para la limpieza y capitalización de nombres."""

    def test_normaliza_y_capitaliza(self):
        self.assertEqual(NameNormalizer.normalize("  maría  lópez "), "María López")

    def test_quita_pipes(self):
        self.assertEqual(NameNormalizer.normalize("| María López |"), "María López")

    def test_quita_guiones_sobrantes(self):
        self.assertEqual(NameNormalizer.normalize("Carlos Ruiz - -"), "Carlos Ruiz")

    def test_conserva_guion_en_apellido(self):
        self.assertEqual(NameNormalizer.normalize("Ana García-López"), "Ana García-López")

    def test_vacio(self):
        self.assertEqual(NameNormalizer.normalize("   "), "")
        self.assertEqual(NameNormalizer.normalize("| - |"), "")


if __name__ == "__main__":
    unittest.main()
