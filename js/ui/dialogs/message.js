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
import { sanitizeSingleLine } from '../../core/text.js';
import { h } from '../dom.js';
import { openDialog } from '../dialog.js';

const KIND_GLYPHS = Object.freeze({
  info: 'ℹ',
  success: '✓',
  warning: '⚠',
  error: '✕',
  question: '?',
});
const DETAIL_PREVIEW_LENGTH = 300;

function messageBody(message, kind, detail = '') {
  return h('div', { className: 'message' }, [
    h('span', { className: `message__glyph message__glyph--${kind}`, 'aria-hidden': 'true' }, [KIND_GLYPHS[kind]]),
    h('div', { className: 'message__content' }, [
      h('p', { className: 'message__text' }, [message]),
      detail ? h('p', { className: 'message__detail' }, [detail]) : null,
    ].filter(Boolean)),
  ]);
}

export async function confirmAction(title, message) {
  const answer = await openDialog({
    title,
    body: messageBody(message, 'question'),
    buttons: [
      { label: 'Sí', value: 'yes' },
      { label: 'No', value: 'no', variant: 'neutral' },
    ],
  });
  return answer === 'yes';
}

export function showError(report, severity, reportable) {
  const detailLines = [`Código de error: ${report.code}`];
  if (severity === 'error' && report.detail) {
    detailLines.push(`Detalles técnicos: ${sanitizeSingleLine(report.detail, DETAIL_PREVIEW_LENGTH)}`);
  }
  const buttons = [{ label: 'Cerrar', value: 'close', variant: 'neutral' }];
  if (reportable) buttons.unshift({ label: '¡Reportar al desarrollador!', value: 'report' });
  return openDialog({
    title: report.title,
    body: messageBody(report.message, severity, detailLines.join('\n')),
    buttons,
  });
}