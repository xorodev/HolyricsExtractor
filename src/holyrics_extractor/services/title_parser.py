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

_TAG_PATTERN = (
    r"(?:official\s*music\s*video|official\s*video|official\s*audio|"
    r"video\s*oficial|audio\s*oficial|lyric\s*video|lyrics?|letra|"
    r"official|oficial|video|audio|visualizer|hd|4k|mv)"
)
_TAG_KEYWORDS_RE = re.compile(r"\b" + _TAG_PATTERN + r"\b", re.IGNORECASE)
_BRACKET_GROUP_RE = re.compile(r"[\(\[][^()\[\]]*[\)\]]")
_TRAILING_TAG_RE = re.compile(r"\s*(?:[-|:]\s*)?" + _TAG_PATTERN + r"\s*$", re.IGNORECASE)
_MULTI_SPACE_RE = re.compile(r"\s{2,}")
_ARTIST_TITLE_SEPARATOR_RE = re.compile(r"\s+[-–—|]\s+")
_TOPIC_SUFFIX_RE = re.compile(r"\s+-\s+Topic$", re.IGNORECASE)

def clean_title(title: str) -> str:
    def strip_if_tag(match: re.Match[str]) -> str:
        content = match.group(0)
        return "" if _TAG_KEYWORDS_RE.search(content) else content

    cleaned = _BRACKET_GROUP_RE.sub(strip_if_tag, title)
    cleaned = _TRAILING_TAG_RE.sub("", cleaned)
    cleaned = _MULTI_SPACE_RE.sub(" ", cleaned)
    return cleaned.strip(" -|:").strip()

def split_title_and_artist(title: str) -> tuple[str, str]:
    parts = _ARTIST_TITLE_SEPARATOR_RE.split(title, maxsplit=1)
    if len(parts) == 2 and parts[0].strip() and parts[1].strip():
        return parts[1].strip(), parts[0].strip()
    return title.strip(), ""

def clean_channel_name(channel: str) -> str:
    return _TOPIC_SUFFIX_RE.sub("", channel.strip()).strip()