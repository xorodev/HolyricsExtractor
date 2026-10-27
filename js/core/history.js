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
import {
  MAX_ARTIST_LENGTH,
  MAX_HISTORY_ENTRIES,
  MAX_HISTORY_TEXT_LENGTH,
  MAX_QUERY_LENGTH,
  STORAGE_KEYS,
} from '../config/constants.js';
import { readJson, writeJson } from './storage.js';

const isText = (value) => typeof value === 'string';

function entryKey(entry) {
  return JSON.stringify([entry.title.toLowerCase(), entry.artist.toLowerCase()]);
}

function parseEntry(raw) {
  if (raw === null || typeof raw !== 'object') return null;
  const { title, artist = '', text } = raw;
  if (!isText(title) || !isText(artist) || !isText(text)) return null;
  if (!title.trim() || !text.trim()) return null;
  if (title.length > MAX_QUERY_LENGTH || artist.length > MAX_ARTIST_LENGTH || text.length > MAX_HISTORY_TEXT_LENGTH) {
    return null;
  }
  return Object.freeze({ title, artist, text });
}

function parseEntries(rawEntries) {
  const entries = [];
  const seen = new Set();
  for (const raw of rawEntries) {
    const entry = parseEntry(raw);
    if (entry === null || seen.has(entryKey(entry))) continue;
    seen.add(entryKey(entry));
    entries.push(entry);
    if (entries.length >= MAX_HISTORY_ENTRIES) break;
  }
  return entries;
}

export class HistoryStore {
  #entries;

  constructor() {
    const stored = readJson(STORAGE_KEYS.HISTORY);
    this.#entries = parseEntries(Array.isArray(stored) ? stored : []);
  }

  get entries() {
    return [...this.#entries];
  }

  add(title, artist, text) {
    const entry = Object.freeze({ title, artist, text });
    this.#entries = [entry, ...this.#entries.filter((item) => entryKey(item) !== entryKey(entry))].slice(
      0,
      MAX_HISTORY_ENTRIES,
    );
    this.#persist();
  }

  clear() {
    this.#entries = [];
    this.#persist();
  }

  #persist() {
    writeJson(STORAGE_KEYS.HISTORY, this.#entries);
  }
}