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
import { formatTimestamp } from './datetime.js';

const UNEXPECTED_ERROR_CODE = 'HE-999';
const DEFAULT_ERROR_TITLE = 'Error en el sistema';
const DEFAULT_ERROR_MESSAGE = 'Ha ocurrido un error inesperado.';

export class OperationCancelled extends Error {
  constructor() {
    super('Operation cancelled');
    this.name = 'OperationCancelled';
  }
}

export class AppError extends Error {
  static code = 'HE-000';
  static title = DEFAULT_ERROR_TITLE;
  static defaultMessage = DEFAULT_ERROR_MESSAGE;
  static severity = 'error';
  static reportable = true;

  constructor(detail = '', userMessage = null) {
    const spec = new.target;
    super(detail || userMessage || spec.defaultMessage);
    this.name = spec.name;
    this.code = spec.code;
    this.title = spec.title;
    this.severity = spec.severity;
    this.reportable = spec.reportable;
    this.detail = detail;
    this.userMessage = userMessage ?? spec.defaultMessage;
  }
}

export class InvalidInputError extends AppError {
  static code = 'HE-100';
  static title = 'Datos no válidos';
  static defaultMessage = 'Los datos ingresados no son válidos.';
  static severity = 'warning';
  static reportable = false;
}

export class UnsupportedLinkError extends InvalidInputError {
  static code = 'HE-101';
  static defaultMessage = 'El enlace ingresado no pertenece a YouTube o no corresponde a un video.';
}

export class NetworkError extends AppError {
  static code = 'HE-200';
  static title = 'Sin conexión con el servidor';
  static defaultMessage =
    'No fue posible comunicarse con el servidor. Verifique su conexión a internet e inténtelo de nuevo.';
}

export class ServiceResponseError extends AppError {
  static code = 'HE-210';
  static title = 'Respuesta inesperada del servicio';
  static defaultMessage = 'El servicio respondió con datos inesperados. Inténtelo de nuevo en unos minutos.';
}

export class LyricsNotFoundError extends AppError {
  static code = 'HE-300';
  static title = 'Búsqueda sin resultados';
  static defaultMessage =
    'No se encontró la letra de la canción. Verifique el título o especifique el nombre del artista.';
  static severity = 'warning';
}

export class YouTubeResolutionError extends AppError {
  static code = 'HE-400';
  static title = 'Error al leer el video';
  static defaultMessage = 'No fue posible obtener la información del video de YouTube.';
}

export function describeError(error) {
  const occurredAt = formatTimestamp(new Date());
  if (error instanceof AppError) {
    return Object.freeze({
      code: error.code,
      title: error.title,
      message: error.userMessage,
      detail: error.detail,
      occurredAt,
    });
  }
  const name = error instanceof Error ? error.name : typeof error;
  const message = error instanceof Error ? error.message : String(error);
  return Object.freeze({
    code: UNEXPECTED_ERROR_CODE,
    title: DEFAULT_ERROR_TITLE,
    message: DEFAULT_ERROR_MESSAGE,
    detail: `${name}: ${message}`,
    occurredAt,
  });
}