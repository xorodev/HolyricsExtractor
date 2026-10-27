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
import { h } from './dom.js';

let dialogCount = 0;

export function openDialog({ title, body, buttons, initialFocus = null }) {
  dialogCount += 1;
  const titleId = `dialog-title-${dialogCount}`;
  let result;

  const dialog = h('dialog', { className: 'dialog', 'aria-labelledby': titleId });
  const close = (value) => {
    result = value;
    dialog.close();
  };

  const footer = h(
    'div',
    { className: 'dialog__footer' },
    buttons.map(({ label, variant = 'primary', value, keepOpen = false, onClick }) =>
      h(
        'button',
        {
          className: `btn btn--${variant}`,
          type: 'button',
          onclick: () => {
            onClick?.();
            if (!keepOpen) close(value);
          },
        },
        [label],
      ),
    ),
  );

  dialog.append(
    h('div', { className: 'dialog__surface' }, [
      h('h2', { className: 'dialog__title', id: titleId }, [title]),
      body,
      footer,
    ]),
  );
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });

  return new Promise((resolve) => {
    dialog.addEventListener('close', () => {
      dialog.remove();
      resolve(result);
    });
    document.body.append(dialog);
    dialog.showModal();
    initialFocus?.focus();
  });
}