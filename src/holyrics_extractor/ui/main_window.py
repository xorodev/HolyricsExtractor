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
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Callable
import requests
from ..constants import APP_NAME, MAX_QUERY_LENGTH, USER_AGENT
from ..core.errors import AppError, ErrorReport, StorageError, describe_error
from ..core.history import HistoryEntry, HistoryStore
from ..core.logging_service import configure_logging, get_logger
from ..core.protected_files import ProtectedFiles
from ..core.sanitizer import sanitize_single_line
from ..core.settings import ANIMATION_RESULTS, SettingsStore
from ..core.storage import read_json
from ..core.tasks import Progress, TaskRunner, Work
from ..paths import data_directory
from ..services.app_updater import AppUpdater
from ..services.http import create_session
from ..services.lrclib import LrclibClient
from ..services.lyrics_service import LyricsService
from ..services.models import LyricsResult
from ..services.youtube import YouTubeResolver
from ..services.ytdlp_component import YtDlpComponent
from .animation.animator import Animation
from .animation.colors import blend_colors
from .animation.motion import Motion
from .animation_dialog import AnimationSettingsDialog
from .dialogs import (
    AboutDialog,
    DialogButton,
    SettingsDialog,
    ShortcutsDialog,
    SupportDialog,
    ask_choice,
    ask_yes_no,
    show_error,
    show_message,
)
from .protected_files_dialog import ManagedFile, ProtectedFilesDialog
from .platform_support import maximize_window
from .shortcuts import IS_MAC, Shortcut, bind_shortcuts
from .theme import Palette, ThemeManager
from .update_controller import UpdateController
from .widgets import (
    CircleButton,
    ThemedButton,
    ThemedFrame,
    ThemedLabel,
    ThemedMenuButton,
    Toast,
    Tooltip,
    apply_window_icon,
    create_menu,
    mono_font,
    ui_font,
)

logger = get_logger("app")

STATUS_PREFIX = "Estado de operación: "
STATUS_ROLES = {
    "idle": "text_muted",
    "busy": "accent",
    "success": "success",
    "warning": "warning",
    "error": "danger",
}
PROCESS_BUTTON_TEXT = "🔍 ¡Buscar y Formatear Letra!"
PROCESS_BUTTON_BUSY_TEXT = "⌛ Procesando solicitud, por favor espere..."
PREVIEW_PLACEHOLDER = "Aquí aparecerán los versos generados a partir de la letra..."
IDLE_STATUS = "En espera de una entrada."
HISTORY_LABEL_LENGTH = 60
TICK_INTERVAL_MS = 500
ELAPSED_VISIBLE_AFTER_SECONDS = 3
RESULT_REVEAL_MS = 260
CLIPBOARD_READ_LIMIT = 2_000
FOCUS_HOLDING_WIDGETS = (tk.Entry, ttk.Entry, tk.Text, tk.Menu)

def slides_text(total: int) -> str:
    return "1 verso" if total == 1 else f"{total} versos"

class HolyricsApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        directory = data_directory()
        self.log_path = configure_logging(directory)
        logger.info("Application initialization started.")

        api_session = create_session(USER_AGENT)
        release_session = create_session(USER_AGENT, accept="application/vnd.github+json")
        self._sessions: tuple[requests.Session, ...] = (api_session, release_session)
        self.files = ProtectedFiles(directory)
        ytdlp = YtDlpComponent(release_session, directory / "bin", self.files)
        self.settings_path = directory / "config.json"
        self.history_path = directory / "history.json"
        self.ytdlp_path = ytdlp.binary_path
        self.integrity_findings = self.files.audit([self.settings_path, self.history_path, self.ytdlp_path])
        self.settings = SettingsStore(self.settings_path, self.files)
        self.history = HistoryStore(self.history_path, self.files)
        self._migrate_legacy_history()
        self.lyrics = LyricsService(YouTubeResolver(api_session, ytdlp), LrclibClient(api_session))

        self.tasks = TaskRunner(self)
        self.current_result: LyricsResult | None = None
        self.last_error: ErrorReport | None = None
        self._busy_started = 0.0
        self._busy_message = ""
        self._progress_determinate = False
        self._tick_job: str | None = None
        self._reporting_error = False
        self._context_menu: tk.Menu | None = None
        self._reveal_animation: Animation | None = None

        self.title(APP_NAME)
        self.geometry("920x740")
        self.minsize(820, 620)
        maximize_window(self)
        apply_window_icon(self)
        self.theme = ThemeManager(self, self.settings.get("theme"), self._handle_theme_changed, Motion(self.settings))
        self.theme.track_window(self, "window_bg")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.updates = UpdateController(self, self, self.settings, ytdlp, AppUpdater(release_session))

        self._build_top_bar()
        self._build_form()
        self._build_actions()
        self._build_preview()
        self._build_overlays()
        self._bind_shortcuts()
        self._refresh_history_menu()
        self._show_placeholder()
        self.set_status(IDLE_STATUS, "idle")

        logger.info("UI rendering completed successfully.")
        self.after(500, self._startup)

    @property
    def is_busy(self) -> bool:
        return self.tasks.is_busy

    def _migrate_legacy_history(self) -> None:
        legacy = self.settings.take_legacy_history()
        if legacy:
            self.history.import_legacy(legacy)
        self.settings.discard_legacy_history()

    def _build_top_bar(self) -> None:
        bar = ThemedFrame(self, self.theme, padx=20, pady=14)
        bar.pack(fill="x", padx=15, pady=(12, 6))
        bar.columnconfigure(0, weight=1)

        heading = ThemedFrame(bar, self.theme)
        heading.grid(row=0, column=0, sticky="w")
        ThemedLabel(heading, self.theme, f"♪ {APP_NAME}", role="title", font=ui_font(16, "bold")).pack(anchor="w")
        ThemedLabel(
            heading,
            self.theme,
            "Ingrese un enlace (URL) de YouTube o el título de la canción para estructurar los versos.",
            font=ui_font(10),
        ).pack(anchor="w", pady=(3, 0))

        controls = ThemedFrame(bar, self.theme)
        controls.grid(row=0, column=1, sticky="e", padx=(16, 0))

        self.history_button = ThemedMenuButton(controls, self.theme, "Historial")
        self.history_button.pack(side="left", padx=(0, 6))

        options_button = ThemedMenuButton(controls, self.theme, "Opciones")
        options_button.pack(side="left", padx=(0, 6))
        options_button.menu.add_command(label="⚙ Ajustes", command=self.open_settings)
        options_button.menu.add_command(label="✦ Animaciones", command=self.open_animation_settings)
        options_button.menu.add_command(label="↻ Actualizar yt-dlp", command=self.updates.update_ytdlp)
        options_button.menu.add_command(label="⌨ Atajos de teclado", command=self.open_shortcuts)
        options_button.menu.add_separator()
        options_button.menu.add_command(label="⊕ Avanzado", command=self.open_protected_files)
        options_button.menu.add_command(label="✖ Salir del programa", command=self.on_close)

        self.theme_button = ThemedButton(
            controls, self.theme, "", self.theme.toggle, variant="neutral", pady=7, padx=12
        )
        self.theme_button.pack(side="left", padx=(0, 6))
        self.theme.track(self.theme_button, self._apply_theme_button_label)

        about_button = CircleButton(
            controls, self.theme, "i", self.open_about, size=34, glyph_size=13, surface="panel_bg", variant="neutral"
        )
        about_button.pack(side="left")
        Tooltip(about_button, self.theme, "Acerca de")

    def _build_form(self) -> None:
        form = ThemedFrame(self, self.theme, padx=20, pady=16)
        form.pack(fill="x", padx=15, pady=5)

        ThemedLabel(form, self.theme, "Enlace de YouTube / Título de la Canción:", font=ui_font(10, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        query_row = ThemedFrame(form, self.theme)
        query_row.pack(fill="x", pady=(0, 12))
        self.entry_query = ttk.Entry(query_row, font=ui_font(10))
        self.entry_query.pack(side="left", fill="x", expand=True)
        self.entry_query.bind("<Return>", lambda _event: self.start_search())
        self._enable_select_all(self.entry_query)
        self._enable_context_menu(self.entry_query)
        self.paste_button = ThemedButton(
            query_row, self.theme, "Pegar enlace", self.paste_from_clipboard, variant="neutral", font=ui_font(9, "bold"), pady=6
        )
        self.paste_button.pack(side="left", padx=(8, 0))

        ThemedLabel(form, self.theme, "Nombre del Artista / Grupo Musical (Opcional):", font=ui_font(10, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        self.entry_artist = ttk.Entry(form, font=ui_font(10))
        self.entry_artist.pack(fill="x", pady=(0, 12))
        self.entry_artist.bind("<Return>", lambda _event: self.start_search())
        self._enable_select_all(self.entry_artist)
        self._enable_context_menu(self.entry_artist)

        self.process_button = ThemedButton(
            form, self.theme, PROCESS_BUTTON_TEXT, self.start_search, font=ui_font(11, "bold")
        )
        self.process_button.pack(fill="x")

        self.busy_frame = ThemedFrame(form, self.theme)
        self.progress = ttk.Progressbar(self.busy_frame, mode="indeterminate", style="Modern.Horizontal.TProgressbar")
        self.progress.pack(side="left", fill="x", expand=True)
        ThemedButton(
            self.busy_frame, self.theme, "Cancelar", self.cancel_operation, variant="danger", font=ui_font(9, "bold"), pady=4, padx=12
        ).pack(side="left", padx=(12, 0))

    @staticmethod
    def _enable_select_all(entry: ttk.Entry) -> None:
        def select_all(event: tk.Event) -> str:
            event.widget.selection_range(0, "end")
            event.widget.icursor("end")
            return "break"

        modifier = "Command" if IS_MAC else "Control"
        for key in ("a", "A"):
            entry.bind(f"<{modifier}-{key}>", select_all)

    def _enable_context_menu(self, entry: ttk.Entry) -> None:
        menu = create_menu(entry, self.theme)
        menu.add_command(
            label="✂ Cortar", accelerator=self._accelerator("X"), command=lambda: entry.event_generate("<<Cut>>")
        )
        menu.add_command(
            label="⧉ Copiar", accelerator=self._accelerator("C"), command=lambda: entry.event_generate("<<Copy>>")
        )
        menu.add_command(
            label="▤ Pegar", accelerator=self._accelerator("V"), command=lambda: entry.event_generate("<<Paste>>")
        )
        menu.add_separator()
        menu.add_command(
            label="⌗ Seleccionar todo", accelerator=self._accelerator("A"), command=lambda: self._select_all_text(entry)
        )

        def show_menu(event: tk.Event) -> str:
            self._close_context_menu()
            entry.focus_set()
            try:
                has_clipboard_text = bool(self.clipboard_get())
            except tk.TclError:
                has_clipboard_text = False

            has_selection = entry.selection_present()
            has_text = bool(entry.get())
            menu.entryconfigure("✂ Cortar", state="normal" if has_selection else "disabled")
            menu.entryconfigure("⧉ Copiar", state="normal" if has_selection else "disabled")
            menu.entryconfigure("▤ Pegar", state="normal" if has_clipboard_text else "disabled")
            menu.entryconfigure("⌗ Seleccionar todo", state="normal" if has_text else "disabled")

            self._context_menu = menu
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
            return "break"

        sequences = ("<Button-2>", "<Control-Button-1>") if IS_MAC else ("<Button-3>",)
        for sequence in sequences:
            entry.bind(sequence, show_menu)

    @staticmethod
    def _accelerator(key: str) -> str:
        return Shortcut(("Mod", key), "").label

    @staticmethod
    def _select_all_text(entry: ttk.Entry) -> None:
        entry.selection_range(0, "end")
        entry.icursor("end")

    def _close_context_menu(self) -> None:
        menu, self._context_menu = self._context_menu, None
        if menu is None:
            return
        try:
            menu.unpost()
            menu.grab_release()
        except tk.TclError:
            pass

    def _handle_global_click(self, event: tk.Event) -> None:
        menu = self._context_menu
        if menu is not None and not str(event.widget).startswith(str(menu)):
            self._close_context_menu()
        clicked = event.widget
        if isinstance(clicked, tk.Misc) and not isinstance(clicked, FOCUS_HOLDING_WIDGETS):
            self._release_focus(clicked.winfo_toplevel())

    def _build_actions(self) -> None:
        actions = ThemedFrame(self, self.theme, surface="window_bg")
        actions.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        actions.columnconfigure((0, 1), weight=1)
        self.copy_button = ThemedButton(
            actions, self.theme, "¡Copiar resultado!", self.copy_result, variant="success", font=ui_font(11, "bold")
        )
        self.copy_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.export_button = ThemedButton(
            actions, self.theme, "¡Exportar resultado!", self.export_result, font=ui_font(11, "bold")
        )
        self.export_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.help_button = CircleButton(
            actions, self.theme, "?", self.open_support, size=46, glyph_size=18, surface="window_bg"
        )
        self.help_button.grid(row=0, column=2, padx=(12, 0))
        Tooltip(self.help_button, self.theme, "Ayuda y Soporte (F1)", above=True)

    def _build_preview(self) -> None:
        panel = ThemedFrame(self, self.theme, padx=20, pady=16)
        panel.pack(fill="both", expand=True, padx=15, pady=10)

        header = ThemedFrame(panel, self.theme)
        header.pack(fill="x", pady=(0, 8))
        header.columnconfigure(1, weight=1)
        ThemedLabel(header, self.theme, "Previsualización de los versos:", font=ui_font(10, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        self.status_label = ThemedLabel(
            header, self.theme, "", role="text_muted", font=ui_font(9, "italic"), wraplength=460, justify="right", anchor="e"
        )
        self.status_label.grid(row=0, column=1, sticky="e", padx=(12, 0))

        body = ThemedFrame(panel, self.theme)
        body.pack(fill="both", expand=True)
        self.preview = tk.Text(
            body, wrap="word", font=mono_font(11), relief="flat", bd=0, padx=10, pady=8, state="disabled", cursor="arrow"
        )
        scrollbar = ttk.Scrollbar(body, orient="vertical", style="Modern.Vertical.TScrollbar", command=self.preview.yview)
        self.preview.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.preview.pack(side="left", fill="both", expand=True)
        self.theme.track(self.preview, self._apply_preview_theme)

    def _build_overlays(self) -> None:
        self.toast = Toast(self, self.theme)

    def _bind_shortcuts(self) -> None:
        self.shortcuts: tuple[Shortcut, ...] = (
            Shortcut(("F1",), "Abrir la ventana de ayuda y soporte.", self.open_support),
            Shortcut(("Esc",), "Salir de cualquier campo o cerrar la ventana emergente."),
            Shortcut(("Enter",), "Buscar y formatear la letra desde cualquiera de los dos campos de texto."),
            Shortcut(("Mod", "A"), "Seleccionar todo el texto del campo activo."),
            Shortcut(("Mod", "C"), "Copiar el texto seleccionado del campo activo."),
            Shortcut(("Mod", "X"), "Cortar el texto seleccionado del campo activo."),
            Shortcut(("Mod", "V"), "Pegar el contenido del portapapeles en el campo activo."),
            Shortcut(("Mod", "S"), "Exportar el resultado a un archivo de texto (.txt).", self.export_result),
            Shortcut(("Mod", "Shift", "K"), "Mostrar esta lista de atajos de teclado.", self.open_shortcuts),
            Shortcut(("Mod", "Shift", "C"), "Copiar el resultado generado al portapapeles.", self.copy_result),
            Shortcut(("Mod", "Shift", "V"), "Pegar el contenido del portapapeles y buscar la letra de inmediato.", self.paste_and_search),
        )
        bind_shortcuts(self, self.shortcuts)
        self.bind("<Escape>", lambda _event: self._release_focus())
        self.bind_all("<Button>", self._handle_global_click, add="+")
        self.bind_all("<Escape>", lambda _event: self._close_context_menu(), add="+")

    def _release_focus(self, window: tk.Misc | None = None) -> None:
        window = window or self
        try:
            focused = self.focus_get()
        except (KeyError, tk.TclError):
            focused = None
        if focused is None or focused is window:
            return
        try:
            if isinstance(focused, (tk.Entry, ttk.Entry)):
                focused.selection_clear()
            elif isinstance(focused, tk.Text):
                focused.tag_remove("sel", "1.0", "end")
        except tk.TclError:
            pass
        window.focus_set()

    def _apply_theme_button_label(self, _palette: Palette) -> None:
        self.theme_button.configure(text="☀ Modo claro" if self.theme.is_dark else "☾ Modo oscuro")

    def _apply_preview_theme(self, palette: Palette) -> None:
        self.preview.configure(
            bg=palette.field_bg,
            fg=palette.text,
            insertbackground=palette.text,
            selectbackground=palette.accent,
            selectforeground=palette.accent_text,
        )
        self.preview.tag_configure("header", foreground=palette.accent, font=mono_font(10, "bold"))
        self.preview.tag_configure("placeholder", foreground=palette.text_faint)

    def _handle_theme_changed(self, theme_name: str) -> None:
        self.settings.set("theme", theme_name)
        self.show_toast("¡Modo oscuro activado!" if self.theme.is_dark else "¡Modo claro activado!", "info")

    def _report_integrity_findings(self) -> None:
        names = "\n".join(
            f"• {finding.path.name} ({'eliminado' if finding.kind == 'deleted' else 'modificado'})"
            for finding in self.integrity_findings
        )
        logger.warning("Protected files changed outside the application: %s", names)
        choice = ask_choice(
            self,
            self.theme,
            "Cambios detectados en archivos protegidos",
            f"Se detectaron cambios hechos fuera de la aplicación en los archivos protegidos. A continuación se muestran los archivos modificados:\n\n{names}\n\n"
            "Por seguridad, se recomienta restaurar el archivo o aceptar los cambios que se hicieron.",
            "warning",
            [DialogButton("Revisar archivos", "review"), DialogButton("Cerrar", "close", "neutral")],
        )
        if choice == "review":
            self.open_protected_files()

    def _startup(self) -> None:
        if self.integrity_findings:
            self._report_integrity_findings()
        pending_version = self.settings.get("pending_update_confirmation")
        if pending_version:
            self.settings.set("pending_update_confirmation", None)
            self.show_message(
                "¡Actualización completada!",
                f"¡Ya se ha instalado la última versión estable correctamente!\nVersión instalada en el sistema: '{pending_version}'",
                "success",
            )
        if self.settings.get("first_run"):
            answer = self.ask_yes_no(
                "Notificación de actualización",
                "¿Desea activar las notificaciones automáticas cuándo exista una nueva actualización de yt-dlp?",
            )
            self.settings.set("check_yt_dlp_updates", answer)
            self.settings.set("first_run", False)
        self.updates.start_background_checks()

    def show_message(self, title: str, message: str, kind: str = "info") -> None:
        show_message(self, self.theme, title, message, kind)

    def ask_yes_no(self, title: str, message: str) -> bool:
        return ask_yes_no(self, self.theme, title, message)

    def show_toast(self, message: str, kind: str = "info") -> None:
        self.toast.show(message, kind)

    def set_status(self, text: str, kind: str = "idle") -> None:
        self.status_label.configure(text=f"{STATUS_PREFIX}{text}")
        self.status_label.set_role(STATUS_ROLES[kind])

    def run_operation(self, work: Work, *, status: str, on_success: Callable[..., None]) -> bool:
        if self.tasks.is_busy:
            self.show_toast("¡Ya hay una operación en curso! Espere a que finalice o cancélela...", "warning")
            return False
        self._enter_busy(status)

        def handle_success(result: object) -> None:
            self._leave_busy()
            on_success(result)

        return self.tasks.start(
            work,
            on_success=handle_success,
            on_failure=self._handle_operation_failure,
            on_progress=self._handle_progress,
            on_cancelled=self._handle_cancelled,
        )

    def cancel_operation(self) -> None:
        self.tasks.cancel()

    def _enter_busy(self, status: str) -> None:
        self._busy_started = time.monotonic()
        self._busy_message = status
        self.process_button.set_enabled(False)
        self.process_button.configure(text=PROCESS_BUTTON_BUSY_TEXT)
        self.paste_button.set_enabled(False)
        self.progress.configure(mode="indeterminate", value=0)
        self._progress_determinate = False
        self.busy_frame.pack(fill="x", pady=(12, 0))
        self.progress.start(12)
        self._render_busy_status()
        self._tick_job = self.after(TICK_INTERVAL_MS, self._tick)

    def _leave_busy(self) -> None:
        if self._tick_job is not None:
            self.after_cancel(self._tick_job)
            self._tick_job = None
        self.progress.stop()
        self.busy_frame.pack_forget()
        self.process_button.configure(text=PROCESS_BUTTON_TEXT)
        self.process_button.set_enabled(True)
        self.paste_button.set_enabled(True)

    def _tick(self) -> None:
        self._tick_job = None
        if not self.tasks.is_busy:
            return
        self._render_busy_status()
        self._tick_job = self.after(TICK_INTERVAL_MS, self._tick)

    def _render_busy_status(self) -> None:
        elapsed = int(time.monotonic() - self._busy_started)
        suffix = f" ({elapsed} s)" if elapsed >= ELAPSED_VISIBLE_AFTER_SECONDS else ""
        self.set_status(f"{self._busy_message}{suffix}", "busy")

    def _handle_progress(self, progress: Progress) -> None:
        self._busy_message = progress.message
        if progress.fraction is not None:
            if not self._progress_determinate:
                self.progress.stop()
                self.progress.configure(mode="determinate", maximum=100)
                self._progress_determinate = True
            self.progress.configure(value=progress.fraction * 100)
        elif self._progress_determinate:
            self.progress.configure(mode="indeterminate", value=0)
            self.progress.start(12)
            self._progress_determinate = False
        self._render_busy_status()

    def _handle_cancelled(self) -> None:
        self._leave_busy()
        self.set_status("Operación cancelada por el usuario.", "idle")
        self.show_toast("¡Operación cancelada!", "info")

    def _handle_operation_failure(self, error: Exception) -> None:
        self._leave_busy()
        self.report_error(error)

    def report_error(self, error: BaseException) -> None:
        report = describe_error(error)
        app_error = error if isinstance(error, AppError) else None
        severity = app_error.severity if app_error is not None else "error"
        reportable = app_error.reportable if app_error is not None else True

        if app_error is None:
            logger.error("[%s] %s", report.code, report.detail, exc_info=error)
        elif severity == "warning":
            logger.warning("[%s] %s", report.code, report.detail or report.message)
        else:
            logger.error("[%s] %s", report.code, report.detail or report.message)

        if reportable:
            self.last_error = report
        self.set_status(f"{report.title} (código: {report.code}).", "warning" if severity == "warning" else "error")
        show_error(
            self,
            self.theme,
            report.title,
            report,
            severity,
            self.open_support if reportable else None,
        )

    def report_callback_exception(self, exc: type[BaseException], value: BaseException, traceback: object) -> None:
        if self._reporting_error:
            logger.error("Nested UI exception suppressed: %s", value)
            return
        self._reporting_error = True
        try:
            if self.tasks.is_busy:
                self.tasks.cancel()
            self.report_error(value)
        finally:
            self._reporting_error = False

    def start_search(self) -> None:
        if self.tasks.is_busy:
            self.show_toast("¡Ya hay una operación en curso! Espere a que finalice o cancélela...", "warning")
            return
        query = self.entry_query.get().strip()
        artist = self.entry_artist.get().strip()
        if not query:
            logger.warning("User attempted search with empty query field.")
            self.set_status("Falta ingresar un enlace de YouTube o el título de una canción.", "warning")
            self.show_toast("¡Ingrese un enlace de YouTube válido o el título de una canción!", "warning")
            self.entry_query.focus_set()
            return
        self.run_operation(
            lambda report, token: self.lyrics.find(query, artist, report, token),
            status="Buscando y procesando la letra...",
            on_success=self._show_result,
        )

    def _show_result(self, result: LyricsResult) -> None:
        self.current_result = result
        self._render_result(result)
        self.history.add(result.title, result.artist, result.formatted_text, result.total_slides)
        self._refresh_history_menu()
        summary = f"{slides_text(result.total_slides)} generados correctamente."
        self.set_status(summary, "success")
        self.show_toast(f"¡Listo! {summary}", "success")

    def _render_result(self, result: LyricsResult) -> None:
        parts: list[str] = []
        for index, slide in enumerate(result.slides, start=1):
            parts.extend((f"--- VERSO {index} ---\n", "header", "\n".join(slide) + "\n\n", ""))
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("end", *parts)
        self.preview.configure(state="disabled")
        self.preview.yview_moveto(0)
        self._reveal_preview()

    def _reveal_preview(self) -> None:
        if self._reveal_animation is not None:
            self._reveal_animation.cancel()

        def render(progress: float) -> None:
            palette = self.theme.palette
            self.preview.configure(fg=blend_colors(palette.field_bg, palette.text, progress))
            self.preview.tag_configure("header", foreground=blend_colors(palette.field_bg, palette.accent, progress))

        self._reveal_animation = self.theme.motion.animate(self.preview, ANIMATION_RESULTS, RESULT_REVEAL_MS, render)

    def _show_placeholder(self) -> None:
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.insert("end", PREVIEW_PLACEHOLDER, "placeholder")
        self.preview.configure(state="disabled")

    def paste_from_clipboard(self) -> bool:
        if self.tasks.is_busy:
            self.show_toast("¡Ya hay una operación en curso! Espere a que finalice o cancélela...", "warning")
            return False
        try:
            raw = self.clipboard_get()
        except tk.TclError:
            raw = ""
        content = sanitize_single_line(raw[:CLIPBOARD_READ_LIMIT], MAX_QUERY_LENGTH)
        if not content:
            logger.warning("User attempted clipboard paste with empty or invalid clipboard.")
            self.set_status("El portapapeles no contiene texto para pegar.", "warning")
            self.show_toast("¡No se encontró ningún texto válido en el portapapeles!", "warning")
            return False
        self.entry_query.delete(0, "end")
        self.entry_query.insert(0, content)
        self.set_status("Enlace pegado desde el portapapeles correctamente.", "success")
        return True

    def paste_and_search(self) -> None:
        if self.paste_from_clipboard():
            self.start_search()

    def copy_result(self) -> None:
        if self.current_result is None:
            self.set_status("Aún no hay ningún texto procesado para copiar.", "warning")
            self.show_toast("¡Aún no hay ningún texto procesado para copiar!", "warning")
            return
        self.clipboard_clear()
        self.clipboard_append(self.current_result.formatted_text)
        logger.info("Formatted content copied to clipboard.")
        self.set_status("Resultado copiado al portapapeles.", "success")
        self.show_toast("¡Resultado copiado al portapapeles!", "success")

    def export_result(self) -> None:
        if self.current_result is None:
            self.set_status("Aún no hay ningún texto procesado para exportar.", "warning")
            self.show_toast("¡Aún no hay ningún texto procesado para exportar!", "warning")
            return
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar estructura",
            defaultextension=".txt",
            initialfile=f"Lyrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(self.current_result.export_text)
        except OSError as error:
            self.report_error(StorageError(str(error), "No fue posible guardar el archivo en la ubicación seleccionada."))
            return
        logger.info("Exported formatted lyrics to file: %s", file_path)
        self.set_status("Archivo exportado correctamente.", "success")
        self.show_toast("¡Archivo exportado correctamente!", "success")

    def _refresh_history_menu(self) -> None:
        menu = self.history_button.menu
        menu.delete(0, "end")
        entries = self.history.entries
        if not entries:
            menu.add_command(label="¡Sin búsquedas recientes!", state="disabled")
            return
        for entry in entries:
            label = f"♪ {entry.title} - {entry.artist}" if entry.artist else f"♪ {entry.title}"
            if len(label) > HISTORY_LABEL_LENGTH:
                label = f"{label[:HISTORY_LABEL_LENGTH - 1]}…"
            menu.add_command(label=label, command=lambda selected=entry: self.load_from_history(selected))
        menu.add_separator()
        menu.add_command(label="Borrar historial completo", command=self.clear_history)

    def load_from_history(self, entry: HistoryEntry) -> None:
        if self.tasks.is_busy:
            self.show_toast("Ya hay una operación en curso. Espere a que finalice o cancélela.", "warning")
            return
        self.entry_query.delete(0, "end")
        self.entry_query.insert(0, entry.title)
        self.entry_artist.delete(0, "end")
        self.entry_artist.insert(0, entry.artist)
        self.current_result = LyricsResult.from_formatted_text(entry.title, entry.artist, entry.formatted_result)
        self._render_result(self.current_result)
        self.set_status(f"{slides_text(self.current_result.total_slides)} cargados desde el historial.", "success")
        logger.info("Loaded search history entry: '%s'", entry.title)

    def clear_history(self) -> None:
        if not self.ask_yes_no(
            "Borrar historial", "¿Está seguro de que desea borrar todo el historial de búsquedas recientes?"
        ):
            return
        self.history.clear()
        self._refresh_history_menu()
        self.show_toast("¡Historial borrado!", "info")
        logger.info("Search history cleared by user.")

    def open_settings(self) -> None:
        SettingsDialog(
            self,
            self.theme,
            self.settings,
            self.log_path,
            self.updates.ytdlp_version_text,
            self.updates.update_ytdlp,
            self.updates.check_app_update,
        )

    def open_animation_settings(self) -> None:
        AnimationSettingsDialog(self, self.theme, self.settings)

    def open_shortcuts(self) -> None:
        ShortcutsDialog(self, self.theme, self.shortcuts)

    def _managed_files(self) -> list[ManagedFile]:
        return [
            ManagedFile(
                "Configuración", "Preferencias y estado de la aplicación", self.settings_path,
                "Restablecer", self._reset_settings, True, self._is_valid_json,
            ),
            ManagedFile(
                "Historial de búsquedas", "Búsquedas recientes y sus resultados", self.history_path,
                "Limpiar historial", self._wipe_history, True, self._is_valid_json,
            ),
            ManagedFile("Registros", "Bitácora de eventos y errores", self.log_path, "Eliminar", self._delete_logs, False),
            ManagedFile(
                "Componente yt-dlp", "Programa auxiliar para leer enlaces de YouTube", self.ytdlp_path,
                "Eliminar", self._delete_ytdlp, True,
            ),
        ]

    @staticmethod
    def _is_valid_json(path: Path) -> bool:
        return read_json(path) is not None

    def _reset_settings(self) -> None:
        self.settings.reset()
        self.theme.set_theme(self.settings.get("theme"))

    def _wipe_history(self) -> None:
        self.history.clear()
        self._refresh_history_menu()

    def _delete_logs(self) -> None:
        self.files.delete(self.log_path, self.log_path.with_name(f"{self.log_path.name}.1"))

    def _delete_ytdlp(self) -> None:
        self.files.delete(self.ytdlp_path)
        self.updates.start_background_checks()

    def open_protected_files(self) -> None:
        ProtectedFilesDialog(self, self.theme, self.files, self._managed_files(), lambda: self.tasks.is_busy)

    def open_about(self) -> None:
        AboutDialog(self, self.theme)

    def open_support(self) -> None:
        SupportDialog(self, self.theme, self.last_error)

    def exit_application(self) -> None:
        logger.info("Application closing.")
        self.destroy()

    def on_close(self) -> None:
        if self.tasks.is_busy:
            proceed = self.ask_yes_no(
                "Operación en curso",
                "Hay una operación en curso (búsqueda o actualización).\n"
                "¿Desea salir de todas formas? La operación se cancelará.",
            )
            if not proceed:
                return
            self.tasks.cancel()
        self.exit_application()