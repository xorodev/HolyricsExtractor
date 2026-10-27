# HolyricsExtractor: A lightweight tool to search, extract, and format song lyrics for Holyrics.
# Copyright (C) 2026 @xorodev (CipherCoreDev)

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

# Third-Party Dependencies & Credits:
# - Built with Python (https://www.python.org/)
# - Metadata extraction powered by yt-dlp (https://github.com/yt-dlp/yt-dlp)
# - HTTP requests powered by Requests (https://requests.readthedocs.io)
# - Lyrics API provided by LRCLIB (https://lrclib.net)
# - Graphic Assets & Icons: Created from scratch by @xorodev

# GitHub: https://github.com/xorodev/HolyricsExtractor
# Contact:
# a. Email: corex.dev@proton.me
# b. Telegram: https://t.me/xorodev
from __future__ import annotations
import tkinter as tk
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from ..constants import (
    APP_NAME,
    APP_VERSION,
    MAX_SUPPORT_MESSAGE_LENGTH,
    SUPPORT_EMAIL,
    SUPPORT_WHATSAPP_DISPLAY,
)
from ..core.errors import ErrorReport
from ..core.sanitizer import sanitize_multiline, sanitize_single_line
from ..core.settings import SettingsStore
from ..services.support import build_mailto_url, build_report_text, build_whatsapp_url
from .animation.transitions import WindowFade
from .shortcuts import MODIFIER_LABEL, Shortcut
from .theme import ThemeManager
from .widgets import (
    ThemedButton,
    ThemedCheckbutton,
    ThemedFrame,
    ThemedLabel,
    apply_window_icon,
    mono_font,
    ui_font,
)

KIND_GLYPHS = {
    "info": ("ⓘ", "accent"),
    "success": ("✔", "success"),
    "warning": ("⚠", "warning"),
    "error": ("✖", "danger"),
    "question": ("?", "accent"),
}

DETAIL_PREVIEW_LENGTH = 300
VERSION_REFRESH_MS = 400
VERSION_PENDING_TEXT = "Consultando..."

@dataclass(frozen=True, slots=True)

class DialogButton:
    label: str
    value: str
    variant: str = "primary"

class ModalDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, theme: ThemeManager, title: str):
        super().__init__(parent)
        self.withdraw()
        self.theme = theme
        self._parent = parent
        self._previous_grab: tk.Misc | None = None
        self._fade = WindowFade(self, theme.motion)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        apply_window_icon(self)
        theme.track_window(self, "panel_bg")
        self.bind("<Escape>", lambda _event: self.close())
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        self.destroy()

    def destroy(self) -> None:
        previous = self._previous_grab
        self._fade.cancel()
        super().destroy()
        if previous is not None:
            try:
                if previous.winfo_exists():
                    previous.grab_set()
            except tk.TclError:
                pass

    def present(self) -> None:
        self.update_idletasks()
        width, height = self.winfo_reqwidth(), self.winfo_reqheight()
        parent = self._parent.winfo_toplevel()
        x = max(parent.winfo_rootx() + (parent.winfo_width() - width) // 2, 0)
        y = max(parent.winfo_rooty() + (parent.winfo_height() - height) // 2, 0)
        self.geometry(f"+{x}+{y}")
        self._fade.prepare()
        self.deiconify()
        self.wait_visibility()
        self._previous_grab = self.grab_current()
        self.grab_set()
        self.focus_set()
        self._fade.play()

class MessageDialog(ModalDialog):
    WRAP_LENGTH = 420

    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        title: str,
        message: str,
        kind: str,
        buttons: list[DialogButton],
        detail: str | None = None,
    ):
        super().__init__(parent, theme, title)
        self.result = buttons[-1].value
        glyph, glyph_role = KIND_GLYPHS[kind]

        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(22, 12))

        ThemedLabel(body, theme, glyph, role=glyph_role, font=ui_font(26, "bold")).grid(
            row=0, column=0, rowspan=2, sticky="n", padx=(0, 16)
        )
        ThemedLabel(
            body, theme, message, font=ui_font(10), wraplength=self.WRAP_LENGTH, justify="left"
        ).grid(row=0, column=1, sticky="w")
        if detail:
            ThemedLabel(
                body,
                theme,
                detail,
                role="text_muted",
                font=mono_font(9),
                wraplength=self.WRAP_LENGTH,
                justify="left",
            ).grid(row=1, column=1, sticky="w", pady=(12, 0))

        footer = ThemedFrame(self, theme)
        footer.pack(fill="x", padx=24, pady=(8, 20))
        for button in reversed(buttons):
            ThemedButton(
                footer, theme, button.label, lambda value=button.value: self._choose(value), variant=button.variant
            ).pack(side="right", padx=(8, 0))

        self.bind("<Return>", lambda _event: self._choose(buttons[0].value))
        self.present()

    def _choose(self, value: str) -> None:
        self.result = value
        self.destroy()

def show_message(
    parent: tk.Misc, theme: ThemeManager, title: str, message: str, kind: str = "info", detail: str | None = None
) -> None:
    dialog = MessageDialog(parent, theme, title, message, kind, [DialogButton("Aceptar", "ok")], detail)
    parent.wait_window(dialog)

def ask_choice(
    parent: tk.Misc, theme: ThemeManager, title: str, message: str, kind: str, buttons: list[DialogButton]
) -> str:
    dialog = MessageDialog(parent, theme, title, message, kind, buttons)
    parent.wait_window(dialog)
    return dialog.result

def ask_yes_no(parent: tk.Misc, theme: ThemeManager, title: str, message: str) -> bool:
    dialog = MessageDialog(
        parent,
        theme,
        title,
        message,
        "question",
        [DialogButton("Sí", "yes"), DialogButton("No", "no", "neutral")],
    )
    parent.wait_window(dialog)
    return dialog.result == "yes"

def show_error(
    parent: tk.Misc,
    theme: ThemeManager,
    title: str,
    report: ErrorReport,
    kind: str,
    on_report: Callable[[], None] | None,
) -> None:
    detail_lines = [f"Código de error: {report.code}"]
    if kind == "error" and report.detail:
        detail_lines.append(f"Detalles técnicos: {sanitize_single_line(report.detail, DETAIL_PREVIEW_LENGTH)}")
    buttons = [DialogButton("Cerrar", "close", "neutral")]
    if on_report is not None:
        buttons.insert(0, DialogButton("¡Reportar al desarrollador!", "report"))
    dialog = MessageDialog(parent, theme, title, report.message, kind, buttons, "\n".join(detail_lines))
    parent.wait_window(dialog)
    if dialog.result == "report" and on_report is not None:
        on_report()

class AboutDialog(ModalDialog):
    LINKS = (
        ("Licencia:", "Clic aquí.", "https://www.gnu.org/licenses/gpl-3.0.txt"),
        ("GitHub:", "Clic aquí.", "https://github.com/xorodev"),
        ("Telegram:", "Clic aquí.", "https://t.me/xorodev"),
        ("Instagram:", "Clic aquí.", "https://instagram.com/xorodev"),
        ("Gmail:", "wilfredorb0218@gmail.com", "mailto:wilfredorb0218@gmail.com"),
        ("Hotmail:", "wilfredorb.dev@hotmail.com", "mailto:wilfredorb.dev@hotmail.com"),
    )

    def __init__(self, parent: tk.Misc, theme: ThemeManager):
        super().__init__(parent, theme, "Acerca del software")
        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=28, pady=(22, 24))

        ThemedLabel(body, theme, f"♪ {APP_NAME}", role="title", font=ui_font(14, "bold")).pack(pady=(0, 6))
        ThemedLabel(
            body,
            theme,
            f"Licencia: GNU GPLv3.0\nVersión actual: '{APP_VERSION}'\nCreated by: @xorodev (CipherCoreDev)",
            role="text_muted",
            font=ui_font(10, "italic"),
        ).pack(pady=(0, 14))
        ThemedLabel(
            body,
            theme,
            "Herramienta diseñada para extraer y formatear automáticamente\n"
            "letras de canciones para el software de Holyrics.",
            font=ui_font(9),
            justify="center",
        ).pack(pady=(0, 16))

        contact = tk.LabelFrame(
            body, text=" Licencia y Contacto del Desarrollador ", font=ui_font(10, "bold"), padx=16, pady=12, bd=1
        )
        theme.register(contact, bg="panel_bg", fg="accent")
        contact.pack(fill="x")
        for label, link_text, url in self.LINKS:
            self._add_link_row(contact, label, link_text, url)
        self.present()

    def _add_link_row(self, parent: tk.Misc, label: str, link_text: str, url: str) -> None:
        row = ThemedFrame(parent, self.theme)
        row.pack(fill="x", pady=4)
        ThemedLabel(row, self.theme, label, font=ui_font(9, "bold"), width=10, anchor="w").pack(side="left")
        link = ThemedLabel(row, self.theme, link_text, role="link", font=ui_font(9, "underline"), cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda _event: webbrowser.open_new_tab(url))
        link.bind("<Enter>", lambda _event: link.set_role("link_hover"))
        link.bind("<Leave>", lambda _event: link.set_role("link"))

class SettingsDialog(ModalDialog):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        settings: SettingsStore,
        log_path: Path,
        ytdlp_version: Callable[[], str],
        on_ytdlp_update: Callable[[], None],
        on_app_update: Callable[[], None],
    ):
        super().__init__(parent, theme, "Ajustes del programa")
        self._settings = settings
        self._ytdlp_version = ytdlp_version
        self._notify_ytdlp = tk.BooleanVar(master=self, value=settings.get("check_yt_dlp_updates"))
        self._notify_app = tk.BooleanVar(master=self, value=settings.get("check_app_updates"))

        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(18, 10))
        ThemedLabel(body, theme, "⚙ Configuración y opciones", role="title", font=ui_font(12, "bold")).pack(
            pady=(0, 12)
        )

        self._version_label = self._build_section(
            body,
            "Componente yt-dlp",
            self._ytdlp_version(),
            self._notify_ytdlp,
            lambda: settings.set("check_yt_dlp_updates", self._notify_ytdlp.get()),
            "↻ Buscar y actualizar yt-dlp",
            "primary",
            lambda: self._launch(on_ytdlp_update),
        )
        self._build_section(
            body,
            "Aplicación",
            APP_VERSION,
            self._notify_app,
            lambda: settings.set("check_app_updates", self._notify_app.get()),
            "↻ Buscar actualizaciones de la aplicación",
            "success",
            lambda: self._launch(on_app_update),
        )

        ThemedLabel(
            body,
            theme,
            f"Los registros de la aplicación se guardan en:\n'{log_path}'",
            role="text_faint",
            font=ui_font(8),
            wraplength=420,
            justify="center",
        ).pack(pady=(4, 0))
        self.present()
        self.after(VERSION_REFRESH_MS, self._refresh_version)

    def _build_section(
        self,
        parent: tk.Misc,
        title: str,
        version: str,
        variable: tk.BooleanVar,
        on_toggle: Callable[[], None],
        button_text: str,
        variant: str,
        on_click: Callable[[], None],
    ) -> ThemedLabel:
        frame = tk.LabelFrame(parent, text=f" {title} ", font=ui_font(9, "bold"), padx=16, pady=12, bd=1)
        self.theme.register(frame, bg="panel_bg", fg="accent")
        frame.pack(fill="x", pady=(0, 14))
        version_label = ThemedLabel(
            frame, self.theme, f"Versión actual: '{version}'", role="text_muted", font=ui_font(9, "italic")
        )
        version_label.pack(anchor="w", pady=(0, 10))
        ThemedCheckbutton(
            frame, self.theme, "Recibir notificaciones automáticas de nuevas versiones", variable, on_toggle, wraplength=400
        ).pack(anchor="w", pady=(0, 10))
        ThemedButton(frame, self.theme, button_text, on_click, variant=variant).pack(fill="x")
        return version_label

    def _refresh_version(self) -> None:
        if not self.winfo_exists():
            return
        version = self._ytdlp_version()
        self._version_label.configure(text=f"Versión actual: '{version}'")
        if version == VERSION_PENDING_TEXT:
            self.after(VERSION_REFRESH_MS, self._refresh_version)

    def _launch(self, action: Callable[[], None]) -> None:
        self.destroy()
        action()

class SupportDialog(ModalDialog):
    def __init__(self, parent: tk.Misc, theme: ThemeManager, last_error: ErrorReport | None):
        super().__init__(parent, theme, "Ayuda y Soporte")
        self._error = last_error
        self._include_error = tk.BooleanVar(master=self, value=last_error is not None)
        self._include_system = tk.BooleanVar(master=self, value=True)

        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(18, 8))

        ThemedLabel(body, theme, "¿Necesita ayuda?", role="title", font=ui_font(14, "bold")).pack()
        ThemedLabel(
            body,
            theme,
            "Describa el problema o su duda. El mensaje se enviará directamente al desarrollador por el canal que usted elija.",
            role="text_muted",
            font=ui_font(9),
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(4, 10))

        self._message = tk.Text(
            body, width=56, height=6, wrap="word", font=ui_font(10), relief="flat", bd=0, padx=8, pady=8
        )
        theme.register(
            self._message,
            bg="field_bg",
            fg="text",
            insertbackground="text",
            selectbackground="accent",
            selectforeground="accent_text",
        )
        self._message.pack(fill="x")
        self._message.bind("<KeyRelease>", lambda _event: self._update_counter())
        self._counter = ThemedLabel(body, theme, "", role="text_faint", font=ui_font(8), anchor="e")
        self._counter.pack(fill="x", pady=(2, 8))
        self._update_counter()

        if last_error is not None:
            ThemedCheckbutton(
                body,
                theme,
                f"Incluir el último error detectado (código: {last_error.code})",
                self._include_error,
                wraplength=460,
            ).pack(anchor="w")
        ThemedCheckbutton(
            body,
            theme,
            "Incluir la versión de la aplicación y del sistema operativo",
            self._include_system,
            wraplength=460,
        ).pack(anchor="w", pady=(2, 10))

        actions = ThemedFrame(body, theme)
        actions.pack(fill="x")
        actions.columnconfigure((0, 1), weight=1)
        ThemedButton(actions, theme, "WhatsApp", self._send_whatsapp, variant="success").grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ThemedButton(actions, theme, "Correo electrónico", self._send_email).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )
        ThemedButton(actions, theme, "¡Copiar reporte al portapapeles!", self._copy_report, variant="neutral").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )

        self._feedback = ThemedLabel(
            body, theme, "", role="text_muted", font=ui_font(9), wraplength=460, justify="left", anchor="w"
        )
        self._feedback.pack(fill="x", pady=(10, 0))
        ThemedLabel(
            body,
            theme,
            f"WhatsApp: {SUPPORT_WHATSAPP_DISPLAY}  ·  Correo: {SUPPORT_EMAIL}",
            role="text_faint",
            font=ui_font(8),
        ).pack(pady=(6, 14))
        self.present()
        self._message.focus_set()

    def _sanitized_text(self) -> str:
        return sanitize_multiline(self._message.get("1.0", "end-1c"), MAX_SUPPORT_MESSAGE_LENGTH * 4)

    def _update_counter(self) -> None:
        length = len(self._sanitized_text())
        self._counter.configure(text=f"{length}/{MAX_SUPPORT_MESSAGE_LENGTH}")
        self._counter.set_role("danger" if length > MAX_SUPPORT_MESSAGE_LENGTH else "text_faint")

    def _set_feedback(self, text: str, role: str) -> None:
        self._feedback.configure(text=text)
        self._feedback.set_role(role)

    def _build_report(self) -> str | None:
        text = self._sanitized_text()
        include_error = self._error is not None and self._include_error.get()
        if len(text) > MAX_SUPPORT_MESSAGE_LENGTH:
            self._set_feedback(f"El mensaje supera el máximo de {MAX_SUPPORT_MESSAGE_LENGTH} caracteres.", "danger")
            return None
        if not text and not include_error:
            self._set_feedback("Describa brevemente el problema antes de enviar el mensaje.", "warning")
            self._message.focus_set()
            return None
        return build_report_text(text, self._error if include_error else None, self._include_system.get())

    def _selected_error(self) -> ErrorReport | None:
        return self._error if self._error is not None and self._include_error.get() else None

    def _open_link(self, url: str, success_text: str) -> None:
        if webbrowser.open(url):
            self._set_feedback(success_text, "success")
        else:
            self._set_feedback(
                "No fue posible abrir la aplicación. Utilice el botón: 'Copiar reporte al portapapeles' y envíelo manualmente.", "danger"
            )

    def _send_whatsapp(self) -> None:
        report = self._build_report()
        if report is not None:
            self._open_link(build_whatsapp_url(report), "Abriendo WhatsApp con su mensaje listo para enviar...")

    def _send_email(self) -> None:
        report = self._build_report()
        if report is not None:
            self._open_link(
                build_mailto_url(report, self._selected_error()), "Abriendo su aplicación de correo electrónico..."
            )

    def _copy_report(self) -> None:
        report = self._build_report()
        if report is None:
            return
        self.clipboard_clear()
        self.clipboard_append(report)
        self._set_feedback("¡El reporte fue copiado al portapapeles!", "success")

class ShortcutsDialog(ModalDialog):
    def __init__(self, parent: tk.Misc, theme: ThemeManager, shortcuts: tuple[Shortcut, ...]):
        super().__init__(parent, theme, "Atajos de teclado")
        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(18, 20))

        ThemedLabel(body, theme, "Atajos de teclado", role="title", font=ui_font(14, "bold")).pack()
        ThemedLabel(
            body,
            theme,
            f"En este equipo la tecla principal es '{MODIFIER_LABEL}'. "
            "Los atajos funcionan con la tecla 'Bloq Mayús' activado o desactivado.",
            role="text_muted",
            font=ui_font(9),
            wraplength=480,
            justify="center",
        ).pack(pady=(4, 14))

        table = ThemedFrame(body, theme)
        table.pack(fill="x")
        table.columnconfigure(1, weight=1)
        for row, shortcut in enumerate(shortcuts):
            self._add_keys(table, row, shortcut.label_parts)
            ThemedLabel(
                table, theme, shortcut.description, font=ui_font(10), wraplength=340, justify="left", anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=(18, 0), pady=6)

        ThemedButton(body, theme, "Cerrar", self.close, variant="neutral").pack(pady=(16, 0))
        self.present()

    def _add_keys(self, table: tk.Misc, row: int, parts: tuple[str, ...]) -> None:
        keys = ThemedFrame(table, self.theme)
        keys.grid(row=row, column=0, sticky="w", pady=6)
        for index, part in enumerate(parts):
            if index:
                ThemedLabel(keys, self.theme, "+", role="text_faint", font=ui_font(9, "bold")).pack(side="left", padx=4)
            border = ThemedFrame(keys, self.theme, surface="border", padx=1, pady=1)
            border.pack(side="left")
            ThemedLabel(
                border, self.theme, part, surface="field_bg", font=mono_font(9, "bold"), padx=8, pady=3
            ).pack()