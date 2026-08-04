<div align="center">

# HolyricsExtractor

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat)](https://www.gnu.org/licenses/gpl-3.0.txt)
[![Release](https://img.shields.io/badge/Version-v1.0.4--stable-blue?style=flat)](https://github.com/xorodev/HolyricsExtractor/releases/tag/v1.0.0-stable)
![Platform](https://img.shields.io/badge/Platform-Windows-4361EE?logo=windows&logoColor=white&style=flat)
![Python](https://img.shields.io/badge/Python-3.14%2B-3776AB?logo=python&logoColor=white&style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)
[![VirusTotal Check](https://img.shields.io/badge/VirusTotal-0%2F62%20Clean-00a0dc?style=flat&logo=virustotal)](https://www.virustotal.com)

</div>

<div align="center">
  <img 
    src="./src/img/icon.ico"
    alt="HolyricsExtractor Logo"
    width="160"
    style="border: 2px solid #89b4fa; border-radius: 20px; padding: 15px; background: #1e1e2e;"
  >
</div>

<br>

> **HolyricsExtractor** es una **aplicación de escritorio** diseñada para la **búsqueda, extracción y estructuración automática de letras de canciones** optimizadas para el software de proyección eclesiástica **Holyrics**.

La herramienta permite transformar enlaces directos de **YouTube** o búsquedas por título y artista en **diapositivas/estrofas perfectamente separadas**, reduciendo el tiempo de preparación de eventos y garantizando la precisión del contenido sin depender de procesos manuales.

<div align="center">

Tecnologías y librerías utilizadas:

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FFD43B?style=flat&logo=python&logoColor=black)
![yt-dlp](https://img.shields.io/badge/Extractor-yt--dlp-red?style=flat)
![PyInstaller](https://img.shields.io/badge/Compiler-PyInstaller-2C3E50?style=flat)
</div>

---

## 📑 Tabla de Contenidos
- [HolyricsExtractor — Extrae y formatea letras para Holyrics!](#holyricsextractor--extrae-y-formatea-letras-para-holyrics)
  - [🚀 Inicio Rápido](#-inicio-rápido)
  - [✨ Características Principales](#-características-principales)
  - [📝 Licencia](#-licencia)
  - [🛠️ Soporte](#️-soporte)
  - [⚡ Contribuciones](#-contribuciones)
  - [🛠️ Descarga del Ejecutable y Código Fuente](#️-descarga-del-ejecutable-y-código-fuente)

---

## 🚀 Inicio Rápido

> [!NOTE]
> Para aprender a utilizar la herramienta, comprender la separación de estrofas y usar el sistema de actualización automática, consulte la [Guía de Uso](./docs/USAGE.md).

1. Vaya a la sección de **[Releases](https://github.com/xorodev/HolyricsExtractor/releases)** del repositorio.
2. Descargue la última versión compilada `HolyricsExtract.exe`.
3. Ejecute el archivo ejecutable directo en Windows (no requiere instalación previa).

---

## ✨ Características Principales

* 🎵 **Resolución inteligente de enlaces:** Acepta URLs directas de YouTube y limpia automáticamente títulos (removiendo etiquetas como `Official Music Video`, `4K`, etc.).
* 📊 **Formateo de diapositivas:** Estructura automáticamente el texto en bloques listos para importar a Holyrics.
* 🚀 **Sistema de Auto-Actualización:** Verifica y actualiza de forma transparente tanto el componente interno `yt-dlp` como la propia aplicación mediante la API de GitHub Releases.
* 📋 **Exportación rápida:** Permite copiar la estructura con un solo clic o exportarla a archivos de texto `.txt`.

---

## 📝 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0 (GPLv3)**.  
Consulte el archivo [LICENSE](./LICENSE) para conocer los términos completos.

---

## 🛠️ Soporte

Este proyecto se proporciona **tal cual** y se **mantendrá actualizado con el tiempo**.  
Si encuentra errores, fallos en la extracción de letras o sugerencias para nuevas funciones, puede **abrir un [issue](https://github.com/xorodev/HolyricsExtractor/issues)** en GitHub.

---

## ⚡ Contribuciones

**Las contribuciones son bienvenidas.** Puede colaborar siguiendo estos pasos:

1. Hacer un fork del repositorio.
2. Crear una rama para su mejora (`git checkout -b my-branch`).
3. Realizar los cambios y hacer commit.
4. Enviar un pull request.

---

## 🛠️ Descarga del Ejecutable y Código Fuente

Este proyecto es **Software Libre** y defiende la **transparencia del código**.

* **Ejecutable Compilado:** Listo para usar en entornos Windows de 64 bits.
* **Código Fuente Original:** Disponible directamente en este repositorio para auditorías de seguridad, modificaciones o aprendizaje.

> [!IMPORTANT]
> 🛡️ Se recomienda verificar siempre las firmas y el hash del ejecutable publicado en la sección de Releases ante la plataforma VirusTotal.

---

Copyright © 2026 @xorodev (CipherCoreDev). Licensed under the GNU General Public License v3.0
