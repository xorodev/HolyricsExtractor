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

const PLACEHOLDER_TEXT = 'Aquí aparecerán los versos generados a partir de la letra...';

export class Preview {
  #element;

  constructor(element) {
    this.#element = element;
  }

  showPlaceholder() {
    this.#element.replaceChildren(h('p', { className: 'preview__placeholder' }, [PLACEHOLDER_TEXT]));
  }

  render(result) {
    const fragment = document.createDocumentFragment();
    result.slides.forEach((slide, index) => {
      fragment.append(
        h('article', { className: 'verse' }, [
          h('h3', { className: 'verse__title' }, [`VERSO ${index + 1}`]),
          h('p', { className: 'verse__text' }, [slide.join('\n')]),
        ]),
      );
    });
    this.#element.replaceChildren(fragment);
    this.#element.scrollTop = 0;
  }
}