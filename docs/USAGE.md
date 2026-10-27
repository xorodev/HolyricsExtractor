# HolyricsExtractor — Guía de Uso

Esta guía detalla el funcionamiento de **HolyricsExtractor** en sus dos versiones, la **aplicación de escritorio para Windows** y la **versión web**, cubriendo desde el flujo básico de extracción hasta los atajos de teclado y las opciones de la interfaz. Los pasos de extracción son iguales en ambas; las diferencias se indican con 🖥️ (escritorio) y 🌐 (web).

---

## 📑 Tabla de Contenido
- [HolyricsExtractor — Guía de Uso](#holyricsextractor--guía-de-uso)
  - [📑 Tabla de Contenido](#-tabla-de-contenido)
  - [⚙️ Requisitos](#️-requisitos)
  - [🚀 Instrucciones de Uso](#-instrucciones-de-uso)
    - [1. Extracción mediante Enlace de YouTube](#1-extracción-mediante-enlace-de-youtube)
    - [2. Búsqueda por Título y Artista](#2-búsqueda-por-título-y-artista)
  - [🕘 Historial y Opciones](#-historial-y-opciones)
  - [⌨️ Atajos de Teclado](#️-atajos-de-teclado)
  - [🧩 Versión de Escritorio y Versión Web](#-versión-de-escritorio-y-versión-web)
  - [💡 Tips y Recomendaciones](#-tips-y-recomendaciones)

---

## ⚙️ Requisitos

**🖥️ Versión de escritorio**
- **Sistema operativo:** Windows 10 y Windows 11 (64 bits).
- **Conexión a Internet:** Requerida para consultar la API de letras (`LRCLIB`) y YouTube.
- **Instalación:** Descargue `HolyricsExtractor.exe` desde [Releases](https://github.com/xorodev/HolyricsExtractor/releases) y ejecútelo.

**🌐 Versión web**
- **Navegador:** Chrome o Edge 84+, Firefox 90+ o Safari 15+ (versiones de 2021 o posteriores).
- **Conexión a Internet:** Requerida para consultar la API de letras (`LRCLIB`) y YouTube.
- **Instalación:** No requiere ninguna.

---

## 🚀 Instrucciones de Uso

### 1. Extracción mediante Enlace de YouTube
1. Copie el enlace del video de YouTube de la canción deseada.
2. Péguelo en el campo **Enlace de YouTube / Título de la Canción** (En la versión web también puede usar el botón **Pegar enlace**).
3. *(Opcional)* Escriba el nombre del artista en el segundo campo para mejorar la precisión.
4. Haga clic en **¡Buscar y Formatear Letra!** o presione `Enter`.

### 2. Búsqueda por Título y Artista
1. Escriba directamente el nombre de la canción en el campo principal.
2. Ingrese el artista o banda en el campo inferior.
3. La aplicación buscará la mejor coincidencia en la base de datos pública y mostrará la vista previa dividida por **VERSOS**.

> [!TIP]
> Puede hacer clic en **¡Copiar resultado!** para pegar directamente el texto formateado en el editor de canciones de Holyrics.
> [!TIP]
> Puede hacer clic en **¡Exportar resultado!** para descargar el texto formateado en formato de texto (`.txt`) y pegar su contenido en el editor de canciones de Holyrics.

> [!NOTE]
> Los coros o estrofas repetidas aparecen una sola vez, marcadas con `//` al inicio del primer verso y al final del último.

---

## 🕘 Historial y Opciones

**En ambas versiones**
- **Historial:** El menú superior conserva las últimas 10 canciones procesadas; al seleccionarlas se cargan al instante sin consultar de nuevo. Incluye la opción **Borrar historial completo**.
- **Modo claro / oscuro:** Se alterna desde el botón de la barra superior y se recuerda en su próxima visita.
- **Animaciones:** Permite activar o desactivar las animaciones, elegir su velocidad y habilitar efectos individuales (menú **Opciones > Animaciones**).
- **Ayuda y soporte:** Disponible con la tecla `F1` o desde el menú **Opciones**. Permite enviar su mensaje por WhatsApp, correo electrónico o copiarlo al portapapeles.
- **Cancelar:** Mientras una búsqueda está en curso, puede detenerla de inmediato.

**🖥️ Solo en la versión de escritorio** (menú **Opciones**)
- **Ajustes:** Permite activar o desactivar las notificaciones automáticas de nuevas versiones de la aplicación y de `yt-dlp`.
- **Actualizar yt-dlp:** Descarga la última versión del componente que lee los enlaces de YouTube. Si un enlace deja de funcionar, actualizarlo suele solucionarlo.
- **Avanzado:** Muestra el estado de los archivos protegidos (configuración, historial, registros y `yt-dlp`) y permite desbloquearlos, restablecerlos o aceptar cambios hechos fuera de la aplicación.
- **Salir del programa:** Cierra la aplicación.

> [!NOTE]
> 🖥️ El historial, los ajustes y los registros se guardan en la carpeta `Documentos/HolyricsExtractor` de su equipo.

> [!NOTE]
> 🌐 El historial y los ajustes se guardan únicamente en el navegador que está utilizando. Si borra los datos del sitio, se eliminarán.

---

## ⌨️ Atajos de Teclado

**🖥️ Versión de escritorio**

| Atajo | Acción |
|---|---|
| `F1` | Abrir la ventana de ayuda y soporte. |
| `Esc` | Salir de cualquier campo o cerrar la ventana emergente. |
| `Enter` | Buscar y formatear la letra desde cualquiera de los dos campos de texto. |
| `Ctrl + A` | Seleccionar todo el texto del campo activo. |
| `Ctrl + C` | Copiar el texto seleccionado del campo activo. |
| `Ctrl + X` | Cortar el texto seleccionado del campo activo. |
| `Ctrl + V` | Pegar el contenido del portapapeles en el campo activo. |
| `Ctrl + S` | Exportar el resultado a un archivo de texto (`.txt`). |
| `Ctrl + Shift + K` | Mostrar la lista de atajos de teclado. |
| `Ctrl + Shift + C` | Copiar el resultado generado al portapapeles. |
| `Ctrl + Shift + V` | Pegar el contenido del portapapeles y buscar la letra de inmediato. |

**🌐 Versión web**

En macOS la tecla `Ctrl` se reemplaza por la tecla `Cmd`.

| Atajo | Acción |
|---|---|
| `F1` | Abrir la ventana de ayuda y soporte. |
| `Esc` | Salir del campo activo o cerrar el menú o la ventana emergente. |
| `Enter` | Buscar y formatear la letra desde cualquiera de los dos campos. |
| `Ctrl + S` | Exportar el resultado a un archivo de texto (`.txt`). |
| `Ctrl + .` | Mostrar la lista de atajos de teclado. |
| `Ctrl + Enter` | Pegar el contenido del portapapeles y buscar la letra de inmediato. |
| `Ctrl + Shift + Enter` | Copiar el resultado generado al portapapeles. |

> [!NOTE]
> Los atajos de ambas versiones **no son idénticos**. Consulte la tabla de la versión que esté utilizando.

---

## 🧩 Versión de Escritorio y Versión Web

HolyricsExtractor ofrece las dos versiones con el mismo resultado final; elija según su necesidad:

- **🖥️ Escritorio:** recomendada para el equipo de proyección o para un uso frecuente. Incluye `yt-dlp` integrado, avisos de actualización y gestión de archivos protegidos. Se descarga como `HolyricsExtractor.exe` desde [Releases](https://github.com/xorodev/HolyricsExtractor/releases).
- **🌐 Web:** ideal para un uso rápido desde cualquier dispositivo, sin instalar nada. El cuadro **Versión de escritorio** de la pantalla principal incluye el botón **Descargar aquí**, que descarga el ejecutable de la última versión publicada en GitHub Releases.

---

## 💡 Tips y Recomendaciones

> [!IMPORTANT]
> Si la búsqueda por enlace de YouTube no devuelve resultados, intente escribir únicamente el título y el artista de la canción. En la versión de escritorio, también puede probar **Opciones > Actualizar yt-dlp**.

> [!NOTE]
> 🌐 Si el navegador bloquea el acceso al portapapeles, permita el permiso cuando lo solicite o pegue el texto con el teclado.

---

Copyright © 2026 @xorodev (CipherCoreDev). Licensed under the GNU General Public License v3.0