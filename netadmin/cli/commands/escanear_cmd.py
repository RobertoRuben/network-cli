import typer
from typing import Optional
from rich import box
from rich.table import Table
from rich.text import Text

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
from netadmin.config.settings import COLORS


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
    comando_str = f"escanear {ip}"
    if solo_activos:
        comando_str += " --activos"
    comando_str += f" --duracion {duracion}"
    console_manager.mostrar_comando_ejecutado(comando_str)
    
    console_manager.console.print()

    if NMAP_INFO["disponible"]:
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] [{COLORS['texto_dim']}]Usando Nmap {NMAP_INFO['version']}[/]"
        )
    else:
        console_manager.console.print(
            f"[{COLORS['advertencia']}]•[/] [{COLORS['texto_dim']}]{NMAP_INFO['mensaje']}[/]"
        )
    
    console_manager.console.print()

    with console_manager.console.status(
        f"[{COLORS['secundario']}]Escaneando la red...", spinner="dots"
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

    red_base = ip.rsplit('.', 1)[0]
    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ ESCANEO DE RED[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{red_base}.0/24[/]")
    console_manager.console.print()

    dispositivos_activos = sum(1 for d in dispositivos if d["estado"] == "up")
    dispositivos_inactivos = len(dispositivos) - dispositivos_activos
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Total:[/] "
        f"[{COLORS['texto']}]{len(dispositivos)} dispositivos[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Estado:[/] "
        f"[{COLORS['texto']}]{dispositivos_activos} activos[/], "
        f"[{COLORS['texto_dim']}]{dispositivos_inactivos} inactivos[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Monitoreo:[/] "
        f"[{COLORS['texto']}]{duracion}s[/]"
    )
    
    console_manager.console.print()

    tabla = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style=f"bold {COLORS['primario']}",
        show_edge=False,
        padding=(0, 1),
    )
    
    tabla.add_column("IP", style=f"{COLORS['secundario']}")
    tabla.add_column("NOMBRE", style=f"{COLORS['texto']}")
    tabla.add_column("MAC", style=f"{COLORS['texto_dim']}")
    tabla.add_column("↑", style=f"{COLORS['secundario']}", justify="right")
    tabla.add_column("↓", style=f"{COLORS['info']}", justify="right")
    tabla.add_column("ESTADO", style=f"{COLORS['texto']}")

    for dispositivo in dispositivos:
        estado = dispositivo["estado"]
        estado_formateado = (
            f"[{COLORS['exito']}]activo[/]"
            if estado == "up"
            else f"[{COLORS['texto_dim']}]inactivo[/]"
        )
            
        tabla.add_row(
            Text(dispositivo["ip"], style=f"bold {COLORS['texto']}"),
            dispositivo["nombre"],
            dispositivo["mac"],
            f"{dispositivo['velocidad_subida']:.2f} KB/s",
            f"{dispositivo['velocidad_descarga']:.2f} KB/s",
            estado_formateado,
        )

    console_manager.console.print(tabla)
    console_manager.console.print()

    if dispositivos_activos > 0:
        try:
            max_trafico = max(
                [d for d in dispositivos if d["estado"] == "up"],
                key=lambda x: x["velocidad_subida"] + x["velocidad_descarga"]
            )
            trafico_total = max_trafico["velocidad_subida"] + max_trafico["velocidad_descarga"]
            
            console_manager.console.print(
                f"[{COLORS['secundario']}]•[/] "
                f"[bold {COLORS['texto']}]Mayor actividad:[/] "
                f"[{COLORS['texto']}]{max_trafico['ip']}[/] "
                f"[dim {COLORS['texto_dim']}]({trafico_total:.2f} KB/s)[/]"
            )
        except Exception:
            pass


@app.command("activos", help="Mostrar solo dispositivos activos en una red")
def activos(
    ip: str = typer.Argument(
        ..., help="Dirección IP base para escanear (ej: 192.168.1.1)"
    ),
    duracion: int = typer.Option(
        3, "--duracion", "-d", help="Duración del monitoreo de tráfico en segundos"
    ),
):
    console_manager.mostrar_comando_ejecutado(f"activos {ip} --duracion {duracion}")

    comando(ip=ip, solo_activos=True, duracion=duracion)