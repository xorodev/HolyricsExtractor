# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## 🛠 Cambios en esta versión — v1.0.1-stable (2026-08-03)

Esta actualización se enfoca en mejorar la organización de las diapositivas generadas y en dar mayor claridad sobre el estado de las actualizaciones de la aplicación.

### 🚀 Novedades
- **Presentaciones de 4 a 5 versos por diapositiva:** Las estrofas largas ahora se dividen automáticamente en bloques balanceados de 4 o 5 versos, en vez de generarse como un único bloque extenso.
- **Detección de coros y estrofas repetidas:** Cuando dos presentaciones resultan idénticas, la segunda ya no se duplica en el resultado. La primera aparición se marca con doble pleca (`// ... //`) al inicio del primer verso y al final del último, indicando que dicha sección se repite.

### ✨ Mejoras
- **Confirmación de actualización exitosa:** Tras completar una actualización automática y reiniciarse, la aplicación ahora muestra un mensaje confirmando que la última versión estable se instaló correctamente.

---

## 🛠 Cambios en esta versión — v1.0.0-stable (2026-08-02)

Esta versión marca el lanzamiento oficial estable de **HolyricsExtractor**, ofreciendo una solución completa para la extracción de letras e integración con el ecosistema Holyrics.

### 🚀 Novedades
- **Interfaz gráfica moderna:** Rediseñada con Tkinter y soporte DPI consciente para Windows.
- **Resolución dinámica de metadatos:** Integración con motor binario `yt-dlp` y fallback de librería.
- **Auto-actualizador integrado:** Sistema de auto-reemplazo mediante scripts en lote (`.bat`) conectado a GitHub Releases.
- **Gestor de logs local:** Rotación automática de registros almacenados en la carpeta `Documentos`.
- **Exportación y formateo:** Limpieza automática de títulos y conversión de stanzas a diapositivas individuales.

---

Copyright © 2026 @xorodev (CipherCoreDev). Licensed under the GNU General Public License v3.0
