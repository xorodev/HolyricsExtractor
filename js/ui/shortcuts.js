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
const IS_MAC = /mac|iphone|ipad|ipod/i.test(navigator.userAgentData?.platform ?? navigator.platform ?? '');

export const MODIFIER_LABEL = IS_MAC ? 'Cmd' : 'Ctrl';

const KEY_LABELS = Object.freeze({
  Mod: MODIFIER_LABEL,
  Shift: 'Mayús',
  Escape: 'Esc',
});

export function shortcutLabels(keys) {
  return keys.map((key) => KEY_LABELS[key] ?? key);
}

function matches(event, keys) {
  const key = keys[keys.length - 1];
  const modifierPressed = IS_MAC ? event.metaKey : event.ctrlKey;
  const foreignModifierPressed = IS_MAC ? event.ctrlKey : event.metaKey;
  return (
    event.key.toLowerCase() === key.toLowerCase() &&
    modifierPressed === keys.includes('Mod') &&
    event.shiftKey === keys.includes('Shift') &&
    !foreignModifierPressed &&
    !event.altKey
  );
}

export function bindShortcuts(shortcuts) {
  const active = shortcuts.filter((shortcut) => shortcut.handler);
  document.addEventListener('keydown', (event) => {
    if (event.repeat || event.isComposing || document.querySelector('dialog[open]') !== null) return;
    const shortcut = active.find((candidate) => matches(event, candidate.keys));
    if (shortcut === undefined) return;
    event.preventDefault();
    shortcut.handler();
  });
}