#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para mostrar los dispositivos conectados en la red local.
"""

import typer
from rich import box
from rich.table import Table

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
from netadmin.config.settings import DEFAULTS, COLORS


@app.command("dispositivos", help="Ver dispositivos conectados a la red")
def comando(
    cantidad: int = typer.Option(
        DEFAULTS["dispositivos_max"], help="Cantidad máxima de dispositivos a mostrar"
    )
):
    """Muestra los dispositivos conectados en la red local."""
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado(f"dispositivos --cantidad {cantidad}")

    # Mostrar estado de nmap antes de escanear
    console_manager.mostrar_estado_nmap(NMAP_INFO)

    with console_manager.console.status(
        "[bold green]Escaneando la red...", spinner="dots10"
    ):
        dispositivos = network_scanner.escanear_red(cantidad_max=cantidad)

    if not dispositivos:
        console_manager.mostrar_advertencia("No se encontraron dispositivos en la red.")
        return

    # Crear tabla para dispositivos
    columnas = [
        {"nombre": "IP", "estilo": "cyan"},
        {"nombre": "Nombre", "estilo": "green"},
        {"nombre": "MAC", "estilo": "magenta"},
        {"nombre": "Estado", "estilo": "yellow"},
    ]
    tabla = console_manager.crear_tabla("Dispositivos Conectados", columnas)

    # Agregar los dispositivos a la tabla
    for dispositivo in dispositivos:
        tabla.add_row(
            dispositivo["ip"],
            dispositivo["nombre"],
            dispositivo["mac"],
            (
                f"[green]Activo[/]"
                if dispositivo["estado"] == "up"
                else f"[{COLORS['error']}]Inactivo[/]"
            ),
        )

    console_manager.console.print(tabla)

    # Mostrar información adicional concisa
    console_manager.mostrar_exito(f"Se encontraron {len(dispositivos)} dispositivos.")
