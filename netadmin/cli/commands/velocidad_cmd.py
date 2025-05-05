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
    console_manager.mostrar_titulo(
        "Prueba de Velocidad de Internet",
        "Midiendo velocidades de carga y descarga..."
    )
    
    # Definir las tareas para la prueba de velocidad
    tareas = [
        {"descripcion": "Conectando al servidor de prueba...", "total": None},
        {"descripcion": "Midiendo velocidad de descarga...", "total": None},
        {"descripcion": "Midiendo velocidad de carga...", "total": None},
    ]
    
    # Ejecutar la prueba con animación de progreso
    with console_manager.progreso_con_animacion(tareas)[0] as progreso:
        # La prueba real ocurre aquí
        resultados = speed_tester.realizar_prueba()
    
    # Si la prueba falló
    if resultados["download"] == 0 and resultados["upload"] == 0:
        console_manager.mostrar_error(
            "No se pudo completar la prueba de velocidad.",
            "Comprueba tu conexión a Internet."
        )
        return
    
    # Mostrar los resultados en formato de tabla
    columnas = [
        {"nombre": "Tipo", "estilo": "cyan"},
        {"nombre": "Velocidad", "estilo": "green", "alineacion": "right"},
    ]
    tabla = console_manager.crear_tabla("Resultados de la Prueba de Velocidad", columnas)
    
    tabla.add_row("Descarga", f"[bold green]{resultados['download']:.2f} Mbps[/]")
    tabla.add_row("Carga", f"[bold {COLORS['secundario']}]{resultados['upload']:.2f} Mbps[/]")
    tabla.add_row("Ping", f"[bold {COLORS['info']}]{resultados['ping']:.2f} ms[/]")
    
    console_manager.console.print("\n")
    console_manager.console.print(tabla)
    
    # Añadir comentario interpretativo sobre la calidad de conexión
    calidad = "excelente" if resultados['download'] > 100 else \
              "buena" if resultados['download'] > 30 else \
              "aceptable" if resultados['download'] > 10 else \
              "baja"
    
    color_calidad = COLORS["exito"] if calidad in ["excelente", "buena"] else \
                   COLORS["advertencia"] if calidad == "aceptable" else \
                   COLORS["error"]
    
    console_manager.console.print(
        f"\nTu conexión tiene una calidad [{color_calidad}]{calidad}[/] " 
        f"para el uso general de Internet."
    )
    
    console_manager.mostrar_exito("Prueba de velocidad completada con éxito.")