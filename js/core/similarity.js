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
const NON_WORD_RE = /[^\p{L}\p{N}]+/gu;

function normalize(text) {
  return Array.from(text.toLowerCase().replace(NON_WORD_RE, ' ').trim());
}

function findLongestMatch(left, right, leftLow, leftHigh, rightLow, rightHigh) {
  let bestLeft = leftLow;
  let bestRight = rightLow;
  let bestSize = 0;
  let previous = new Array(rightHigh - rightLow + 1).fill(0);
  for (let i = leftLow; i < leftHigh; i += 1) {
    const current = new Array(rightHigh - rightLow + 1).fill(0);
    for (let j = rightLow; j < rightHigh; j += 1) {
      if (left[i] !== right[j]) continue;
      const size = previous[j - rightLow] + 1;
      current[j - rightLow + 1] = size;
      if (size > bestSize) {
        bestLeft = i - size + 1;
        bestRight = j - size + 1;
        bestSize = size;
      }
    }
    previous = current;
  }
  return [bestLeft, bestRight, bestSize];
}

function countMatches(left, right) {
  const pending = [[0, left.length, 0, right.length]];
  let total = 0;
  while (pending.length > 0) {
    const [leftLow, leftHigh, rightLow, rightHigh] = pending.pop();
    const [i, j, size] = findLongestMatch(left, right, leftLow, leftHigh, rightLow, rightHigh);
    if (size === 0) continue;
    total += size;
    if (leftLow < i && rightLow < j) pending.push([leftLow, i, rightLow, j]);
    if (i + size < leftHigh && j + size < rightHigh) pending.push([i + size, leftHigh, j + size, rightHigh]);
  }
  return total;
}

export function textSimilarity(first, second) {
  const left = normalize(first);
  const right = normalize(second);
  const length = left.length + right.length;
  return length === 0 ? 1 : (2 * countMatches(left, right)) / length;
}