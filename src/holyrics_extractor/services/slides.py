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
from ..constants import SLIDE_BLOCK_TARGET_LINES, SLIDE_MAX_LINES, SLIDE_REPEAT_MARK
from .models import Slide

def build_slides(raw_lyrics: str) -> tuple[Slide, ...]:
    lines = [line.strip() for line in raw_lyrics.splitlines()]
    stanzas = _group_stanzas(lines)
    if len(stanzas) == 1 and len(stanzas[0]) > SLIDE_MAX_LINES:
        slides = _split_balanced(stanzas[0], SLIDE_BLOCK_TARGET_LINES)
    else:
        slides = [chunk for stanza in stanzas for chunk in _split_balanced(stanza, SLIDE_MAX_LINES)]
    return _mark_repeated(slides)

def _group_stanzas(lines: list[str]) -> list[list[str]]:
    stanzas: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line:
            current.append(line)
        elif current:
            stanzas.append(current)
            current = []
    if current:
        stanzas.append(current)
    return stanzas

def _split_balanced(lines: list[str], max_size: int) -> list[Slide]:
    total = len(lines)
    if total <= max_size:
        return [tuple(lines)]
    groups = -(-total // max_size)
    base, remainder = divmod(total, groups)
    slides: list[Slide] = []
    index = 0
    for position in range(groups):
        size = base + 1 if position < remainder else base
        slides.append(tuple(lines[index:index + size]))
        index += size
    return slides

def _mark_repeated(slides: list[Slide]) -> tuple[Slide, ...]:
    first_seen: dict[tuple[str, ...], int] = {}
    repeated_firsts: set[int] = set()
    duplicates: set[int] = set()

    for index, slide in enumerate(slides):
        key = tuple(line.casefold() for line in slide)
        if key in first_seen:
            repeated_firsts.add(first_seen[key])
            duplicates.add(index)
        else:
            first_seen[key] = index

    result: list[Slide] = []
    for index, slide in enumerate(slides):
        if index in duplicates:
            continue
        if index in repeated_firsts:
            marked = list(slide)
            marked[0] = f"{SLIDE_REPEAT_MARK} {marked[0]}"
            marked[-1] = f"{marked[-1]} {SLIDE_REPEAT_MARK}"
            slide = tuple(marked)
        result.append(slide)
    return tuple(result)