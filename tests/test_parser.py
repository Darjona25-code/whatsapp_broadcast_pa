"""Pruebas del parser de contactos."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Permite ejecutar las pruebas desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.models import ContactStatus  # noqa: E402
from core.parser import ContactParser  # noqa: E402


class TestContactParser(unittest.TestCase):
    """Casos para la extracción de contactos desde texto libre."""

    def setUp(self):
        self.parser = ContactParser()

    def test_formato_lineas_separadas(self):
        """Nombre, correo y teléfono en líneas propias."""
        texto = """Patricia Guevara
pangelica_27@hotmail.com
6673-2629"""
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        c = contacts[0]
        self.assertEqual(c.name, "Patricia Guevara")
        self.assertEqual(c.phone, "+50766732629")
        self.assertEqual(c.email, "pangelica_27@hotmail.com")
        self.assertEqual(c.status, ContactStatus.VALIDO)

    def test_formato_pipes(self):
        """Nombre, teléfono y correo separados por |."""
        texto = "María López | 6222-3344 | maria@gmail.com"
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        c = contacts[0]
        self.assertEqual(c.name, "María López")
        self.assertEqual(c.phone, "+50762223344")
        self.assertEqual(c.email, "maria@gmail.com")
        self.assertEqual(c.status, ContactStatus.VALIDO)

    def test_formato_guiones(self):
        """Nombre, correo y teléfono separados por guiones."""
        texto = "Carlos Ruiz - carlos@hotmail.com - 6777-8888"
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        c = contacts[0]
        self.assertEqual(c.name, "Carlos Ruiz")
        self.assertEqual(c.phone, "+50767778888")
        self.assertEqual(c.email, "carlos@hotmail.com")

    def test_varios_contactos(self):
        """Múltiples personas en un solo pegado, con líneas en blanco."""
        texto = """Juan Pérez
6000-1111
juan@email.com

María López | 6222-3344 | maria@gmail.com

Carlos Ruiz - carlos@hotmail.com - 6777-8888"""
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 3)
        self.assertEqual(contacts[0].phone, "+50760001111")
        self.assertEqual(contacts[1].phone, "+50762223344")
        self.assertEqual(contacts[2].phone, "+50767778888")

    def test_telefono_invalido_marcado(self):
        """Un teléfono con formato no panameño se marca para revisión."""
        texto = """Pedro Gómez
pedro@email.com
123-4567"""
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].status, ContactStatus.REVISAR_TELEFONO)

    def test_informacion_incompleta(self):
        """Falta el teléfono: el contacto queda incompleto."""
        texto = "Ana Torres\nana@email.com"
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].status, ContactStatus.INCOMPLETO)

    def test_ignora_lineas_irrelevantes(self):
        """Textos sueltos antes del primer contacto no crean registros."""
        texto = """Contactos de la empresa
Juan Pérez
6000-1111
juan@email.com"""
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].name, "Juan Pérez")

    def test_orden_campos_no_importa(self):
        """El nombre puede ir después del teléfono y el correo."""
        texto = """6673-2629
pangelica_27@hotmail.com
Patricia Guevara"""
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 1)
        c = contacts[0]
        self.assertEqual(c.name, "Patricia Guevara")
        self.assertEqual(c.phone, "+50766732629")
        self.assertEqual(c.status, ContactStatus.VALIDO)

    def test_nombres_sin_datos_no_rompen_siguiente(self):
        """Un nombre aislado al final queda como registro incompleto."""
        texto = """María López | 6222-3344 | maria@gmail.com

Pedro Solís"""
        contacts = self.parser.parse(texto)
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].status, ContactStatus.VALIDO)
        self.assertEqual(contacts[1].status, ContactStatus.INCOMPLETO)

    def test_texto_vacio(self):
        self.assertEqual(self.parser.parse(""), [])


if __name__ == "__main__":
    unittest.main()
