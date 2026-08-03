# HolyricsExtractor — Guía de Uso

Esta guía detalla el funcionamiento interno de **HolyricsExtractor**, cubriendo desde el flujo básico de extracción hasta los mecanismos de actualización automática.

---

## 📑 Tabla de Contenido
- [HolyricsExtractor — Guía de Uso](#holyricsextractor--guía-de-uso)
  - [📑 Tabla de Contenido](#-tabla-de-contenido)
  - [⚙️ Requisitos del Sistema](#️-requisitos-del-sistema)
  - [🚀 Instrucciones de Uso](#-instrucciones-de-uso)
    - [1. Extracción mediante Enlace de YouTube](#1-extracción-mediante-enlace-de-youtube)
    - [2. Búsqueda por Título y Artista](#2-búsqueda-por-título-y-artista)
  - [🔄 Sistema de Actualizaciones](#-sistema-de-actualizaciones)
    - [Actualización del Software (HolyricsExtract)](#actualización-del-software-holyricsextract)
    - [Actualización del Componente yt-dlp](#actualización-del-componente-yt-dlp)
  - [💡 Tips y Recomendaciones](#-tips-y-recomendaciones)

---

## ⚙️ Requisitos del Sistema

- **Sistema Operativo:** Windows 10 / Windows 11 (64-bit).
- **Conexión a Internet:** Requerida para la consulta de la API de letras (`LRCGET`), YouTube y GitHub Releases.
- **Espacio en Disco:** ~30 MB para el ejecutable y archivos temporales de registro.

---

## 🚀 Instrucciones de Uso

### 1. Extracción mediante Enlace de YouTube
1. Copie el enlace del video de YouTube de la canción deseada.
2. Péguelo en el campo **Enlace de YouTube / Título de la Canción**.
3. *(Opcional)* Escriba el nombre del artista en el segundo campo para mejorar la precisión.
4. Haga clic en **🔍 ¡Buscar y formatear letra!** o presione `Enter`.

### 2. Búsqueda por Título y Artista
1. Escriba directamente el nombre de la canción en el campo principal.
2. Ingrese el artista o banda en el campo inferior.
3. El programa buscará la mejor coincidencia en la base de datos pública y mostrará la vista previa dividida por **PRESENTACIONES**.

> [!TIP]
> Puede hacer clic en **📋 Copiar resultado** para pegar directamente el texto formateado en el editor de canciones de Holyrics.
> [!TIP]
> Puede hacer clic en **💾 Exportar resultado** para exportar directamente el texto formateado en formato de texto (.txt) y pegar el resultado de la exportanción en el editor de canciones de Holyrics.

---

## 🔄 Sistema de Actualizaciones

### Actualización del Software (HolyricsExtract)
- En el menú superior, seleccione **Opciones > ⚙️ Ajustes > Buscar actualizaciones de la aplicación**.
- El sistema consultará la API de GitHub Releases. Si existe una versión más reciente, descargará el ejecutable en segundo plano y ejecutará un proceso de reemplazo transparente.

### Actualización del Componente yt-dlp
- En el menú superior, seleccione **Opciones > 🔄 Actualizar yt-dlp** o hágalo desde la ventana de **⚙️ Ajustes**.
- Esto garantiza que el motor de extracción de metadatos de YouTube nunca quede obsoleto ante cambios de algoritmo.

> [!NOTE]
> Los archivos de registro de operaciones se guardan localmente en:  
> `Documentos\HolyricsExtractor\logs.txt`

---

## 💡 Tips y Recomendaciones

> [!IMPORTANT]
> Si la extracción por enlace de YouTube no devuelve resultados, intente limpiar manualmente el campo escribiendo únicamente el título y el artista de la canción.

---

Copyright © 2026 @xorodev (CipherCoreDev). Licensed under the GNU General Public License v3.0