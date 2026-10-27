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
import { APP_AUTHOR, APP_LICENSE, APP_NAME, APP_VERSION, DEVELOPER_LINKS } from '../../config/constants.js';
import { openDialog } from '../dialog.js';
import { externalLink, h } from '../dom.js';

export function showAboutDialog() {
  const rows = DEVELOPER_LINKS.map(({ label, text, url }) =>
    h('li', { className: 'link-row' }, [
      h('span', { className: 'link-row__label' }, [label]),
      externalLink(url, text),
    ]),
  );
  const body = h('div', { className: 'about' }, [
    h('p', { className: 'about__meta' }, [`Licencia: ${APP_LICENSE}\nVersión actual: '${APP_VERSION}'\nCreated by: ${APP_AUTHOR}`]),
    h('p', { className: 'about__summary' }, [
      'Herramienta diseñada para extraer y formatear automáticamente letras de canciones para el software de Holyrics.',
    ]),
    h('fieldset', { className: 'group' }, [
      h('legend', { className: 'group__legend' }, ['Licencia y Contacto del Desarrollador']),
      h('ul', { className: 'link-list' }, rows),
    ]),
  ]);
  return openDialog({
    title: `♪ ${APP_NAME}`,
    body,
    buttons: [{ label: 'Cerrar', variant: 'neutral' }],
  });
}