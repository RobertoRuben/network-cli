#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para monitorear el tráfico de red por dispositivo en tiempo real.
"""

import typer
import time
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.panel import Panel
from rich import box

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_monitor, network_scanner
from netadmin.config.settings import COLORS, DEFAULTS


@app.command(
    "monitor", help="Monitorear el tráfico de red por dispositivo en tiempo real"
)
def comando(
    ip: str = typer.Argument(
        ..., help="Dirección IP base para monitoreo (ej: 192.168.1.1)"
    ),
    duracion: int = typer.Option(
        60, "--duracion", "-d", help="Duración en segundos del monitoreo"
    ),
    intervalo: int = typer.Option(
        1, "--intervalo", "-i", help="Intervalo de actualización en segundos"
    ),
    cantidad: int = typer.Option(
        5, "--cantidad", "-c", help="Cantidad de dispositivos a monitorear"
    ),
):
    """Monitorea el tráfico de red por dispositivo en tiempo real.

    Muestra gráficos de barras actualizados con el tráfico de subida y bajada para cada dispositivo activo.

    Ejemplo: netadmin monitor 192.168.1.1 -d 60 -i 1
    """
    # Mostrar comando que se está ejecutando
    console_manager.mostrar_comando_ejecutado(
        f"monitor {ip} --duracion {duracion} --intervalo {intervalo} --cantidad {cantidad}"
    )

    # Escanear la red para obtener dispositivos activos
    with console_manager.console.status(
        f"[bold {COLORS['primario']}]Escaneando la red para encontrar dispositivos activos...",
        spinner="dots12",
    ):
        # Obtener red base
        red_base = network_scanner.obtener_red_desde_ip(ip)
        # Escanear dispositivos activos
        dispositivos = network_scanner.escanear_red_especifica(
            ip_red=ip, solo_activos=True, duracion_monitoreo=1
        )

    if not dispositivos:
        console_manager.mostrar_advertencia(
            f"No se encontraron dispositivos activos en la red {red_base}.0/24."
        )
        return

    # Limitar la cantidad de dispositivos
    dispositivos = dispositivos[:cantidad]
    ips = [d["ip"] for d in dispositivos]

    # Crear la tabla para mostrar el tráfico
    def generar_tabla(datos=None):
        # Usar estilo SIMPLE para tabla más minimalista
        tabla = Table(
            title=f"Tráfico en Tiempo Real - Red {red_base}.0/24", box=box.SIMPLE
        )

        # Columnas
        tabla.add_column("IP", style="cyan")
        tabla.add_column("Dispositivo", style="green")
        tabla.add_column("MAC", style="magenta")
        tabla.add_column("Carga (KB/s)", style="yellow", justify="right")
        tabla.add_column("Descarga (KB/s)", style="blue", justify="right")
        # Quitar barras visuales para simplificar
        # tabla.add_column("Barra de Carga", justify="center")
        # tabla.add_column("Barra de Descarga", justify="center")

        # Si no hay datos, mostrar filas vacías
        if not datos:
            for disp in dispositivos:
                tabla.add_row(
                    disp["ip"],
                    disp["nombre"],
                    disp["mac"],
                    "0.00",
                    "0.00",
                    # "░" * 10,
                    # "░" * 10
                )
            return tabla

        # Agregar filas con datos
        for dato in datos:
            tabla.add_row(
                dato.get("ip", "N/A"),
                dato.get("nombre", "Desconocido"),
                dato.get("mac", "Desconocido"),
                f"{dato.get('velocidad_carga', 0):.2f}",
                f"{dato.get('velocidad_descarga', 0):.2f}",
            )

        return tabla

    # Información para el panel de estadísticas
    estadisticas = {
        "inicio": time.time(),
        "total_enviado": 0,
        "total_recibido": 0,
        "max_carga": 0,
        "max_descarga": 0,
        "dispositivo_max_trafico": None,
    }

    # Panel de estadísticas simplificado
    def generar_panel_estadisticas():
        tiempo_transcurrido = time.time() - estadisticas["inicio"]

        texto = Text()
        texto.append(f"Tiempo: {tiempo_transcurrido:.1f}s | ", style="bold")
        texto.append(
            f"Enviado: {estadisticas['total_enviado'] / 1024:.2f} MB | ", style="yellow"
        )
        texto.append(
            f"Recibido: {estadisticas['total_recibido'] / 1024:.2f} MB | ", style="blue"
        )

        if estadisticas["dispositivo_max_trafico"]:
            texto.append("Mayor tráfico: ", style="bold")
            texto.append(f"{estadisticas['dispositivo_max_trafico']}")

        # Usar Panel simple sin título
        return Panel(texto, border_style=COLORS["primario"], box=box.SIMPLE)

    # Layout para el panel y la tabla
    def generar_layout(tabla):
        layout = Layout()
        layout.split(
            Layout(
                generar_panel_estadisticas(), name="estadisticas", size=3
            ),  # Reducir tamaño del panel
            Layout(tabla, name="tabla"),
        )
        return layout

    # Mostrar instrucciones
    console_manager.console.print(
        f"\n[{COLORS['info']}]Iniciando monitoreo. Presiona Ctrl+C para detener.[/]\n"
    )

    # Usar Live para actualizar la tabla en tiempo real
    try:
        # Inicializar tabla
        with Live(generar_layout(generar_tabla()), refresh_per_second=4) as live:
            # Obtener datos en tiempo real
            monitor = network_monitor.monitorear_trafico_tiempo_real(
                ips=ips, intervalo=intervalo, duracion_total=duracion
            )

            # Actualizar la tabla con los datos nuevos
            for datos in monitor:
                # Actualizar estadísticas
                if datos:
                    for dato in datos:
                        estadisticas["total_enviado"] += dato.get(
                            "bytes_enviados_inc", 0
                        )
                        estadisticas["total_recibido"] += dato.get(
                            "bytes_recibidos_inc", 0
                        )

                        # Actualizar velocidades máximas
                        velocidad_carga = dato.get("velocidad_carga", 0)
                        velocidad_descarga = dato.get("velocidad_descarga", 0)

                        if velocidad_carga > estadisticas["max_carga"]:
                            estadisticas["max_carga"] = velocidad_carga

                        if velocidad_descarga > estadisticas["max_descarga"]:
                            estadisticas["max_descarga"] = velocidad_descarga

                        # Actualizar dispositivo con mayor tráfico
                        trafico_total = velocidad_carga + velocidad_descarga
                        if estadisticas[
                            "dispositivo_max_trafico"
                        ] is None or trafico_total > estadisticas.get(
                            "max_trafico_total", 0
                        ):
                            estadisticas["max_trafico_total"] = trafico_total
                            estadisticas["dispositivo_max_trafico"] = (
                                f"{dato['ip']} ({dato['nombre']})"
                            )

                # Actualizar la tabla en vivo
                live.update(generar_layout(generar_tabla(datos)))
    except KeyboardInterrupt:
        # Si el usuario detiene el monitoreo con Ctrl+C
        console_manager.console.print("\n")
        console_manager.mostrar_exito(
            f"Monitoreo finalizado ({time.time() - estadisticas['inicio']:.1f}s). Total: {estadisticas['total_enviado'] / 1024:.2f} MB enviados, {estadisticas['total_recibido'] / 1024:.2f} MB recibidos."
        )
