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
from typing import Callable, Protocol
from ..constants import APP_VERSION
from ..core.errors import AppError, UpdateError
from ..core.logging_service import get_logger
from ..core.settings import SettingsStore
from ..core.tasks import CancellationToken, TaskRunner, Work
from ..services.app_updater import AppUpdater
from ..services.releases import ReleaseInfo
from ..services.ytdlp_component import YtDlpComponent
from .dialogs import VERSION_PENDING_TEXT

logger = get_logger("updates")

VERSION_UNAVAILABLE_TEXT = "¡No disponible!"

class UpdateHost(Protocol):
    @property
    def is_busy(self) -> bool: ...

    def run_operation(self, work: Work, *, status: str, on_success: Callable[..., None]) -> bool: ...

    def show_message(self, title: str, message: str, kind: str = "info") -> None: ...

    def ask_yes_no(self, title: str, message: str) -> bool: ...

    def set_status(self, text: str, kind: str) -> None: ...

    def report_error(self, error: BaseException) -> None: ...

    def exit_application(self) -> None: ...

@dataclass(slots=True)
class UpdateCheck:
    ytdlp_installed: str | None = None
    ytdlp_latest: str | None = None
    app_release: ReleaseInfo | None = None

class UpdateController:
    def __init__(
        self,
        host: UpdateHost,
        root: tk.Misc,
        settings: SettingsStore,
        ytdlp: YtDlpComponent,
        app_updater: AppUpdater,
    ):
        self._host = host
        self._settings = settings
        self._ytdlp = ytdlp
        self._app_updater = app_updater
        self._background = TaskRunner(root)
        self._version_known = False
        self._ytdlp_version: str | None = None

    def ytdlp_version_text(self) -> str:
        if not self._version_known:
            return VERSION_PENDING_TEXT
        return self._ytdlp_version or VERSION_UNAVAILABLE_TEXT

    def start_background_checks(self) -> None:
        check_ytdlp = bool(self._settings.get("check_yt_dlp_updates"))
        check_app = self._app_updater.is_supported() and bool(self._settings.get("check_app_updates"))
        self._background.start(
            lambda report, token: self._run_checks(check_ytdlp, check_app, token),
            on_success=self._handle_checks,
            on_failure=lambda error: logger.warning("Background update check failed: %s", error),
        )

    def update_ytdlp(self, on_done: Callable[[], None] | None = None) -> None:
        def finished(tag: str) -> None:
            self._set_version(tag)
            self._host.set_status(f"yt-dlp actualizado a la versión: '{tag}'.", "success")
            self._host.show_message(
                "¡Actualización exitosa!",
                f"El componente yt-dlp ha sido actualizado de forma limpia a la nueva versión: '{tag}'",
                "success",
            )
            if on_done is not None:
                on_done()

        self._host.run_operation(
            lambda report, token: self._ytdlp.install_latest(report, token),
            status="Actualizando el componente yt-dlp...",
            on_success=finished,
        )

    def check_app_update(self) -> None:
        if not self._app_updater.is_supported():
            self._host.show_message(
                "¡Función no disponible!",
                "La búsqueda de actualizaciones de la aplicación solo está disponible en la versión compilada (.exe) del programa.",
            )
            return
        self._host.run_operation(
            lambda report, token: self._app_updater.latest_release(token),
            status="Buscando actualizaciones de la aplicación...",
            on_success=self._handle_manual_app_check,
        )

    def _run_checks(self, check_ytdlp: bool, check_app: bool, token: CancellationToken) -> UpdateCheck:
        result = UpdateCheck(ytdlp_installed=self._ytdlp.installed_version())
        if check_ytdlp:
            try:
                result.ytdlp_latest = self._ytdlp.latest_version(token)
            except AppError as error:
                logger.warning("Could not check yt-dlp updates: %s", error)
        if check_app:
            try:
                release = self._app_updater.latest_release(token)
                if release.tag != APP_VERSION and self._app_updater.has_installer(release):
                    result.app_release = release
            except AppError as error:
                logger.warning("Could not check application updates: %s", error)
        return result

    def _handle_checks(self, check: UpdateCheck) -> None:
        self._set_version(check.ytdlp_installed)

        def offer_app() -> None:
            self._offer_app_update(check.app_release)

        ytdlp_outdated = check.ytdlp_latest is not None and check.ytdlp_latest != check.ytdlp_installed
        if ytdlp_outdated and not self._host.is_busy:
            logger.info("New yt-dlp version detected: %s (current: %s)", check.ytdlp_latest, check.ytdlp_installed)
            self._prompt_ytdlp_update(check.ytdlp_installed, check.ytdlp_latest, offer_app)
        else:
            offer_app()

    def _prompt_ytdlp_update(self, current: str | None, latest: str, then: Callable[[], None]) -> None:
        accepted = self._host.ask_yes_no(
            "¡Actualización disponible!",
            "Se ha detectado una nueva versión en yt-dlp.\n\n"
            f"• Versión instalada en el sistema: '{current or VERSION_UNAVAILABLE_TEXT}'\n"
            f"• Versión disponible: '{latest}'\n\n"
            "¿Desea realizar la actualización en este momento?",
        )
        if accepted:
            self.update_ytdlp(on_done=then)
        else:
            then()

    def _offer_app_update(self, release: ReleaseInfo | None) -> None:
        if release is not None and not self._host.is_busy:
            logger.info("New application version detected: %s (current: %s)", release.tag, APP_VERSION)
            self._confirm_app_update(release)

    def _handle_manual_app_check(self, release: ReleaseInfo) -> None:
        if release.tag == APP_VERSION:
            self._host.set_status("¡La aplicación está actualizada!", "success")
            self._host.show_message(
                "¡Aplicación actualizada!", f"Ya tiene instalada la última versión disponible: '{APP_VERSION}'", "success"
            )
        elif not self._app_updater.has_installer(release):
            self._host.show_message(
                "¡Actualización no disponible!",
                f"La versión '{release.tag}' todavía no incluye el ejecutable de instalación. Inténtelo de nuevo más tarde...",
                "warning",
            )
        else:
            self._confirm_app_update(release)

    def _confirm_app_update(self, release: ReleaseInfo) -> None:
        accepted = self._host.ask_yes_no(
            "¡Nueva versión disponible!",
            "Hay una nueva versión de la aplicación disponible.\n\n"
            f"• Versión instalada: '{APP_VERSION}'\n"
            f"• Versión disponible: '{release.tag}'\n\n"
            "¿Desea descargarla e instalarla ahora? La aplicación se reiniciará automáticamente al finalizar.",
        )
        if accepted:
            self._host.run_operation(
                lambda report, token: self._app_updater.download(release, report, token),
                status="Descargando la nueva versión...",
                on_success=lambda path: self._finalize_app_update(release.tag, path),
            )

    def _finalize_app_update(self, tag: str, new_build: Path) -> None:
        self._host.show_message(
            "¡Actualización lista!",
            "La nueva versión se descargó correctamente.\n"
            "La aplicación se cerrará y se reiniciará automáticamente para completar la instalación.",
            "success",
        )
        self._settings.set("pending_update_confirmation", tag)
        try:
            self._app_updater.apply_and_relaunch(new_build)
        except UpdateError as error:
            self._settings.set("pending_update_confirmation", None)
            try:
                new_build.unlink()
            except OSError:
                pass
            self._host.report_error(error)
            return
        logger.info("Application update downloaded; relaunching with version %s", tag)
        self._host.exit_application()

    def _set_version(self, version: str | None) -> None:
        self._ytdlp_version = version
        self._version_known = True