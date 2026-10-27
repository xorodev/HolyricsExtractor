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
import { MAX_SUPPORT_MESSAGE_LENGTH, SUPPORT_EMAIL, SUPPORT_WHATSAPP_DISPLAY } from '../../config/constants.js';
import { codePointLength, sanitizeMultiline } from '../../core/text.js';
import { buildMailtoUrl, buildReportText, buildWhatsAppUrl } from '../../services/support.js';
import { copyText } from '../clipboard.js';
import { createCheckbox } from '../controls.js';
import { openDialog } from '../dialog.js';
import { h, openLink } from '../dom.js';

const SANITIZE_LIMIT = MAX_SUPPORT_MESSAGE_LENGTH * 4;

export function showSupportDialog(lastError) {
  const textarea = h('textarea', {
    className: 'field__input field__input--area',
    rows: '6',
    'aria-label': 'Descripción del problema',
    spellcheck: 'true',
  });
  const counter = h('p', { className: 'support__counter' });
  const feedback = h('p', { className: 'support__feedback', role: 'status' });
  const includeError =
    lastError === null
      ? null
      : createCheckbox({
          label: `Incluir el último error detectado (código: ${lastError.code})`,
          checked: true,
        });
  const includeSystem = createCheckbox({
    label: 'Incluir la versión de la aplicación y del navegador',
    checked: true,
  });

  const sanitizedText = () => sanitizeMultiline(textarea.value, SANITIZE_LIMIT);

  const updateCounter = () => {
    const length = codePointLength(sanitizedText());
    counter.textContent = `${length}/${MAX_SUPPORT_MESSAGE_LENGTH}`;
    counter.dataset.state = length > MAX_SUPPORT_MESSAGE_LENGTH ? 'over' : 'ok';
  };

  const setFeedback = (text, state) => {
    feedback.textContent = text;
    feedback.dataset.state = state;
  };

  const selectedError = () => (lastError !== null && includeError.input.checked ? lastError : null);

  const buildReport = () => {
    const text = sanitizedText();
    const error = selectedError();
    if (codePointLength(text) > MAX_SUPPORT_MESSAGE_LENGTH) {
      setFeedback(`El mensaje supera el máximo de ${MAX_SUPPORT_MESSAGE_LENGTH} caracteres.`, 'danger');
      return null;
    }
    if (!text && error === null) {
      setFeedback('Describa brevemente el problema antes de enviar el mensaje.', 'warning');
      textarea.focus();
      return null;
    }
    return buildReportText(text, error, includeSystem.input.checked);
  };

  const send = (buildUrl, successText) => {
    const report = buildReport();
    if (report === null) return;
    openLink(buildUrl(report));
    setFeedback(successText, 'success');
  };

  const sendWhatsApp = () => send(buildWhatsAppUrl, 'Abriendo WhatsApp con su mensaje listo para enviar...');

  const sendEmail = () =>
    send((report) => buildMailtoUrl(report, selectedError()), 'Abriendo su aplicación de correo electrónico...');

  const copyReport = async () => {
    const report = buildReport();
    if (report === null) return;
    const copied = await copyText(report);
    setFeedback(
      copied ? '¡El reporte fue copiado al portapapeles!' : 'No fue posible acceder al portapapeles del navegador.',
      copied ? 'success' : 'danger',
    );
  };

  textarea.addEventListener('input', updateCounter);
  updateCounter();

  const body = h('div', { className: 'dialog-stack' }, [
    h('p', { className: 'dialog__hint' }, [
      'Describa el problema o su duda. El mensaje se enviará directamente al desarrollador por el canal que usted elija.',
    ]),
    textarea,
    counter,
    ...(includeError === null ? [] : [includeError.root]),
    includeSystem.root,
    h('div', { className: 'support__actions' }, [
      h('button', { className: 'btn btn--success', type: 'button', onclick: sendWhatsApp }, ['WhatsApp']),
      h('button', { className: 'btn btn--primary', type: 'button', onclick: sendEmail }, ['Correo electrónico']),
      h(
        'button',
        { className: 'btn btn--neutral support__copy', type: 'button', onclick: copyReport },
        ['¡Copiar reporte al portapapeles!'],
      ),
    ]),
    feedback,
    h('p', { className: 'support__contact' }, [`WhatsApp: ${SUPPORT_WHATSAPP_DISPLAY}  ·  Correo: ${SUPPORT_EMAIL}`]),
  ]);

  return openDialog({
    title: '¿Necesita ayuda?',
    body,
    buttons: [{ label: 'Cerrar', variant: 'neutral' }],
    initialFocus: textarea,
  });
}