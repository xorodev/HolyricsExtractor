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
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..constants import MAX_LOG_MESSAGE_LENGTH
from .file_lock import unlocked
from .sanitizer import sanitize_single_line

ROOT_LOGGER_NAME = "holyrics"
LOG_FILE_NAME = "logs.txt"
MAX_LOG_BYTES = 1_000_000

class SanitizingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.msg = sanitize_single_line(record.getMessage(), MAX_LOG_MESSAGE_LENGTH)
        record.args = ()
        return super().format(record)

class ProtectedRotatingFileHandler(RotatingFileHandler):
    def emit(self, record: logging.LogRecord) -> None:
        base = Path(self.baseFilename)
        with unlocked(base, base.with_name(f"{base.name}.1")):
            super().emit(record)
            if self.stream is not None:
                try:
                    self.stream.close()
                except OSError:
                    pass
                self.stream = None

def configure_logging(directory: Path) -> Path:
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    log_path = directory / LOG_FILE_NAME
    try:
        directory.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = ProtectedRotatingFileHandler(
            log_path, maxBytes=MAX_LOG_BYTES, backupCount=1, encoding="utf-8", delay=True
        )
    except OSError:
        handler = logging.NullHandler()
    handler.setFormatter(SanitizingFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    return log_path

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")