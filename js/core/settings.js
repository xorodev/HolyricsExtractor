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
import { STORAGE_KEYS } from '../config/constants.js';
import { readJson, writeJson } from './storage.js';

export const THEME_DARK = 'dark';
export const THEME_LIGHT = 'light';

export const SPEED_SLOW = 'slow';
export const SPEED_NORMAL = 'normal';
export const SPEED_FAST = 'fast';

export const SettingKey = Object.freeze({
  THEME: 'theme',
  ANIMATIONS_ENABLED: 'animationsEnabled',
  ANIMATION_SPEED: 'animationSpeed',
  ANIMATION_HOVER: 'animationHover',
  ANIMATION_NOTIFICATIONS: 'animationNotifications',
  ANIMATION_WINDOWS: 'animationWindows',
  ANIMATION_RESULTS: 'animationResults',
});

const isBoolean = (value) => typeof value === 'boolean';
const oneOf = (choices) => (value) => choices.includes(value);

const VALIDATORS = new Map([
  [SettingKey.THEME, oneOf([THEME_DARK, THEME_LIGHT])],
  [SettingKey.ANIMATIONS_ENABLED, isBoolean],
  [SettingKey.ANIMATION_SPEED, oneOf([SPEED_SLOW, SPEED_NORMAL, SPEED_FAST])],
  [SettingKey.ANIMATION_HOVER, isBoolean],
  [SettingKey.ANIMATION_NOTIFICATIONS, isBoolean],
  [SettingKey.ANIMATION_WINDOWS, isBoolean],
  [SettingKey.ANIMATION_RESULTS, isBoolean],
]);

function systemTheme() {
  return window.matchMedia('(prefers-color-scheme: light)').matches ? THEME_LIGHT : THEME_DARK;
}

function createDefaults() {
  return {
    [SettingKey.THEME]: systemTheme(),
    [SettingKey.ANIMATIONS_ENABLED]: true,
    [SettingKey.ANIMATION_SPEED]: SPEED_NORMAL,
    [SettingKey.ANIMATION_HOVER]: true,
    [SettingKey.ANIMATION_NOTIFICATIONS]: true,
    [SettingKey.ANIMATION_WINDOWS]: true,
    [SettingKey.ANIMATION_RESULTS]: true,
  };
}

export class SettingsStore {
  #values = createDefaults();

  constructor() {
    const stored = readJson(STORAGE_KEYS.SETTINGS);
    if (stored === null || typeof stored !== 'object' || Array.isArray(stored)) return;
    for (const [key, isValid] of VALIDATORS) {
      if (isValid(stored[key])) this.#values[key] = stored[key];
    }
  }

  get(key) {
    return this.#values[key];
  }

  set(key, value) {
    const isValid = VALIDATORS.get(key);
    if (isValid === undefined || !isValid(value)) throw new RangeError(`Invalid setting: ${String(key)}`);
    this.#values[key] = value;
    writeJson(STORAGE_KEYS.SETTINGS, this.#values);
  }
}