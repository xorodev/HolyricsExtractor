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
from pathlib import Path
from typing import Any
from .errors import StorageError
from .logging_service import get_logger
from .protected_files import ProtectedFiles
from .storage import read_json

logger = get_logger("settings")

THEME_DARK = "dark"
THEME_LIGHT = "light"
VALID_THEMES = (THEME_DARK, THEME_LIGHT)

ANIMATIONS_ENABLED = "animations_enabled"
ANIMATION_SPEED = "animation_speed"
ANIMATION_HOVER = "animation_hover"
ANIMATION_NOTIFICATIONS = "animation_notifications"
ANIMATION_WINDOWS = "animation_windows"
ANIMATION_RESULTS = "animation_results"

SPEED_SLOW = "slow"
SPEED_NORMAL = "normal"
SPEED_FAST = "fast"
VALID_ANIMATION_SPEEDS = (SPEED_SLOW, SPEED_NORMAL, SPEED_FAST)

_DEFAULTS: dict[str, Any] = {
    "first_run": True,
    "check_yt_dlp_updates": True,
    "check_app_updates": True,
    "theme": THEME_DARK,
    "pending_update_confirmation": None,
    ANIMATIONS_ENABLED: True,
    ANIMATION_SPEED: SPEED_NORMAL,
    ANIMATION_HOVER: True,
    ANIMATION_NOTIFICATIONS: True,
    ANIMATION_WINDOWS: True,
    ANIMATION_RESULTS: True,
}

_EXPECTED_TYPES: dict[str, tuple[type, ...]] = {
    "first_run": (bool,),
    "check_yt_dlp_updates": (bool,),
    "check_app_updates": (bool,),
    "theme": (str,),
    "pending_update_confirmation": (str, type(None)),
    ANIMATIONS_ENABLED: (bool,),
    ANIMATION_SPEED: (str,),
    ANIMATION_HOVER: (bool,),
    ANIMATION_NOTIFICATIONS: (bool,),
    ANIMATION_WINDOWS: (bool,),
    ANIMATION_RESULTS: (bool,),
}

_VALID_CHOICES: dict[str, tuple[str, ...]] = {
    "theme": VALID_THEMES,
    ANIMATION_SPEED: VALID_ANIMATION_SPEEDS,
}

class SettingsStore:
    def __init__(self, path: Path, files: ProtectedFiles):
        self._path = path
        self._files = files
        self._values: dict[str, Any] = dict(_DEFAULTS)
        self._legacy_history: list[Any] | None = None
        self._load()

    def _load(self) -> None:
        raw = read_json(self._path)
        if not isinstance(raw, dict):
            return
        for key, expected in _EXPECTED_TYPES.items():
            value = raw.get(key, _DEFAULTS[key])
            if isinstance(value, expected):
                self._values[key] = value
        for key, choices in _VALID_CHOICES.items():
            if self._values[key] not in choices:
                self._values[key] = _DEFAULTS[key]
        legacy = raw.get("search_history")
        if isinstance(legacy, list) and legacy:
            self._legacy_history = legacy

    def get(self, key: str) -> Any:
        return self._values[key]

    def set(self, key: str, value: Any) -> None:
        if key not in _EXPECTED_TYPES or not isinstance(value, _EXPECTED_TYPES[key]):
            raise ValueError(f"Invalid setting: {key}")
        if key in _VALID_CHOICES and value not in _VALID_CHOICES[key]:
            raise ValueError(f"Invalid value for setting: {key}")
        self._values[key] = value
        self._persist()

    def reset(self) -> None:
        self._values = dict(_DEFAULTS)
        self._legacy_history = None
        self._persist()

    def take_legacy_history(self) -> list[Any]:
        return list(self._legacy_history or [])

    def discard_legacy_history(self) -> None:
        if self._legacy_history is None:
            return
        self._legacy_history = None
        self._persist()

    def _persist(self) -> None:
        try:
            self._files.write_json(self._path, self._values)
        except StorageError as error:
            logger.error("Failed to save settings: %s", error)