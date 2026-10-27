<div align="center">

# HolyricsExtractor

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg?logo=gnu&style=flat)](https://www.gnu.org/licenses/gpl-3.0.txt)
[![Release](https://img.shields.io/badge/Version-v1.0.0--stable-blue?style=flat)](https://github.com/xorodev/HolyricsExtractor/releases)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Web-4361EE?logo=googlechrome&logoColor=white&style=flat)
![Python](https://img.shields.io/badge/Python-Desktop-3776AB?logo=python&logoColor=white&style=flat)
![JavaScript](https://img.shields.io/badge/JavaScript-Web%20ES2022-F7DF1E?logo=javascript&logoColor=white&style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

</div>

<div align="center">
  <img
    src="./assets/icon.svg"
    alt="HolyricsExtractor Logo"
    width="160"
    style="border: 2px solid #89b4fa; border-radius: 20px; padding: 15px; background: #1e1e2e;"
  >
</div>

<br>

> **HolyricsExtractor** es una herramienta diseñada para la **búsqueda, extracción y estructuración automática de letras de canciones** optimizadas para el software de proyección eclesiástica **Holyrics**. Está disponible en **dos versiones**. Una **aplicación de escritorio para Windows** y una **versión web** que funciona directamente desde el navegador.

Ambas versiones permiten transformar enlaces directos de **YouTube** o búsquedas por título y artista en **diapositivas/estrofas perfectamente separadas**, con el mismo formato de salida. Elija la que mejor se adapte a su equipo e instálela en Windows o úsela en línea sin instalar nada.

<div align="center">

Tecnologías utilizadas:

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-306998?logo=python&logoColor=white&style=flat)
![yt-dlp](https://img.shields.io/badge/yt--dlp-FF0000?style=flat&logo=youtube&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=white)
![LRCLIB](https://img.shields.io/badge/%F0%9F%8E%B5-LRCLIB-blueviolet?style=flat)
</div>

---

## 📑 Tabla de Contenidos
- [HolyricsExtractor](#holyricsextractor)
  - [🧩 Versiones Disponibles](#-versiones-disponibles)
  - [🚀 Inicio Rápido](#-inicio-rápido)
  - [✨ Características Principales](#-características-principales)
  - [🔒 Seguridad y Privacidad](#-seguridad-y-privacidad)
  - [💻 Ejecución Local](#-ejecución-local)
  - [📝 Licencia](#-licencia)
  - [🛠️ Soporte](#️-soporte)
  - [⚡ Contribuciones](#-contribuciones)
  - [🛡️ Verificación del Ejecutable](#️-verificación-del-ejecutable)

---

## 🧩 Versiones Disponibles

| | 🖥️ Escritorio (Windows) | 🌐 Web |
|---|---|---|
| **Instalación** | Descargar el `.exe` desde [Releases].(https://github.com/xorodev/HolyricsExtractor/releases) | Ninguna, se abre en el navegador. |
| **Plataforma** | Windows 10 y Windows 11 (64 bits). | Chrome, Edge, Firefox o Safari actualizados. |
| **Tecnología** | Python + Tkinter. | HTML, CSS y JavaScript (sin dependencias). |
| **Lectura de enlaces de YouTube** | `yt-dlp` integrado, actualizable desde la aplicación. | YouTube oEmbed. |
| **Actualizaciones** | Avisos automáticos de la aplicación y de `yt-dlp`. | Siempre la última versión publicada. |
| **Datos guardados en** | Carpeta `Documentos/HolyricsExtractor`. | Almacenamiento local del navegador. |
| **Ideal para** | Equipo fijo de proyección o uso frecuente. | Uso rápido desde cualquier dispositivo. |

> [!NOTE]
> El resultado generado (los versos, y coros marcados con `// ... //` y la exportación en formato `.txt`) es el mismo en ambas versiones.

---

## 🚀 Inicio Rápido

> [!NOTE]
> Para aprender a utilizar la herramienta, comprender la separación de estrofas y conocer los atajos de teclado de cada versión, consulte la [Guía de Uso](./docs/USAGE.md).

**🖥️ Versión de escritorio**

1. Descargue `HolyricsExtractor.exe` desde la sección de **[Releases](https://github.com/xorodev/HolyricsExtractor/releases)** y ejecútelo.
2. Pegue un enlace de YouTube o escriba el título de la canción.
3. Haga clic en **¡Buscar y Formatear Letra!** y copie o exporte el resultado.

**🌐 Versión web**

1. Abra la aplicación web en su navegador (Chrome, Edge, Firefox o Safari actualizados).
2. Pegue un enlace de YouTube o escriba el título de la canción.
3. Haga clic en **¡Buscar y Formatear Letra!** y copie o exporte el resultado.

---

## ✨ Características Principales

**Comunes a ambas versiones**

* 🎵 **Resolución inteligente de enlaces:** Acepta URLs directas de YouTube y limpia automáticamente títulos (removiendo etiquetas como `Official Music Video`, `4K`, etc.).
* 📊 **Formateo de diapositivas:** Estructura automáticamente el texto en bloques de 4 a 5 versos y marca los coros repetidos con `// ... //`.
* 📋 **Exportación rápida:** Permite copiar la estructura con un solo clic o exportarla a archivos de texto `.txt`.
* 🕘 **Historial de búsquedas:** Conserva las últimas 10 canciones procesadas.
* 🎨 **Modo claro y oscuro:** Con animaciones configurables para equipos de bajos recursos.
* ⌨️ **Atajos de teclado:** Para buscar, pegar, copiar y exportar sin usar el ratón.

**🖥️ Exclusivas de la versión de escritorio**

* 🔄 **Actualización de `yt-dlp` desde la aplicación:** Menú **Opciones > Actualizar yt-dlp**.
* 🔔 **Avisos de nuevas versiones:** Notificaciones automáticas de la aplicación y de `yt-dlp`, configurables en **Ajustes**.
* 🛡️ **Archivos protegidos:** Verificación de integridad de la configuración, el historial y el componente `yt-dlp` (menú **Avanzado**).
* 🪟 **Integración con Windows:** Compatible con Windows 10 y Windows 11, con soporte de pantallas de alta densidad (DPI).

**🌐 Exclusivas de la versión web**

* 📱 **Diseño responsive:** Se adapta desde pantallas de 320 px hasta monitores 4K y UltraWide.
* 🌍 **Sin instalación:** Funciona desde cualquier navegador moderno, en cualquier sistema operativo.
* 💻 **Descarga de la versión de escritorio:** Botón integrado para obtener el ejecutable de Windows.

---

## 🔒 Seguridad y Privacidad

**🖥️ Versión de escritorio**

* Los datos (ajustes, historial y registros) se guardan únicamente en su equipo, en la carpeta `Documentos/HolyricsExtractor`.
* Las conexiones externas se limitan a **LRCLIB** (letras), **YouTube** (título del video) y **GitHub** (búsqueda de actualizaciones), sin cookies ni credenciales.
* Las descargas de actualizaciones se aceptan solo desde dominios de confianza de GitHub y se validan mediante sumas de verificación (`SHA2-256SUMS`).

**🌐 Versión web**

* Todo el código se ejecuta en su navegador: no existe ningún servidor propio ni base de datos.
* Las únicas conexiones externas son a **LRCLIB** (letras) y a **YouTube oEmbed** (título del video), ambas restringidas mediante una política de seguridad de contenido (CSP).
* Las solicitudes se envían sin cookies ni credenciales y sin cabecera de referencia.
* El historial y los ajustes se guardan únicamente en el almacenamiento local de su navegador.

---

## 💻 Ejecución Local

**🌐 Versión web**

Los módulos de JavaScript requieren servirse mediante HTTP. Desde la carpeta de la aplicación:

```bash
python -m http.server 8000
```

Después abra `http://localhost:8000` en su navegador.

**🖥️ Versión de escritorio (desde el código fuente)**

Requiere Python 3.10 o superior y las dependencias `requests` y `yt-dlp`. Desde la carpeta de la aplicación:

```bash
pip install requests yt-dlp
python src/app.py
```

---

## 📝 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0 (GPLv3)**.  
Consulte los [términos completos](https://www.gnu.org/licenses/gpl-3.0.txt).

---

## 🛠️ Soporte

Este proyecto se proporciona **tal cual** y se **mantendrá actualizado con el tiempo**, tanto en su versión de escritorio como en su versión web.  
Si encuentra errores, fallos en la extracción de letras o sugerencias para nuevas funciones, puede **abrir un [issue](https://github.com/xorodev/HolyricsExtractor/issues)** en GitHub indicando **qué versión utiliza** (escritorio o web).

---

## ⚡ Contribuciones

**Las contribuciones son bienvenidas.** Puede colaborar siguiendo estos pasos:

1. Hacer un fork del repositorio.
2. Crear una rama para su mejora (`git checkout -b my-branch`).
3. Realizar los cambios y hacer commit.
4. Enviar un pull request.

---

## 🛡️ Verificación del Ejecutable

Este proyecto es **Software Libre** y defiende la **transparencia del código**. La **aplicación de escritorio para Windows de 64 bits** se descarga desde la sección de **[Releases](https://github.com/xorodev/HolyricsExtractor/releases)** o con el botón **Descargar aquí** de la versión web.

> [!IMPORTANT]
> 🛡️ Se recomienda verificar siempre las firmas y el hash del ejecutable publicado en la sección de Releases ante la plataforma VirusTotal.

---

Copyright © 2026 @xorodev (CipherCoreDev). Licensed under the GNU General Public License v3.0