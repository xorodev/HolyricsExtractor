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
import { EXPORT_SEPARATOR } from '../config/constants.js';

export class LyricsResult {
  constructor(title, artist, slides) {
    this.title = title;
    this.artist = artist;
    this.slides = Object.freeze(slides.map((slide) => Object.freeze([...slide])));
    Object.freeze(this);
  }

  static fromFormattedText(title, artist, text) {
    const slides = text
      .split('\n\n')
      .filter((block) => block.trim())
      .map((block) => block.split('\n'));
    return new LyricsResult(title, artist, slides);
  }

  get totalSlides() {
    return this.slides.length;
  }

  get formattedText() {
    return this.slides.map((slide) => slide.join('\n')).join('\n\n');
  }

  get exportText() {
    return this.slides.map((slide) => slide.join('\n')).join(`\n${EXPORT_SEPARATOR}\n`);
  }
}