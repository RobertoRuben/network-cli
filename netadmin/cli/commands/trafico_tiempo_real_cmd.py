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
    console_manager.mostrar_comando_ejecutado(
        f"monitor {ip} --duracion {duracion} --intervalo {intervalo} --cantidad {cantidad}"
    )
    
    console_manager.console.print()

    with console_manager.console.status(
        f"[{COLORS['secundario']}]Escaneando la red...", spinner="dots"
    ):
        red_base = network_scanner.obtener_red_desde_ip(ip)
        dispositivos = network_scanner.escanear_red_especifica(
            ip_red=ip, solo_activos=True, duracion_monitoreo=1
        )

    if not dispositivos:
        console_manager.mostrar_advertencia(
            f"No se encontraron dispositivos activos en la red {red_base}.0/24."
        )
        return

    dispositivos = dispositivos[:cantidad]
    ips = [d["ip"] for d in dispositivos]
    
    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ MONITOR DE TRÁFICO[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{red_base}.0/24[/]")
    console_manager.console.print()

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Dispositivos:[/] "
        f"[{COLORS['texto']}]{len(dispositivos)} activos[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Configuración:[/] "
        f"[{COLORS['texto']}]intervalo: {intervalo}s[/], "
        f"[{COLORS['texto']}]duración: {duracion}s[/]"
    )
    
    console_manager.console.print()
    
    console_manager.console.print(f"[{COLORS['info']}]Iniciando monitoreo. Presiona Ctrl+C para detener.[/]")
    console_manager.console.print()

    def generar_tabla(datos=None):
        tabla = Table(
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style=f"bold {COLORS['primario']}",
            show_edge=False,
            padding=(0, 1),
        )

        tabla.add_column("IP", style=f"{COLORS['secundario']}")
        tabla.add_column("DISPOSITIVO", style=f"{COLORS['texto']}")
        tabla.add_column("↑", style=f"{COLORS['secundario']}", justify="right")
        tabla.add_column("↓", style=f"{COLORS['info']}", justify="right")

        if not datos:
            for disp in dispositivos:
                tabla.add_row(
                    disp["ip"],
                    disp["nombre"],
                    "0.00 KB/s",
                    "0.00 KB/s",
                )
            return tabla

        for dato in datos:
            tabla.add_row(
                Text(dato.get("ip", "N/A"), style=f"bold {COLORS['texto']}"),
                dato.get("nombre", "Desconocido"),
                f"{dato.get('velocidad_carga', 0):.2f} KB/s",
                f"{dato.get('velocidad_descarga', 0):.2f} KB/s",
            )

        return tabla

    estadisticas = {
        "inicio": time.time(),
        "total_enviado": 0,
        "total_recibido": 0,
        "max_carga": 0,
        "max_descarga": 0,
        "dispositivo_max_trafico": None,
    }

    def generar_panel_estadisticas():
        tiempo_transcurrido = time.time() - estadisticas["inicio"]
        
        tiempo_format = f"{int(tiempo_transcurrido // 60):02d}:{int(tiempo_transcurrido % 60):02d}"
        total_enviado_mb = estadisticas["total_enviado"] / 1024
        total_recibido_mb = estadisticas["total_recibido"] / 1024

        # Creamos el contenido del panel como una lista de líneas separadas
        linea1 = f"[bold {COLORS['texto']}]Tiempo:[/] [{COLORS['texto']}]{tiempo_format}[/] • [bold {COLORS['texto']}]Enviado:[/] [{COLORS['secundario']}]{total_enviado_mb:.2f} MB[/]"
        linea2 = f"[bold {COLORS['texto']}]Recibido:[/] [{COLORS['info']}]{total_recibido_mb:.2f} MB[/]"
        
        if estadisticas["dispositivo_max_trafico"]:
            linea2 += f" • [bold {COLORS['texto']}]Mayor tráfico:[/] [{COLORS['texto']}]{estadisticas['dispositivo_max_trafico']}[/]"

        # Usamos una tabla para organizar mejor el contenido
        return Panel(
            f"{linea1}\n{linea2}",
            box=box.SIMPLE,
            padding=(0, 1),
            border_style=COLORS["secundario"],
        )

    def generar_layout(tabla):
        layout = Layout()
        layout.split(
            Layout(generar_panel_estadisticas(), name="estadisticas", size=3),
            Layout(tabla, name="tabla"),
        )
        return layout

    try:
        with Live(generar_layout(generar_tabla()), refresh_per_second=4) as live:
            monitor = network_monitor.monitorear_trafico_tiempo_real(
                ips=ips, intervalo=intervalo, duracion_total=duracion
            )

            for datos in monitor:
                if datos:
                    for dato in datos:
                        estadisticas["total_enviado"] += dato.get(
                            "bytes_enviados_inc", 0
                        )
                        estadisticas["total_recibido"] += dato.get(
                            "bytes_recibidos_inc", 0
                        )

                        velocidad_carga = dato.get("velocidad_carga", 0)
                        velocidad_descarga = dato.get("velocidad_descarga", 0)

                        if velocidad_carga > estadisticas["max_carga"]:
                            estadisticas["max_carga"] = velocidad_carga

                        if velocidad_descarga > estadisticas["max_descarga"]:
                            estadisticas["max_descarga"] = velocidad_descarga

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

                live.update(generar_layout(generar_tabla(datos)))
    except KeyboardInterrupt:
        console_manager.console.print()

        tiempo_total = time.time() - estadisticas["inicio"]
        
        console_manager.console.print(f"[bold {COLORS['primario']}]⟡ RESUMEN DE MONITOREO[/]")
        console_manager.console.print()
        
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Duración:[/] "
            f"[{COLORS['texto']}]{tiempo_total:.1f}s[/]"
        )
        
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Datos transferidos:[/] "
            f"[{COLORS['secundario']}]{estadisticas['total_enviado'] / 1024:.2f} MB[/] enviados, "
            f"[{COLORS['info']}]{estadisticas['total_recibido'] / 1024:.2f} MB[/] recibidos"
        )
        
        if estadisticas["dispositivo_max_trafico"]:
            console_manager.console.print(
                f"[{COLORS['secundario']}]•[/] "
                f"[bold {COLORS['texto']}]Mayor actividad:[/] "
                f"[{COLORS['texto']}]{estadisticas['dispositivo_max_trafico']}[/]"
            )