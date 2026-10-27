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
import { LRCLIB_SEARCH_URL } from '../config/constants.js';
import { ServiceResponseError } from '../core/errors.js';
import { textSimilarity } from '../core/similarity.js';
import { splitLines } from '../core/text.js';
import { fetchJson } from './http.js';

const MAX_CANDIDATES = 20;
const TITLE_WEIGHT = 0.7;
const ARTIST_WEIGHT = 0.3;
const TIMESTAMP_PREFIX_RE = /^\s*(?:\[\d{1,3}:\d{2}(?:[.:]\d{1,3})?\]\s*)+/;
const METADATA_LINE_RE = /^\s*\[[A-Za-z]+:[^\]]*\]\s*$/;

function stripSyncedLyrics(synced) {
  return splitLines(synced)
    .filter((line) => !METADATA_LINE_RE.test(line))
    .map((line) => line.replace(TIMESTAMP_PREFIX_RE, '').trim())
    .join('\n');
}

function extractLyrics(item) {
  if (item.instrumental === true) return null;
  if (typeof item.plainLyrics === 'string' && item.plainLyrics.trim()) return item.plainLyrics;
  if (typeof item.syncedLyrics === 'string' && item.syncedLyrics.trim()) {
    const stripped = stripSyncedLyrics(item.syncedLyrics);
    return stripped.trim() ? stripped : null;
  }
  return null;
}

function scoreCandidate(item, track, artist) {
  const trackName = item.trackName || item.name || '';
  const titleScore = typeof trackName === 'string' ? textSimilarity(track, trackName) : 0;
  if (!artist) return titleScore;
  const artistScore = typeof item.artistName === 'string' ? textSimilarity(artist, item.artistName) : 0;
  return TITLE_WEIGHT * titleScore + ARTIST_WEIGHT * artistScore;
}

function buildQueryPlan(track, artist) {
  const plan = [];
  if (artist) {
    plan.push({ track_name: track, artist_name: artist });
    plan.push({ q: `${artist} ${track}` });
  }
  plan.push({ q: track });
  return plan;
}

async function searchOnce(params, track, artist, signal) {
  const payload = await fetchJson(LRCLIB_SEARCH_URL, params, signal);
  if (payload === null) return null;
  if (!Array.isArray(payload)) throw new ServiceResponseError('LRCLIB search returned a non-list payload');

  let bestLyrics = null;
  let bestScore = -1;
  for (const item of payload.slice(0, MAX_CANDIDATES)) {
    if (item === null || typeof item !== 'object' || Array.isArray(item)) continue;
    const lyrics = extractLyrics(item);
    if (lyrics === null) continue;
    const score = scoreCandidate(item, track, artist);
    if (score > bestScore) {
      bestLyrics = lyrics;
      bestScore = score;
    }
  }
  return bestLyrics;
}

export async function searchLyrics(track, artist, signal) {
  for (const params of buildQueryPlan(track, artist)) {
    signal.throwIfAborted();
    const lyrics = await searchOnce(params, track, artist, signal);
    if (lyrics) return lyrics;
  }
  return null;
}