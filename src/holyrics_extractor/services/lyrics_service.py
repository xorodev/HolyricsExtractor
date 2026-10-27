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
from ..constants import MAX_ARTIST_LENGTH, MAX_QUERY_LENGTH
from ..core.errors import InvalidInputError, LyricsNotFoundError, UnsupportedLinkError, YouTubeResolutionError
from ..core.logging_service import get_logger
from ..core.sanitizer import sanitize_single_line
from ..core.tasks import CancellationToken, ProgressReporter
from .lrclib import LrclibClient
from .models import LyricsResult
from .slides import build_slides
from .title_parser import clean_channel_name, clean_title, split_title_and_artist
from .youtube import QueryKind, YouTubeResolver, classify_query

logger = get_logger("lyrics")

def _validated(text: str, limit: int, label: str) -> str:
    cleaned = sanitize_single_line(text, limit + 1)
    if len(cleaned) > limit:
        raise InvalidInputError(
            f"{label} exceeds {limit} characters",
            f"El texto ingresado supera el máximo permitido de {limit} caracteres.",
        )
    return cleaned

class LyricsService:
    def __init__(self, resolver: YouTubeResolver, lrclib: LrclibClient):
        self._resolver = resolver
        self._lrclib = lrclib

    def find(self, query: str, artist: str, report: ProgressReporter, token: CancellationToken) -> LyricsResult:
        query = _validated(query, MAX_QUERY_LENGTH, "Query")
        artist = _validated(artist, MAX_ARTIST_LENGTH, "Artist")
        if not query:
            raise InvalidInputError(
                "Empty query",
                "Ingrese un enlace (URL) de YouTube válido o el título de una canción para continuar.",
            )

        track, artist = self._identify_track(query, artist, report, token)

        report("Buscando la letra en LRCLIB...", None)
        logger.info("Searching lyrics for track '%s' by '%s'", track, artist)
        lyrics = self._lrclib.find_lyrics(track, artist, token)
        if not lyrics:
            raise LyricsNotFoundError(
                f"No lyrics for '{track}' / '{artist}'",
                f"No fue posible encontrar la letra de la canción: '{track}'. "
                "Verifique el título o especifique el nombre del artista.",
            )

        report("Formateando las presentaciones...", None)
        slides = build_slides(lyrics)
        if not slides:
            raise LyricsNotFoundError(f"Lyrics for '{track}' contained no usable lines")
        logger.info("Lyrics formatted into %d slides", len(slides))
        return LyricsResult(track, artist, slides)

    def _identify_track(
        self, query: str, artist: str, report: ProgressReporter, token: CancellationToken
    ) -> tuple[str, str]:
        kind = classify_query(query)
        if kind is QueryKind.OTHER_LINK:
            raise UnsupportedLinkError("Link is not hosted on YouTube")
        if kind is QueryKind.TITLE:
            return query, artist

        report("Leyendo la información del video de YouTube...", None)
        metadata = self._resolver.resolve(query, token)
        track, detected_artist = split_title_and_artist(clean_title(metadata.title))
        if not track:
            raise YouTubeResolutionError("The video title is empty after cleanup")
        return track, artist or detected_artist or clean_channel_name(metadata.channel)