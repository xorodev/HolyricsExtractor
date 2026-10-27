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
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Callable
from ..core.errors import AppError
from ..core.protected_files import FileState, ProtectedFiles
from .dialogs import ModalDialog, ask_yes_no
from .theme import ThemeManager
from .widgets import ThemedButton, ThemedFrame, ThemedLabel, mono_font, ui_font

UNLOCK_KEYWORD = "UNLOCK"
DELETE_KEYWORD = "RESET"
WRAP_LENGTH = 380
BUSY_MESSAGE = "¡Espere a que finalice la operación en curso antes de modificar archivos protegidos!"

STATE_PRESENTATION = {
    FileState.PROTECTED: ("Protegido (solo lectura)", "success"),
    FileState.UNLOCKED: ("Desbloqueado (vuelva a protegerlo al terminar)", "warning"),
    FileState.MODIFIED: ("¡Modificado fuera de la aplicación!", "danger"),
    FileState.MISSING: ("Aún no existe, la aplicación lo creará cuando lo necesite...", "text_muted"),
}

@dataclass(frozen=True, slots=True)
class ManagedFile:
    label: str
    description: str
    path: Path
    reset_label: str
    on_reset: Callable[[], None]
    hashed: bool
    validator: Callable[[Path], bool] | None = None

class ConfirmDangerDialog(ModalDialog):
    def __init__(
        self, parent: tk.Misc, theme: ThemeManager, title: str, message: str, keyword: str, confirm_label: str
    ):
        super().__init__(parent, theme, title)
        self.confirmed = False
        self._keyword = keyword
        self._typed = tk.StringVar(master=self)

        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(22, 12))
        body.columnconfigure(1, weight=1)
        ThemedLabel(body, theme, "⚠", role="warning", font=ui_font(26, "bold")).grid(
            row=0, column=0, rowspan=3, sticky="n", padx=(0, 16)
        )
        ThemedLabel(body, theme, message, wraplength=WRAP_LENGTH, justify="left").grid(row=0, column=1, sticky="w")
        ThemedLabel(
            body,
            theme,
            f"Para continuar, escriba: '{keyword}', en el siguiente recuadro:",
            role="text_muted",
            font=ui_font(9),
            wraplength=WRAP_LENGTH,
            justify="left",
        ).grid(row=1, column=1, sticky="w", pady=(12, 4))
        entry = ttk.Entry(body, textvariable=self._typed, font=ui_font(10))
        entry.grid(row=2, column=1, sticky="ew")

        footer = ThemedFrame(self, theme)
        footer.pack(fill="x", padx=24, pady=(8, 20))
        self._confirm_button = ThemedButton(footer, theme, confirm_label, self._confirm, variant="danger")
        self._confirm_button.pack(side="right", padx=(8, 0))
        self._confirm_button.set_enabled(False)
        ThemedButton(footer, theme, "Cancelar", self.close, variant="neutral").pack(side="right")

        self._typed.trace_add("write", lambda *_args: self._refresh_confirm())
        entry.bind("<Return>", lambda _event: self._confirm())
        self.present()
        entry.focus_set()

    def _refresh_confirm(self) -> None:
        self._confirm_button.set_enabled(self._typed.get().strip() == self._keyword)

    def _confirm(self) -> None:
        if self._typed.get().strip() == self._keyword:
            self.confirmed = True
            self.destroy()

def ask_danger(
    parent: tk.Misc, theme: ThemeManager, title: str, message: str, keyword: str, confirm_label: str
) -> bool:
    dialog = ConfirmDangerDialog(parent, theme, title, message, keyword, confirm_label)
    parent.wait_window(dialog)
    return dialog.confirmed

class ProtectedFilesDialog(ModalDialog):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        files: ProtectedFiles,
        managed_files: list[ManagedFile],
        is_busy: Callable[[], bool],
    ):
        super().__init__(parent, theme, "Archivos protegidos")
        self._files = files
        self._managed_files = managed_files
        self._is_busy = is_busy

        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(18, 18))
        ThemedLabel(body, theme, "Avanzado", role="title", font=ui_font(14, "bold")).pack()
        ThemedLabel(
            body,
            theme,
            "Estos archivos son esenciales para el software. Permanecen en solo lectura y la aplicación detecta "
            "sí alguien los altera o los elimina. Desde aquí puede desbloquearlos, restablecerlos o eliminarlos "
            "de forma permanente, siempre con confirmación.",
            role="text_muted",
            font=ui_font(9),
            wraplength=560,
            justify="center",
        ).pack(pady=(4, 14))

        self._rows = ThemedFrame(body, theme)
        self._rows.pack(fill="x")
        self._feedback = ThemedLabel(
            body, theme, "", role="text_muted", font=ui_font(9), wraplength=560, justify="left", anchor="w"
        )
        self._feedback.pack(fill="x", pady=(4, 10))
        ThemedButton(body, theme, "Cerrar", self.close, variant="neutral").pack()

        self._render()
        self.present()

    def _render(self) -> None:
        for child in self._rows.winfo_children():
            child.destroy()
        for item in self._managed_files:
            self._render_card(item)

    def _render_card(self, item: ManagedFile) -> None:
        theme = self.theme
        state = self._files.state(item.path, item.hashed)
        status_text, status_role = STATE_PRESENTATION[state]

        card = ThemedFrame(self._rows, theme, surface="field_bg", padx=14, pady=10)
        card.pack(fill="x", pady=(0, 10))
        card.columnconfigure(0, weight=1)

        info = ThemedFrame(card, theme, surface="field_bg")
        info.grid(row=0, column=0, sticky="w")
        ThemedLabel(info, theme, item.label, surface="field_bg", font=ui_font(10, "bold")).pack(anchor="w")
        ThemedLabel(
            info, theme, item.description, surface="field_bg", role="text_muted", font=ui_font(9),
            wraplength=WRAP_LENGTH, justify="left",
        ).pack(anchor="w")
        ThemedLabel(
            info, theme, str(item.path), surface="field_bg", role="text_faint", font=mono_font(8),
            wraplength=WRAP_LENGTH, justify="left",
        ).pack(anchor="w", pady=(2, 0))
        ThemedLabel(
            info, theme, f"Estado: {status_text}", surface="field_bg", role=status_role, font=ui_font(9, "bold"),
            wraplength=WRAP_LENGTH, justify="left",
        ).pack(anchor="w", pady=(4, 0))

        if state is FileState.MISSING:
            return
        actions = ThemedFrame(card, theme, surface="field_bg")
        actions.grid(row=0, column=1, sticky="e", padx=(14, 0))
        if state is FileState.PROTECTED:
            primary = ("Desbloquear", "neutral", lambda: self._unlock(item))
        elif state is FileState.UNLOCKED:
            primary = ("Proteger de nuevo", "success", lambda: self._protect(item))
        else:
            primary = ("Aceptar cambios", "neutral", lambda: self._accept(item))
        for label, variant, command in (primary, (item.reset_label, "danger", lambda: self._reset(item))):
            ThemedButton(actions, theme, label, command, variant=variant, font=ui_font(9, "bold"), pady=5).pack(
                fill="x", pady=2
            )

    def _say(self, text: str, role: str) -> None:
        self._feedback.configure(text=text)
        self._feedback.set_role(role)

    def _blocked_by_operation(self) -> bool:
        if self._is_busy():
            self._say(BUSY_MESSAGE, "warning")
            return True
        return False

    def _run(self, action: Callable[[], None], success_text: str, success_role: str) -> None:
        try:
            action()
        except AppError as error:
            self._say(error.user_message, "danger")
        except OSError as error:
            self._say(f"No fue posible completar la acción: {error}", "danger")
        else:
            self._say(success_text, success_role)
        self._render()

    def _unlock(self, item: ManagedFile) -> None:
        if self._blocked_by_operation():
            return
        confirmed = ask_danger(
            self,
            self.theme,
            "Desbloquear archivo protegido",
            f"Va a desbloquear «{item.label}». Mientras esté desbloqueado, cualquier programa o persona podrá "
            "modificarlo o eliminarlo, y un cambio incorrecto puede impedir que la aplicación funcione correctamente. "
            "¡Vuelva a protegerlo cuando termine!",
            UNLOCK_KEYWORD,
            "Desbloquear",
        )
        if confirmed:
            self._run(
                lambda: self._files.unlock(item.path),
                f"«{item.label}», desbloqueado. Vuelva a protegerlo cuando termine de editarlo...",
                "warning",
            )

    def _protect(self, item: ManagedFile) -> None:
        if self._blocked_by_operation():
            return
        if item.validator is not None and not item.validator(item.path):
            self._say(f"El contenido de «{item.label}», no es válido. ¡Restáurelo antes de protegerlo!", "danger")
            return
        self._run(lambda: self._files.accept(item.path, item.hashed), f"«{item.label}», protegido de nuevo.", "success")

    def _accept(self, item: ManagedFile) -> None:
        if self._blocked_by_operation():
            return
        confirmed = ask_yes_no(
            self,
            self.theme,
            "Aceptar cambios",
            f"«{item.label}», fue modificado fuera de la aplicación. ¿Desea aceptar su contenido actual como "
            "válido y volver a protegerlo?",
        )
        if confirmed:
            self._protect(item)

    def _reset(self, item: ManagedFile) -> None:
        if self._blocked_by_operation():
            return
        confirmed = ask_danger(
            self,
            self.theme,
            f"{item.reset_label} archivo protegido",
            f"Va a ejecutar la acción «{item.reset_label}», sobre «{item.label}». Esta acción es permanente y "
            "no se puede deshacer.",
            DELETE_KEYWORD,
            item.reset_label,
        )
        if confirmed:
            self._run(item.on_reset, f"«{item.label}» | Acción ejecutada: «{item.reset_label}», realizada correctamente.", "success")