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
import { MAX_ARTIST_LENGTH, MAX_QUERY_LENGTH } from '../config/constants.js';
import {
  InvalidInputError,
  LyricsNotFoundError,
  UnsupportedLinkError,
  YouTubeResolutionError,
} from '../core/errors.js';
import { codePointLength, sanitizeSingleLine } from '../core/text.js';
import { searchLyrics } from './lrclib.js';
import { LyricsResult } from './models.js';
import { buildSlides } from './slides.js';
import { cleanChannelName, cleanTitle, splitTitleAndArtist } from './titleParser.js';
import { QueryKind, classifyQuery, resolveVideo } from './youtube.js';

function validated(text, limit, label) {
  const cleaned = sanitizeSingleLine(text, limit + 1);
  if (codePointLength(cleaned) > limit) {
    throw new InvalidInputError(
      `${label} exceeds ${limit} characters`,
      `El texto ingresado supera el máximo permitido de ${limit} caracteres.`,
    );
  }
  return cleaned;
}

async function identifyTrack(query, artist, report, signal) {
  const kind = classifyQuery(query);
  if (kind === QueryKind.OTHER_LINK) throw new UnsupportedLinkError('Link is not hosted on YouTube');
  if (kind === QueryKind.TITLE) return { track: query, artist };

  report('Leyendo la información del video de YouTube...');
  const metadata = await resolveVideo(query, signal);
  const { track, artist: detectedArtist } = splitTitleAndArtist(cleanTitle(metadata.title));
  if (!track) throw new YouTubeResolutionError('The video title is empty after cleanup');
  return { track, artist: artist || detectedArtist || cleanChannelName(metadata.channel) };
}

export async function findLyrics(rawQuery, rawArtist, report, signal) {
  const query = validated(rawQuery, MAX_QUERY_LENGTH, 'Query');
  const requestedArtist = validated(rawArtist, MAX_ARTIST_LENGTH, 'Artist');
  if (!query) {
    throw new InvalidInputError(
      'Empty query',
      'Ingrese un enlace (URL) de YouTube válido o el título de una canción para continuar.',
    );
  }

  const { track, artist } = await identifyTrack(query, requestedArtist, report, signal);

  report('Buscando la letra en LRCLIB...');
  const lyrics = await searchLyrics(track, artist, signal);
  if (!lyrics) {
    throw new LyricsNotFoundError(
      `No lyrics for '${track}' / '${artist}'`,
      `No fue posible encontrar la letra de la canción: '${track}'. Verifique el título o especifique el nombre del artista.`,
    );
  }

  report('Formateando las presentaciones...');
  const slides = buildSlides(lyrics);
  if (slides.length === 0) throw new LyricsNotFoundError(`Lyrics for '${track}' contained no usable lines`);
  return new LyricsResult(track, artist, slides);
}