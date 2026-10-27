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

export function createCheckbox({ label, checked, onChange }) {
  const input = h('input', { className: 'choice__input', type: 'checkbox', checked });
  input.addEventListener('change', () => onChange?.(input.checked));
  const root = h('label', { className: 'choice' }, [input, h('span', { className: 'choice__label' }, [label])]);
  return { root, input };
}

export function createGroup(legend, children) {
  return h('fieldset', { className: 'group' }, [h('legend', { className: 'group__legend' }, [legend]), ...children]);
}

export function createRadioGroup({ legend, name, options, value, onChange }) {
  const choices = options.map(([optionValue, label]) => {
    const input = h('input', {
      className: 'choice__input',
      type: 'radio',
      name,
      value: optionValue,
      checked: optionValue === value,
    });
    input.addEventListener('change', () => onChange(optionValue));
    const root = h('label', { className: 'choice choice--inline' }, [
      input,
      h('span', { className: 'choice__label' }, [label]),
    ]);
    return { root, input };
  });
  return {
    root: createGroup(
      legend,
      choices.map((choice) => choice.root),
    ),
    inputs: choices.map((choice) => choice.input),
  };
}