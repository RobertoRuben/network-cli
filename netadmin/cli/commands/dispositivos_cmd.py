import typer
from rich import box
from rich.table import Table
from rich.text import Text

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
    console_manager.mostrar_comando_ejecutado(f"dispositivos --cantidad {cantidad}")
    
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
        dispositivos = network_scanner.escanear_red(cantidad_max=cantidad)

    if not dispositivos:
        console_manager.mostrar_advertencia("No se encontraron dispositivos en la red.")
        return

    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ DISPOSITIVOS EN RED[/]")
    console_manager.console.print()

    activos = sum(1 for d in dispositivos if d["estado"] == "up")
    inactivos = len(dispositivos) - activos

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Total:[/] "
        f"[{COLORS['texto']}]{len(dispositivos)} dispositivos[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Estado:[/] "
        f"[{COLORS['texto']}]{activos} activos[/], "
        f"[{COLORS['texto_dim']}]{inactivos} inactivos[/]"
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
            estado_formateado,
        )

    console_manager.console.print(tabla)