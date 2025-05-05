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
    console_manager.mostrar_titulo(
        "Información de Red",
        "Detalles de configuración e interfaces"
    )
    
    # Obtener información con animación
    console_manager.mostrar_animacion_carga("Obteniendo información de red", duracion=1.5)
    
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
    
    # Mostrar detalles de interfaces en formato de tabla
    columnas = [
        {"nombre": "Nombre", "estilo": "cyan"},
        {"nombre": "IP", "estilo": "green"},
        {"nombre": "MAC", "estilo": "magenta"},
        {"nombre": "Estado", "estilo": "yellow"},
        {"nombre": "Velocidad", "estilo": "blue"}
    ]
    tabla = console_manager.crear_tabla("Interfaces de Red", columnas)
    
    # Agregar información de interfaces a la tabla
    for interfaz in info_red["interfaces"]:
        estado = f"[green]Activo[/]" if interfaz["activa"] else f"[{COLORS['error']}]Inactivo[/]"
        velocidad = f"{interfaz['velocidad']} Mbps" if interfaz["velocidad"] else "Desconocido"
        
        tabla.add_row(
            interfaz["nombre"],
            interfaz["ipv4"],
            interfaz["mac"],
            estado,
            velocidad
        )
    
    console_manager.console.print("\n")
    console_manager.console.print(tabla)
    
    # Mostrar resumen visual de interfaces activas/inactivas
    paneles = []
    for interfaz in info_red["interfaces"]:
        color_panel = "green" if interfaz["activa"] else "red"
        content = f"[bold]{interfaz['nombre']}[/]\n" \
                 f"IP: {interfaz['ipv4']}\n" \
                 f"MAC: {interfaz['mac'][:8]}...\n" \
                 f"{'Activo' if interfaz['activa'] else 'Inactivo'}"
        
        paneles.append(
            Panel(
                content,
                title=interfaz["nombre"],
                border_style=color_panel,
                width=30
            )
        )
    
    # Mostrar paneles si hay interfaces
    if paneles:
        console_manager.console.print("\n[bold]Resumen de Interfaces:[/]")
        console_manager.console.print(Columns(paneles))
    
    console_manager.mostrar_exito("Información de red obtenida con éxito.")