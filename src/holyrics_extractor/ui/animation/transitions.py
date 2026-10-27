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
import tkinter as tk
from typing import Callable
from ...core.settings import ANIMATION_HOVER, ANIMATION_WINDOWS
from .animator import Animation
from .colors import blend_colors, is_hex_color
from .motion import Motion

HOVER_TRANSITION_MS = 140
WINDOW_FADE_MS = 170

class HoverTransition:
    def __init__(self, widget: tk.Misc, motion: Motion, apply_color: Callable[[str], None]):
        self._widget = widget
        self._motion = motion
        self._apply_color = apply_color
        self._animation: Animation | None = None

    def run(self, current: str, target: str) -> None:
        self.cancel()
        if current == target:
            return
        if not (is_hex_color(current) and is_hex_color(target)):
            self._apply_color(target)
            return
        self._animation = self._motion.animate(
            self._widget,
            ANIMATION_HOVER,
            HOVER_TRANSITION_MS,
            lambda progress: self._apply_color(blend_colors(current, target, progress)),
        )

    def cancel(self) -> None:
        if self._animation is not None:
            self._animation.cancel()
            self._animation = None

class WindowFade:
    def __init__(self, window: tk.Wm, motion: Motion):
        self._window = window
        self._motion = motion
        self._animation: Animation | None = None
        self._prepared = False

    def prepare(self) -> None:
        self._prepared = self._motion.duration(ANIMATION_WINDOWS, WINDOW_FADE_MS) > 0 and self._set_alpha(0.0)

    def play(self) -> None:
        if not self._prepared:
            return
        self._prepared = False
        self._animation = self._motion.animate(self._window, ANIMATION_WINDOWS, WINDOW_FADE_MS, self._set_alpha)

    def cancel(self) -> None:
        if self._animation is not None:
            self._animation.cancel()
            self._animation = None

    def _set_alpha(self, alpha: float) -> bool:
        try:
            self._window.attributes("-alpha", alpha)
        except tk.TclError:
            return False
        return True