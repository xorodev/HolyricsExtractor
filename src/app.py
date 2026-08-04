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

import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

import requests
import yt_dlp

def resource_path(relative_path):
    """ Obtiene la ruta absoluta del recurso, funciona para desarrollo y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def enable_windows_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    try:
        import ctypes
        myappid = "xorodev.holyricsextractor.gui.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass
    
class ApplicationLogger:
    MAX_LOG_BYTES = 1_000_000
    MAX_LOG_LINES_KEPT = 500

    def __init__(self):
        user_documents = os.path.join(os.path.expanduser("~"), "Documents")
        self.log_directory = os.path.join(user_documents, "HolyricsExtractor")
        os.makedirs(self.log_directory, exist_ok=True)
        self.log_file_path = os.path.join(self.log_directory, "logs.txt")

    def write_log(self, level, message):
        try:
            self._rotate_if_needed()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{timestamp}] [{level}] {message}\n"
            with open(self.log_file_path, "a", encoding="utf-8") as file:
                file.write(entry)
        except OSError:
            pass

    def _rotate_if_needed(self):
        try:
            if os.path.getsize(self.log_file_path) <= self.MAX_LOG_BYTES:
                return
            with open(self.log_file_path, "r", encoding="utf-8", errors="replace") as file:
                lines = file.readlines()
            with open(self.log_file_path, "w", encoding="utf-8") as file:
                file.writelines(lines[-self.MAX_LOG_LINES_KEPT:])
        except FileNotFoundError:
            pass


class ConfigurationManager:
    DEFAULT_SETTINGS = {"first_run": True, "check_yt_dlp_updates": True, "check_app_updates": True}

    def __init__(self, logger):
        self.logger = logger
        user_documents = os.path.join(os.path.expanduser("~"), "Documents")
        config_dir = os.path.join(user_documents, "HolyricsExtractor")
        os.makedirs(config_dir, exist_ok=True)
        self.config_file_path = os.path.join(config_dir, "config.json")
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, "r", encoding="utf-8") as file:
                    loaded = json.load(file)
                merged = dict(self.DEFAULT_SETTINGS)
                merged.update(loaded)
                return merged
            except Exception as error:
                self.logger.write_log("WARNING", f"Failed to load config file: {str(error)}")
                return dict(self.DEFAULT_SETTINGS)
        return dict(self.DEFAULT_SETTINGS)

    def save_settings(self):
        try:
            with open(self.config_file_path, "w", encoding="utf-8") as file:
                json.dump(self.settings, file, indent=4)
            self.logger.write_log("INFO", "Configuration saved successfully.")
        except Exception as error:
            self.logger.write_log("ALERT", f"Failed to save configuration: {str(error)}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()


class UpdateManager:
    RELEASES_API_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
    APP_GITHUB_OWNER = "xorodev"
    APP_GITHUB_REPOSITORY = "HolyricsExtractor"
    APP_RELEASES_API_URL = f"https://api.github.com/repos/{APP_GITHUB_OWNER}/{APP_GITHUB_REPOSITORY}/releases/latest"
    APP_EXECUTABLE_ASSET_NAME = "HolyricsExtractor.exe"

    def __init__(self, logger):
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "HolyricsExtractor/1.2",
            "Accept": "application/vnd.github+json",
        })
        user_documents = os.path.join(os.path.expanduser("~"), "Documents")
        self.bin_directory = os.path.join(user_documents, "HolyricsExtractor", "bin")
        os.makedirs(self.bin_directory, exist_ok=True)
        self.binary_name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
        self.binary_path = os.path.join(self.bin_directory, self.binary_name)

    def has_local_binary(self):
        return os.path.isfile(self.binary_path)

    def get_installed_version(self):
        if self.has_local_binary():
            try:
                creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                result = subprocess.run(
                    [self.binary_path, "--version"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=10,
                    creationflags=creation_flags,
                )
                version = result.stdout.strip()
                if result.returncode == 0 and version:
                    return version
            except Exception as error:
                self.logger.write_log("WARNING", f"Could not read local yt-dlp binary version: {str(error)}")
        return yt_dlp.version.__version__

    def get_latest_available_version(self):
        try:
            response = self.session.get(self.RELEASES_API_URL, timeout=8)
            if response.status_code == 200:
                data = response.json()
                tag = data.get("tag_name")
                assets = data.get("assets", [])
                download_url = next(
                    (asset.get("browser_download_url") for asset in assets if asset.get("name") == self.binary_name),
                    None,
                )
                if tag and download_url:
                    return tag, download_url
        except Exception as error:
            self.logger.write_log("WARNING", f"Could not fetch latest yt-dlp release info: {str(error)}")
        return None, None

    def perform_clean_update(self):
        self.logger.write_log("INFO", "Initiating clean update of yt-dlp component.")
        latest_version, download_url = self.get_latest_available_version()

        if not download_url:
            message = "No fue posible obtener el enlace de descarga de la última versión disponible."
            self.logger.write_log("ALERT", message)
            return False, message

        temp_path = None
        try:
            response = self.session.get(download_url, timeout=90, stream=True)
            if response.status_code != 200:
                message = f"El servidor de descargas respondió con el código: {response.status_code}"
                self.logger.write_log("ALERT", message)
                return False, message

            temp_fd, temp_path = tempfile.mkstemp(dir=self.bin_directory, suffix=".tmp")
            with os.fdopen(temp_fd, "wb") as temp_file:
                for chunk in response.iter_content(chunk_size=262144):
                    if chunk:
                        temp_file.write(chunk)

            if sys.platform != "win32":
                os.chmod(temp_path, 0o755)

            os.replace(temp_path, self.binary_path)
            temp_path = None

        except requests.RequestException as error:
            message = f"Falló la descarga de la actualización: {str(error)}"
            self.logger.write_log("ALERT", message)
            return False, message
        except OSError as error:
            message = f"No fue posible guardar el archivo actualizado: {str(error)}"
            self.logger.write_log("ALERT", message)
            return False, message
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        self.logger.write_log("INFO", f"yt-dlp updated successfully to version: {latest_version}")
        return True, latest_version

    def is_frozen(self):
        return bool(getattr(sys, "frozen", False))

    def get_latest_app_release(self):
        try:
            response = self.session.get(self.APP_RELEASES_API_URL, timeout=8)
            if response.status_code == 200:
                data = response.json()
                tag = data.get("tag_name")
                assets = data.get("assets", [])
                download_url = next(
                    (asset.get("browser_download_url") for asset in assets if asset.get("name") == self.APP_EXECUTABLE_ASSET_NAME),
                    None,
                )
                if tag and download_url:
                    return tag, download_url
        except Exception as error:
            self.logger.write_log("WARNING", f"Could not fetch latest application release info: {str(error)}")
        return None, None

    def download_new_build(self, download_url, progress_callback=None):
        current_exe = os.path.abspath(sys.executable)
        destination_dir = os.path.dirname(current_exe)
        temp_fd, temp_path = tempfile.mkstemp(dir=destination_dir, suffix=".new.exe")

        try:
            response = self.session.get(download_url, timeout=180, stream=True)
            if response.status_code != 200:
                raise RuntimeError(f"El servidor de descargas respondió con el código: {response.status_code}")

            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            with os.fdopen(temp_fd, "wb") as temp_file:
                for chunk in response.iter_content(chunk_size=262144):
                    if not chunk:
                        continue
                    temp_file.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)

            if downloaded < 1_000_000:
                raise RuntimeError("El archivo descargado no corresponde a un ejecutable válido.")

            return temp_path
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def apply_self_update_and_relaunch(self, new_exe_path):
        current_exe = os.path.abspath(sys.executable)
        current_dir = os.path.dirname(current_exe)
        backup_name = os.path.basename(current_exe) + ".old"
        backup_full_path = os.path.join(current_dir, backup_name)

        script_path = os.path.join(tempfile.gettempdir(), "holyrics_app_updater.bat")
        script_content = (
            "@echo off\n"
            "set _MEIPASS2=\n"
            f'set "CURRENT_EXE={current_exe}"\n'
            f'set "NEW_EXE={new_exe_path}"\n'
            f'set "BACKUP_NAME={backup_name}"\n'
            f'set "BACKUP_FULL={backup_full_path}"\n'
            'set "RETRY=0"\n'
            "\n"
            ":wait_loop\n"
            'ren "%CURRENT_EXE%" "%BACKUP_NAME%" >nul 2>&1\n'
            'if not exist "%CURRENT_EXE%" goto replace_ok\n'
            "set /a RETRY+=1\n"
            "if %RETRY% GEQ 20 goto give_up\n"
            "ping 127.0.0.1 -n 2 >nul\n"
            "goto wait_loop\n"
            "\n"
            ":replace_ok\n"
            'move /y "%NEW_EXE%" "%CURRENT_EXE%" >nul 2>&1\n'
            'del "%BACKUP_FULL%" >nul 2>&1\n'
            "ping 127.0.0.1 -n 3 >nul\n"
            'start "" "%CURRENT_EXE%"\n'
            "goto cleanup\n"
            "\n"
            ":give_up\n"
            'start "" "%CURRENT_EXE%"\n'
            'del "%NEW_EXE%" >nul 2>&1\n'
            "\n"
            ":cleanup\n"
            'del "%~f0" >nul 2>&1\n'
        )
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(script_content)

        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        subprocess.Popen(
            ["cmd", "/c", script_path],
            creationflags=creation_flags,
            close_fds=True,
        )


class LyricsService:
    _TAG_PATTERN = (
        r'(?:official\s*music\s*video|official\s*video|official\s*audio|'
        r'video\s*oficial|audio\s*oficial|lyric\s*video|lyrics?|letra|'
        r'official|oficial|video|audio|visualizer|hd|4k|mv)'
    )
    _TAG_KEYWORDS_RE = re.compile(r'\b' + _TAG_PATTERN + r'\b', re.IGNORECASE)
    _BRACKET_GROUP_RE = re.compile(r'[\(\[][^()\[\]]*[\)\]]')
    _TRAILING_TAG_RE = re.compile(r'\s*(?:[-|:]\s*)?' + _TAG_PATTERN + r'\s*$', re.IGNORECASE)
    _MULTI_SPACE_RE = re.compile(r'\s{2,}')
    _YOUTUBE_HOST_RE = re.compile(
        r'(?:https?://)?(?:[\w-]+\.)*(?<![\w-])(?:youtube\.com|youtube-nocookie\.com|youtu\.be)(?:[/?#]|$)',
        re.IGNORECASE,
    )

    def __init__(self, logger, update_manager):
        self.logger = logger
        self.update_manager = update_manager
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "HolyricsExtractor/1.2"})

    def is_youtube_url(self, text):
        return bool(self._YOUTUBE_HOST_RE.search(text.strip()))

    def clean_title(self, title):
        def strip_if_tag(match):
            content = match.group(0)
            return '' if self._TAG_KEYWORDS_RE.search(content) else content

        cleaned = self._BRACKET_GROUP_RE.sub(strip_if_tag, title)
        cleaned = self._TRAILING_TAG_RE.sub('', cleaned)
        cleaned = self._MULTI_SPACE_RE.sub(' ', cleaned)
        return cleaned.strip(' -|:').strip()

    def resolve_youtube_query(self, url):
        self.logger.write_log("INFO", f"Extracting metadata from YouTube URL: {url}")
        if self.update_manager.has_local_binary():
            title = self._resolve_with_binary(url)
            if title:
                return title
        return self._resolve_with_library(url)

    def _resolve_with_binary(self, url):
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run(
                [
                    self.update_manager.binary_path,
                    "--skip-download",
                    "--no-warnings",
                    "--no-playlist",
                    "--print", "%(title)s",
                    url,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                creationflags=creation_flags,
            )
            if result.returncode == 0:
                lines = [line for line in result.stdout.splitlines() if line.strip()]
                if lines:
                    return self.clean_title(lines[0])
        except Exception as error:
            self.logger.write_log("WARNING", f"Local yt-dlp binary extraction failed: {str(error)}")
        return None

    def _resolve_with_library(self, url):
        options = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'socket_timeout': 10,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            raw_title = info.get('title', '') if info else ''
            return self.clean_title(raw_title)

    def fetch_lyrics(self, track, artist):
        self.logger.write_log("INFO", f"Initiating API request for track: '{track}', artist: '{artist}'")
        params = {"track_name": track}
        if artist:
            params["artist_name"] = artist

        query_string = urllib.parse.urlencode(params)
        endpoint = f"https://lrclib.net/api/search?{query_string}"

        response = self.session.get(endpoint, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                lyrics = next((item.get("plainLyrics") for item in data if item.get("plainLyrics")), None)
                if lyrics:
                    self.logger.write_log("INFO", "Lyrics retrieved successfully.")
                    return lyrics

        self.logger.write_log("WARNING", "Lyrics query returned empty or invalid dataset.")
        return None

    def format_stanzas(self, text):
        lines = [line.strip() for line in text.splitlines()]
        stanzas = []
        current_stanza = []

        for line in lines:
            if line:
                current_stanza.append(line)
            else:
                if current_stanza:
                    stanzas.append(current_stanza)
                    current_stanza = []

        if current_stanza:
            stanzas.append(current_stanza)

        if len(stanzas) == 1 and len(lines) > 5:
            stanzas = [lines[i:i + 4] for i in range(0, len(lines), 4) if lines[i:i + 4]]

        slides = []
        for stanza in stanzas:
            slides.extend(self._split_stanza_into_slides(stanza))

        slides = self._mark_repeated_slides(slides)

        blocks = ["\n".join(slide) for slide in slides]
        return "\n\n".join(blocks), len(blocks)

    def _split_stanza_into_slides(self, stanza_lines, min_size=4, max_size=5):
        total = len(stanza_lines)
        if total <= max_size:
            return [stanza_lines]

        sizes = None
        for num_groups in range(1, (total // min_size) + 2):
            if num_groups * min_size <= total <= num_groups * max_size:
                base = total // num_groups
                remainder = total % num_groups
                sizes = [base + 1 if i < remainder else base for i in range(num_groups)]
                break

        if sizes is None:
            num_groups = max(1, round(total / ((min_size + max_size) / 2)))
            base = total // num_groups
            remainder = total % num_groups
            sizes = [base + 1 if i < remainder else base for i in range(num_groups)]

        slides = []
        index = 0
        for size in sizes:
            slides.append(stanza_lines[index:index + size])
            index += size
        return slides

    def _mark_repeated_slides(self, slides):
        first_seen_index = {}
        slides_to_mark = set()
        slides_to_skip = set()

        for index, slide in enumerate(slides):
            key = "\n".join(line.casefold() for line in slide)
            if key in first_seen_index:
                slides_to_mark.add(first_seen_index[key])
                slides_to_skip.add(index)
            else:
                first_seen_index[key] = index

        result = []
        for index, slide in enumerate(slides):
            if index in slides_to_skip:
                continue
            if index in slides_to_mark:
                slide = list(slide)
                slide[0] = f"// {slide[0]}"
                slide[-1] = f"{slide[-1]} //"
            result.append(slide)
        return result


def bind_hover_effect(widget, normal_bg, hover_bg):
    widget.bind("<Enter>", lambda event: widget.config(bg=hover_bg))
    widget.bind("<Leave>", lambda event: widget.config(bg=normal_bg))


class AboutDialog(tk.Toplevel):
    def __init__(self, parent, version):
        super().__init__(parent)
        self.title("Acerca de - Extractor de Letras")
        self.geometry("500x420")
        self.resizable(False, False)
        self.configure(bg="#2b2b3b")
        self.transient(parent)
        self.bind("<Escape>", lambda event: self.destroy())
        self.grab_set()

        try:
            self.iconbitmap(resource_path("./img/icon.ico"))
        except Exception:
            pass

        self.version = version
        self.setup_ui()

    def setup_ui(self):
        title_lbl = tk.Label(
            self, text="🎵 Extractor de Letras para Holyrics",
            font=("Segoe UI", 14, "bold"), bg="#2b2b3b", fg="#74c7ec"
        )
        title_lbl.pack(pady=(20, 5))

        version_lbl = tk.Label(
            self, text=f"Licencia: GNU GPLv3.0\nVersión actual: '{self.version}'\nCreated by: @xorodev (CipherCoreDev)",
            font=("Segoe UI", 10, "italic"), bg="#2b2b3b", fg="#a6adc8"
        )
        version_lbl.pack(pady=(0, 15))

        desc_lbl = tk.Label(
            self,
            text="Herramienta diseñada para extraer y formatear automáticamente\n"
                 "letras de canciones para el software de proyección Holyrics.",
            font=("Segoe UI", 9), bg="#2b2b3b", fg="#cdd6f4", justify="center"
        )
        desc_lbl.pack(pady=(0, 20))

        contact_frame = tk.LabelFrame(
            self, text=" Contacto del Desarrollador ",
            font=("Segoe UI", 10, "bold"), bg="#2b2b3b", fg="#89b4fa", padx=15, pady=15
        )
        contact_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.create_hyperlink_row(contact_frame, "Licencia:", "Clic aquí.", "https://www.gnu.org/licenses/gpl-3.0.txt")
        self.create_hyperlink_row(contact_frame, "GitHub:", "Clic aquí.", "https://github.com/xorodev")
        self.create_hyperlink_row(contact_frame, "Instagram:", "Clic aquí.", "https://instagram.com/xorodev")
        self.create_hyperlink_row(contact_frame, "Gmail:", "wilfredorb0218@gmail.com", "mailto:wilfredorb0218@gmail.com")
        self.create_hyperlink_row(contact_frame, "Hotmail:", "wilfredorb.dev@hotmail.com", "mailto:wilfredorb.dev@hotmail.com")

    def create_hyperlink_row(self, parent, label_text, link_text, url):
        frame = tk.Frame(parent, bg="#2b2b3b")
        frame.pack(fill="x", pady=4)

        tk.Label(
            frame, text=label_text, font=("Segoe UI", 9, "bold"),
            bg="#2b2b3b", fg="#cdd6f4", width=10, anchor="w"
        ).pack(side="left")

        link_lbl = tk.Label(
            frame, text=link_text, font=("Segoe UI", 9, "underline"),
            bg="#2b2b3b", fg="#89b4fa", cursor="hand2"
        )
        link_lbl.pack(side="left")
        link_lbl.bind("<Button-1>", lambda event: webbrowser.open_new_tab(url))
        link_lbl.bind("<Enter>", lambda event: link_lbl.config(fg="#74c7ec"))
        link_lbl.bind("<Leave>", lambda event: link_lbl.config(fg="#89b4fa"))


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, config, update_manager, app_version, on_ytdlp_update_callback, on_app_update_callback):
        super().__init__(parent)
        self.title("Ajustes del programa")
        self.geometry("480x460")
        self.resizable(False, False)
        self.configure(bg="#2b2b3b")
        self.transient(parent)
        self.bind("<Escape>", lambda event: self.destroy())
        self.grab_set()

        try:
            self.iconbitmap(resource_path("./img/icon.ico"))
        except Exception:
            pass

        self.app_config = config
        self.update_manager = update_manager
        self.app_version = app_version
        self.on_ytdlp_update_callback = on_ytdlp_update_callback
        self.on_app_update_callback = on_app_update_callback

        self.setup_ui()

    def setup_ui(self):
        title_lbl = tk.Label(
            self, text="⚙️ Configuración y opciones",
            font=("Segoe UI", 12, "bold"), bg="#2b2b3b", fg="#74c7ec"
        )
        title_lbl.pack(pady=(15, 12))

        ytdlp_frame = tk.LabelFrame(
            self, text=" Componente yt-dlp ",
            font=("Segoe UI", 9, "bold"), bg="#2b2b3b", fg="#89b4fa", padx=15, pady=12
        )
        ytdlp_frame.pack(fill="x", padx=20, pady=(0, 14))

        installed_version = self.update_manager.get_installed_version()
        tk.Label(
            ytdlp_frame, text=f"Versión actual: '{installed_version}'",
            font=("Segoe UI", 9, "italic"), bg="#2b2b3b", fg="#a6adc8"
        ).pack(anchor="w", pady=(0, 10))

        self.notify_ytdlp_var = tk.BooleanVar(value=self.app_config.get("check_yt_dlp_updates", True))
        tk.Checkbutton(
            ytdlp_frame,
            text="Recibir notificaciones automáticas de nuevas versiones",
            variable=self.notify_ytdlp_var,
            font=("Segoe UI", 9),
            bg="#2b2b3b", fg="#cdd6f4",
            selectcolor="#1e1e2e", activebackground="#2b2b3b", activeforeground="#cdd6f4",
            wraplength=400, justify="left",
            command=self.toggle_ytdlp_notification_preference
        ).pack(anchor="w", pady=(0, 10))

        btn_ytdlp_update = tk.Button(
            ytdlp_frame,
            text="🔄 Buscar y actualizar yt-dlp",
            font=("Segoe UI", 10, "bold"),
            bg="#89b4fa", fg="#11111b",
            activebackground="#74c7ec", relief="flat", cursor="hand2",
            padx=8, pady=8,
            command=self.trigger_ytdlp_update
        )
        btn_ytdlp_update.pack(fill="x")
        bind_hover_effect(btn_ytdlp_update, "#89b4fa", "#74c7ec")

        app_frame = tk.LabelFrame(
            self, text=" Aplicación ",
            font=("Segoe UI", 9, "bold"), bg="#2b2b3b", fg="#89b4fa", padx=15, pady=12
        )
        app_frame.pack(fill="x", padx=20, pady=(0, 14))

        tk.Label(
            app_frame, text=f"Versión actual: '{self.app_version}'",
            font=("Segoe UI", 9, "italic"), bg="#2b2b3b", fg="#a6adc8"
        ).pack(anchor="w", pady=(0, 10))

        self.notify_app_var = tk.BooleanVar(value=self.app_config.get("check_app_updates", True))
        tk.Checkbutton(
            app_frame,
            text="Recibir notificaciones automáticas de nuevas versiones",
            variable=self.notify_app_var,
            font=("Segoe UI", 9),
            bg="#2b2b3b", fg="#cdd6f4",
            selectcolor="#1e1e2e", activebackground="#2b2b3b", activeforeground="#cdd6f4",
            wraplength=400, justify="left",
            command=self.toggle_app_notification_preference
        ).pack(anchor="w", pady=(0, 10))

        btn_app_update = tk.Button(
            app_frame,
            text="🔄 Buscar actualizaciones de la aplicación",
            font=("Segoe UI", 10, "bold"),
            bg="#a6e3a1", fg="#11111b",
            activebackground="#94e2d5", relief="flat", cursor="hand2",
            padx=8, pady=8,
            command=self.trigger_app_update
        )
        btn_app_update.pack(fill="x")
        bind_hover_effect(btn_app_update, "#a6e3a1", "#94e2d5")

        log_hint = tk.Label(
            self,
            text="Los registros de la aplicación se guardan en:\n"
                 "'Documentos\\HolyricsExtractor\\logs.txt'",
            font=("Segoe UI", 8), bg="#2b2b3b", fg="#6c7086", justify="center"
        )
        log_hint.pack(side="bottom", pady=(0, 12))

    def toggle_ytdlp_notification_preference(self):
        self.app_config.set("check_yt_dlp_updates", self.notify_ytdlp_var.get())

    def toggle_app_notification_preference(self):
        self.app_config.set("check_app_updates", self.notify_app_var.get())

    def trigger_ytdlp_update(self):
        self.destroy()
        self.on_ytdlp_update_callback()

    def trigger_app_update(self):
        self.destroy()
        self.on_app_update_callback()


class HolyricsApp(tk.Tk):
    EXPORT_SEPARATOR = "-" * 14

    def __init__(self):
        super().__init__()
        self.official_version = "v1.0.3-stable"

        self.logger = ApplicationLogger()
        self.app_config = ConfigurationManager(self.logger)
        self.update_manager = UpdateManager(self.logger)
        self.service = LyricsService(self.logger, self.update_manager)

        self.formatted_result = ""
        self.is_busy = False
        self.logger.write_log("INFO", "Application initialization started.")

        self.title("Extractor de Letras para Holyrics")
        self.geometry("900x720")
        self.minsize(800, 600)
        self.configure(bg="#1e1e2e")
        style = ttk.Style(self)
        try:
            icon_p = resource_path("./img/icon.ico")
            self.iconbitmap(icon_p)
        except Exception:
            pass
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TEntry", padding=6, relief="flat")
        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#181825", background="#89b4fa", thickness=6
        )

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup_menu()
        self.setup_ui()
        self.logger.write_log("INFO", "UI rendering completed successfully.")

        self.after(500, self.check_first_run_and_updates)

    def setup_menu(self):
        menubar = tk.Menu(self)

        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="⚙️ Ajustes", command=self.open_settings_dialog)
        options_menu.add_command(label="🔄 Actualizar yt-dlp", command=self.start_yt_dlp_update_thread)
        options_menu.add_separator()
        options_menu.add_command(label="❌ Salir del programa", command=self.on_close)
        menubar.add_cascade(label="Opciones", menu=options_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="ℹ️ Acerca de", command=self.open_about_dialog)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.config(menu=menubar)

    def setup_ui(self):
        header_frame = tk.Frame(self, bg="#2b2b3b", padx=20, pady=15)
        header_frame.pack(fill="x", padx=15, pady=12)

        tk.Label(
            header_frame,
            text="🎵 Extractor de Letras para Holyrics",
            font=("Segoe UI", 16, "bold"),
            bg="#2b2b3b",
            fg="#74c7ec"
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Ingrese un enlace (URL) de YouTube o el título de la canción para estructurar las diapositivas.",
            font=("Segoe UI", 10),
            bg="#2b2b3b",
            fg="#cdd6f4"
        ).pack(anchor="w", pady=(3, 0))

        form_frame = tk.Frame(self, bg="#2b2b3b", padx=20, pady=15)
        form_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(
            form_frame,
            text="Enlace de YouTube / Título de la Canción:",
            font=("Segoe UI", 10, "bold"),
            bg="#2b2b3b",
            fg="#cdd6f4"
        ).pack(anchor="w", pady=(0, 4))

        self.entry_query = ttk.Entry(form_frame, font=("Segoe UI", 10))
        self.entry_query.pack(fill="x", pady=(0, 12))
        self.entry_query.bind("<Return>", lambda event: self.start_processing_thread())

        self.btn_paste = tk.Button(
            form_frame,
            text="Pegar enlace desde el portapapeles",
            font=("Segoe UI", 9, "bold"),
            bg="#585b70",
            fg="#cdd6f4",
            activebackground="#6c7086",
            relief="flat",
            cursor="hand2",
            padx=8, pady=6,
            command=self.paste_from_clipboard
        )
        self.btn_paste.pack(fill="x", pady=(0, 12))
        bind_hover_effect(self.btn_paste, "#585b70", "#6c7086")

        tk.Label(
            form_frame,
            text="Nombre del Artista / Grupo (Opcional):",
            font=("Segoe UI", 10, "bold"),
            bg="#2b2b3b",
            fg="#cdd6f4"
        ).pack(anchor="w", pady=(0, 4))

        self.entry_artist = ttk.Entry(form_frame, font=("Segoe UI", 10))
        self.entry_artist.pack(fill="x", pady=(0, 12))
        self.entry_artist.bind("<Return>", lambda event: self.start_processing_thread())

        self.btn_process = tk.Button(
            form_frame,
            text="🔍 ¡Buscar y formatear letra!",
            font=("Segoe UI", 11, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#74c7ec",
            relief="flat",
            cursor="hand2",
            padx=8, pady=8,
            command=self.start_processing_thread
        )
        self.btn_process.pack(fill="x")
        bind_hover_effect(self.btn_process, "#89b4fa", "#74c7ec")

        self.progress_bar = ttk.Progressbar(
            form_frame, mode="indeterminate", style="Modern.Horizontal.TProgressbar"
        )

        bottom_frame = tk.Frame(self, bg="#1e1e2e")
        bottom_frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        self.btn_copy = tk.Button(
            bottom_frame,
            text="📋 Copiar resultado",
            font=("Segoe UI", 11, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            activebackground="#94e2d5",
            relief="flat",
            cursor="hand2",
            padx=8, pady=8,
            command=self.copy_to_clipboard
        )
        self.btn_copy.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        bind_hover_effect(self.btn_copy, "#a6e3a1", "#94e2d5")

        self.btn_export = tk.Button(
            bottom_frame,
            text="💾 Exportar resultado",
            font=("Segoe UI", 11, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#74c7ec",
            relief="flat",
            cursor="hand2",
            padx=8, pady=8,
            command=self.export_to_file
        )
        self.btn_export.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        bind_hover_effect(self.btn_export, "#89b4fa", "#74c7ec")

        preview_frame = tk.Frame(self, bg="#2b2b3b", padx=20, pady=15)
        preview_frame.pack(fill="both", expand=True, padx=15, pady=10)

        top_preview_frame = tk.Frame(preview_frame, bg="#2b2b3b")
        top_preview_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            top_preview_frame,
            text="Previsualización de las presentaciones:",
            font=("Segoe UI", 10, "bold"),
            bg="#2b2b3b",
            fg="#cdd6f4"
        ).pack(side="left")

        self.lbl_status = tk.Label(
            top_preview_frame,
            text="Estado de operación: En espera de una entrada",
            font=("Segoe UI", 9, "italic"),
            bg="#2b2b3b",
            fg="#a6adc8"
        )
        self.lbl_status.pack(side="right")

        self.txt_preview = scrolledtext.ScrolledText(
            preview_frame,
            wrap="word",
            font=("Consolas", 11),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="white",
            relief="flat",
            bd=5,
            state="disabled",
            cursor="arrow"
        )
        self.txt_preview.pack(fill="both", expand=True)

    def check_first_run_and_updates(self):
        pending_version = self.app_config.get("pending_update_confirmation")
        if pending_version:
            self.app_config.set("pending_update_confirmation", None)
            messagebox.showinfo(
                "Actualización completada",
                f"¡Ya se ha instalado la última versión estable correctamente!\nVersión instalada en el sistema: '{pending_version}'"
            )

        if self.app_config.get("first_run", True):
            answer = messagebox.askyesno(
                "Notificación de actualización",
                "¿Desea activar las notificaciones automáticas cuando exista una nueva actualización de yt-dlp?"
            )
            self.app_config.set("check_yt_dlp_updates", answer)
            self.app_config.set("first_run", False)

        if self.app_config.get("check_yt_dlp_updates", True):
            thread = threading.Thread(target=self.execute_background_update_check, daemon=True)
            thread.start()

        if self.update_manager.is_frozen() and self.app_config.get("check_app_updates", True):
            thread = threading.Thread(target=self.execute_background_app_update_check, daemon=True)
            thread.start()

    def execute_background_app_update_check(self):
        latest_tag, download_url = self.update_manager.get_latest_app_release()
        if latest_tag and download_url and latest_tag != self.official_version:
            self.logger.write_log("INFO", f"New application version detected: {latest_tag} (Current: {self.official_version})")
            self.after(0, self.confirm_and_start_app_update_if_idle, latest_tag, download_url)

    def confirm_and_start_app_update_if_idle(self, latest_tag, download_url):
        if self.is_busy:
            return
        self.confirm_and_start_app_update(latest_tag, download_url)

    def execute_background_update_check(self):
        current_version = self.update_manager.get_installed_version()
        latest_version, _ = self.update_manager.get_latest_available_version()

        if latest_version and latest_version != current_version:
            self.logger.write_log("INFO", f"New yt-dlp version detected: {latest_version} (Current: {current_version})")
            self.after(0, self.prompt_yt_dlp_update, current_version, latest_version)

    def prompt_yt_dlp_update(self, current_v, latest_v):
        if self.is_busy:
            return
        answer = messagebox.askyesno(
            "¡Actualización disponible!",
            f"Se ha detectado una nueva versión en yt-dlp.\n\n"
            f"• Versión instalada en el sistema: '{current_v}'\n"
            f"• Versión disponible: '{latest_v}'\n\n"
            "¿Desea realizar la actualización en este momento?"
        )
        if answer:
            self.start_yt_dlp_update_thread()

    def start_yt_dlp_update_thread(self):
        if self.is_busy:
            messagebox.showinfo(
                "Operación en Curso",
                "Ya hay una operación en curso. Espere a que finalice antes de iniciar otra."
            )
            return
        self.set_ui_state(True)
        self.lbl_status.config(text="Estado de operación: Actualizando componente yt-dlp...")
        thread = threading.Thread(target=self.execute_yt_dlp_update, daemon=True)
        thread.start()

    def execute_yt_dlp_update(self):
        try:
            success, message = self.update_manager.perform_clean_update()
        except Exception as error:
            success, message = False, str(error)
            self.logger.write_log("ALERT", f"Unexpected error during yt-dlp update: {str(error)}")
        self.after(0, self.handle_yt_dlp_update_result, success, message)

    def handle_yt_dlp_update_result(self, success, message):
        self.set_ui_state(False)
        if success:
            new_v = self.update_manager.get_installed_version()
            self.lbl_status.config(text=f"Estado de operación: yt-dlp actualizado a la versión '{new_v}'")
            messagebox.showinfo(
                "Actualización exitosa",
                f"El componente yt-dlp ha sido actualizado de forma limpia a la nueva versión: '{new_v}'"
            )
        else:
            self.lbl_status.config(text="Estado de operación: Fallo al actualizar yt-dlp")
            messagebox.showerror(
                "Error de actualización",
                f"No fue posible completar la actualización de yt-dlp.\n\nDetalles técnicos:\n{message}"
            )

    def start_app_update_thread(self):
        if not self.update_manager.is_frozen():
            messagebox.showinfo(
                "Función no disponible",
                "La búsqueda de actualizaciones de la aplicación solo está disponible en la versión compilada (.exe) del programa."
            )
            return
        if self.is_busy:
            messagebox.showinfo(
                "Operación en curso",
                "Ya hay una operación en curso. Espere a que finalice antes de iniciar otra..."
            )
            return
        self.set_ui_state(True)
        self.lbl_status.config(text="Estado de operación: Buscando actualizaciones de la aplicación...")
        thread = threading.Thread(target=self.execute_app_update_check, daemon=True)
        thread.start()

    def execute_app_update_check(self):
        latest_tag, download_url = self.update_manager.get_latest_app_release()
        self.after(0, self.handle_app_update_check_result, latest_tag, download_url)

    def handle_app_update_check_result(self, latest_tag, download_url):
        self.set_ui_state(False)
        if not latest_tag or not download_url:
            messagebox.showwarning(
                "Sin conexión con el servidor",
                "No fue posible comprobar si existen actualizaciones disponibles en este momento."
            )
            return
        if latest_tag == self.official_version:
            messagebox.showinfo(
                "Aplicación actualizada",
                f"Ya tiene instalada la última versión disponible: '{self.official_version}'"
            )
            return
        self.confirm_and_start_app_update(latest_tag, download_url)

    def confirm_and_start_app_update(self, latest_tag, download_url):
        answer = messagebox.askyesno(
            "Nueva versión disponible",
            f"Hay una nueva versión de la aplicación disponible.\n\n"
            f"• Versión instalada: '{self.official_version}'\n"
            f"• Versión disponible: '{latest_tag}'\n\n"
            "¿Desea descargarla e instalarla ahora? La aplicación se reiniciará automáticamente al finalizar."
        )
        if answer:
            self.start_app_update_download_thread(latest_tag, download_url)

    def start_app_update_download_thread(self, latest_tag, download_url):
        self.set_ui_state(True)
        self.progress_bar.config(mode="determinate", maximum=100, value=0)
        self.lbl_status.config(text="Estado de operación: Descargando la nueva versión (0%)...")
        thread = threading.Thread(target=self.execute_app_update_download, args=(latest_tag, download_url), daemon=True)
        thread.start()

    def execute_app_update_download(self, latest_tag, download_url):
        def report_progress(downloaded, total):
            percent = int((downloaded / total) * 100) if total else 0
            self.after(0, self.update_app_download_progress, percent)

        try:
            new_exe_path = self.update_manager.download_new_build(download_url, progress_callback=report_progress)
            self.after(0, self.finalize_app_update, latest_tag, new_exe_path)
        except Exception as error:
            self.logger.write_log("ALERT", f"Application self-update download failed: {str(error)}")
            self.after(0, self.handle_app_update_failure, str(error))

    def update_app_download_progress(self, percent):
        self.progress_bar.config(value=percent)
        self.lbl_status.config(text=f"Estado de operación: Descargando la nueva versión ({percent}%)...")

    def finalize_app_update(self, latest_tag, new_exe_path):
        self.set_ui_state(False)
        self.progress_bar.config(mode="indeterminate")
        messagebox.showinfo(
            "Actualización lista",
            "La nueva versión se descargó correctamente.\nLa aplicación se cerrará y se reiniciará automáticamente para completar la instalación."
        )
        self.app_config.set("pending_update_confirmation", latest_tag)
        self.logger.write_log("INFO", "Application self-update download complete. Relaunching with new build.")
        self.update_manager.apply_self_update_and_relaunch(new_exe_path)
        self.destroy()

    def handle_app_update_failure(self, message):
        self.set_ui_state(False)
        self.progress_bar.config(mode="indeterminate")
        self.lbl_status.config(text="Estado de operación: Fallo al actualizar la aplicación.")
        messagebox.showerror(
            "Error de actualización",
            f"No fue posible completar la actualización de la aplicación.\n\nDetalles técnicos:\n{message}"
        )

    def open_about_dialog(self):
        AboutDialog(self, self.official_version)

    def open_settings_dialog(self):
        SettingsDialog(
            self, self.app_config, self.update_manager, self.official_version,
            self.start_yt_dlp_update_thread, self.start_app_update_thread
        )

    def set_ui_state(self, is_processing):
        self.is_busy = is_processing
        if is_processing:
            self.btn_process.config(state="disabled", text="⌛ Procesando solicitud, por favor espere...")
            self.progress_bar.pack(fill="x", pady=(10, 0))
            self.progress_bar.start(12)
        else:
            self.btn_process.config(state="normal", text="🔍 ¡Buscar y formatear letra!")
            self.progress_bar.stop()
            self.progress_bar.pack_forget()

    def start_processing_thread(self):
        if self.is_busy:
            messagebox.showinfo(
                "Operación en Curso",
                "Ya hay una operación en curso. Espere a que finalice antes de iniciar otra."
            )
            return

        query = self.entry_query.get().strip()
        artist = self.entry_artist.get().strip()

        if not query:
            self.logger.write_log("WARNING", "User attempted search with empty query field.")
            messagebox.showwarning(
                "Campo requerido",
                "Por favor, ingrese un enlace (URL) de YouTube válida, o sino el título de una canción para continuar con el proceso..."
            )
            return

        self.set_ui_state(True)
        self.lbl_status.config(text="Estado de operación: Buscando y procesando la letra...")
        thread = threading.Thread(target=self.execute_lyrics_extraction, args=(query, artist), daemon=True)
        thread.start()

    def execute_lyrics_extraction(self, query, artist):
        try:
            target_query = query
            if self.service.is_youtube_url(query):
                self.logger.write_log("INFO", "Detectado enlace de YouTube en la entrada.")
                target_query = self.service.resolve_youtube_query(query)

            raw_lyrics = self.service.fetch_lyrics(target_query, artist)

            if not raw_lyrics and artist:
                self.logger.write_log("INFO", "Failing back to query search without artist filter.")
                raw_lyrics = self.service.fetch_lyrics(target_query, "")

            if not raw_lyrics:
                self.logger.write_log("ALERT", f"Could not find lyrics for query: '{target_query}'")
                self.after(0, self.handle_extraction_failure, target_query)
                return

            formatted_text, total_slides = self.service.format_stanzas(raw_lyrics)
            self.formatted_result = formatted_text

            self.logger.write_log("INFO", f"Extraction successful. Total slides created: {total_slides}")
            self.after(0, self.update_preview_ui, formatted_text, total_slides)

        except Exception as error:
            self.logger.write_log("ALERT", f"Critical exception during execution: {str(error)}")
            self.after(0, self.handle_critical_error, str(error))

    def update_preview_ui(self, formatted_text, total_slides):
        self.set_ui_state(False)
        self.txt_preview.config(state="normal")
        self.txt_preview.delete("1.0", tk.END)

        blocks = formatted_text.split("\n\n")
        for index, block in enumerate(blocks, start=1):
            self.txt_preview.insert(tk.END, f"--- PRESENTACIÓN {index} ---\n", "header")
            self.txt_preview.insert(tk.END, f"{block}\n\n")

        self.txt_preview.tag_config("header", foreground="#89b4fa", font=("Consolas", 10, "bold"))
        self.txt_preview.config(state="disabled")
        self.lbl_status.config(text=f"Estado de operación: {total_slides} presentaciones generadas correctamente.")

        messagebox.showinfo(
            "Proceso completado",
            f"¡Se ha procesado la letra correctamente!\nSe generaron un total de: {total_slides} presentaciones independientes."
        )

    def handle_extraction_failure(self, query):
        self.set_ui_state(False)
        self.lbl_status.config(text="Estado de operación: ¡No se encontraron resultados disponibles!")
        messagebox.showerror(
            "Búsqueda sin resultados",
            f"No fue posible encontrar la letra correspondiente en la canción: '{query}'\n\n"
            "¡Inténtelo de nuevo! Verificar el título de la canción, o intente especificar el nombre del artista deseado."
        )

    def handle_critical_error(self, error_message):
        self.set_ui_state(False)
        self.lbl_status.config(text="Estado de operación: ¡Error inesperado en el sistema!")
        messagebox.showerror(
            "Error en el sistema",
            "Ha ocurrido un error durante la ejecución de la tarea.\n"
            f"Detalles técnicos: {error_message}\n\n"
            "Los detalles han sido registrados en el archivo de registros de la aplicación."
        )

    def paste_from_clipboard(self):
        try:
            clipboard_content = self.clipboard_get().strip()
        except tk.TclError:
            self.logger.write_log("WARNING", "User attempted clipboard paste with empty or invalid clipboard.")
            messagebox.showwarning(
                "Portapapeles vacío",
                "No se encontró ningún contenido de texto válido en el portapapeles para pegar..."
            )
            return

        if not clipboard_content:
            self.logger.write_log("WARNING", "User attempted clipboard paste with empty clipboard content.")
            messagebox.showwarning(
                "Portapapeles vacío",
                "No se encontró ningún contenido de texto válido en el portapapeles para pegar..."
            )
            return

        if not self.service.is_youtube_url(clipboard_content):
            self.logger.write_log("WARNING", f"Clipboard content rejected as invalid YouTube URL: '{clipboard_content}'")
            messagebox.showwarning(
                "Enlace no válido",
                "El contenido copiado no corresponde a un enlace (URL) de YouTube válido.\n\n"
                "Solo se aceptan enlaces de YouTube. "
                "¡Verifique el enlace copiado que sea de YouTube e inténtelo nuevamente!"
            )
            return

        self.entry_query.delete(0, tk.END)
        self.entry_query.insert(0, clipboard_content)
        self.logger.write_log("INFO", "Clipboard content pasted successfully into query field.")
        self.lbl_status.config(text="Estado de operación: Enlace pegado desde el portapapeles correctamente.")

    def copy_to_clipboard(self):
        if self.formatted_result:
            self.clipboard_clear()
            self.clipboard_append(self.formatted_result)
            self.logger.write_log("INFO", "Formatted content successfully copied to user clipboard.")
            messagebox.showinfo(
                "Contenido copiado",
                "El texto estructurado ha sido copiado al portapapeles."
            )
        else:
            self.logger.write_log("WARNING", "User requested copy operation on empty result set.")
            messagebox.showwarning(
                "Sin contenido",
                "Aún no hay ningún texto procesado para copiar en el portapapeles..."
            )

    def build_export_content(self):
        blocks = [block for block in self.formatted_result.split("\n\n") if block.strip()]
        return f"\n{self.EXPORT_SEPARATOR}\n".join(blocks)

    def export_to_file(self):
        if not self.formatted_result:
            self.logger.write_log("WARNING", "User requested export operation on empty result set.")
            messagebox.showwarning(
                "Sin contenido",
                "Aún no hay ningún texto procesado para exportar..."
            )
            return

        default_name = f"Lyrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar estructura de presentaciones",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.build_export_content())
            self.logger.write_log("INFO", f"Exported formatted lyrics to file: {file_path}")
            messagebox.showinfo(
                "Exportación completada",
                f"El archivo se ha exportado correctamente en:\n{file_path}"
            )
        except OSError as error:
            self.logger.write_log("ALERT", f"Failed to export file: {str(error)}")
            messagebox.showerror(
                "Error al exportar",
                f"No fue posible guardar el archivo.\n\nDetalles técnicos:\n{str(error)}"
            )

    def on_close(self):
        if self.is_busy:
            proceed = messagebox.askyesno(
                "Operación en curso",
                "Hay una operación en curso (búsqueda o actualización).\n"
                "¿Desea salir de todas formas? La operación se cancelará."
            )
            if not proceed:
                return
        self.logger.write_log("INFO", "Application closing.")
        self.destroy()


if __name__ == "__main__":
    enable_windows_dpi_awareness()
    app = HolyricsApp()
    app.mainloop()
