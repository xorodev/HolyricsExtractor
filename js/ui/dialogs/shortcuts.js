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
import { openDialog } from '../dialog.js';
import { h } from '../dom.js';
import { MODIFIER_LABEL, shortcutLabels } from '../shortcuts.js';

function keyCombination(keys) {
  const parts = [];
  shortcutLabels(keys).forEach((label, index) => {
    if (index > 0) parts.push(' + ');
    parts.push(h('kbd', { className: 'key' }, [label]));
  });
  return h('span', { className: 'shortcut__keys' }, parts);
}

export function showShortcutsDialog(shortcuts) {
  const rows = shortcuts.map(({ keys, description }) =>
    h('li', { className: 'shortcut' }, [keyCombination(keys), h('span', { className: 'shortcut__text' }, [description])]),
  );
  const body = h('div', { className: 'dialog-stack' }, [
    h('p', { className: 'dialog__hint' }, [
      `En este equipo la tecla principal es '${MODIFIER_LABEL}'. Los atajos funcionan con la tecla 'Bloq Mayús' activada o desactivada.`,
    ]),
    h('ul', { className: 'shortcut-list' }, rows),
  ]);
  return openDialog({
    title: 'Atajos de teclado',
    body,
    buttons: [{ label: 'Cerrar', variant: 'neutral' }],
  });
}