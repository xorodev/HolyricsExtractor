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
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Callable
from ..core.settings import THEME_DARK, THEME_LIGHT
from .animation.motion import Motion
from .platform_support import apply_title_bar_theme

@dataclass(frozen=True, slots=True)

class Palette:
    window_bg: str
    panel_bg: str
    field_bg: str
    text: str
    text_muted: str
    text_faint: str
    title: str
    accent: str
    accent_hover: str
    accent_text: str
    success: str
    success_hover: str
    success_text: str
    danger: str
    danger_hover: str
    danger_text: str
    warning: str
    neutral: str
    neutral_hover: str
    neutral_text: str
    disabled_bg: str
    link: str
    link_hover: str
    border: str

DARK_PALETTE = Palette(
    window_bg="#1e1e2e",
    panel_bg="#2b2b3b",
    field_bg="#181825",
    text="#cdd6f4",
    text_muted="#a6adc8",
    text_faint="#6c7086",
    title="#74c7ec",
    accent="#89b4fa",
    accent_hover="#74c7ec",
    accent_text="#11111b",
    success="#a6e3a1",
    success_hover="#94e2d5",
    success_text="#11111b",
    danger="#f38ba8",
    danger_hover="#eba0ac",
    danger_text="#11111b",
    warning="#f9e2af",
    neutral="#585b70",
    neutral_hover="#6c7086",
    neutral_text="#cdd6f4",
    disabled_bg="#3b3b4f",
    link="#89b4fa",
    link_hover="#74c7ec",
    border="#45475a",
)

LIGHT_PALETTE = Palette(
    window_bg="#eff1f5",
    panel_bg="#ffffff",
    field_bg="#e6e9ef",
    text="#4c4f69",
    text_muted="#5c5f77",
    text_faint="#7c7f93",
    title="#1e66f5",
    accent="#1e66f5",
    accent_hover="#1a56cc",
    accent_text="#ffffff",
    success="#2e8b22",
    success_hover="#26751c",
    success_text="#ffffff",
    danger="#d20f39",
    danger_hover="#b30c30",
    danger_text="#ffffff",
    warning="#b45f06",
    neutral="#bcc0cc",
    neutral_hover="#acb0be",
    neutral_text="#4c4f69",
    disabled_bg="#ccd0da",
    link="#1e66f5",
    link_hover="#1a56cc",
    border="#ccd0da",
)

PALETTES = {THEME_DARK: DARK_PALETTE, THEME_LIGHT: LIGHT_PALETTE}

ThemeApplier = Callable[[Palette], None]

class ThemeManager:
    def __init__(self, root: tk.Tk, theme_name: str, on_change: Callable[[str], None], motion: Motion):
        self._root = root
        self._motion = motion
        self._name = theme_name if theme_name in PALETTES else THEME_DARK
        self._on_change = on_change
        self._entries: dict[str, tuple[tk.Misc, list[ThemeApplier]]] = {}
        self._style = ttk.Style(root)
        try:
            self._style.theme_use("clam")
        except tk.TclError:
            pass
        self._apply_ttk_styles()

    @property
    def motion(self) -> Motion:
        return self._motion

    @property
    def name(self) -> str:
        return self._name

    @property
    def palette(self) -> Palette:
        return PALETTES[self._name]

    @property
    def is_dark(self) -> bool:
        return self._name == THEME_DARK

    def track(self, widget: tk.Misc, applier: ThemeApplier) -> None:
        key = str(widget)
        entry = self._entries.get(key)
        if entry is None:
            self._entries[key] = (widget, [applier])
            widget.bind("<Destroy>", lambda event, path=key, owner=widget: self._forget(event, path, owner), add="+")
        else:
            entry[1].append(applier)
        applier(self.palette)

    def register(self, widget: tk.Misc, **option_roles: str) -> None:
        def applier(palette: Palette) -> None:
            widget.configure(**{option: getattr(palette, role) for option, role in option_roles.items()})

        self.track(widget, applier)

    def toggle(self) -> None:
        self.set_theme(THEME_LIGHT if self.is_dark else THEME_DARK)

    def set_theme(self, theme_name: str) -> None:
        if theme_name not in PALETTES or theme_name == self._name:
            return
        self._name = theme_name
        self._apply_ttk_styles()
        for widget, appliers in list(self._entries.values()):
            for applier in appliers:
                try:
                    applier(self.palette)
                except tk.TclError:
                    continue
        self._on_change(theme_name)

    def _forget(self, event: tk.Event, key: str, owner: tk.Misc) -> None:
        if event.widget is owner:
            self._entries.pop(key, None)

    def _apply_ttk_styles(self) -> None:
        palette = self.palette
        self._style.configure(
            "TEntry",
            padding=6,
            relief="flat",
            fieldbackground=palette.field_bg,
            foreground=palette.text,
            insertcolor=palette.text,
            bordercolor=palette.border,
            lightcolor=palette.border,
            darkcolor=palette.border,
        )
        self._style.map(
            "TEntry",
            bordercolor=[("focus", palette.accent)],
            lightcolor=[("focus", palette.accent)],
            darkcolor=[("focus", palette.accent)],
        )
        self._style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor=palette.field_bg,
            background=palette.accent,
            bordercolor=palette.field_bg,
            lightcolor=palette.accent,
            darkcolor=palette.accent,
            thickness=6,
        )
        self._style.configure(
            "Modern.Vertical.TScrollbar",
            troughcolor=palette.field_bg,
            background=palette.neutral,
            bordercolor=palette.field_bg,
            lightcolor=palette.neutral,
            darkcolor=palette.neutral,
            arrowcolor=palette.text,
            relief="flat",
        )
        self._style.map("Modern.Vertical.TScrollbar", background=[("active", palette.neutral_hover)])

    def track_window(self, window: tk.Misc, surface: str) -> None:
        self.register(window, bg=surface)
        self.track(window, lambda palette: apply_title_bar_theme(window, self.is_dark))