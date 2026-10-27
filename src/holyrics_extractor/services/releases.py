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
import hashlib
import hmac
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse
import requests
from ..constants import (
    CHECKSUMS_ASSET,
    DOWNLOAD_CHUNK_BYTES,
    DOWNLOAD_TIMEOUT,
    MAX_DOWNLOAD_BYTES,
    TRUSTED_DOWNLOAD_HOST_SUFFIXES,
)
from ..core.errors import IntegrityError, NetworkError, ServiceResponseError, UpdateError
from ..core.tasks import CancellationToken, ProgressReporter
from .http import fetch_bytes, fetch_json

_CHECKSUM_LINE_RE = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(\S.*?)\s*$")
_MAX_CHECKSUM_FILE_BYTES = 200_000

DownloadProgress = Callable[[int, int], None]

@dataclass(frozen=True, slots=True)

class ReleaseInfo:
    tag: str
    assets: dict[str, str]

def is_trusted_download_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in TRUSTED_DOWNLOAD_HOST_SUFFIXES)

def fetch_latest_release(
    session: requests.Session, api_url: str, token: CancellationToken | None = None
) -> ReleaseInfo:
    payload = fetch_json(session, api_url, token=token)
    if not isinstance(payload, dict):
        raise ServiceResponseError("Release payload is not an object")
    tag = payload.get("tag_name")
    raw_assets = payload.get("assets")
    if not isinstance(tag, str) or not tag or not isinstance(raw_assets, list):
        raise ServiceResponseError("Release payload is missing tag or assets")
    assets: dict[str, str] = {}
    for asset in raw_assets:
        if not isinstance(asset, dict):
            continue
        name = asset.get("name")
        url = asset.get("browser_download_url")
        if isinstance(name, str) and isinstance(url, str) and is_trusted_download_url(url):
            assets[name] = url
    return ReleaseInfo(tag, assets)

def resolve_expected_checksum(
    session: requests.Session,
    release: ReleaseInfo,
    asset_name: str,
    token: CancellationToken | None = None,
) -> str | None:
    checksums_url = release.assets.get(CHECKSUMS_ASSET)
    if checksums_url is None:
        return None
    _, body = fetch_bytes(session, checksums_url, max_bytes=_MAX_CHECKSUM_FILE_BYTES, token=token)
    checksums: dict[str, str] = {}
    for line in body.decode("utf-8", errors="replace").splitlines():
        match = _CHECKSUM_LINE_RE.match(line.strip())
        if match:
            checksums[match.group(2)] = match.group(1).lower()
    expected = checksums.get(asset_name)
    if expected is None:
        raise IntegrityError(f"No checksum published for {asset_name}")
    return expected

def make_download_progress(report: ProgressReporter, label: str) -> DownloadProgress:
    def callback(downloaded: int, total: int) -> None:
        if total > 0:
            fraction = min(downloaded / total, 1.0)
            report(f"{label} ({int(fraction * 100)}%)...", fraction)
        else:
            report(f"{label} ({downloaded // 1_000_000} MB)...", None)

    return callback

def download_asset(
    session: requests.Session,
    url: str,
    destination_directory: Path,
    *,
    suffix: str,
    expected_sha256: str | None = None,
    progress: DownloadProgress | None = None,
    token: CancellationToken | None = None,
) -> Path:
    if not is_trusted_download_url(url):
        raise UpdateError("Download URL is not trusted")

    digest = hashlib.sha256()
    temp_name: str | None = None
    try:
        with session.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True) as response:
            if response.status_code != 200:
                raise UpdateError(f"Download server answered HTTP {response.status_code}")
            if not is_trusted_download_url(response.url):
                raise UpdateError("Download was redirected to an untrusted host")
            declared = response.headers.get("Content-Length", "")
            total = int(declared) if declared.isdigit() else 0
            if total > MAX_DOWNLOAD_BYTES:
                raise UpdateError("Download exceeds the allowed size")

            file_descriptor, temp_name = tempfile.mkstemp(dir=destination_directory, suffix=suffix)
            downloaded = 0
            with os.fdopen(file_descriptor, "wb") as handle:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_BYTES):
                    if not chunk:
                        continue
                    if token is not None:
                        token.raise_if_cancelled()
                    downloaded += len(chunk)
                    if downloaded > MAX_DOWNLOAD_BYTES:
                        raise UpdateError("Download exceeds the allowed size")
                    handle.write(chunk)
                    digest.update(chunk)
                    if progress is not None:
                        progress(downloaded, total)

        if expected_sha256 is not None and not hmac.compare_digest(digest.hexdigest(), expected_sha256.lower()):
            raise IntegrityError("SHA-256 mismatch")

        result = Path(temp_name)
        temp_name = None
        return result
    except requests.RequestException as error:
        raise NetworkError(f"Download failed: {type(error).__name__}") from error
    except OSError as error:
        raise UpdateError(f"Could not write the downloaded file: {error}") from error
    finally:
        if temp_name is not None:
            try:
                os.remove(temp_name)
            except OSError:
                pass