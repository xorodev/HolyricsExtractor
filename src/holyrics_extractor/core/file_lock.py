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
import contextlib
import os
import stat
import threading
from pathlib import Path
from typing import Iterator

_WRITE_BITS = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
_GUARD = threading.RLock()

def is_locked(path: Path) -> bool:
    try:
        return path.is_file() and not (path.stat().st_mode & stat.S_IWUSR)
    except OSError:
        return False

def lock_file(path: Path) -> bool:
    try:
        os.chmod(path, path.stat().st_mode & ~_WRITE_BITS)
        return True
    except OSError:
        return False

def unlock_file(path: Path) -> bool:
    try:
        os.chmod(path, path.stat().st_mode | stat.S_IWUSR)
        return True
    except OSError:
        return False

@contextlib.contextmanager
def unlocked(*paths: Path) -> Iterator[None]:
    with _GUARD:
        for path in paths:
            if is_locked(path):
                unlock_file(path)
        try:
            yield
        finally:
            for path in paths:
                if path.is_file():
                    lock_file(path)