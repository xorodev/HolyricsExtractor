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
import re

_CONTROL_CHARACTERS_RE = re.compile(r"[\x00-\x1f\x7f-\x9f]")

def sanitize_single_line(text: str, max_length: int) -> str:
    collapsed = " ".join(str(text).split())
    cleaned = _CONTROL_CHARACTERS_RE.sub("", collapsed)
    return cleaned[:max_length].strip()

_CONTROL_EXCEPT_NEWLINE_RE = re.compile(r"[\x00-\x09\x0b-\x1f\x7f-\x9f]")
_EXTRA_BLANK_LINES_RE = re.compile(r"\n{3,}")

def sanitize_multiline(text: str, max_length: int) -> str:
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    cleaned = _CONTROL_EXCEPT_NEWLINE_RE.sub("", normalized)
    lines = "\n".join(line.rstrip() for line in cleaned.split("\n"))
    return _EXTRA_BLANK_LINES_RE.sub("\n\n", lines)[:max_length].strip()