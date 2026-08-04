# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## 🛠 Cambios en esta versión — v1.0.4-stable (2026-08-03)

Esta actualización introduce el sistema de historial persistente de búsquedas recientes, atajos de teclado globales para agilizar el flujo de trabajo y mejoras en la separación estructural de diapositivas al exportar archivos.

### 🚀 Novedades
- **Historial de búsquedas recientes:** Se integró un menú dinámico en la barra superior que guarda persistentemente hasta las últimas 10 canciones procesadas en `config.json`. Permite recargar instantáneamente el contenido procesado y previsualizado previamente sin necesidad de consultar la API nuevamente.
- **Limpieza del historial:** Opción dedicada dentro del menú para vaciar y restablecer todo el registro de búsquedas guardadas a voluntad del usuario.
- **Atajos de teclado rápidos (Shortcuts):**
  - `Ctrl + S`: Exportación rápida del resultado generado a archivo de texto (`.txt`).
  - `Ctrl + Shift + C`: Copiado instantáneo de las presentaciones estructuradas al portapapeles.
  - `Ctrl + Shift + V`: Pegado automático del contenido del portapapeles con inicio inmediato del proceso de búsqueda.

### ✨ Mejoras
- **Formato estandarizado de exportación:** Se implementó un delimitador uniforme (`--------------`) entre bloques al guardar los archivos `.txt`, facilitando la lectura externa e importación de diapositivas en Holyrics.

---

## 🛠 Cambios en esta versión — v1.0.3-stable (2026-08-03)

Esta actualización es un parche de estabilidad enfocado en perfeccionar el mecanismo de auto-actualización en ejecutables empaquetados con PyInstaller, garantizando una transición totalmente silenciosa y sin advertencias entre versiones.

### 🐛 Correcciones de errores
- **Aislamiento de entorno PyInstaller (`_MEIPASS2`):** Se incorporó la limpieza de la variable de entorno `_MEIPASS2` en el script ejecutable de actualización en lote (`.bat`), previniendo que la nueva versión herede la carpeta temporal del proceso anterior y asegurando la carga limpia de módulos dinámicos nativos.
- **Sincronización en la liberación de procesos:** Se reubicó la pausa de retardo dentro de la sección de reemplazo exitoso (`:replace_ok`), otorgando el tiempo necesario al sistema operativo para liberar los descriptores de archivos antes de iniciar el nuevo ejecutable.

---

## 🛠 Cambios en esta versión — v1.0.2-stable (2026-08-03)

Esta actualización introduce la función de pegado rápido desde el portapapeles con validación automática de enlaces de YouTube, mejorando la agilidad en la búsqueda de letras.

### 🚀 Novedades
- **Botón "Pegar enlace desde el portapapeles":** Se integró un botón de acción rápida que permite pegar enlaces directamente con un solo clic, agilizando el flujo de trabajo del usuario.
- **Validación inteligente del portapapeles:** El sistema verifica automáticamente que el contenido copiado corresponda a una URL válida de YouTube antes de insertarla, mostrando advertencias en pantalla si el portapapeles está vacío o incluye texto no compatible.

### ✨ Mejoras
- **Coherencia en la interfaz y auditoría:** Se aplicó el efecto visual interactivo (*hover*) al nuevo botón para alinearlo con el diseño de la aplicación, y se incorporó el registro de eventos del portapapeles en el sistema de logs.

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
