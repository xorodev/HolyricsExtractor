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

APP_NAME = "Extractor de Letras para Holyrics"
APP_VERSION = "v1.0.0-stable"
APP_DATA_FOLDER = "HolyricsExtractor"
USER_AGENT = f"HolyricsExtractor/{APP_VERSION.lstrip('v')}"

GITHUB_API_ROOT = "https://api.github.com/repos"
YTDLP_RELEASES_URL = f"{GITHUB_API_ROOT}/yt-dlp/yt-dlp/releases/latest"
APP_RELEASES_URL = f"{GITHUB_API_ROOT}/xorodev/HolyricsExtractor/releases/latest"
APP_EXECUTABLE_ASSET = "HolyricsExtractor.exe"
CHECKSUMS_ASSET = "SHA2-256SUMS"
TRUSTED_DOWNLOAD_HOST_SUFFIXES = ("github.com", "githubusercontent.com")

LRCLIB_SEARCH_URL = "https://lrclib.net/api/search"
YOUTUBE_OEMBED_URL = "https://www.youtube.com/oembed"

SUPPORT_WHATSAPP_NUMBER = "50497764448"
SUPPORT_WHATSAPP_DISPLAY = "+504 9776-4448"
SUPPORT_EMAIL = "wilfredorb0218@gmail.com"

MAX_QUERY_LENGTH = 300
MAX_ARTIST_LENGTH = 120
MAX_SUPPORT_MESSAGE_LENGTH = 1000
MAX_LOG_MESSAGE_LENGTH = 1000
MAX_HISTORY_ENTRIES = 10
MAX_HISTORY_TEXT_LENGTH = 200_000
MAX_STORAGE_FILE_BYTES = 5_000_000
MAX_API_RESPONSE_BYTES = 2_000_000
MAX_DOWNLOAD_BYTES = 250_000_000
MIN_EXECUTABLE_BYTES = 1_000_000

HTTP_TIMEOUT = (4, 8)
DOWNLOAD_TIMEOUT = (6, 30)
SUBPROCESS_TIMEOUT_SECONDS = 20
DOWNLOAD_CHUNK_BYTES = 262_144

SLIDE_MAX_LINES = 5
SLIDE_BLOCK_TARGET_LINES = 4
SLIDE_REPEAT_MARK = "//"
EXPORT_SEPARATOR = "-" * 14