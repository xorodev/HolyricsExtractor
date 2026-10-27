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
import contextlib
import hashlib
import hmac
import json
import os
import re
import tempfile
import threading
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, ContextManager
from .errors import StorageError
from .file_lock import is_locked, lock_file, unlock_file, unlocked
from .logging_service import get_logger
from .storage import read_json

logger = get_logger("protection")

MANIFEST_NAME = "integrity.json"
HASH_CHUNK_BYTES = 1_048_576
_DIGEST_RE = re.compile(r"[0-9a-f]{64}")

class FileState(Enum):
    PROTECTED = "protected"
    UNLOCKED = "unlocked"
    MODIFIED = "modified"
    MISSING = "missing"

@dataclass(frozen=True, slots=True)
class Finding:
    path: Path
    kind: str

def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()

class ProtectedFiles:
    def __init__(self, directory: Path):
        self._directory = directory
        self._manifest_path = directory / MANIFEST_NAME
        self._lock = threading.RLock()
        self._hashes = self._load_manifest()

    def _load_manifest(self) -> dict[str, str]:
        raw = read_json(self._manifest_path)
        if not isinstance(raw, dict):
            return {}
        return {
            key: value
            for key, value in raw.items()
            if isinstance(key, str) and isinstance(value, str) and _DIGEST_RE.fullmatch(value)
        }

    def _key(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self._directory.resolve()).as_posix()
        except ValueError:
            return str(path)

    def _atomic_write(self, path: Path, payload: bytes) -> None:
        temp_name: str | None = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            file_descriptor, temp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
            with os.fdopen(file_descriptor, "wb") as handle:
                handle.write(payload)
            with unlocked(path):
                os.replace(temp_name, path)
                temp_name = None
        except OSError as error:
            raise StorageError(f"{path.name}: {error}") from error
        finally:
            if temp_name is not None:
                with contextlib.suppress(OSError):
                    os.remove(temp_name)

    def _save_manifest(self) -> None:
        try:
            payload = json.dumps(self._hashes, indent=2, sort_keys=True).encode("utf-8")
            self._atomic_write(self._manifest_path, payload)
        except StorageError as error:
            logger.warning("Could not save the integrity manifest: %s", error)

    def _record(self, path: Path, digest: str) -> None:
        with self._lock:
            self._hashes[self._key(path)] = digest
            self._save_manifest()

    def _forget(self, path: Path) -> None:
        with self._lock:
            if self._hashes.pop(self._key(path), None) is not None:
                self._save_manifest()

    def writable(self, *paths: Path) -> ContextManager[None]:
        return unlocked(*paths)

    def write_json(self, path: Path, data: Any) -> None:
        try:
            payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        except (TypeError, ValueError) as error:
            raise StorageError(f"{path.name}: {error}") from error
        self._atomic_write(path, payload)
        self._record(path, hashlib.sha256(payload).hexdigest())

    def seal(self, path: Path) -> None:
        try:
            digest = file_digest(path)
        except OSError as error:
            raise StorageError(f"{path.name}: {error}") from error
        lock_file(path)
        self._record(path, digest)

    def accept(self, path: Path, hashed: bool = True) -> None:
        if hashed:
            self.seal(path)
        elif not lock_file(path):
            raise StorageError(f"{path.name}: could not be protected")

    def unlock(self, path: Path) -> None:
        if not unlock_file(path):
            raise StorageError(f"{path.name}: could not be unlocked")

    def delete(self, *paths: Path) -> None:
        for path in paths:
            try:
                with unlocked(path):
                    path.unlink(missing_ok=True)
            except OSError as error:
                raise StorageError(f"{path.name}: {error}") from error
            self._forget(path)

    def is_intact(self, path: Path) -> bool:
        registered = self._hashes.get(self._key(path))
        if registered is None or not path.is_file():
            return False
        try:
            return hmac.compare_digest(file_digest(path), registered)
        except OSError:
            return False

    def state(self, path: Path, hashed: bool = True) -> FileState:
        if not path.is_file():
            return FileState.MISSING
        if hashed and self._key(path) in self._hashes and not self.is_intact(path):
            return FileState.MODIFIED
        return FileState.PROTECTED if is_locked(path) else FileState.UNLOCKED

    def audit(self, paths: list[Path]) -> list[Finding]:
        findings: list[Finding] = []
        for path in paths:
            registered = self._hashes.get(self._key(path))
            if not path.is_file():
                if registered is not None:
                    findings.append(Finding(path, "deleted"))
                    self._forget(path)
                continue
            try:
                digest = file_digest(path)
            except OSError:
                continue
            if registered is None:
                self._record(path, digest)
            elif not hmac.compare_digest(digest, registered):
                findings.append(Finding(path, "modified"))
            lock_file(path)
        return findings