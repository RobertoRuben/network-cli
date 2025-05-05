#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para escanear redes específicas y mostrar información detallada sobre dispositivos.
"""

import typer
from typing import Optional
from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
from netadmin.config.settings import COLORS, ANIMATION_STYLES


@app.command("escanear", help="Escanear una red específica y mostrar dispositivos")
def comando(
    ip: str = typer.Argument(
        ..., help="Dirección IP base para escanear (ej: 192.168.1.1)"
    ),
    solo_activos: bool = typer.Option(
        False, "--activos", "-a", help="Mostrar solo dispositivos activos"
    ),
    duracion: int = typer.Option(
        5, "--duracion", "-d", help="Duración del monitoreo de tráfico en segundos"
    ),
):
    """Escanea una red específica basada en una IP proporcionada y muestra información detallada de dispositivos.

    Ejemplo: netadmin escanear 192.168.1.35
    """
    # Mostrar comando que se está ejecutando
    comando_str = f"escanear {ip}"
    if solo_activos:
        comando_str += " --activos"
    comando_str += f" --duracion {duracion}"
    console_manager.mostrar_comando_ejecutado(comando_str)

    # Mostrar estado de nmap antes de escanear
    console_manager.mostrar_estado_nmap(NMAP_INFO)

    with console_manager.console.status(
        f"[bold {COLORS['primario']}]Realizando escaneo detallado de red...",
        spinner=ANIMATION_STYLES["carga"],
    ):
        dispositivos = network_scanner.escanear_red_especifica(
            ip_red=ip, solo_activos=solo_activos, duracion_monitoreo=duracion
        )

    if not dispositivos:
        console_manager.mostrar_advertencia(
            f"No se encontraron {'dispositivos activos' if solo_activos else 'dispositivos'} "
            f"en la red {ip.rsplit('.', 1)[0]}.0/24."
        )
        return

    # Crear tabla para mostrar la información detallada
    columnas = [
        {"nombre": "IP", "estilo": "cyan"},
        {"nombre": "MAC", "estilo": "magenta"},
        {"nombre": "Dispositivo", "estilo": "green"},
        {"nombre": "Subida (KB/s)", "estilo": "yellow", "alineacion": "right"},
        {"nombre": "Descarga (KB/s)", "estilo": "blue", "alineacion": "right"},
        {"nombre": "Estado", "estilo": "bold", "alineacion": "center"},
    ]

    tabla = console_manager.crear_tabla(
        f"Dispositivos de Red - {ip.rsplit('.', 1)[0]}.0/24", columnas
    )

    # Añadir dispositivos a la tabla
    dispositivos_activos = 0
    for dispositivo in dispositivos:
        estado = dispositivo["estado"]
        estado_formateado = (
            f"[green]Activo[/]" if estado == "up" else f"[{COLORS['error']}]Inactivo[/]"
        )

        if estado == "up":
            dispositivos_activos += 1

        tabla.add_row(
            dispositivo["ip"],
            dispositivo["mac"],
            dispositivo["nombre"],
            f"{dispositivo['velocidad_subida']:.2f}",
            f"{dispositivo['velocidad_descarga']:.2f}",
            estado_formateado,
        )

    console_manager.console.print(tabla)

    # Mostrar información adicional concisa
    total_dispositivos = len(dispositivos)
    console_manager.mostrar_exito(
        f"Escaneo completado: {dispositivos_activos} activos de {total_dispositivos} encontrados."
    )

    # Mostrar notas sobre el tráfico de forma más concisa
    console_manager.console.print(
        f"[{COLORS['info']}]Nota:[/] Velocidades aprox. durante {duracion}s."
    )

    # Si se encontró algún dispositivo, mostrar el que más tráfico genera
    if dispositivos_activos > 0:
        dispositivo_mas_trafico = max(
            [d for d in dispositivos if d["estado"] == "up"],
            key=lambda x: x["velocidad_subida"] + x["velocidad_descarga"],
        )

        console_manager.console.print(
            f"Mayor tráfico: [bold cyan]{dispositivo_mas_trafico['ip']}[/] "
            f"({dispositivo_mas_trafico['velocidad_subida'] + dispositivo_mas_trafico['velocidad_descarga']:.2f} KB/s)"
        )


@app.command("activos", help="Mostrar solo dispositivos activos en una red")
def activos(
    ip: str = typer.Argument(
        ..., help="Dirección IP base para escanear (ej: 192.168.1.1)"
    ),
    duracion: int = typer.Option(
        3, "--duracion", "-d", help="Duración del monitoreo de tráfico en segundos"
    ),
):
    """Escanea una red específica y muestra solo los dispositivos activos.

    Ejemplo: netadmin activos 192.168.1.1
    """
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado(f"activos {ip} --duracion {duracion}")

    # Mostrar estado de nmap antes de escanear
    # console_manager.mostrar_estado_nmap(NMAP_INFO) # Ya se muestra dentro de la función 'comando'

    # Reutilizamos la función principal con solo_activos=True
    comando(ip=ip, solo_activos=True, duracion=duracion)
