#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para medir la velocidad de conexión a Internet.
"""

import typer
from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import speed_tester
from netadmin.config.settings import COLORS


@app.command("velocidad", help="Medir la velocidad de conexión a Internet")
def comando():
    """Mide la velocidad de carga y descarga de la conexión a Internet."""
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado("velocidad")

    # Usar una única animación más simple
    with console_manager.console.status(
        f"[bold {COLORS['primario']}]Realizando prueba de velocidad...", spinner="dots"
    ):
        # La prueba real ocurre aquí
        resultados = speed_tester.realizar_prueba()

    # Si la prueba falló
    if resultados["download"] == 0 and resultados["upload"] == 0:
        console_manager.mostrar_error("No se pudo completar la prueba de velocidad")
        return

    # Mostrar los resultados simplificados
    console_manager.datos_formateados(
        "Resultados de Velocidad",
        {
            "Descarga": f"{resultados['download']:.2f} Mbps",
            "Carga": f"{resultados['upload']:.2f} Mbps",
            "Ping": f"{resultados['ping']:.2f} ms",
        },
        estilo="lista",
    )

    # Añadir comentario conciso sobre la calidad
    calidad = (
        "excelente"
        if resultados["download"] > 100
        else (
            "buena"
            if resultados["download"] > 30
            else "aceptable" if resultados["download"] > 10 else "baja"
        )
    )

    color_calidad = (
        COLORS["exito"]
        if calidad in ["excelente", "buena"]
        else COLORS["advertencia"] if calidad == "aceptable" else COLORS["error"]
    )

    console_manager.console.print(f"[{color_calidad}]Calidad de conexión: {calidad}[/]")
