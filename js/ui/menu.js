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

let openMenu = null;

document.addEventListener('pointerdown', (event) => {
  if (openMenu !== null && !openMenu.contains(event.target)) openMenu.close();
});

export class DropdownMenu {
  #root;
  #trigger;
  #list;

  constructor(root) {
    this.#root = root;
    this.#trigger = root.querySelector('.menu__trigger');
    this.#list = root.querySelector('.menu__list');
    this.#trigger.addEventListener('click', () => (this.#isOpen ? this.close() : this.#open()));
    this.#trigger.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowDown') return;
      event.preventDefault();
      this.#open();
    });
    this.#list.addEventListener('keydown', (event) => this.#handleListKey(event));
  }

  get #isOpen() {
    return !this.#list.hidden;
  }

  get #enabledItems() {
    return [...this.#list.querySelectorAll('[role="menuitem"]:not(:disabled)')];
  }

  contains(node) {
    return this.#root.contains(node);
  }

  setItems(items) {
    this.#list.replaceChildren(
      ...items.map((item) => {
        if (item.separator) return h('div', { className: 'menu__separator', role: 'separator' });
        return h(
          'button',
          {
            className: 'menu__item',
            type: 'button',
            role: 'menuitem',
            disabled: item.disabled === true,
            onclick: () => {
              this.close();
              item.onSelect?.();
            },
          },
          [item.label],
        );
      }),
    );
  }

  close() {
    if (!this.#isOpen) return;
    this.#list.hidden = true;
    this.#trigger.setAttribute('aria-expanded', 'false');
    if (openMenu === this) openMenu = null;
  }

  #open() {
    if (openMenu !== null && openMenu !== this) openMenu.close();
    this.#list.hidden = false;
    this.#trigger.setAttribute('aria-expanded', 'true');
    openMenu = this;
    this.#enabledItems[0]?.focus();
  }

  #handleListKey(event) {
    const items = this.#enabledItems;
    const index = items.indexOf(document.activeElement);
    const moves = {
      ArrowDown: items[(index + 1) % items.length],
      ArrowUp: items[(index - 1 + items.length) % items.length],
      Home: items[0],
      End: items[items.length - 1],
    };
    if (event.key in moves) {
      event.preventDefault();
      moves[event.key]?.focus();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      this.close();
      this.#trigger.focus();
    } else if (event.key === 'Tab') {
      this.close();
    }
  }
}