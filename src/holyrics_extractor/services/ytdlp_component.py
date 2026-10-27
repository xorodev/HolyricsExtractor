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
import time
from pathlib import Path
import requests
from ..constants import SUBPROCESS_TIMEOUT_SECONDS, YTDLP_RELEASES_URL
from ..core.errors import UpdateError
from ..core.logging_service import get_logger
from ..core.protected_files import ProtectedFiles
from ..core.tasks import CancellationToken, ProgressReporter
from .releases import (
    download_asset,
    fetch_latest_release,
    make_download_progress,
    resolve_expected_checksum,
)

logger = get_logger("ytdlp")

_VERSION_TIMEOUT_SECONDS = 10
_REPLACE_ATTEMPTS = 5
_REPLACE_DELAY_SECONDS = 0.5
_PROCESS_POLL_SECONDS = 0.25
_MISSING_VALUE = "NA"

class YtDlpComponent:
    def __init__(self, session: requests.Session, bin_directory: Path, files: ProtectedFiles):
        self._session = session
        self._files = files
        self._bin_directory = bin_directory
        self._binary_name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
        self.binary_path = bin_directory / self._binary_name

    def has_local_binary(self) -> bool:
        if not self.binary_path.is_file():
            return False
        if self._files.is_intact(self.binary_path):
            return True
        logger.warning("Local yt-dlp binary failed the integrity check and will not be executed.")
        return False

    def installed_version(self) -> str | None:
        if self.has_local_binary():
            try:
                return_code, output = self._run_binary(["--version"], _VERSION_TIMEOUT_SECONDS, None)
                version = output.strip()
                if return_code == 0 and version:
                    return version
            except (OSError, subprocess.SubprocessError, TimeoutError) as error:
                logger.warning("Could not read local yt-dlp version: %s", error)
        try:
            from yt_dlp.version import __version__
        except ImportError:
            return None
        return __version__

    def latest_version(self, token: CancellationToken | None = None) -> str:
        return fetch_latest_release(self._session, YTDLP_RELEASES_URL, token).tag

    def extract_metadata(self, video_url: str, token: CancellationToken) -> tuple[str, str] | None:
        if self.has_local_binary():
            metadata = self._extract_with_binary(video_url, token)
            if metadata is not None:
                return metadata
        return self._extract_with_library(video_url)

    def install_latest(self, report: ProgressReporter, token: CancellationToken) -> str:
        report("Consultando la última versión de yt-dlp...", None)
        release = fetch_latest_release(self._session, YTDLP_RELEASES_URL, token)
        asset_url = release.assets.get(self._binary_name)
        if asset_url is None:
            raise UpdateError(f"Release {release.tag} has no asset {self._binary_name}")

        expected_checksum = resolve_expected_checksum(self._session, release, self._binary_name, token)
        if expected_checksum is None:
            raise UpdateError(
                f"Release {release.tag} has no checksum file",
                "No fue posible verificar la integridad de la descarga, por lo que la actualización fue cancelada...",
            )

        self._bin_directory.mkdir(parents=True, exist_ok=True)
        temp_path = download_asset(
            self._session,
            asset_url,
            self._bin_directory,
            suffix=".tmp",
            expected_sha256=expected_checksum,
            progress=make_download_progress(report, "Descargando yt-dlp..."),
            token=token,
        )
        try:
            report("Instalando el componente yt-dlp...", None)
            if sys.platform != "win32":
                os.chmod(temp_path, 0o755)
            self._replace_binary(temp_path)
            self._files.seal(self.binary_path)
        except BaseException:
            self._remove_quietly(temp_path)
            raise
        logger.info("yt-dlp updated successfully to version %s", release.tag)
        return release.tag

    def _replace_binary(self, temp_path: Path) -> None:
        with self._files.writable(self.binary_path):
            for attempt in range(_REPLACE_ATTEMPTS):
                try:
                    os.replace(temp_path, self.binary_path)
                    return
                except PermissionError as error:
                    if attempt == _REPLACE_ATTEMPTS - 1:
                        raise UpdateError(f"Could not replace yt-dlp binary: {error}") from error
                    time.sleep(_REPLACE_DELAY_SECONDS)
                except OSError as error:
                    raise UpdateError(f"Could not replace yt-dlp binary: {error}") from error

    @staticmethod
    def _remove_quietly(path: Path) -> None:
        try:
            path.unlink()
        except OSError:
            pass

    def _extract_with_binary(self, video_url: str, token: CancellationToken) -> tuple[str, str] | None:
        arguments = [
            "--skip-download",
            "--no-warnings",
            "--no-playlist",
            "--socket-timeout", "10",
            "--print", "%(title)s",
            "--print", "%(uploader)s",
            "--",
            video_url,
        ]
        try:
            return_code, output = self._run_binary(arguments, SUBPROCESS_TIMEOUT_SECONDS, token)
        except (OSError, subprocess.SubprocessError, TimeoutError) as error:
            logger.warning("Local yt-dlp extraction failed: %s", error)
            return None
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if return_code != 0 or not lines:
            return None
        channel = lines[1] if len(lines) > 1 and lines[1] != _MISSING_VALUE else ""
        return lines[0], channel

    @staticmethod
    def _extract_with_library(video_url: str) -> tuple[str, str] | None:
        try:
            import yt_dlp
        except ImportError:
            return None
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "socket_timeout": 10,
            "cachedir": False,
        }
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                info = downloader.extract_info(video_url, download=False)
        except yt_dlp.utils.YoutubeDLError as error:
            logger.warning("Library yt-dlp extraction failed: %s", error)
            return None
        if not isinstance(info, dict) or not isinstance(info.get("title"), str):
            return None
        channel = info.get("uploader") or info.get("channel") or ""
        return info["title"], channel if isinstance(channel, str) else ""

    def _run_binary(
        self, arguments: list[str], timeout_seconds: float, token: CancellationToken | None
    ) -> tuple[int, str]:
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        process = subprocess.Popen(
            [str(self.binary_path), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation_flags,
        )
        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                stdout, _ = process.communicate(timeout=_PROCESS_POLL_SECONDS)
                return process.returncode, stdout or ""
            except subprocess.TimeoutExpired:
                cancelled = token is not None and token.is_cancelled
                if cancelled or time.monotonic() >= deadline:
                    process.kill()
                    process.communicate()
                    if token is not None:
                        token.raise_if_cancelled()
                    raise TimeoutError("yt-dlp binary timed out")