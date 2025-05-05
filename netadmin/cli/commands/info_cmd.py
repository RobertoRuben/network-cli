#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para mostrar información básica de la configuración de red.
"""

import typer
from rich.columns import Columns
from rich.panel import Panel

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_monitor
from netadmin.config.settings import COLORS

@app.command("info", help="Mostrar información básica de red")
def comando():
    """Muestra información básica de la configuración de red."""
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado("info")
    
    # Obtener información con animación más corta
    console_manager.mostrar_animacion_carga("Obteniendo información de red", duracion=1)
    
    # Recopilar información de red
    info_red = network_monitor.obtener_info_red()
    
    # Mostrar información básica
    console_manager.datos_formateados(
        "Información Básica", 
        {
            "IP Local": info_red["ip_local"],
            "Nombre del equipo": info_red["hostname"],
            "Interfaces activas": sum(1 for i in info_red["interfaces"] if i["activa"]),
            "Total interfaces": len(info_red["interfaces"])
        }
    )
    
    # Mostrar detalles de interfaces en formato de tabla conciso
    columnas = [
        {"nombre": "Nombre", "estilo": "cyan"},
        {"nombre": "IP", "estilo": "green"},
        {"nombre": "MAC", "estilo": "magenta"},
        {"nombre": "Estado", "estilo": "yellow"}
    ]
    tabla = console_manager.crear_tabla("Interfaces de Red", columnas)
    
    # Agregar información de interfaces a la tabla
    for interfaz in info_red["interfaces"]:
        estado = f"[green]Activo[/]" if interfaz["activa"] else f"[{COLORS['error']}]Inactivo[/]"
        
        tabla.add_row(
            interfaz["nombre"],
            interfaz["ipv4"],
            interfaz["mac"],
            estado
        )
    
    console_manager.console.print(tabla)