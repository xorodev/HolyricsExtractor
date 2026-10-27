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
from dataclasses import dataclass
from ..constants import EXPORT_SEPARATOR

Slide = tuple[str, ...]

@dataclass(frozen=True, slots=True)

class LyricsResult:
    title: str
    artist: str
    slides: tuple[Slide, ...]

    @property
    def total_slides(self) -> int:
        return len(self.slides)

    @property
    def formatted_text(self) -> str:
        return "\n\n".join("\n".join(slide) for slide in self.slides)

    @property
    def export_text(self) -> str:
        return f"\n{EXPORT_SEPARATOR}\n".join("\n".join(slide) for slide in self.slides)

    @classmethod
    def from_formatted_text(cls, title: str, artist: str, text: str) -> LyricsResult:
        blocks = (block for block in text.split("\n\n") if block.strip())
        slides = tuple(tuple(block.split("\n")) for block in blocks)
        return cls(title, artist, slides)