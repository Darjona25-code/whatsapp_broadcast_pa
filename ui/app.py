"""Ventana principal de la aplicación de listas de difusión."""

from __future__ import annotations

import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.exporter import export_csv, export_xlsx
from core.models import Contact, ContactStatus
from core.parser import ContactParser
from core.persistence import StateStore
from core.report import ReportGenerator

from .widgets import ResultTable

APP_TITLE = "WhatsApp Business PA — Listas de Difusión"


class WhatsAppBroadcastApp(ctk.CTk):
    """Aplicación de escritorio para generar listas de difusión."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1120x840")
        self.minsize(920, 700)

        # Servicios de la lógica de negocio.
        self.parser = ContactParser()
        self.reporter = ReportGenerator()
        self.store = StateStore()
        self.contacts: list[Contact] = []

        self._configure_theme()
        self._build_layout()
        self._restore_state()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _configure_theme(self) -> None:
        """Define la paleta de colores de la interfaz."""
        self.colors = {
            "table_bg": "#1E293B",
            "table_fg": "#E2E8F0",
            "heading_bg": "#334155",
            "heading_fg": "#F1F5F9",
            "border": "#0F172A",
            "accent": "#2563EB",
        }

    def _build_layout(self) -> None:
        """Crea todos los widgets de la ventana."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_input_area()
        self._build_action_bar()
        self._build_table_area()
        self._build_output_areas()
        self._build_status_bar()

    def _build_input_area(self) -> None:
        """Área grande donde el usuario pega el texto copiado."""
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="nsew")
        input_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            input_frame,
            text="Pega aquí el texto copiado desde la página web",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.input_text = ctk.CTkTextbox(
            input_frame, height=170, wrap="word", font=ctk.CTkFont(size=12)
        )
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def _build_action_bar(self) -> None:
        """Botones de acción y contador de registros."""
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=1, column=0, padx=14, pady=6, sticky="ew")
        actions.grid_columnconfigure(6, weight=1)

        buttons = [
            ("Procesar", self._procesar, "#2563EB", "#3B82F6"),
            ("Limpiar", self._limpiar, "#475569", "#64748B"),
            ("Copiar lista WhatsApp", self._copiar_broadcast, "#0E7A5F", "#12A37F"),
            ("Copiar reporte completo", self._copiar_reporte, "#0E7A5F", "#12A37F"),
            ("Exportar CSV", lambda: self._exportar("csv"), "#334155", "#475569"),
            ("Exportar Excel", lambda: self._exportar("xlsx"), "#334155", "#475569"),
        ]
        for col, (text, command, fg, hover) in enumerate(buttons):
            ctk.CTkButton(
                actions, text=text, command=command, fg_color=fg, hover_color=hover
            ).grid(row=0, column=col, padx=(0, 8))

        self.lbl_count = ctk.CTkLabel(
            actions,
            text="Registros encontrados: 0",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.lbl_count.grid(row=1, column=0, columnspan=6, sticky="w", pady=(6, 2))

    def _build_table_area(self) -> None:
        """Tabla de resultados procesados."""
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, padx=14, pady=6, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.table = ResultTable(table_frame, self.colors)
        self.table.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _build_output_areas(self) -> None:
        """Lista para Broadcast y reporte completo, con su botón de copia."""
        outputs = ctk.CTkFrame(self)
        outputs.grid(row=3, column=0, padx=14, pady=(6, 8), sticky="nsew")
        outputs.grid_columnconfigure(0, weight=1, uniform="outs")
        outputs.grid_columnconfigure(1, weight=1, uniform="outs")

        self.broadcast_text = self._build_output_panel(
            outputs, 0, "Lista para Broadcast", self._copiar_broadcast
        )
        self.report_text = self._build_output_panel(
            outputs, 1, "Reporte completo", self._copiar_reporte
        )

    def _build_output_panel(self, parent, column: int, title: str, copy_cmd):
        """Crea un panel de salida con encabezado, texto y botón Copiar."""
        panel = ctk.CTkFrame(parent)
        panel.grid(row=0, column=column, sticky="nsew", padx=(0, 6) if column == 0 else (6, 0))
        panel.grid_columnconfigure(0, weight=1)

        head = ctk.CTkFrame(panel, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
        ctk.CTkLabel(head, text=title, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        ctk.CTkButton(head, text="Copiar", width=70, command=copy_cmd).pack(side="right")

        textbox = ctk.CTkTextbox(panel, height=130, wrap="none", font=ctk.CTkFont(size=12))
        textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        return textbox

    def _build_status_bar(self) -> None:
        """Barra de estado inferior con mensajes para el usuario."""
        self.lbl_status = ctk.CTkLabel(
            self, text="Listo", anchor="w", font=ctk.CTkFont(size=12)
        )
        self.lbl_status.grid(row=4, column=0, padx=16, pady=(0, 10), sticky="ew")

    # ------------------------------------------------------------------
    # Acciones del usuario
    # ------------------------------------------------------------------
    def _procesar(self) -> None:
        """Analiza el texto pegado y actualiza todos los resultados."""
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Sin datos", "Pega primero el texto a procesar.")
            return

        try:
            self.contacts = self.parser.parse(text)
        except Exception as exc:  # noqa: BLE001 - nunca permitir un crash
            messagebox.showerror("Error", f"No se pudo procesar el texto:\n{exc}")
            return

        self.table.set_contacts(self.contacts)
        self._refresh_outputs()
        self._set_status(f"Procesados {len(self.contacts)} registros.")
        self.store.save(text, self.contacts)

    def _limpiar(self) -> None:
        """Vacía la entrada, la tabla y los reportes."""
        self.contacts = []
        self.input_text.delete("1.0", "end")
        self.table.set_contacts([])
        self._set_text(self.broadcast_text, "")
        self._set_text(self.report_text, "")
        self.lbl_count.configure(text="Registros encontrados: 0")
        self._set_status("Contenido limpiado.")

    def _refresh_outputs(self) -> None:
        """Actualiza el contador y los dos reportes de salida."""
        validos = sum(1 for c in self.contacts if c.status is ContactStatus.VALIDO)
        revisar = sum(1 for c in self.contacts if c.status is ContactStatus.REVISAR_TELEFONO)
        incompletos = sum(1 for c in self.contacts if c.status is ContactStatus.INCOMPLETO)
        self.lbl_count.configure(
            text=(
                f"Registros encontrados: {len(self.contacts)}  ·  "
                f"Válidos: {validos}  ·  Revisar: {revisar}  ·  "
                f"Incompletos: {incompletos}"
            )
        )

        self._set_text(self.broadcast_text, self.reporter.build_broadcast_list(self.contacts))
        self._set_text(self.report_text, self.reporter.build_full_report(self.contacts))

    def _copiar_broadcast(self) -> None:
        """Copia la lista de teléfonos para broadcast al portapapeles."""
        content = self.reporter.build_broadcast_list(self.contacts)
        if not content:
            self._set_status("No hay teléfonos que copiar.")
            return
        self._copy_clipboard(content)
        self._set_status("Lista para Broadcast copiada al portapapeles.")

    def _copiar_reporte(self) -> None:
        """Copia el reporte completo (Nombre | Teléfono | Correo)."""
        content = self.reporter.build_full_report(self.contacts)
        if not content:
            self._set_status("No hay reporte que copiar.")
            return
        self._copy_clipboard(content)
        self._set_status("Reporte completo copiado al portapapeles.")

    def _exportar(self, kind: str) -> None:
        """Exporta los resultados a CSV o Excel según el tipo."""
        if not self.contacts:
            messagebox.showinfo("Sin datos", "No hay resultados para exportar.")
            return

        extension = "csv" if kind == "csv" else "xlsx"
        filetypes = (
            [("CSV (compatible con Excel)", "*.csv")]
            if kind == "csv"
            else [("Excel", "*.xlsx")]
        )
        path = filedialog.asksaveasfilename(
            defaultextension=f".{extension}",
            initialfile=f"contactos_whatsapp.{extension}",
            filetypes=filetypes,
        )
        if not path:
            return

        try:
            if kind == "csv":
                export_csv(path, self.contacts)
            else:
                export_xlsx(path, self.contacts)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error de exportación", f"No se pudo exportar:\n{exc}")
            return

        self._set_status(f"Archivo exportado: {Path(path).name}")

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def _restore_state(self) -> None:
        """Restaura el texto y resultados de la última sesión, si existen."""
        text, contacts = self.store.load()
        if text:
            self._set_text(self.input_text, text)
        if contacts:
            self.contacts = contacts
            self.table.set_contacts(contacts)
            self._refresh_outputs()
            self._set_status(f"Última sesión restaurada ({len(contacts)} registros).")

    def _on_close(self) -> None:
        """Guarda el estado actual antes de cerrar la aplicación."""
        try:
            text = self.input_text.get("1.0", "end").strip()
            self.store.save(text, self.contacts)
        except Exception:  # noqa: BLE001
            pass
        self.destroy()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _copy_clipboard(self, content: str) -> None:
        """Copia texto al portapapeles con respaldo en clip.exe de Windows."""
        try:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
        except tk.TclError:
            subprocess.run(["clip.exe"], input=content.encode("utf-16le"), check=True)

    @staticmethod
    def _set_text(textbox, content: str) -> None:
        """Reemplaza el contenido completo de un CTkTextbox."""
        textbox.delete("1.0", "end")
        textbox.insert("1.0", content)

    def _set_status(self, message: str) -> None:
        """Muestra un mensaje en la barra de estado."""
        self.lbl_status.configure(text=message)
