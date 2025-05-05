#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para monitorear el tráfico de red por interfaz.
"""

import typer
from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_monitor
from netadmin.config.settings import DEFAULTS, COLORS, ANIMATION_STYLES


@app.command("trafico", help="Monitorear el tráfico de red por interfaz")
def comando(
    duracion: int = typer.Option(
        DEFAULTS["trafico_duracion"], help="Duración en segundos del monitoreo"
    )
):
    """Monitorea el tráfico de red por interfaz durante un tiempo específico."""
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado(f"trafico --duracion {duracion}")

    # Recopilar datos de tráfico con animación
    with console_manager.console.status(
        f"[bold {COLORS['secundario']}]Recopilando datos de tráfico...",
        spinner=ANIMATION_STYLES["carga"],
    ):
        resultados = network_monitor.monitorear_trafico(duracion=duracion)

    if not resultados:
        console_manager.mostrar_advertencia(
            "No se detectó tráfico de red en las interfaces activas."
        )
        return

    # Crear tabla para mostrar el tráfico
    columnas = [
        {"nombre": "Interfaz", "estilo": "cyan"},
        {"nombre": "Enviado", "estilo": "green", "alineacion": "right"},
        {"nombre": "Recibido", "estilo": "yellow", "alineacion": "right"},
        {"nombre": "Vel. Carga", "estilo": "magenta", "alineacion": "right"},
        {"nombre": "Vel. Descarga", "estilo": "blue", "alineacion": "right"},
    ]
    tabla = console_manager.crear_tabla(f"Tráfico de Red ({duracion}s)", columnas)

    # Total para estadísticas
    total_enviado = 0
    total_recibido = 0

    # Agregar datos a la tabla
    for dato in resultados:
        bytes_enviados = dato["bytes_enviados"]
        bytes_recibidos = dato["bytes_recibidos"]
        velocidad_carga = dato["velocidad_carga"]
        velocidad_descarga = dato["velocidad_descarga"]

        total_enviado += bytes_enviados
        total_recibido += bytes_recibidos

        tabla.add_row(
            dato["interfaz"],
            f"{bytes_enviados / 1024:.2f} KB",
            f"{bytes_recibidos / 1024:.2f} KB",
            f"{velocidad_carga:.2f} KB/s",
            f"{velocidad_descarga:.2f} KB/s",
        )

    # Añadir fila de totales
    tabla.add_section()
    tabla.add_row(
        "[bold]TOTAL",
        f"[bold]{total_enviado / 1024:.2f} KB",
        f"[bold]{total_recibido / 1024:.2f} KB",
        "",
        "",
    )

    console_manager.console.print(tabla)

    # Mostrar dispositivo con mayor tráfico de forma concisa
    if resultados:
        max_trafico = max(
            resultados, key=lambda x: x["bytes_enviados"] + x["bytes_recibidos"]
        )
        console_manager.mostrar_exito(
            f"Interfaz con mayor tráfico: {max_trafico['interfaz']} "
            f"({(max_trafico['bytes_enviados'] + max_trafico['bytes_recibidos']) / 1024:.2f} KB)"
        )
    else:
        console_manager.mostrar_exito("Monitoreo de tráfico completado.")
