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
from difflib import SequenceMatcher
from typing import Any
import requests
from ..constants import LRCLIB_SEARCH_URL
from ..core.errors import ServiceResponseError
from ..core.logging_service import get_logger
from ..core.tasks import CancellationToken
from .http import fetch_json

logger = get_logger("lrclib")

_MAX_CANDIDATES = 20
_TITLE_WEIGHT = 0.7
_ARTIST_WEIGHT = 0.3
_NORMALIZE_RE = re.compile(r"[\W_]+")
_TIMESTAMP_PREFIX_RE = re.compile(r"^\s*(?:\[\d{1,3}:\d{2}(?:[.:]\d{1,3})?\]\s*)+")
_METADATA_LINE_RE = re.compile(r"^\s*\[[A-Za-z]+:[^\]]*\]\s*$")

def _normalize(text: str) -> str:
    return _NORMALIZE_RE.sub(" ", text.casefold()).strip()

def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()

def _strip_synced_lyrics(synced: str) -> str:
    lines = []
    for line in synced.splitlines():
        if _METADATA_LINE_RE.match(line):
            continue
        lines.append(_TIMESTAMP_PREFIX_RE.sub("", line).strip())
    return "\n".join(lines)

def _extract_lyrics(item: dict[str, Any]) -> str | None:
    if item.get("instrumental") is True:
        return None
    plain = item.get("plainLyrics")
    if isinstance(plain, str) and plain.strip():
        return plain
    synced = item.get("syncedLyrics")
    if isinstance(synced, str) and synced.strip():
        stripped = _strip_synced_lyrics(synced)
        return stripped if stripped.strip() else None
    return None

class LrclibClient:
    def __init__(self, session: requests.Session):
        self._session = session

    def find_lyrics(self, track: str, artist: str, token: CancellationToken) -> str | None:
        for params in self._query_plan(track, artist):
            token.raise_if_cancelled()
            lyrics = self._search(params, track, artist, token)
            if lyrics:
                return lyrics
        return None

    @staticmethod
    def _query_plan(track: str, artist: str) -> list[dict[str, str]]:
        plan: list[dict[str, str]] = []
        if artist:
            plan.append({"track_name": track, "artist_name": artist})
            plan.append({"q": f"{artist} {track}"})
        plan.append({"q": track})
        return plan

    def _search(self, params: dict[str, str], track: str, artist: str, token: CancellationToken) -> str | None:
        payload = fetch_json(self._session, LRCLIB_SEARCH_URL, params=params, token=token)
        if payload is None:
            return None
        if not isinstance(payload, list):
            raise ServiceResponseError("LRCLIB search returned a non-list payload")

        best_lyrics: str | None = None
        best_score = -1.0
        for item in payload[:_MAX_CANDIDATES]:
            if not isinstance(item, dict):
                continue
            lyrics = _extract_lyrics(item)
            if lyrics is None:
                continue
            score = self._score(item, track, artist)
            if score > best_score:
                best_lyrics, best_score = lyrics, score
        return best_lyrics

    @staticmethod
    def _score(item: dict[str, Any], track: str, artist: str) -> float:
        track_name = item.get("trackName") or item.get("name") or ""
        title_score = _similarity(track, track_name) if isinstance(track_name, str) else 0.0
        if not artist:
            return title_score
        artist_name = item.get("artistName")
        artist_score = _similarity(artist, artist_name) if isinstance(artist_name, str) else 0.0
        return _TITLE_WEIGHT * title_score + _ARTIST_WEIGHT * artist_score