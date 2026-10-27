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
import {
  CLIPBOARD_READ_LIMIT,
  ELAPSED_VISIBLE_AFTER_SECONDS,
  HISTORY_LABEL_LENGTH,
  MAX_QUERY_LENGTH,
  TICK_INTERVAL_MS,
} from '../config/constants.js';
import { AppError, OperationCancelled, describeError } from '../core/errors.js';
import { formatFileStamp } from '../core/datetime.js';
import { OperationRunner } from '../core/operation.js';
import { SettingKey, THEME_DARK, THEME_LIGHT } from '../core/settings.js';
import { ellipsize, sanitizeSingleLine } from '../core/text.js';
import { LyricsResult } from '../services/models.js';
import { findLyrics } from '../services/lyricsService.js';
import { applyAppearance } from './appearance.js';
import { copyText, readText } from './clipboard.js';
import { showAboutDialog } from './dialogs/about.js';
import { showAnimationsDialog } from './dialogs/animations.js';
import { confirmAction, showError } from './dialogs/message.js';
import { showShortcutsDialog } from './dialogs/shortcuts.js';
import { showSupportDialog } from './dialogs/support.js';
import { requireElement } from './dom.js';
import { downloadTextFile } from './download.js';
import { DropdownMenu } from './menu.js';
import { Preview } from './preview.js';
import { bindShortcuts } from './shortcuts.js';
import { Toast } from './toast.js';

const STATUS_PREFIX = 'Estado de operación: ';
const IDLE_STATUS = 'En espera de una entrada.';
const SEARCH_BUTTON_TEXT = '¡Buscar y Formatear Letra!';
const SEARCH_BUTTON_BUSY_TEXT = 'Procesando solicitud, por favor espere...';
const BUSY_MESSAGE = '¡Ya hay una operación en curso! Espere a que finalice o cancélela...';
const SEARCH_STATUS = 'Buscando y procesando la letra...';

const slidesText = (total) => (total === 1 ? '1 verso' : `${total} versos`);

export class App {
  #settings;
  #history;
  #runner = new OperationRunner();
  #preview;
  #toast;
  #historyMenu;
  #optionsMenu;
  #elements;
  #current = null;
  #lastError = null;
  #busyStartedAt = 0;
  #busyMessage = '';
  #tickTimer = null;
  #handlingUnexpected = false;
  #shortcuts;

  constructor(settings, history) {
    this.#settings = settings;
    this.#history = history;
    this.#elements = {
      form: requireElement('search-form'),
      query: requireElement('query-input'),
      artist: requireElement('artist-input'),
      searchButton: requireElement('search-button'),
      pasteButton: requireElement('paste-button'),
      busyPanel: requireElement('busy-panel'),
      cancelButton: requireElement('cancel-button'),
      status: requireElement('status'),
      copyButton: requireElement('copy-button'),
      exportButton: requireElement('export-button'),
      helpButton: requireElement('help-button'),
      themeButton: requireElement('theme-button'),
      aboutButton: requireElement('about-button'),
    };
    this.#preview = new Preview(requireElement('preview'));
    this.#toast = new Toast(requireElement('toast-region'));
    this.#historyMenu = new DropdownMenu(requireElement('history-menu'));
    this.#optionsMenu = new DropdownMenu(requireElement('options-menu'));
    this.#shortcuts = Object.freeze([
      { keys: ['F1'], description: 'Abrir la ventana de ayuda y soporte.', handler: () => this.#openSupport() },
      { keys: ['Escape'], description: 'Salir del campo activo.', handler: () => this.#releaseFocus() },
      { keys: ['Enter'], description: 'Buscar y formatear la letra desde cualquiera de los dos campos de texto.' },
      { keys: ['Mod', 'S'], description: 'Exportar el resultado a un archivo de texto (.txt).', handler: () => this.#exportResult() },
      {
        keys: ['Mod', '.'],
        description: 'Mostrar esta lista de atajos de teclado.',
        handler: () => this.#openShortcuts(),
      },
      {
        keys: ['Mod', 'Enter'],
        description: 'Pegar el contenido del portapapeles y buscar la letra de inmediato.',
        handler: () => this.#pasteAndSearch(),
      },
      {
        keys: ['Mod', 'Shift', 'Enter'],
        description: 'Copiar el resultado generado al portapapeles.',
        handler: () => this.#copyResult(),
      },
    ]);
  }

  start() {
    const { form, pasteButton, cancelButton, copyButton, exportButton, helpButton, themeButton, aboutButton } =
      this.#elements;
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      this.#startSearch();
    });
    pasteButton.addEventListener('click', () => this.#pasteFromClipboard());
    cancelButton.addEventListener('click', () => this.#runner.cancel());
    copyButton.addEventListener('click', () => this.#copyResult());
    exportButton.addEventListener('click', () => this.#exportResult());
    helpButton.addEventListener('click', () => this.#openSupport());
    themeButton.addEventListener('click', () => this.#toggleTheme());
    aboutButton.addEventListener('click', () => showAboutDialog());

    this.#optionsMenu.setItems([
      { label: '✦ | Animaciones', onSelect: () => showAnimationsDialog(this.#settings) },
      { label: '⌨ | Atajos de teclado', onSelect: () => this.#openShortcuts() },
      { label: '? | Ayuda y Soporte', onSelect: () => this.#openSupport() },
    ]);
    bindShortcuts(this.#shortcuts);
    this.#refreshHistoryMenu();
    this.#renderThemeButton();
    this.#preview.showPlaceholder();
    this.#setStatus(IDLE_STATUS, 'idle');
  }

  handleUnexpected(error) {
    if (this.#handlingUnexpected) return;
    this.#handlingUnexpected = true;
    try {
      this.#runner.cancel();
      this.#reportError(error);
    } finally {
      this.#handlingUnexpected = false;
    }
  }

  #setStatus(text, kind) {
    this.#elements.status.textContent = `${STATUS_PREFIX}${text}`;
    this.#elements.status.dataset.kind = kind;
  }

  #notify(message, kind = 'info') {
    this.#toast.show(message, kind);
  }

  #warn(statusText, toastText) {
    this.#setStatus(statusText, 'warning');
    this.#notify(toastText, 'warning');
  }

  #releaseFocus() {
    const active = document.activeElement;
    if (active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement) active.blur();
  }

  #toggleTheme() {
    const next = this.#settings.get(SettingKey.THEME) === THEME_DARK ? THEME_LIGHT : THEME_DARK;
    this.#settings.set(SettingKey.THEME, next);
    applyAppearance(this.#settings);
    this.#renderThemeButton();
    this.#notify(next === THEME_DARK ? '¡Modo oscuro activado!' : '¡Modo claro activado!');
  }

  #renderThemeButton() {
    this.#elements.themeButton.textContent =
      this.#settings.get(SettingKey.THEME) === THEME_DARK ? '☀ Modo claro' : '☾ Modo oscuro';
  }

  #enterBusy(message) {
    const { searchButton, pasteButton, busyPanel, form } = this.#elements;
    this.#busyStartedAt = performance.now();
    this.#busyMessage = message;
    searchButton.disabled = true;
    searchButton.textContent = SEARCH_BUTTON_BUSY_TEXT;
    pasteButton.disabled = true;
    busyPanel.hidden = false;
    form.setAttribute('aria-busy', 'true');
    this.#renderBusyStatus();
    this.#tickTimer = setInterval(() => this.#renderBusyStatus(), TICK_INTERVAL_MS);
  }

  #leaveBusy() {
    const { searchButton, pasteButton, busyPanel, form } = this.#elements;
    clearInterval(this.#tickTimer);
    this.#tickTimer = null;
    busyPanel.hidden = true;
    searchButton.disabled = false;
    searchButton.textContent = SEARCH_BUTTON_TEXT;
    pasteButton.disabled = false;
    form.removeAttribute('aria-busy');
  }

  #renderBusyStatus() {
    const elapsed = Math.floor((performance.now() - this.#busyStartedAt) / 1000);
    const suffix = elapsed >= ELAPSED_VISIBLE_AFTER_SECONDS ? ` (${elapsed} s)` : '';
    this.#setStatus(`${this.#busyMessage}${suffix}`, 'busy');
  }

  #reportProgress = (message) => {
    this.#busyMessage = message;
    this.#renderBusyStatus();
  };

  async #startSearch() {
    if (this.#runner.isBusy) {
      this.#notify(BUSY_MESSAGE, 'warning');
      return;
    }
    const { query, artist } = this.#elements;
    const queryText = query.value.trim();
    const artistText = artist.value.trim();
    if (!queryText) {
      this.#warn(
        'Falta ingresar un enlace de YouTube o el título de una canción.',
        '¡Ingrese un enlace de YouTube válido o el título de una canción!',
      );
      query.focus();
      return;
    }

    this.#enterBusy(SEARCH_STATUS);
    let result;
    try {
      result = await this.#runner.run((signal) => findLyrics(queryText, artistText, this.#reportProgress, signal));
    } catch (error) {
      if (error instanceof OperationCancelled) {
        this.#setStatus('Operación cancelada por el usuario.', 'idle');
        this.#notify('¡Operación cancelada!');
      } else {
        this.#reportError(error);
      }
      return;
    } finally {
      this.#leaveBusy();
    }
    this.#showResult(result);
  }

  #showResult(result) {
    this.#current = result;
    this.#preview.render(result);
    this.#history.add(result.title, result.artist, result.formattedText);
    this.#refreshHistoryMenu();
    const summary = `${slidesText(result.totalSlides)} generados correctamente.`;
    this.#setStatus(summary, 'success');
    this.#notify(`¡Listo! ${summary}`, 'success');
  }

  #reportError(error) {
    const report = describeError(error);
    const appError = error instanceof AppError ? error : null;
    const severity = appError?.severity ?? 'error';
    const reportable = appError?.reportable ?? true;

    if (severity === 'error') console.error(`[${report.code}] ${report.detail || report.message}`, error);

    if (reportable) this.#lastError = report;
    this.#setStatus(`${report.title} (código: ${report.code}).`, severity === 'warning' ? 'warning' : 'error');
    showError(report, severity, reportable).then((choice) => {
      if (choice === 'report') this.#openSupport();
    });
  }

  async #pasteFromClipboard() {
    if (this.#runner.isBusy) {
      this.#notify(BUSY_MESSAGE, 'warning');
      return false;
    }
    const raw = await readText();
    if (raw === null) {
      this.#warn(
        'No fue posible acceder al portapapeles del navegador.',
        '¡Permita el acceso al portapapeles o pegue el texto con el teclado!',
      );
      return false;
    }
    const content = sanitizeSingleLine(raw.slice(0, CLIPBOARD_READ_LIMIT), MAX_QUERY_LENGTH);
    if (!content) {
      this.#warn(
        'El portapapeles no contiene texto para pegar.',
        '¡No se encontró ningún texto válido en el portapapeles!',
      );
      return false;
    }
    this.#elements.query.value = content;
    this.#setStatus('Enlace pegado desde el portapapeles correctamente.', 'success');
    return true;
  }

  async #pasteAndSearch() {
    if (await this.#pasteFromClipboard()) await this.#startSearch();
  }

  async #copyResult() {
    if (this.#current === null) {
      this.#warn('Aún no hay ningún texto procesado para copiar.', '¡Aún no hay ningún texto procesado para copiar!');
      return;
    }
    if (!(await copyText(this.#current.formattedText))) {
      this.#warn('No fue posible acceder al portapapeles del navegador.', '¡No fue posible copiar el resultado!');
      return;
    }
    this.#setStatus('Resultado copiado al portapapeles.', 'success');
    this.#notify('¡Resultado copiado al portapapeles!', 'success');
  }

  #exportResult() {
    if (this.#current === null) {
      this.#warn(
        'Aún no hay ningún texto procesado para exportar.',
        '¡Aún no hay ningún texto procesado para exportar!',
      );
      return;
    }
    downloadTextFile(`Lyrics_${formatFileStamp(new Date())}.txt`, this.#current.exportText);
    this.#setStatus('Archivo exportado correctamente.', 'success');
    this.#notify('¡Archivo exportado correctamente!', 'success');
  }

  #refreshHistoryMenu() {
    const entries = this.#history.entries;
    if (entries.length === 0) {
      this.#historyMenu.setItems([{ label: '¡Sin búsquedas recientes!', disabled: true }]);
      return;
    }
    this.#historyMenu.setItems([
      ...entries.map((entry) => ({
        label: ellipsize(entry.artist ? `♪ ${entry.title} - ${entry.artist}` : `♪ ${entry.title}`, HISTORY_LABEL_LENGTH),
        onSelect: () => this.#loadFromHistory(entry),
      })),
      { separator: true },
      { label: 'Borrar historial completo', onSelect: () => this.#clearHistory() },
    ]);
  }

  #loadFromHistory(entry) {
    if (this.#runner.isBusy) {
      this.#notify(BUSY_MESSAGE, 'warning');
      return;
    }
    this.#elements.query.value = entry.title;
    this.#elements.artist.value = entry.artist;
    this.#current = LyricsResult.fromFormattedText(entry.title, entry.artist, entry.text);
    this.#preview.render(this.#current);
    this.#setStatus(`${slidesText(this.#current.totalSlides)} cargados desde el historial.`, 'success');
  }

  async #clearHistory() {
    const confirmed = await confirmAction(
      'Borrar historial',
      '¿Está seguro de que desea borrar todo el historial de búsquedas recientes?',
    );
    if (!confirmed) return;
    this.#history.clear();
    this.#refreshHistoryMenu();
    this.#notify('¡Historial borrado!');
  }

  #openSupport() {
    return showSupportDialog(this.#lastError);
  }

  #openShortcuts() {
    return showShortcutsDialog(this.#shortcuts);
  }
}