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
import { TOAST_DURATION_MS } from '../config/constants.js';
import { h } from './dom.js';

export class Toast {
  #region;
  #current = null;
  #timer = null;

  constructor(region) {
    this.#region = region;
  }

  show(message, kind = 'info') {
    this.#dismissNow();
    const toast = h('div', { className: `toast toast--${kind}` }, [message]);
    this.#region.append(toast);
    this.#current = toast;
    this.#timer = setTimeout(() => this.#leave(toast), TOAST_DURATION_MS);
  }

  #dismissNow() {
    clearTimeout(this.#timer);
    this.#current?.remove();
    this.#current = null;
  }

  #leave(toast) {
    toast.classList.add('toast--leaving');
    Promise.allSettled(toast.getAnimations().map((animation) => animation.finished)).then(() => {
      toast.remove();
      if (this.#current === toast) this.#current = null;
    });
  }
}