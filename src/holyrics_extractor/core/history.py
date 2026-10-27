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
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from ..constants import MAX_ARTIST_LENGTH, MAX_HISTORY_ENTRIES, MAX_HISTORY_TEXT_LENGTH, MAX_QUERY_LENGTH
from .errors import StorageError
from .logging_service import get_logger
from .protected_files import ProtectedFiles
from .storage import read_json

logger = get_logger("history")

@dataclass(frozen=True, slots=True)

class HistoryEntry:
    title: str
    artist: str
    formatted_result: str
    total_slides: int
    timestamp: str

    @property
    def key(self) -> tuple[str, str]:
        return self.title.casefold(), self.artist.casefold()

def _parse_entry(raw: Any) -> HistoryEntry | None:
    if not isinstance(raw, dict):
        return None
    title = raw.get("title")
    artist = raw.get("artist", "")
    text = raw.get("formatted_result")
    total = raw.get("total_slides")
    timestamp = raw.get("timestamp", "")
    if not (isinstance(title, str) and isinstance(artist, str) and isinstance(text, str)):
        return None
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        return None
    if not isinstance(timestamp, str):
        timestamp = ""
    if not title.strip() or not text.strip():
        return None
    if len(title) > MAX_QUERY_LENGTH or len(artist) > MAX_ARTIST_LENGTH or len(text) > MAX_HISTORY_TEXT_LENGTH:
        return None
    return HistoryEntry(title, artist, text, total, timestamp)

class HistoryStore:
    def __init__(self, path: Path, files: ProtectedFiles):
        self._path = path
        self._files = files
        self._entries: list[HistoryEntry] = self._load()

    def _load(self) -> list[HistoryEntry]:
        raw = read_json(self._path)
        return self._parse_many(raw if isinstance(raw, list) else [])

    @staticmethod
    def _parse_many(raw_entries: list[Any]) -> list[HistoryEntry]:
        entries: list[HistoryEntry] = []
        seen: set[tuple[str, str]] = set()
        for raw in raw_entries:
            entry = _parse_entry(raw)
            if entry is None or entry.key in seen:
                continue
            seen.add(entry.key)
            entries.append(entry)
            if len(entries) >= MAX_HISTORY_ENTRIES:
                break
        return entries

    @property
    def entries(self) -> tuple[HistoryEntry, ...]:
        return tuple(self._entries)

    def import_legacy(self, legacy_entries: list[Any]) -> None:
        if self._entries:
            return
        self._entries = self._parse_many(legacy_entries)
        self._persist()

    def add(self, title: str, artist: str, formatted_result: str, total_slides: int) -> None:
        entry = HistoryEntry(
            title=title,
            artist=artist,
            formatted_result=formatted_result,
            total_slides=total_slides,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._entries = [item for item in self._entries if item.key != entry.key]
        self._entries.insert(0, entry)
        del self._entries[MAX_HISTORY_ENTRIES:]
        self._persist()

    def clear(self) -> None:
        self._entries = []
        self._persist()

    def _persist(self) -> None:
        try:
            self._files.write_json(self._path, [asdict(entry) for entry in self._entries])
        except StorageError as error:
            logger.error("Failed to save history: %s", error)