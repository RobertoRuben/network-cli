from rich import box
from rich.table import Table

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_monitor
from netadmin.config.settings import COLORS


@app.command("info", help="Mostrar información básica de red")
def comando():
    console_manager.mostrar_comando_ejecutado("info")
    
    console_manager.console.print()

    with console_manager.console.status(
        f"[{COLORS['secundario']}]Obteniendo información de red...", spinner="dots"
    ):
        info_red = network_monitor.obtener_info_red()

    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ INFORMACIÓN DE RED[/]")
    console_manager.console.print()

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]IP Local:[/] "
        f"[{COLORS['texto']}]{info_red['ip_local']}[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Equipo:[/] "
        f"[{COLORS['texto']}]{info_red['hostname']}[/]"
    )
    
    interfaces_activas = sum(1 for i in info_red["interfaces"] if i["activa"])
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Interfaces:[/] "
        f"[{COLORS['texto']}]{interfaces_activas} activas[/] "
        f"[{COLORS['texto_dim']}](de {len(info_red['interfaces'])})[/]"
    )
    
    console_manager.console.print()

    tabla = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style=f"bold {COLORS['primario']}",
        show_edge=False,
        padding=(0, 1),
    )
    
    tabla.add_column("NOMBRE", style=f"{COLORS['secundario']}")
    tabla.add_column("IP", style=f"{COLORS['texto']}")
    tabla.add_column("MAC", style=f"{COLORS['texto_dim']}")
    tabla.add_column("ESTADO", style=f"{COLORS['texto']}")

    for interfaz in info_red["interfaces"]:
        estado = (
            f"[{COLORS['exito']}]activa[/]"
            if interfaz["activa"]
            else f"[{COLORS['texto_dim']}]inactiva[/]"
        )
        
        tabla.add_row(
            interfaz["nombre"],
            interfaz["ipv4"],
            interfaz["mac"],
            estado
        )

    console_manager.console.print(tabla)