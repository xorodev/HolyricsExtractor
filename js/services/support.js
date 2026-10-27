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
  APP_NAME,
  APP_VERSION,
  MAX_SUPPORT_MESSAGE_LENGTH,
  SUPPORT_EMAIL,
  SUPPORT_WHATSAPP_NUMBER,
} from '../config/constants.js';
import { clamp, sanitizeMultiline, sanitizeSingleLine } from '../core/text.js';

const ENCODED_LIMIT = 1_800;
const ELLIPSIS = '…';
const TRIM_RATIO = 0.9;
const DETAIL_LIMIT = 400;
const USER_AGENT_LIMIT = 200;

export function buildReportText(userMessage, error, includeSystemInfo) {
  const message = sanitizeMultiline(userMessage, MAX_SUPPORT_MESSAGE_LENGTH) || '(Sin descripción)';
  const sections = [`Hola, necesito ayuda con la aplicación: '${APP_NAME}'.`, '', 'Mensaje descriptivo:', message];
  if (error !== null) {
    sections.push(
      '',
      `Código de error: ${error.code}`,
      `Fecha del error: ${error.occurredAt}`,
      `Detalle técnico: ${sanitizeSingleLine(error.detail, DETAIL_LIMIT) || '¡No disponible!'}`,
    );
  }
  if (includeSystemInfo) {
    sections.push(
      '',
      `Versión de la aplicación: ${APP_VERSION}`,
      `Navegador: ${sanitizeSingleLine(navigator.userAgent, USER_AGENT_LIMIT)}`,
    );
  }
  return sections.join('\n');
}

function encodeWithinLimit(text, limit) {
  const encoded = encodeURIComponent(text);
  if (encoded.length <= limit) return encoded;
  const suffix = encodeURIComponent(ELLIPSIS);
  let trimmed = text;
  while (trimmed && encodeURIComponent(trimmed).length + suffix.length > limit) {
    trimmed = clamp(trimmed, Math.floor(Array.from(trimmed).length * TRIM_RATIO));
  }
  return encodeURIComponent(trimmed) + suffix;
}

export function buildWhatsAppUrl(report) {
  return `https://wa.me/${SUPPORT_WHATSAPP_NUMBER}?text=${encodeWithinLimit(report, ENCODED_LIMIT)}`;
}

export function buildMailtoUrl(report, error) {
  const subject = error === null ? `Soporte - ${APP_NAME}` : `Soporte - ${APP_NAME} (${error.code})`;
  return `mailto:${SUPPORT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeWithinLimit(report, ENCODED_LIMIT)}`;
}