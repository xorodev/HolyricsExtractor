# HolyricsExtractor: A lightweight tool to search, extract, and format song lyrics for Holyrics.
# Copyright (C) 2026 @xorodev (CipherCoreDev)

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

# Third-Party Dependencies & Credits:
# - Built with Python (https://www.python.org/)
# - Metadata extraction powered by yt-dlp (https://github.com/yt-dlp/yt-dlp)
# - HTTP requests powered by Requests (https://requests.readthedocs.io)
# - Lyrics API provided by LRCLIB (https://lrclib.net)
# - Graphic Assets & Icons: Created from scratch by @xorodev

# GitHub: https://github.com/xorodev/HolyricsExtractor
# Contact:
# a. Email: corex.dev@proton.me
# b. Telegram: https://t.me/xorodev
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

UNEXPECTED_ERROR_CODE = "HE-999"
DEFAULT_ERROR_TITLE = "Error en el sistema"

class OperationCancelled(Exception):
    pass

class AppError(Exception):
    code = "HE-000"
    title = DEFAULT_ERROR_TITLE
    default_message = "Ha ocurrido un error inesperado."
    severity = "error"
    reportable = True

    def __init__(self, detail: str = "", user_message: str | None = None):
        super().__init__(detail or user_message or self.default_message)
        self.detail = detail
        self.user_message = user_message or self.default_message

class InvalidInputError(AppError):
    code = "HE-100"
    title = "Datos no válidos"
    default_message = "Los datos ingresados no son válidos."
    severity = "warning"
    reportable = False

class UnsupportedLinkError(InvalidInputError):
    code = "HE-101"
    default_message = "El enlace ingresado no pertenece a YouTube o no corresponde a un video."

class NetworkError(AppError):
    code = "HE-200"
    title = "Sin conexión con el servidor"
    default_message = "No fue posible comunicarse con el servidor. Verifique su conexión a internet e inténtelo de nuevo."

class ServiceResponseError(AppError):
    code = "HE-210"
    title = "Respuesta inesperada del servicio"
    default_message = "El servicio respondió con datos inesperados. Inténtelo de nuevo en unos minutos."

class LyricsNotFoundError(AppError):
    code = "HE-300"
    title = "Búsqueda sin resultados"
    default_message = "No se encontró la letra de la canción. Verifique el título o especifique el nombre del artista."
    severity = "warning"

class YouTubeResolutionError(AppError):
    code = "HE-400"
    title = "Error al leer el video"
    default_message = "No fue posible obtener la información del video de YouTube."

class UpdateError(AppError):
    code = "HE-500"
    title = "Error de actualización"
    default_message = "No fue posible completar la actualización."

class IntegrityError(UpdateError):
    code = "HE-510"
    default_message = "El archivo descargado no superó la verificación de integridad y fue descartado."

class StorageError(AppError):
    code = "HE-600"
    title = "Error de almacenamiento"
    default_message = "No fue posible leer o guardar los datos locales de la aplicación."

@dataclass(frozen=True, slots=True)

class ErrorReport:
    code: str
    title: str
    message: str
    detail: str
    occurred_at: str

def describe_error(error: BaseException) -> ErrorReport:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(error, AppError):
        return ErrorReport(error.code, error.title, error.user_message, error.detail, timestamp)
    return ErrorReport(
        UNEXPECTED_ERROR_CODE,
        DEFAULT_ERROR_TITLE,
        AppError.default_message,
        f"{type(error).__name__}: {error}",
        timestamp,
    )