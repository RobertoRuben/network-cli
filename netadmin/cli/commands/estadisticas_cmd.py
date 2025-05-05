import typer
import time
import psutil
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich import box
from datetime import datetime

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_monitor
from netadmin.config.settings import COLORS


@app.command("estadisticas", help="Mostrar estadísticas de red en tiempo real")
def comando(
    duracion: int = typer.Option(
        60, "--duracion", "-d", help="Duración del monitoreo en segundos (0 para continuo)"
    ),
    intervalo: float = typer.Option(
        1.0, "--intervalo", "-i", help="Intervalo de actualización en segundos"
    ),
):
    duracion_str = "continua" if duracion == 0 else f"{duracion}s"
    console_manager.mostrar_comando_ejecutado(
        f"estadisticas --duracion {duracion_str} --intervalo {intervalo}"
    )
    
    console_manager.console.print()
    
    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ ESTADÍSTICAS DE RED EN TIEMPO REAL[/]")
    console_manager.console.print()

    io_inicial = psutil.net_io_counters(pernic=True)
    tiempo_inicio = time.time()
    bytes_enviados_total = {}
    bytes_recibidos_total = {}
    picos_velocidad_carga = {}
    picos_velocidad_descarga = {}

    def generar_tabla() -> Table:
        io_actual = psutil.net_io_counters(pernic=True)
        tiempo_actual = time.time()
        tiempo_transcurrido = int(tiempo_actual - tiempo_inicio)
        
        tabla = Table(
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style=f"bold {COLORS['primario']}",
            show_edge=False,
            padding=(0, 1),
        )
        
        tabla.add_column("INTERFAZ", style=f"{COLORS['secundario']}")
        tabla.add_column("↑", style=f"{COLORS['secundario']}", justify="right")
        tabla.add_column("↓", style=f"{COLORS['info']}", justify="right")
        tabla.add_column("TOTAL ↑", style=f"{COLORS['texto']}", justify="right")
        tabla.add_column("TOTAL ↓", style=f"{COLORS['texto']}", justify="right")
        
        tabla.caption = f"[{COLORS['texto_dim']}]Tiempo: {tiempo_transcurrido}s • Intervalo: {intervalo}s[/]"

        interfaces_activas = []
        
        for interfaz, datos in io_actual.items():
            if interfaz in io_inicial:
                datos_iniciales = io_inicial[interfaz]

                sent_total = datos.bytes_sent - datos_iniciales.bytes_sent
                recv_total = datos.bytes_recv - datos_iniciales.bytes_recv

                if interfaz not in bytes_enviados_total:
                    bytes_enviados_total[interfaz] = 0
                    bytes_recibidos_total[interfaz] = 0
                    picos_velocidad_carga[interfaz] = 0
                    picos_velocidad_descarga[interfaz] = 0

                bytes_anteriores_enviados = bytes_enviados_total.get(interfaz, 0)
                bytes_anteriores_recibidos = bytes_recibidos_total.get(interfaz, 0)

                enviados_recientes = sent_total - bytes_anteriores_enviados
                recibidos_recientes = recv_total - bytes_anteriores_recibidos

                bytes_enviados_total[interfaz] = sent_total
                bytes_recibidos_total[interfaz] = recv_total

                velocidad_carga = enviados_recientes / intervalo / 1024  # KB/s
                velocidad_descarga = recibidos_recientes / intervalo / 1024  # KB/s

                if velocidad_carga > picos_velocidad_carga[interfaz]:
                    picos_velocidad_carga[interfaz] = velocidad_carga
                if velocidad_descarga > picos_velocidad_descarga[interfaz]:
                    picos_velocidad_descarga[interfaz] = velocidad_descarga

                if velocidad_carga > 0 or velocidad_descarga > 0 or bytes_enviados_total[interfaz] > 0:
                    tabla.add_row(
                        Text(interfaz, style=f"bold {COLORS['texto']}"),
                        f"{velocidad_carga:.2f} KB/s",
                        f"{velocidad_descarga:.2f} KB/s",
                        f"{bytes_enviados_total[interfaz]/1024:.2f} KB",
                        f"{bytes_recibidos_total[interfaz]/1024:.2f} KB",
                    )
                    interfaces_activas.append(interfaz)
        
        if not interfaces_activas:
            tabla.add_row(
                Text("Sin actividad", style=f"dim {COLORS['texto_dim']}"),
                "0.00 KB/s",
                "0.00 KB/s",
                "0.00 KB",
                "0.00 KB",
            )
            
        return tabla

    try:
        with Live(generar_tabla(), refresh_per_second=4) as live:
            inicio_monitoreo = time.time()
            while True:
                io_inicial = psutil.net_io_counters(pernic=True)

                time.sleep(intervalo)

                live.update(generar_tabla())

                if duracion > 0 and (time.time() - inicio_monitoreo) >= duracion:
                    break
                    
    except KeyboardInterrupt:
        pass
        
    console_manager.console.print()
    
    tiempo_total = time.time() - tiempo_inicio
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Duración:[/] "
        f"[{COLORS['texto']}]{tiempo_total:.1f}s[/]"
    )
    
    if picos_velocidad_carga and picos_velocidad_descarga:
        interfaz_max_pico_descarga = max(picos_velocidad_descarga.items(), key=lambda x: x[1])
        interfaz_max_pico_carga = max(picos_velocidad_carga.items(), key=lambda x: x[1])
        
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Pico descarga:[/] "
            f"[{COLORS['texto']}]{interfaz_max_pico_descarga[0]}[/] "
            f"[dim {COLORS['texto_dim']}]({interfaz_max_pico_descarga[1]:.2f} KB/s)[/]"
        )
        
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Pico carga:[/] "
            f"[{COLORS['texto']}]{interfaz_max_pico_carga[0]}[/] "
            f"[dim {COLORS['texto_dim']}]({interfaz_max_pico_carga[1]:.2f} KB/s)[/]"
        )