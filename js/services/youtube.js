/*
HolyricsExtractor: A lightweight tool to search, extract, and format song lyrics for Holyrics.
Copyright (C) 2026 @xorodev (CipherCoreDev)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

Third-Party Dependencies & Credits:
- Built with Python (https://www.python.org/)
- Metadata extraction powered by yt-dlp (https://github.com/yt-dlp/yt-dlp)
- HTTP requests powered by Requests (https://requests.readthedocs.io)
- Lyrics API provided by LRCLIB (https://lrclib.net)
- Graphic Assets & Icons: Created from scratch by @xorodev

GitHub: https://github.com/xorodev/HolyricsExtractor
Contact:
a. Email: corex.dev@proton.me
b. Telegram: https://t.me/xorodev
*/
import { YOUTUBE_OEMBED_URL } from '../config/constants.js';
import { ServiceResponseError, UnsupportedLinkError, YouTubeResolutionError } from '../core/errors.js';
import { fetchJson } from './http.js';

const YOUTUBE_DOMAINS = Object.freeze(['youtube.com', 'youtube-nocookie.com', 'youtu.be']);
const SHORT_LINK_DOMAIN = 'youtu.be';
const VIDEO_ID_PATH_PREFIXES = new Set(['shorts', 'embed', 'live', 'v']);
const VIDEO_ID_RE = /^[A-Za-z0-9_-]{11}$/;
const HTTP_SCHEME_RE = /^https?:\/\//i;
const WHITESPACE_RE = /\s/;

export const QueryKind = Object.freeze({
  TITLE: 'title',
  YOUTUBE_LINK: 'youtube_link',
  OTHER_LINK: 'other_link',
});

function parseUrl(candidate) {
  try {
    return new URL(candidate.includes('://') ? candidate : `https://${candidate}`);
  } catch {
    return null;
  }
}

function hostMatches(host, domain) {
  return host === domain || host.endsWith(`.${domain}`);
}

export function classifyQuery(text) {
  const candidate = text.trim();
  if (!candidate || WHITESPACE_RE.test(candidate)) return QueryKind.TITLE;
  const url = parseUrl(candidate);
  if (url !== null && (url.protocol === 'http:' || url.protocol === 'https:')) {
    if (YOUTUBE_DOMAINS.some((domain) => hostMatches(url.hostname, domain))) return QueryKind.YOUTUBE_LINK;
  }
  return HTTP_SCHEME_RE.test(candidate) ? QueryKind.OTHER_LINK : QueryKind.TITLE;
}

export function extractVideoId(link) {
  const url = parseUrl(link.trim());
  if (url === null) throw new UnsupportedLinkError('Malformed link');
  const segments = url.pathname.split('/').filter(Boolean);
  let candidate;
  if (hostMatches(url.hostname, SHORT_LINK_DOMAIN)) {
    candidate = segments[0] ?? '';
  } else if (segments.length > 1 && VIDEO_ID_PATH_PREFIXES.has(segments[0])) {
    candidate = segments[1];
  } else {
    candidate = url.searchParams.get('v') ?? '';
  }
  if (!VIDEO_ID_RE.test(candidate)) throw new UnsupportedLinkError('The link does not contain a valid video id');
  return candidate;
}

function canonicalVideoUrl(videoId) {
  return `https://www.youtube.com/watch?v=${videoId}`;
}

async function fetchOembed(videoUrl, signal) {
  let payload;
  try {
    payload = await fetchJson(YOUTUBE_OEMBED_URL, { url: videoUrl, format: 'json' }, signal);
  } catch (error) {
    if (error instanceof ServiceResponseError) return null;
    throw error;
  }
  if (payload === null || typeof payload !== 'object' || Array.isArray(payload)) return null;
  const { title, author_name: author } = payload;
  if (typeof title !== 'string' || !title.trim()) return null;
  return { title: title.trim(), channel: typeof author === 'string' ? author.trim() : '' };
}

export async function resolveVideo(link, signal) {
  const metadata = await fetchOembed(canonicalVideoUrl(extractVideoId(link)), signal);
  if (metadata === null) {
    throw new YouTubeResolutionError(
      'Embed could not resolve the video',
      'No fue posible obtener la información del video de YouTube. Escriba el título de la canción para buscarla manualmente.',
    );
  }
  return metadata;
}