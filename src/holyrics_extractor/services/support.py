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
import platform
from urllib.parse import quote
from ..constants import (
    APP_NAME,
    APP_VERSION,
    MAX_SUPPORT_MESSAGE_LENGTH,
    SUPPORT_EMAIL,
    SUPPORT_WHATSAPP_NUMBER,
)
from ..core.errors import ErrorReport
from ..core.sanitizer import sanitize_multiline, sanitize_single_line

_WHATSAPP_ENCODED_LIMIT = 1_800
_EMAIL_ENCODED_LIMIT = 1_800
_ELLIPSIS = "…"

def build_report_text(user_message: str, error: ErrorReport | None, include_system_info: bool) -> str:
    message = sanitize_multiline(user_message, MAX_SUPPORT_MESSAGE_LENGTH) or "(Sin descripción)"
    sections = [f"Hola, necesito ayuda con la aplicación: '{APP_NAME}'.", "", "Mensaje descriptivo:", message]
    if error is not None:
        sections += [
            "",
            f"Código de error: {error.code}",
            f"Fecha del error: {error.occurred_at}",
            f"Detalle técnico: {sanitize_single_line(error.detail, 400) or '¡No disponible!'}",
        ]
    if include_system_info:
        sections += [
            "",
            f"Versión de la aplicación: {APP_VERSION}",
            f"Versión del sistema operativo: {platform.platform()}",
        ]
    return "\n".join(sections)

def _encode_within_limit(text: str, limit: int) -> str:
    encoded = quote(text, safe="")
    if len(encoded) <= limit:
        return encoded
    suffix = quote(_ELLIPSIS, safe="")
    trimmed = text
    while trimmed and len(quote(trimmed, safe="")) + len(suffix) > limit:
        trimmed = trimmed[: int(len(trimmed) * 0.9)]
    return quote(trimmed, safe="") + suffix

def build_whatsapp_url(report: str) -> str:
    return f"https://wa.me/{SUPPORT_WHATSAPP_NUMBER}?text={_encode_within_limit(report, _WHATSAPP_ENCODED_LIMIT)}"

def build_mailto_url(report: str, error: ErrorReport | None) -> str:
    subject = f"Soporte - {APP_NAME}"
    if error is not None:
        subject = f"{subject} ({error.code})"
    return (
        f"mailto:{SUPPORT_EMAIL}?subject={quote(subject, safe='')}"
        f"&body={_encode_within_limit(report, _EMAIL_ENCODED_LIMIT)}"
    )