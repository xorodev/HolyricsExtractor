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
import sys
import tkinter as tk
from dataclasses import dataclass
from typing import Callable

IS_MAC = sys.platform == "darwin"
MODIFIER_LABEL = "Cmd" if IS_MAC else "Ctrl"
_MODIFIER_EVENT = "Command" if IS_MAC else "Control"
_PRIMARY_KEY = "Mod"

@dataclass(frozen=True, slots=True)

class Shortcut:
    keys: tuple[str, ...]
    description: str
    handler: Callable[[], None] | None = None

    @property
    def label_parts(self) -> tuple[str, ...]:
        return tuple(MODIFIER_LABEL if key == _PRIMARY_KEY else key for key in self.keys)

    @property
    def label(self) -> str:
        return " + ".join(self.label_parts)

    @property
    def sequences(self) -> tuple[str, ...]:
        *modifiers, final = self.keys
        prefix = [_MODIFIER_EVENT if key == _PRIMARY_KEY else key for key in modifiers]
        finals = (final.lower(), final.upper()) if len(final) == 1 else (final,)
        return tuple("<" + "-".join([*prefix, key]) + ">" for key in dict.fromkeys(finals))

def bind_shortcuts(window: tk.Misc, shortcuts: tuple[Shortcut, ...]) -> None:
    for shortcut in shortcuts:
        if shortcut.handler is None:
            continue
        for sequence in shortcut.sequences:
            window.bind(sequence, lambda _event, handler=shortcut.handler: handler())