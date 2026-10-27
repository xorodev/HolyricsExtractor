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
function pad(value) {
  return String(value).padStart(2, '0');
}

function formatDate(date, separator) {
  return `${date.getFullYear()}${separator}${pad(date.getMonth() + 1)}${separator}${pad(date.getDate())}`;
}

function formatTime(date, separator) {
  return `${pad(date.getHours())}${separator}${pad(date.getMinutes())}${separator}${pad(date.getSeconds())}`;
}

export function formatTimestamp(date) {
  return `${formatDate(date, '-')} ${formatTime(date, ':')}`;
}

export function formatFileStamp(date) {
  return `${formatDate(date, '')}_${formatTime(date, '')}`;
}