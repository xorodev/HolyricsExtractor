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
export const APP_NAME = 'Extractor de Letras para Holyrics';
export const APP_VERSION = 'v1.0.0-stable';
export const APP_LICENSE = 'GNU GPLv3.0';
export const APP_AUTHOR = '@xorodev (CipherCoreDev)';

export const LRCLIB_SEARCH_URL = 'https://lrclib.net/api/search';
export const YOUTUBE_OEMBED_URL = 'https://www.youtube.com/oembed';

export const SUPPORT_WHATSAPP_NUMBER = '50497764448';
export const SUPPORT_WHATSAPP_DISPLAY = '+504 9776-4448';
export const SUPPORT_EMAIL = 'wilfredorb0218@gmail.com';

export const DEVELOPER_LINKS = Object.freeze([
  Object.freeze({ label: 'Licencia:', text: 'Clic aquí.', url: 'https://www.gnu.org/licenses/gpl-3.0.txt' }),
  Object.freeze({ label: 'GitHub:', text: 'Clic aquí.', url: 'https://github.com/xorodev' }),
  Object.freeze({ label: 'Telegram:', text: 'Clic aquí.', url: 'https://t.me/xorodev' }),
  Object.freeze({ label: 'Instagram:', text: 'Clic aquí.', url: 'https://instagram.com/xorodev' }),
  Object.freeze({ label: 'Gmail:', text: 'wilfredorb0218@gmail.com', url: 'mailto:wilfredorb0218@gmail.com' }),
  Object.freeze({ label: 'Hotmail:', text: 'wilfredorb.dev@hotmail.com', url: 'mailto:wilfredorb.dev@hotmail.com' }),
]);

export const STORAGE_KEYS = Object.freeze({
  SETTINGS: 'holyricsExtractor.settings',
  HISTORY: 'holyricsExtractor.history',
});

export const MAX_QUERY_LENGTH = 300;
export const MAX_ARTIST_LENGTH = 120;
export const MAX_SUPPORT_MESSAGE_LENGTH = 1000;
export const MAX_HISTORY_ENTRIES = 10;
export const MAX_HISTORY_TEXT_LENGTH = 200_000;
export const MAX_STORAGE_BYTES = 5_000_000;
export const MAX_API_RESPONSE_BYTES = 2_000_000;
export const CLIPBOARD_READ_LIMIT = 2_000;
export const HISTORY_LABEL_LENGTH = 60;

export const REQUEST_TIMEOUT_MS = 12_000;
export const MAX_RETRIES = 2;
export const RETRY_BACKOFF_MS = 400;
export const RETRYABLE_STATUSES = Object.freeze([429, 500, 502, 503, 504]);

export const SLIDE_MAX_LINES = 5;
export const SLIDE_BLOCK_TARGET_LINES = 4;
export const SLIDE_REPEAT_MARK = '//';
export const EXPORT_SEPARATOR = '-'.repeat(14);

export const TICK_INTERVAL_MS = 500;
export const ELAPSED_VISIBLE_AFTER_SECONDS = 3;
export const TOAST_DURATION_MS = 3_000;
export const OBJECT_URL_REVOKE_DELAY_MS = 1_000;