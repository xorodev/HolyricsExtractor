# Registro de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo. **HolyricsExtractor** cuenta con dos versiones, una **de escritorio (Windows)** y una **web**, por lo que cada entrada indica a cuál corresponde:

- 🖥️ **Escritorio:** aplicación para Windows.
- 🌐 **Web:** aplicación en línea que funciona desde el navegador.

---

## 🛠 Cambios en esta versión — v1.0.0-stable (2026-10-27)

Esta versión marca el lanzamiento oficial estable de **HolyricsExtractor en sus dos versiones**: la aplicación de **escritorio para Windows** y la **versión web**, ambas con extracción y formateo de letras para Holyrics y el mismo formato de salida.

### 🚀 Novedades

**Comunes a ambas versiones (🖥️ + 🌐)**
- **Búsqueda por enlace de YouTube o por título:** Acepta URLs de YouTube (`youtube.com`, `youtu.be`, `shorts`, `embed`, `live`) o el título de la canción con el artista opcional, consultando la API pública de LRCLIB y seleccionando la mejor coincidencia.
- **Formateo de diapositivas:** Las estrofas se dividen en bloques balanceados de 4 a 5 versos y las presentaciones idénticas se unifican, marcando la primera aparición con doble pleca (`// ... //`).
- **Previsualización por versos:** Resultado mostrado en bloques numerados.
- **Copiado y exportación:** Copia del resultado al portapapeles y exportación a archivo `.txt` con delimitador uniforme (`--------------`).
- **Historial de búsquedas recientes:** Guarda hasta las 10 últimas canciones, con opción de borrado total.
- **Cancelación de operaciones:** Permite detener una búsqueda en curso.
- **Atajos de teclado:** Disponibles en ambas versiones (consulte la [Guía de Uso](./docs/USAGE.md) para ver los atajos de cada una).
- **Ayuda y soporte:** Envío del reporte por WhatsApp, correo electrónico o copiado al portapapeles, con el último error detectado opcional.

**🖥️ Versión de escritorio**
- **Lectura de enlaces con `yt-dlp`:** Componente integrado que se puede actualizar desde **Opciones > Actualizar yt-dlp**.
- **Búsqueda automática de actualizaciones:** Avisos de nuevas versiones de la aplicación y de `yt-dlp`, configurables desde **Ajustes**.
- **Archivos protegidos (menú Avanzado):** Verificación de integridad de la configuración, el historial, los registros y el componente `yt-dlp`.
- **Almacenamiento local:** Datos guardados en la carpeta `Documentos/HolyricsExtractor`.

**🌐 Versión web**
- **Botón "Pegar enlace":** Pega el contenido del portapapeles en el campo de búsqueda con un solo clic.
- **Reintentos automáticos:** Reintentos ante fallos temporales de red.
- **Sin instalación:** Funciona directamente desde el navegador.
- **Descarga de la versión de escritorio:** Botón integrado que descarga el ejecutable de Windows desde GitHub Releases.

### ✨ Mejoras

**Comunes a ambas versiones (🖥️ + 🌐)**
- **Modo claro y oscuro:** Alternancia desde la interfaz con preferencia guardada.
- **Animaciones configurables:** Activación, velocidad y efectos individuales, pensadas para equipos de bajos recursos.

**🖥️ Versión de escritorio**
- **Compatibilidad con Windows 10 y Windows 11:** Incluye soporte para pantallas de alta densidad (DPI).

**🌐 Versión web**
- **Diseño responsive:** Interfaz adaptada desde 320 px hasta 4K y UltraWide, sin librerías externas.
- **Respeto del movimiento reducido:** Las animaciones se desactivan automáticamente si el sistema solicita reducir el movimiento.
- **Seguridad:** Política de seguridad de contenido (CSP) estricta, tipos de confianza (*Trusted Types*), validación y sanitización de entradas, límites de tamaño en respuestas y solicitudes sin credenciales.

---

Copyright © 2026 @xorodev (CipherCoreDev). Licensed under the GNU General Public License v3.0