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
import time
import tkinter as tk
from typing import Callable
from ..core.settings import ANIMATION_NOTIFICATIONS
from ..paths import resource_path
from .animation.animator import Animation
from .animation.colors import blend_colors
from .animation.transitions import HoverTransition
from .platform_support import MENU_POST_BLOCKS
from .theme import Palette, ThemeManager

FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"

MENU_ARROW_CLOSED = "▾"
MENU_ARROW_OPEN = "▴"
MENU_REOPEN_GUARD_SECONDS = 0.3

VARIANT_ROLES = {
    "primary": ("accent", "accent_hover", "accent_text"),
    "success": ("success", "success_hover", "success_text"),
    "danger": ("danger", "danger_hover", "danger_text"),
    "neutral": ("neutral", "neutral_hover", "neutral_text"),
}

TOAST_BORDER_ROLES = {
    "info": "accent",
    "success": "success",
    "warning": "warning",
    "error": "danger",
}

def ui_font(size: int, style: str = "") -> tuple:
    return (FONT_FAMILY, size, style) if style else (FONT_FAMILY, size)

def mono_font(size: int, style: str = "") -> tuple:
    return (MONO_FAMILY, size, style) if style else (MONO_FAMILY, size)

def apply_window_icon(window: tk.Wm) -> None:
    try:
        window.iconbitmap(str(resource_path("img/icon.ico")))
    except tk.TclError:
        pass

class ThemedFrame(tk.Frame):
    def __init__(self, parent: tk.Misc, theme: ThemeManager, surface: str = "panel_bg", **options):
        super().__init__(parent, bd=0, highlightthickness=0, **options)
        theme.register(self, bg=surface)

class ThemedLabel(tk.Label):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        text: str = "",
        *,
        role: str = "text",
        surface: str = "panel_bg",
        font: tuple | None = None,
        **options,
    ):
        super().__init__(parent, text=text, font=font or ui_font(10), bd=0, **options)
        self._theme = theme
        self._role = role
        self._surface = surface
        theme.track(self, self._apply)

    def _apply(self, palette: Palette) -> None:
        self.configure(bg=getattr(palette, self._surface), fg=getattr(palette, self._role))

    def set_role(self, role: str) -> None:
        self._role = role
        self._apply(self._theme.palette)

class ThemedButton(tk.Button):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        text: str,
        command: Callable[[], None],
        *,
        variant: str = "primary",
        font: tuple | None = None,
        padx: int = 10,
        pady: int = 8,
        **options,
    ):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=font or ui_font(10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            padx=padx,
            pady=pady,
            **options,
        )
        self._theme = theme
        self._variant = variant
        self._hovered = False
        self._transition = HoverTransition(self, theme.motion, lambda color: self.configure(bg=color))
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        theme.track(self, self._apply)

    @property
    def is_enabled(self) -> bool:
        return str(self.cget("state")) != "disabled"

    def set_enabled(self, enabled: bool) -> None:
        self.configure(state="normal" if enabled else "disabled", cursor="hand2" if enabled else "arrow")
        self._hovered = self._hovered and enabled
        self._apply(self._theme.palette)

    def _on_enter(self, _event: tk.Event) -> None:
        self._hovered = self.is_enabled
        self._animate_background()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hovered = False
        self._animate_background()

    def _animate_background(self) -> None:
        if not self.is_enabled:
            return
        base_role, hover_role, _ = VARIANT_ROLES[self._variant]
        target = getattr(self._theme.palette, hover_role if self._hovered else base_role)
        self._transition.run(str(self.cget("bg")), target)

    def _apply(self, palette: Palette) -> None:
        self._transition.cancel()
        base_role, hover_role, text_role = VARIANT_ROLES[self._variant]
        if not self.is_enabled:
            self.configure(bg=palette.disabled_bg, fg=palette.text_faint, activebackground=palette.disabled_bg)
            return
        background = getattr(palette, hover_role if self._hovered else base_role)
        foreground = getattr(palette, text_role)
        self.configure(
            bg=background,
            fg=foreground,
            activebackground=getattr(palette, hover_role),
            activeforeground=foreground,
        )

class ThemedCheckbutton(tk.Checkbutton):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        text: str,
        variable: tk.BooleanVar,
        command: Callable[[], None] | None = None,
        *,
        wraplength: int = 0,
    ):
        super().__init__(
            parent,
            text=text,
            variable=variable,
            command=command,
            font=ui_font(9),
            bd=0,
            highlightthickness=0,
            wraplength=wraplength,
            justify="left",
            anchor="w",
            cursor="hand2",
        )
        theme.register(
            self,
            bg="panel_bg",
            fg="text",
            selectcolor="field_bg",
            activebackground="panel_bg",
            activeforeground="text",
            disabledforeground="text_faint",
        )

class ThemedRadiobutton(tk.Radiobutton):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        text: str,
        variable: tk.StringVar,
        value: str,
        command: Callable[[], None] | None = None,
    ):
        super().__init__(
            parent,
            text=text,
            variable=variable,
            value=value,
            command=command,
            font=ui_font(9),
            bd=0,
            highlightthickness=0,
            anchor="w",
            cursor="hand2",
        )
        theme.register(
            self,
            bg="panel_bg",
            fg="text",
            selectcolor="field_bg",
            activebackground="panel_bg",
            activeforeground="text",
            disabledforeground="text_faint",
        )

class ThemedMenuButton(tk.Menubutton):
    def __init__(self, parent: tk.Misc, theme: ThemeManager, text: str):
        self._label = text
        self._theme = theme
        self._closed_at = 0.0
        self._is_open = False
        self._hovered = False
        super().__init__(
            parent,
            text=f"{text} {MENU_ARROW_CLOSED}",
            font=ui_font(10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=7,
            cursor="hand2",
        )
        self._transition = HoverTransition(self, theme.motion, lambda color: self.configure(bg=color))
        self.bindtags(tuple(tag for tag in self.bindtags() if tag != "Menubutton"))
        self.bind("<Enter>", lambda _event: self._set_hovered(True))
        self.bind("<Leave>", lambda _event: self._set_hovered(False))
        self.bind("<ButtonPress-1>", self._on_press)
        self.menu = create_menu(self, theme)
        if not MENU_POST_BLOCKS:
            self.menu.bind("<Unmap>", self._mark_closed)
        theme.track(self, self._apply)

    def _target_background(self, palette: Palette) -> str:
        return palette.neutral_hover if self._hovered or self._is_open else palette.neutral

    def _apply(self, palette: Palette) -> None:
        self._transition.cancel()
        self.configure(
            bg=self._target_background(palette),
            fg=palette.neutral_text,
            activebackground=palette.neutral_hover,
            activeforeground=palette.neutral_text,
        )

    def _animate_background(self) -> None:
        self._transition.run(str(self.cget("bg")), self._target_background(self._theme.palette))

    def _set_hovered(self, hovered: bool) -> None:
        self._hovered = hovered
        self._animate_background()

    def _on_press(self, _event: tk.Event) -> None:
        if self._is_open:
            self.menu.unpost()
        elif time.monotonic() - self._closed_at >= MENU_REOPEN_GUARD_SECONDS:
            self._open_menu()

    def _open_menu(self) -> None:
        self._is_open = True
        self.configure(text=f"{self._label} {MENU_ARROW_OPEN}")
        self._animate_background()
        try:
            self.menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())
        finally:
            self.menu.grab_release()
        if MENU_POST_BLOCKS:
            self._mark_closed()

    def _mark_closed(self, _event: tk.Event | None = None) -> None:
        self._is_open = False
        self._closed_at = time.monotonic()
        self.configure(text=f"{self._label} {MENU_ARROW_CLOSED}")
        self._animate_background()

def create_menu(parent: tk.Misc, theme: ThemeManager) -> tk.Menu:
    menu = tk.Menu(parent, tearoff=0, bd=0, relief="flat", activeborderwidth=0, font=ui_font(10))
    theme.register(
        menu,
        bg="panel_bg",
        fg="text",
        activebackground="accent",
        activeforeground="accent_text",
        disabledforeground="text_faint",
    )
    return menu

class CircleButton(tk.Canvas):
    def __init__(
        self,
        parent: tk.Misc,
        theme: ThemeManager,
        glyph: str,
        command: Callable[[], None],
        *,
        size: int,
        glyph_size: int,
        surface: str,
        variant: str = "primary",
    ):
        super().__init__(parent, width=size, height=size, highlightthickness=0, bd=0, cursor="hand2")
        self._theme = theme
        self._surface = surface
        self._variant = variant
        self._hovered = False
        self._circle = self.create_oval(1, 1, size - 1, size - 1, width=0)
        self._glyph = self.create_text(size // 2, size // 2, text=glyph, font=ui_font(glyph_size, "bold"))
        self._transition = HoverTransition(self, theme.motion, lambda color: self.itemconfigure(self._circle, fill=color))
        self.bind("<Button-1>", lambda _event: command())
        self.bind("<Enter>", lambda _event: self._set_hover(True))
        self.bind("<Leave>", lambda _event: self._set_hover(False))
        theme.track(self, self._apply)

    def _set_hover(self, hovered: bool) -> None:
        self._hovered = hovered
        base_role, hover_role, _ = VARIANT_ROLES[self._variant]
        target = getattr(self._theme.palette, hover_role if hovered else base_role)
        self._transition.run(str(self.itemcget(self._circle, "fill")), target)

    def _apply(self, palette: Palette) -> None:
        self._transition.cancel()
        base_role, hover_role, text_role = VARIANT_ROLES[self._variant]
        self.configure(bg=getattr(palette, self._surface))
        self.itemconfigure(self._circle, fill=getattr(palette, hover_role if self._hovered else base_role))
        self.itemconfigure(self._glyph, fill=getattr(palette, text_role))

class Tooltip:
    DELAY_MS = 450
    GAP = 6

    def __init__(self, widget: tk.Misc, theme: ThemeManager, text: str, *, above: bool = False):
        self._widget = widget
        self._theme = theme
        self._text = text
        self._above = above
        self._job: str | None = None
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")
        widget.bind("<Destroy>", self._hide, add="+")

    def _schedule(self, _event: tk.Event) -> None:
        self._hide()
        self._job = self._widget.after(self.DELAY_MS, self._show)

    def _show(self) -> None:
        self._job = None
        tip = tk.Toplevel(self._widget)
        tip.wm_overrideredirect(True)
        tip.configure(bg=self._theme.palette.border)
        ThemedLabel(tip, self._theme, self._text, font=ui_font(9), padx=10, pady=5).pack(padx=1, pady=1)
        tip.update_idletasks()
        width, height = tip.winfo_reqwidth(), tip.winfo_reqheight()
        center = self._widget.winfo_rootx() + self._widget.winfo_width() // 2
        x = min(max(center - width // 2, 0), max(self._widget.winfo_screenwidth() - width, 0))
        top = self._widget.winfo_rooty()
        y = top - height - self.GAP if self._above else top + self._widget.winfo_height() + self.GAP
        tip.geometry(f"+{x}+{max(y, 0)}")
        self._tip = tip

    def _hide(self, _event: tk.Event | None = None) -> None:
        if self._job is not None:
            self._widget.after_cancel(self._job)
            self._job = None
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None

class Toast(ThemedLabel):
    DURATION_MS = 3000
    SLIDE_MS = 220
    BASE_OFFSET_PX = 78
    SLIDE_DISTANCE_PX = 26

    def __init__(self, parent: tk.Misc, theme: ThemeManager):
        self._border_role = "accent"
        self._hide_job: str | None = None
        self._animation: Animation | None = None
        self._visible = False
        super().__init__(
            parent,
            theme,
            "",
            role="text",
            surface="panel_bg",
            font=ui_font(10, "bold"),
            padx=18,
            pady=10,
            highlightthickness=2,
            wraplength=560,
        )

    def _apply(self, palette: Palette) -> None:
        super()._apply(palette)
        self.configure(highlightbackground=getattr(palette, self._border_role))

    def show(self, message: str, kind: str = "info") -> None:
        self._border_role = TOAST_BORDER_ROLES.get(kind, "accent")
        self.configure(text=message)
        self._apply(self._theme.palette)
        if self._hide_job is not None:
            self.after_cancel(self._hide_job)
        self._run_slide(entering=True, base_ms=0 if self._visible else self.SLIDE_MS)
        self.lift()
        self._visible = True
        self._hide_job = self.after(self.DURATION_MS, self._hide)

    def _hide(self) -> None:
        self._hide_job = None
        self._run_slide(entering=False, base_ms=self.SLIDE_MS, on_done=self._finish_hide)

    def _finish_hide(self) -> None:
        self._visible = False
        self.place_forget()

    def _run_slide(self, *, entering: bool, base_ms: int, on_done: Callable[[], None] | None = None) -> None:
        if self._animation is not None:
            self._animation.cancel()

        def render(progress: float) -> None:
            shown = progress if entering else 1 - progress
            palette = self._theme.palette
            self.configure(
                fg=blend_colors(palette.panel_bg, palette.text, shown),
                highlightbackground=blend_colors(palette.panel_bg, getattr(palette, self._border_role), shown),
            )
            self.place(
                relx=0.5, rely=1.0, anchor="s", y=-self.BASE_OFFSET_PX + round(self.SLIDE_DISTANCE_PX * (1 - shown))
            )

        self._animation = self._theme.motion.animate(self, ANIMATION_NOTIFICATIONS, base_ms, render, on_done)