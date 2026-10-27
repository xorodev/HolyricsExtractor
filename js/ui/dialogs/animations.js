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
import { SPEED_FAST, SPEED_NORMAL, SPEED_SLOW, SettingKey } from '../../core/settings.js';
import { applyAppearance } from '../appearance.js';
import { createCheckbox, createGroup, createRadioGroup } from '../controls.js';
import { openDialog } from '../dialog.js';
import { h } from '../dom.js';

const SPEED_OPTIONS = Object.freeze([
  [SPEED_SLOW, 'Lenta'],
  [SPEED_NORMAL, 'Normal'],
  [SPEED_FAST, 'Rápida'],
]);

const EFFECT_OPTIONS = Object.freeze([
  [SettingKey.ANIMATION_HOVER, 'Transición de color al pasar el cursor sobre los botones'],
  [SettingKey.ANIMATION_NOTIFICATIONS, 'Aparición y salida suave de las notificaciones'],
  [SettingKey.ANIMATION_WINDOWS, 'Aparición gradual de las ventanas emergentes'],
  [SettingKey.ANIMATION_RESULTS, 'Aparición gradual de los versos generados'],
]);

export function showAnimationsDialog(settings) {
  const save = (key, value) => {
    settings.set(key, value);
    applyAppearance(settings);
  };

  const enabled = createCheckbox({
    label: 'Activar animaciones',
    checked: settings.get(SettingKey.ANIMATIONS_ENABLED),
    onChange: (checked) => {
      save(SettingKey.ANIMATIONS_ENABLED, checked);
      refreshDependentControls();
    },
  });
  const speed = createRadioGroup({
    legend: 'Velocidad',
    name: 'animation-speed',
    options: SPEED_OPTIONS,
    value: settings.get(SettingKey.ANIMATION_SPEED),
    onChange: (value) => save(SettingKey.ANIMATION_SPEED, value),
  });
  const effects = EFFECT_OPTIONS.map(([key, label]) =>
    createCheckbox({ label, checked: settings.get(key), onChange: (checked) => save(key, checked) }),
  );

  const dependentInputs = [...speed.inputs, ...effects.map((effect) => effect.input)];
  function refreshDependentControls() {
    for (const input of dependentInputs) input.disabled = !enabled.input.checked;
  }
  refreshDependentControls();

  const body = h('div', { className: 'dialog-stack' }, [
    h('p', { className: 'dialog__hint' }, [
      'Los cambios se aplican de forma inmediata. Desactivar las animaciones hace que la interfaz responda al instante.',
    ]),
    enabled.root,
    speed.root,
    createGroup(
      'Efectos',
      effects.map((effect) => effect.root),
    ),
  ]);
  return openDialog({
    title: '✦ Animaciones de la interfaz',
    body,
    buttons: [{ label: 'Cerrar', variant: 'neutral' }],
  });
}