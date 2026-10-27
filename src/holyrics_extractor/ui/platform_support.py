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
import ctypes
import sys
import tkinter as tk

MENU_POST_BLOCKS = sys.platform in ("win32", "darwin")
_APP_USER_MODEL_ID = "xorodev.holyricsextractor.gui.1.0"
_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY = 19

def enable_windows_dpi_awareness() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_APP_USER_MODEL_ID)
    except (AttributeError, OSError):
        pass

def apply_title_bar_theme(window: tk.Misc, dark: bool) -> None:
    if sys.platform != "win32":
        return
    try:
        from ctypes import wintypes

        window.update_idletasks()
        user32 = ctypes.WinDLL("user32")
        user32.GetParent.argtypes = [wintypes.HWND]
        user32.GetParent.restype = wintypes.HWND
        dwmapi = ctypes.WinDLL("dwmapi")
        dwmapi.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
        handle = user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        for attribute in (_DWMWA_USE_IMMERSIVE_DARK_MODE, _DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY):
            if dwmapi.DwmSetWindowAttribute(handle, attribute, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                break
    except (AttributeError, OSError, ctypes.ArgumentError, tk.TclError):
        pass

def maximize_window(window: tk.Tk) -> None:
    try:
        if sys.platform == "win32":
            window.state("zoomed")
        else:
            window.attributes("-zoomed", True)
    except tk.TclError:
        window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")