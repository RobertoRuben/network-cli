#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuraciones centralizadas para la aplicación NetAdmin CLI.
"""

# Configuración general
APP_NAME = "NetAdmin CLI"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Herramienta de línea de comandos para administración de red con animaciones"

# Configuración de colores
COLORS = {
    "primario": "blue",
    "secundario": "green",
    "advertencia": "yellow",
    "error": "red",
    "info": "cyan",
    "exito": "green",
}

# Configuración de red
NETWORK_CONFIG = {
    "timeout_ping": 1.0,  # Segundos
    "timeout_scan": 5.0,  # Segundos para escaneo de red
    "default_scan_range": "0/24",  # Rango CIDR para escaneo predeterminado
}

# Configuración de prueba de velocidad
SPEEDTEST_CONFIG = {
    "force_json": True,
    "include_ping": True,
    "servers": [],  # Lista vacía para seleccionar automáticamente el mejor servidor
}

# Animaciones y estilos
ANIMATION_STYLES = {
    "carga": "dots",
    "progreso": "dots10",
    "ping": "dots12",
}

# Límites y valores predeterminados
DEFAULTS = {
    "dispositivos_max": 10,
    "trafico_duracion": 10,  # Segundos
}

# Configuración de tablas
TABLE_STYLES = {
    "box": "ROUNDED",
    "header_style": "bold cyan",
    "row_styles": ["dim", ""]  # Estilos alternantes para filas
}