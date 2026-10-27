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
import { SLIDE_BLOCK_TARGET_LINES, SLIDE_MAX_LINES, SLIDE_REPEAT_MARK } from '../config/constants.js';
import { splitLines } from '../core/text.js';

function groupStanzas(lines) {
  const stanzas = [];
  let current = [];
  for (const line of lines) {
    if (line) {
      current.push(line);
    } else if (current.length > 0) {
      stanzas.push(current);
      current = [];
    }
  }
  if (current.length > 0) stanzas.push(current);
  return stanzas;
}

function splitBalanced(lines, maxSize) {
  const total = lines.length;
  if (total <= maxSize) return [lines];
  const groups = Math.ceil(total / maxSize);
  const base = Math.floor(total / groups);
  const remainder = total % groups;
  const slides = [];
  let index = 0;
  for (let position = 0; position < groups; position += 1) {
    const size = position < remainder ? base + 1 : base;
    slides.push(lines.slice(index, index + size));
    index += size;
  }
  return slides;
}

function markRepeated(slides) {
  const firstSeen = new Map();
  const repeatedFirsts = new Set();
  const duplicates = new Set();

  slides.forEach((slide, index) => {
    const key = JSON.stringify(slide.map((line) => line.toLowerCase()));
    if (firstSeen.has(key)) {
      repeatedFirsts.add(firstSeen.get(key));
      duplicates.add(index);
    } else {
      firstSeen.set(key, index);
    }
  });

  const result = [];
  slides.forEach((slide, index) => {
    if (duplicates.has(index)) return;
    if (!repeatedFirsts.has(index)) {
      result.push(slide);
      return;
    }
    const marked = [...slide];
    marked[0] = `${SLIDE_REPEAT_MARK} ${marked[0]}`;
    marked[marked.length - 1] = `${marked[marked.length - 1]} ${SLIDE_REPEAT_MARK}`;
    result.push(marked);
  });
  return result;
}

export function buildSlides(rawLyrics) {
  const lines = splitLines(rawLyrics).map((line) => line.trim());
  const stanzas = groupStanzas(lines);
  const slides =
    stanzas.length === 1 && stanzas[0].length > SLIDE_MAX_LINES
      ? splitBalanced(stanzas[0], SLIDE_BLOCK_TARGET_LINES)
      : stanzas.flatMap((stanza) => splitBalanced(stanza, SLIDE_MAX_LINES));
  return markRepeated(slides);
}