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
import time
import tkinter as tk
from typing import Callable

FRAME_INTERVAL_MS = 16

FrameHandler = Callable[[float], None]
DoneHandler = Callable[[], None]

def ease_out_cubic(progress: float) -> float:
    return 1 - (1 - progress) ** 3

class Animation:
    def __init__(
        self, widget: tk.Misc, duration_ms: int, on_frame: FrameHandler, on_done: DoneHandler | None = None
    ):
        self._widget = widget
        self._duration_ms = duration_ms
        self._on_frame = on_frame
        self._on_done = on_done
        self._job: str | None = None
        self._started_at = 0.0
        self._running = False

    def start(self) -> None:
        self._running = True
        self._started_at = time.monotonic()
        self._step()

    def cancel(self) -> None:
        self._running = False
        if self._job is None:
            return
        try:
            self._widget.after_cancel(self._job)
        except tk.TclError:
            pass
        self._job = None

    def _step(self) -> None:
        self._job = None
        if not self._running:
            return
        elapsed_ms = (time.monotonic() - self._started_at) * 1000
        progress = 1.0 if self._duration_ms <= 0 else min(elapsed_ms / self._duration_ms, 1.0)
        try:
            self._on_frame(ease_out_cubic(progress))
            if progress < 1.0:
                self._job = self._widget.after(FRAME_INTERVAL_MS, self._step)
                return
            self._running = False
            if self._on_done is not None:
                self._on_done()
        except tk.TclError:
            self._running = False