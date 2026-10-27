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
import queue
import threading
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Callable
from .errors import OperationCancelled

class CancellationToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        if self._event.is_set():
            raise OperationCancelled()

@dataclass(frozen=True, slots=True)

class Progress:
    message: str
    fraction: float | None = None

ProgressReporter = Callable[[str, float | None], None]
Work = Callable[[ProgressReporter, CancellationToken], Any]

@dataclass(slots=True)
class _ActiveTask:
    task_id: int
    token: CancellationToken
    on_progress: Callable[[Progress], None] | None
    on_success: Callable[[Any], None]
    on_failure: Callable[[Exception], None]
    on_cancelled: Callable[[], None] | None

class TaskRunner:
    POLL_INTERVAL_MS = 40

    def __init__(self, root: tk.Misc) -> None:
        self._root = root
        self._messages: queue.Queue[tuple[int, str, Any]] = queue.Queue()
        self._active: _ActiveTask | None = None
        self._next_id = 0
        self._poll_job: str | None = None

    @property
    def is_busy(self) -> bool:
        return self._active is not None

    def start(
        self,
        work: Work,
        *,
        on_success: Callable[[Any], None],
        on_failure: Callable[[Exception], None],
        on_progress: Callable[[Progress], None] | None = None,
        on_cancelled: Callable[[], None] | None = None,
    ) -> bool:
        if self._active is not None:
            return False
        self._drain()
        self._next_id += 1
        token = CancellationToken()
        self._active = _ActiveTask(self._next_id, token, on_progress, on_success, on_failure, on_cancelled)
        threading.Thread(target=self._run, args=(self._next_id, work, token), daemon=True).start()
        self._schedule_poll()
        return True

    def cancel(self) -> None:
        active = self._active
        if active is None:
            return
        active.token.cancel()
        self._active = None
        if active.on_cancelled is not None:
            active.on_cancelled()

    def _run(self, task_id: int, work: Work, token: CancellationToken) -> None:
        def report(message: str, fraction: float | None = None) -> None:
            self._messages.put((task_id, "progress", Progress(message, fraction)))

        try:
            result = work(report, token)
        except OperationCancelled:
            self._messages.put((task_id, "cancelled", None))
        except Exception as error:
            self._messages.put((task_id, "failure", error))
        else:
            self._messages.put((task_id, "success", result))

    def _schedule_poll(self) -> None:
        if self._poll_job is None:
            self._poll_job = self._root.after(self.POLL_INTERVAL_MS, self._poll)

    def _poll(self) -> None:
        self._poll_job = None
        try:
            while True:
                try:
                    task_id, kind, payload = self._messages.get_nowait()
                except queue.Empty:
                    break
                self._dispatch(task_id, kind, payload)
        finally:
            if self._active is not None:
                self._schedule_poll()

    def _dispatch(self, task_id: int, kind: str, payload: Any) -> None:
        active = self._active
        if active is None or active.task_id != task_id:
            return
        if kind == "progress":
            if active.on_progress is not None:
                active.on_progress(payload)
            return
        self._active = None
        if kind == "success":
            active.on_success(payload)
        elif kind == "failure":
            active.on_failure(payload)
        elif active.on_cancelled is not None:
            active.on_cancelled()

    def _drain(self) -> None:
        while True:
            try:
                self._messages.get_nowait()
            except queue.Empty:
                return