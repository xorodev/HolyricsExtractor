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
import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import ParseResult, parse_qs, urlparse
import requests
from ..constants import YOUTUBE_OEMBED_URL
from ..core.errors import ServiceResponseError, UnsupportedLinkError, YouTubeResolutionError
from ..core.logging_service import get_logger
from ..core.tasks import CancellationToken
from .http import fetch_json
from .ytdlp_component import YtDlpComponent

logger = get_logger("youtube")

_YOUTUBE_DOMAINS = ("youtube.com", "youtube-nocookie.com", "youtu.be")
_SHORT_LINK_DOMAIN = "youtu.be"
_VIDEO_ID_PATH_PREFIXES = frozenset({"shorts", "embed", "live", "v"})
_VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
_HTTP_SCHEME_RE = re.compile(r"^https?://", re.IGNORECASE)

class QueryKind(Enum):
    TITLE = "title"
    YOUTUBE_LINK = "youtube_link"
    OTHER_LINK = "other_link"

@dataclass(frozen=True, slots=True)

class VideoMetadata:
    title: str
    channel: str

def _parse(candidate: str) -> ParseResult | None:
    try:
        return urlparse(candidate if "://" in candidate else f"https://{candidate}")
    except ValueError:
        return None

def _host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")

def classify_query(text: str) -> QueryKind:
    candidate = text.strip()
    if not candidate or len(candidate.split()) > 1:
        return QueryKind.TITLE
    parsed = _parse(candidate)
    if parsed is not None and parsed.scheme in ("http", "https"):
        host = (parsed.hostname or "").lower()
        if any(_host_matches(host, domain) for domain in _YOUTUBE_DOMAINS):
            return QueryKind.YOUTUBE_LINK
    if _HTTP_SCHEME_RE.match(candidate):
        return QueryKind.OTHER_LINK
    return QueryKind.TITLE

def extract_video_id(link: str) -> str:
    parsed = _parse(link.strip())
    if parsed is None:
        raise UnsupportedLinkError("Malformed link")
    host = (parsed.hostname or "").lower()
    segments = [segment for segment in parsed.path.split("/") if segment]
    if _host_matches(host, _SHORT_LINK_DOMAIN):
        candidate = segments[0] if segments else ""
    elif len(segments) > 1 and segments[0] in _VIDEO_ID_PATH_PREFIXES:
        candidate = segments[1]
    else:
        candidate = parse_qs(parsed.query).get("v", [""])[0]
    if not _VIDEO_ID_RE.fullmatch(candidate):
        raise UnsupportedLinkError("The link does not contain a valid video id")
    return candidate

def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"

class YouTubeResolver:
    def __init__(self, session: requests.Session, ytdlp: YtDlpComponent):
        self._session = session
        self._ytdlp = ytdlp

    def resolve(self, link: str, token: CancellationToken) -> VideoMetadata:
        video_url = canonical_video_url(extract_video_id(link))
        metadata = self._from_oembed(video_url, token)
        if metadata is None:
            raw = self._ytdlp.extract_metadata(video_url, token)
            if raw is not None and raw[0].strip():
                metadata = VideoMetadata(raw[0].strip(), raw[1].strip())
        if metadata is None:
            raise YouTubeResolutionError("No metadata source could resolve the video")
        return metadata

    def _from_oembed(self, video_url: str, token: CancellationToken) -> VideoMetadata | None:
        try:
            payload = fetch_json(
                self._session,
                YOUTUBE_OEMBED_URL,
                params={"url": video_url, "format": "json"},
                token=token,
            )
        except ServiceResponseError as error:
            logger.info("Embed unavailable for this video: %s", error)
            return None
        if not isinstance(payload, dict):
            return None
        title = payload.get("title")
        author = payload.get("author_name")
        if not isinstance(title, str) or not title.strip():
            return None
        return VideoMetadata(title.strip(), author.strip() if isinstance(author, str) else "")