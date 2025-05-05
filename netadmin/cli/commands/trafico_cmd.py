import typer
from rich import box
from rich.table import Table
from rich.text import Text

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
    console_manager.mostrar_comando_ejecutado(f"trafico --duracion {duracion}")

    with console_manager.console.status(
        f"[{COLORS['secundario']}]Recopilando datos de tráfico...",
        spinner=ANIMATION_STYLES["carga"],
    ):
        resultados = network_monitor.monitorear_trafico(duracion=duracion)

    if not resultados:
        console_manager.mostrar_advertencia(
            "No se detectó tráfico de red en las interfaces activas."
        )
        return

    console_manager.console.print()

    console_manager.console.print(
        f"[bold {COLORS['primario']}]⟡ TRÁFICO DE RED[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{duracion}s[/]"
    )
    console_manager.console.print()

    tabla = Table(
        box=box.SIMPLE_HEAD, 
        show_header=True,
        header_style=f"bold {COLORS['primario']}",
        show_edge=False,  
        padding=(0, 1),  
    )

    tabla.add_column("INTERFAZ", style=f"{COLORS['secundario']}")
    tabla.add_column("ENVIADO", style=f"{COLORS['texto']}", justify="right")
    tabla.add_column("RECIBIDO", style=f"{COLORS['texto']}", justify="right")
    tabla.add_column(
        "↑", style=f"{COLORS['secundario']}", justify="right"
    )  
    tabla.add_column(
        "↓", style=f"{COLORS['info']}", justify="right"
    ) 

    total_enviado = 0
    total_recibido = 0

    max_trafico = {"interfaz": "", "total": 0}

    for dato in resultados:
        bytes_enviados = dato["bytes_enviados"]
        bytes_recibidos = dato["bytes_recibidos"]
        velocidad_carga = dato["velocidad_carga"]
        velocidad_descarga = dato["velocidad_descarga"]

        total_trafico = bytes_enviados + bytes_recibidos
        if total_trafico > max_trafico["total"]:
            max_trafico = {"interfaz": dato["interfaz"], "total": total_trafico}

        total_enviado += bytes_enviados
        total_recibido += bytes_recibidos

        tabla.add_row(
            Text(dato["interfaz"], style=f"bold {COLORS['texto']}"),
            f"{bytes_enviados / 1024:.2f} KB",
            f"{bytes_recibidos / 1024:.2f} KB",
            f"{velocidad_carga:.2f} KB/s",
            f"{velocidad_descarga:.2f} KB/s",
        )

    tabla.add_row("", "", "", "", "")

    tabla.add_row(
        Text("TOTAL", style=f"bold {COLORS['primario']}"),
        Text(f"{total_enviado / 1024:.2f} KB", style=f"bold {COLORS['texto']}"),
        Text(f"{total_recibido / 1024:.2f} KB", style=f"bold {COLORS['texto']}"),
        "",
        "",
    )

    console_manager.console.print(tabla)
    console_manager.console.print()

    if resultados:
        trafico_total = max_trafico["total"] / 1024
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Mayor actividad:[/] "
            f"[{COLORS['texto']}]{max_trafico['interfaz']}[/] "
            f"[dim {COLORS['texto_dim']}]({trafico_total:.2f} KB)[/]"
        )
