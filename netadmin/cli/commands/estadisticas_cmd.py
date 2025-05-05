#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para mostrar estadísticas de red en tiempo real.
"""

import typer
import time
import psutil
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from datetime import datetime

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.config.settings import COLORS, TABLE_STYLES


@app.command("estadisticas", help="Mostrar estadísticas de red en tiempo real")
def comando(
    duracion: int = typer.Option(
        60,
        "--duracion",
        "-d",
        help="Duración del monitoreo en segundos (0 para continuo)",
    ),
    intervalo: float = typer.Option(
        1.0, "--intervalo", "-i", help="Intervalo de actualización en segundos"
    ),
):
    """Muestra estadísticas de red actualizadas en tiempo real, incluyendo uso de ancho de banda por interfaz.

    Ejemplo: netadmin estadisticas --duracion 120 --intervalo 2
    """
    # Mostrar comando que se está ejecutando
    duracion_str = "continua" if duracion == 0 else f"{duracion}s"
    console_manager.mostrar_comando_ejecutado(f"estadisticas --duracion {duracion_str} --intervalo {intervalo}")

    # Inicializar contadores
    io_inicial = psutil.net_io_counters(pernic=True)
    tiempo_inicio = time.time()
    bytes_enviados_total = {}
    bytes_recibidos_total = {}
    picos_velocidad_carga = {}
    picos_velocidad_descarga = {}

    # Función para generar la tabla de estadísticas
    def generar_tablas():
        # Obtener datos actuales
        io_actual = psutil.net_io_counters(pernic=True)
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - tiempo_inicio

        # Tabla principal para estadísticas actuales (simplificada)
        tabla_principal = Table(
            title=f"Estadísticas de Red (Intervalo: {intervalo}s)",
            box=getattr(box, TABLE_STYLES["box"]),
        )
        tabla_principal.add_column("Interfaz", style="cyan")
        tabla_principal.add_column("Vel. Carga", style="green", justify="right")
        tabla_principal.add_column("Vel. Descarga", style="yellow", justify="right")
        tabla_principal.add_column("Total Enviado", style="green", justify="right")
        tabla_principal.add_column("Total Recibido", style="yellow", justify="right")

        # Generar filas para cada interfaz
        interfaces_activas = []
        for interfaz, datos in io_actual.items():
            # Obtener datos iniciales para esta interfaz
            if interfaz in io_inicial:
                datos_iniciales = io_inicial[interfaz]

                # Calcular totales
                sent_total = datos.bytes_sent - datos_iniciales.bytes_sent
                recv_total = datos.bytes_recv - datos_iniciales.bytes_recv

                # Inicializar contadores si es la primera vez
                if interfaz not in bytes_enviados_total:
                    bytes_enviados_total[interfaz] = 0
                    bytes_recibidos_total[interfaz] = 0
                    picos_velocidad_carga[interfaz] = 0
                    picos_velocidad_descarga[interfaz] = 0

                # Actualizar totales
                bytes_anteriores_enviados = bytes_enviados_total.get(interfaz, 0)
                bytes_anteriores_recibidos = bytes_recibidos_total.get(interfaz, 0)

                enviados_recientes = sent_total - bytes_anteriores_enviados
                recibidos_recientes = recv_total - bytes_anteriores_recibidos

                bytes_enviados_total[interfaz] = sent_total
                bytes_recibidos_total[interfaz] = recv_total

                # Calcular velocidades actuales (por segundo)
                velocidad_carga = enviados_recientes / intervalo / 1024  # KB/s
                velocidad_descarga = recibidos_recientes / intervalo / 1024  # KB/s

                # Actualizar picos
                if velocidad_carga > picos_velocidad_carga[interfaz]:
                    picos_velocidad_carga[interfaz] = velocidad_carga
                if velocidad_descarga > picos_velocidad_descarga[interfaz]:
                    picos_velocidad_descarga[interfaz] = velocidad_descarga

                # Agregar a la tabla principal si hay actividad
                if velocidad_carga > 0 or velocidad_descarga > 0:
                    tabla_principal.add_row(
                        interfaz,
                        f"{velocidad_carga:.2f} KB/s",
                        f"{velocidad_descarga:.2f} KB/s",
                        f"{bytes_enviados_total[interfaz]/1024:.2f} KB",
                        f"{bytes_recibidos_total[interfaz]/1024:.2f} KB",
                    )
                    interfaces_activas.append(interfaz)

        # Panel informativo simplificado
        ahora = datetime.now().strftime("%H:%M:%S")
        info_panel = Panel(
            f"[bold]Hora:[/] {ahora} | [bold]Tiempo:[/] {int(tiempo_transcurrido)}s | [bold]Interfaces activas:[/] {len(interfaces_activas)}",
            border_style=COLORS["primario"],
            box=box.SIMPLE # Usar borde simple
        )

        # Crear un layout para organizar todo
        layout = Layout()
        layout.split(Layout(info_panel, name="header", size=3), Layout(name="main"))

        # Dividir la sección principal según el contenido
        if interfaces_activas:
            layout["main"].update(tabla_principal)
        else:
            mensaje_espera = Panel(
                "[italic]Esperando actividad en las interfaces de red...[/]",
                border_style=COLORS["advertencia"],
                box=box.SIMPLE
            )
            layout["main"].update(mensaje_espera)

        return layout

    try:
        # Ejecutar el monitoreo en tiempo real
        with Live(generar_tablas(), refresh_per_second=4, screen=True) as live:
            inicio_monitoreo = time.time()
            while True:
                # Actualizar los datos iniciales para el siguiente intervalo
                io_inicial = psutil.net_io_counters(pernic=True)

                # Esperar el intervalo especificado
                time.sleep(intervalo)

                # Actualizar la interfaz
                live.update(generar_tablas())

                # Verificar si se ha alcanzado la duración especificada
                if duracion > 0 and (time.time() - inicio_monitoreo) >= duracion:
                    break
    except KeyboardInterrupt:
        console_manager.console.print(
            "\n[bold yellow]Monitoreo interrumpido por el usuario.[/]"
        )
    except Exception as e:
        console_manager.mostrar_error(f"Error durante el monitoreo", str(e))
    finally:
        # Mensaje final más conciso
        tiempo_total = time.time() - tiempo_inicio
        console_manager.mostrar_exito(f"Monitoreo finalizado ({tiempo_total:.1f}s).")
