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
const CONTROL_CHARACTERS_RE = /[\x00-\x1f\x7f-\x9f]/g;
const CONTROL_EXCEPT_NEWLINE_RE = /[\x00-\x09\x0b-\x1f\x7f-\x9f]/g;
const EXTRA_BLANK_LINES_RE = /\n{3,}/g;
const LINE_BREAK_RE = /\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/;
const LONE_SURROGATE_RE = /[\ud800-\udfff]/;
const REPLACEMENT_CHARACTER = '\ufffd';

function toWellFormedCharacter(character) {
  return character.length === 1 && LONE_SURROGATE_RE.test(character) ? REPLACEMENT_CHARACTER : character;
}

export function clamp(text, maxLength) {
  return Array.from(text, toWellFormedCharacter).slice(0, maxLength).join('');
}

export function codePointLength(text) {
  return Array.from(text).length;
}

export function ellipsize(text, maxLength) {
  return codePointLength(text) > maxLength ? `${clamp(text, maxLength - 1)}…` : text;
}

export function splitLines(text) {
  return String(text).split(LINE_BREAK_RE);
}

export function sanitizeSingleLine(text, maxLength) {
  const collapsed = String(text).split(/\s+/).filter(Boolean).join(' ');
  return clamp(collapsed.replace(CONTROL_CHARACTERS_RE, ''), maxLength).trim();
}

export function sanitizeMultiline(text, maxLength) {
  const normalized = String(text).replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/\t/g, ' ');
  const cleaned = normalized.replace(CONTROL_EXCEPT_NEWLINE_RE, '');
  const lines = cleaned
    .split('\n')
    .map((line) => line.trimEnd())
    .join('\n');
  return clamp(lines.replace(EXTRA_BLANK_LINES_RE, '\n\n'), maxLength).trim();
}