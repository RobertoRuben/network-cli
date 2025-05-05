#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para hacer ping a un host para comprobar conectividad.
"""

import typer
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner
from netadmin.config.settings import COLORS, NETWORK_CONFIG


@app.command("ping", help="Hacer ping a un host para comprobar conectividad")
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host"),
    repeticiones: int = typer.Option(4, help="Número de veces a realizar el ping"),
):
    """Hace ping a un host para comprobar la conectividad."""
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado(f"ping {host}")

    resultados = []
    resultado_general = True
    tiempo_total = 0
    intentos_exitosos = 0

    # Realizar ping el número de veces indicado
    for i in range(1, repeticiones + 1):
        with console_manager.console.status(
            f"[bold {COLORS['primario']}]Ping {i}/{repeticiones}...", spinner="dots12"
        ):
            resultado, tiempo = network_scanner.ping_host(host)
            resultados.append((resultado, tiempo))

            # Actualizar estadísticas
            if resultado:
                tiempo_total += tiempo
                intentos_exitosos += 1
            else:
                resultado_general = False

    # Calcular tiempo promedio
    tiempo_promedio = tiempo_total / intentos_exitosos if intentos_exitosos > 0 else 0
    porcentaje_exito = (intentos_exitosos / repeticiones) * 100

    # Mostrar resultados simplificados
    console_manager.datos_formateados(
        "Resultados de Ping",
        {
            "Host": host,
            "Exitosos": f"{intentos_exitosos}/{repeticiones} ({porcentaje_exito:.1f}%)",
            "Tiempo promedio": (
                f"{tiempo_promedio:.2f} ms" if tiempo_promedio > 0 else "N/A"
            ),
            "Estado": (
                "Conectividad correcta"
                if resultado_general
                else (
                    "Conectividad intermitente"
                    if intentos_exitosos > 0
                    else "Sin conectividad"
                )
            ),
        },
        estilo="lista",
    )
