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
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import requests
from ..constants import (
    APP_EXECUTABLE_ASSET,
    APP_RELEASES_URL,
    MIN_EXECUTABLE_BYTES,
)
from ..core.errors import UpdateError
from ..core.logging_service import get_logger
from ..core.tasks import CancellationToken, ProgressReporter
from ..paths import is_frozen
from .releases import (
    ReleaseInfo,
    download_asset,
    fetch_latest_release,
    make_download_progress,
    resolve_expected_checksum,
)

logger = get_logger("app_updater")

_PE_MAGIC = b"MZ"

def _escape_for_batch(value: str) -> str:
    return value.replace("%", "%%")

class AppUpdater:
    def __init__(self, session: requests.Session):
        self._session = session

    @staticmethod
    def is_supported() -> bool:
        return is_frozen() and sys.platform == "win32"

    def latest_release(self, token: CancellationToken | None = None) -> ReleaseInfo:
        return fetch_latest_release(self._session, APP_RELEASES_URL, token)

    @staticmethod
    def has_installer(release: ReleaseInfo) -> bool:
        return APP_EXECUTABLE_ASSET in release.assets

    def download(self, release: ReleaseInfo, report: ProgressReporter, token: CancellationToken) -> Path:
        asset_url = release.assets.get(APP_EXECUTABLE_ASSET)
        if asset_url is None:
            raise UpdateError(f"Release {release.tag} has no asset {APP_EXECUTABLE_ASSET}")

        expected_checksum = resolve_expected_checksum(self._session, release, APP_EXECUTABLE_ASSET, token)
        if expected_checksum is None:
            logger.warning("Release %s publishes no checksum file; skipping hash verification", release.tag)

        destination = Path(sys.executable).resolve().parent
        new_build = download_asset(
            self._session,
            asset_url,
            destination,
            suffix=".new.exe",
            expected_sha256=expected_checksum,
            progress=make_download_progress(report, "Descargando la nueva versión.."),
            token=token,
        )
        try:
            self._validate_executable(new_build)
        except BaseException:
            try:
                new_build.unlink()
            except OSError:
                pass
            raise
        return new_build

    @staticmethod
    def _validate_executable(path: Path) -> None:
        try:
            size = path.stat().st_size
            with path.open("rb") as handle:
                header = handle.read(len(_PE_MAGIC))
        except OSError as error:
            raise UpdateError(f"Could not inspect the downloaded file: {error}") from error
        if size < MIN_EXECUTABLE_BYTES or header != _PE_MAGIC:
            raise UpdateError(
                "Downloaded file is not a valid executable",
                "¡El archivo descargado no corresponde a un ejecutable válido!",
            )

    def apply_and_relaunch(self, new_build: Path) -> None:
        current_exe = Path(sys.executable).resolve()
        backup_name = f"{current_exe.name}.old"
        backup_full = current_exe.with_name(backup_name)
        script_content = (
            "@echo off\n"
            "set _MEIPASS2=\n"
            'set "PYINSTALLER_RESET_ENVIRONMENT=1"\n'
            f'set "CURRENT_EXE={_escape_for_batch(str(current_exe))}"\n'
            f'set "CURRENT_NAME={_escape_for_batch(current_exe.name)}"\n'
            f'set "NEW_EXE={_escape_for_batch(str(new_build))}"\n'
            f'set "BACKUP_NAME={_escape_for_batch(backup_name)}"\n'
            f'set "BACKUP_FULL={_escape_for_batch(str(backup_full))}"\n'
            'set "RETRY=0"\n'
            'del "%BACKUP_FULL%" >nul 2>&1\n'
            "\n"
            ":wait_loop\n"
            'ren "%CURRENT_EXE%" "%BACKUP_NAME%" >nul 2>&1\n'
            'if not exist "%CURRENT_EXE%" goto replace_ok\n'
            "set /a RETRY+=1\n"
            "if %RETRY% GEQ 20 goto give_up\n"
            "ping 127.0.0.1 -n 2 >nul\n"
            "goto wait_loop\n"
            "\n"
            ":replace_ok\n"
            'move /y "%NEW_EXE%" "%CURRENT_EXE%" >nul 2>&1\n'
            'if not exist "%CURRENT_EXE%" goto rollback\n'
            "ping 127.0.0.1 -n 3 >nul\n"
            'del "%BACKUP_FULL%" >nul 2>&1\n'
            'start "" "%CURRENT_EXE%"\n'
            "goto cleanup\n"
            "\n"
            ":rollback\n"
            'ren "%BACKUP_FULL%" "%CURRENT_NAME%" >nul 2>&1\n'
            "\n"
            ":give_up\n"
            'start "" "%CURRENT_EXE%"\n'
            'del "%NEW_EXE%" >nul 2>&1\n'
            "\n"
            ":cleanup\n"
            'del "%~f0" >nul 2>&1\n'
        )
        script_path: str | None = None
        try:
            file_descriptor, script_path = tempfile.mkstemp(prefix="holyrics_updater_", suffix=".bat")
            with os.fdopen(file_descriptor, "w", encoding="mbcs") as script_file:
                script_file.write(script_content)
            subprocess.Popen(
                ["cmd", "/c", script_path],
                creationflags=subprocess.CREATE_NO_WINDOW,
                close_fds=True,
            )
        except (OSError, UnicodeError, LookupError) as error:
            if script_path is not None:
                try:
                    os.remove(script_path)
                except OSError:
                    pass
            raise UpdateError(f"Could not launch the updater script: {error}") from error