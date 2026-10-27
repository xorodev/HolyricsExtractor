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
import json
from typing import Any
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..constants import HTTP_TIMEOUT, MAX_API_RESPONSE_BYTES
from ..core.errors import NetworkError, ServiceResponseError
from ..core.tasks import CancellationToken

RETRYABLE_STATUSES = (429, 500, 502, 503, 504)
READ_CHUNK_BYTES = 65_536

def create_session(user_agent: str, accept: str | None = None) -> requests.Session:
    retry = Retry(
        total=2,
        connect=2,
        read=1,
        status=2,
        backoff_factor=0.4,
        status_forcelist=RETRYABLE_STATUSES,
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=2, pool_maxsize=2))
    session.headers["User-Agent"] = user_agent
    if accept:
        session.headers["Accept"] = accept
    return session

def fetch_bytes(
    session: requests.Session,
    url: str,
    *,
    params: dict[str, str] | None = None,
    timeout: tuple[float, float] = HTTP_TIMEOUT,
    max_bytes: int = MAX_API_RESPONSE_BYTES,
    token: CancellationToken | None = None,
) -> tuple[int, bytes]:
    host = urlparse(url).hostname or "unknown-host"
    try:
        with session.get(url, params=params, timeout=timeout, stream=True) as response:
            status = response.status_code
            if status == 404:
                return status, b""
            if status != 200:
                raise ServiceResponseError(f"HTTP {status} from {host}")
            declared = response.headers.get("Content-Length", "")
            if declared.isdigit() and int(declared) > max_bytes:
                raise ServiceResponseError(f"Response from {host} exceeds {max_bytes} bytes")
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_content(chunk_size=READ_CHUNK_BYTES):
                if token is not None:
                    token.raise_if_cancelled()
                total += len(chunk)
                if total > max_bytes:
                    raise ServiceResponseError(f"Response from {host} exceeds {max_bytes} bytes")
                chunks.append(chunk)
            return status, b"".join(chunks)
    except requests.RequestException as error:
        raise NetworkError(f"{host}: {type(error).__name__}") from error

def fetch_json(
    session: requests.Session,
    url: str,
    *,
    params: dict[str, str] | None = None,
    token: CancellationToken | None = None,
) -> Any | None:
    status, body = fetch_bytes(session, url, params=params, token=token)
    if status == 404:
        return None
    try:
        return json.loads(body)
    except ValueError as error:
        raise ServiceResponseError("Invalid JSON payload") from error