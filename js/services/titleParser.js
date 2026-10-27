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
const TAG_PATTERN =
  '(?:official\\s*music\\s*video|official\\s*video|official\\s*audio|' +
  'video\\s*oficial|audio\\s*oficial|lyric\\s*video|lyrics?|letra|' +
  'official|oficial|video|audio|visualizer|hd|4k|mv)';

const TAG_KEYWORDS_RE = new RegExp(`\\b${TAG_PATTERN}\\b`, 'i');
const BRACKET_GROUP_RE = /[(\[][^()\[\]]*[)\]]/g;
const TRAILING_TAG_RE = new RegExp(`\\s*(?:[-|:]\\s*)?${TAG_PATTERN}\\s*$`, 'i');
const MULTI_SPACE_RE = /\s{2,}/g;
const ARTIST_TITLE_SEPARATOR_RE = /\s+[-–—|]\s+/;
const TOPIC_SUFFIX_RE = /\s+-\s+Topic$/i;
const EDGE_SEPARATORS_RE = /^[ \-|:]+|[ \-|:]+$/g;

export function cleanTitle(title) {
  const withoutTags = title.replace(BRACKET_GROUP_RE, (group) => (TAG_KEYWORDS_RE.test(group) ? '' : group));
  return withoutTags
    .replace(TRAILING_TAG_RE, '')
    .replace(MULTI_SPACE_RE, ' ')
    .replace(EDGE_SEPARATORS_RE, '')
    .trim();
}

export function splitTitleAndArtist(title) {
  const separator = ARTIST_TITLE_SEPARATOR_RE.exec(title);
  if (separator !== null) {
    const artist = title.slice(0, separator.index).trim();
    const track = title.slice(separator.index + separator[0].length).trim();
    if (artist && track) return { track, artist };
  }
  return { track: title.trim(), artist: '' };
}

export function cleanChannelName(channel) {
  return channel.trim().replace(TOPIC_SUFFIX_RE, '').trim();
}