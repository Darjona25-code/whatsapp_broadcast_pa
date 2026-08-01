"""Widgets personalizados de la interfaz gráfica."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.models import Contact, ContactStatus

# Etiqueta de tag del Treeview y color de texto por estado.
STATUS_TAGS = {
    ContactStatus.VALIDO: ("status_valid", "#2E7D32"),
    ContactStatus.REVISAR_TELEFONO: ("status_review", "#F9A825"),
    ContactStatus.INCOMPLETO: ("status_incomplete", "#C62828"),
}


class ResultTable(tk.Frame):
    """Tabla de resultados basada en ttk.Treeview con estilo oscuro."""

    def __init__(self, master, colors: dict, **kwargs):
        super().__init__(master, bg=colors["table_bg"], **kwargs)

        self._configure_style(colors)

        columns = ("name", "phone", "email", "status")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Result.Treeview",
        )

        headings = {"name": "Nombre", "phone": "Teléfono", "email": "Correo", "status": "Estado"}
        widths = {"name": 220, "phone": 150, "email": 240, "status": 170}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        # Colores de la celda "Estado".
        for status, (tag, color) in STATUS_TAGS.items():
            self.tree.tag_configure(tag, foreground=color, font=("Segoe UI", 10, "bold"))

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _configure_style(self, colors: dict) -> None:
        """Configura un tema oscuro consistente con CustomTkinter."""
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Result.Treeview",
            background=colors["table_bg"],
            fieldbackground=colors["table_bg"],
            foreground=colors["table_fg"],
            rowheight=28,
            bordercolor=colors["border"],
        )
        style.map(
            "Result.Treeview",
            background=[("selected", colors["accent"])],
            foreground=[("selected", colors["table_fg"])],
        )
        style.configure(
            "Result.Treeview.Heading",
            background=colors["heading_bg"],
            foreground=colors["heading_fg"],
            font=("Segoe UI", 10, "bold"),
            padding=(6, 6),
        )
        style.map("Result.Treeview.Heading", background=[("active", colors["heading_bg"])])

    def set_contacts(self, contacts: list[Contact]) -> None:
        """Rellena la tabla con los contactos procesados."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for contact in contacts:
            tag, _ = STATUS_TAGS.get(contact.status, (None, None))
            self.tree.insert(
                "",
                "end",
                values=(contact.name, contact.phone, contact.email, contact.status.value),
                tags=(tag,) if tag else (),
            )
