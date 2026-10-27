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
from ..core.settings import (
    ANIMATION_HOVER,
    ANIMATION_NOTIFICATIONS,
    ANIMATION_RESULTS,
    ANIMATION_SPEED,
    ANIMATION_WINDOWS,
    ANIMATIONS_ENABLED,
    SPEED_FAST,
    SPEED_NORMAL,
    SPEED_SLOW,
    SettingsStore,
)
from .dialogs import ModalDialog
from .theme import ThemeManager
from .widgets import ThemedButton, ThemedCheckbutton, ThemedFrame, ThemedLabel, ThemedRadiobutton, ui_font

SPEED_OPTIONS = (
    (SPEED_SLOW, "Lenta"),
    (SPEED_NORMAL, "Normal"),
    (SPEED_FAST, "Rápida"),
)

EFFECT_OPTIONS = (
    (ANIMATION_HOVER, "Transición de color al pasar el cursor sobre los botones"),
    (ANIMATION_NOTIFICATIONS, "Aparición y salida suave de las notificaciones"),
    (ANIMATION_WINDOWS, "Aparición gradual de las ventanas emergentes"),
    (ANIMATION_RESULTS, "Aparición gradual de los versos generados"),
)

class AnimationSettingsDialog(ModalDialog):
    WRAP_LENGTH = 420

    def __init__(self, parent: tk.Misc, theme: ThemeManager, settings: SettingsStore):
        super().__init__(parent, theme, "Animaciones")
        self._settings = settings
        self._enabled = tk.BooleanVar(master=self, value=settings.get(ANIMATIONS_ENABLED))
        self._speed = tk.StringVar(master=self, value=settings.get(ANIMATION_SPEED))
        self._effects = {key: tk.BooleanVar(master=self, value=settings.get(key)) for key, _label in EFFECT_OPTIONS}
        self._dependent_controls: list[tk.Widget] = []

        body = ThemedFrame(self, theme)
        body.pack(fill="both", expand=True, padx=24, pady=(18, 10))
        ThemedLabel(body, theme, "✦ Animaciones de la interfaz", role="title", font=ui_font(12, "bold")).pack(
            pady=(0, 6)
        )
        ThemedLabel(
            body,
            theme,
            "Los cambios se aplican de forma inmediata. Desactivar las animaciones hace que la interfaz responda al instante.",
            role="text_muted",
            font=ui_font(9),
            wraplength=self.WRAP_LENGTH,
            justify="center",
        ).pack(pady=(0, 12))

        ThemedCheckbutton(
            body, theme, "Activar animaciones", self._enabled, self._save_enabled, wraplength=self.WRAP_LENGTH
        ).pack(anchor="w", pady=(0, 12))

        self._build_speed_section(body)
        self._build_effects_section(body)

        ThemedButton(body, theme, "Cerrar", self.close, variant="neutral").pack(pady=(4, 0))
        self._refresh_dependent_controls()
        self.present()

    def _build_section(self, parent: tk.Misc, title: str) -> tk.LabelFrame:
        frame = tk.LabelFrame(parent, text=f" {title} ", font=ui_font(9, "bold"), padx=16, pady=10, bd=1)
        self.theme.register(frame, bg="panel_bg", fg="accent")
        frame.pack(fill="x", pady=(0, 14))
        return frame

    def _build_speed_section(self, parent: tk.Misc) -> None:
        frame = self._build_section(parent, "Velocidad")
        for value, label in SPEED_OPTIONS:
            option = ThemedRadiobutton(frame, self.theme, label, self._speed, value, self._save_speed)
            option.pack(side="left", padx=(0, 22))
            self._dependent_controls.append(option)

    def _build_effects_section(self, parent: tk.Misc) -> None:
        frame = self._build_section(parent, "Efectos")
        for key, label in EFFECT_OPTIONS:
            option = ThemedCheckbutton(
                frame, self.theme, label, self._effects[key], lambda effect=key: self._save_effect(effect),
                wraplength=self.WRAP_LENGTH - 40,
            )
            option.pack(anchor="w", pady=3)
            self._dependent_controls.append(option)

    def _save_enabled(self) -> None:
        self._settings.set(ANIMATIONS_ENABLED, self._enabled.get())
        self._refresh_dependent_controls()

    def _save_speed(self) -> None:
        self._settings.set(ANIMATION_SPEED, self._speed.get())

    def _save_effect(self, key: str) -> None:
        self._settings.set(key, self._effects[key].get())

    def _refresh_dependent_controls(self) -> None:
        state = "normal" if self._enabled.get() else "disabled"
        for control in self._dependent_controls:
            control.configure(state=state)