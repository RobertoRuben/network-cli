import typer
from rich import box
from rich.table import Table

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner
from netadmin.config.settings import COLORS


@app.command("ping", help="Hacer ping a un host para comprobar conectividad")
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host"),
    repeticiones: int = typer.Option(4, help="Número de veces a realizar el ping"),
):
    console_manager.mostrar_comando_ejecutado(f"ping {host} --repeticiones {repeticiones}")
    
    console_manager.console.print()

    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ RESULTADOS DE PING[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{host}[/]")
    console_manager.console.print()

    tabla = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style=f"bold {COLORS['primario']}",
        show_edge=False,
        padding=(0, 1),
    )
    
    tabla.add_column("INTENTO", style=f"{COLORS['secundario']}", justify="center")
    tabla.add_column("ESTADO", style=f"{COLORS['texto']}")
    tabla.add_column("TIEMPO", style=f"{COLORS['texto']}", justify="right")

    resultados = []
    resultado_general = True
    tiempo_total = 0
    intentos_exitosos = 0

    for i in range(1, repeticiones + 1):
        with console_manager.console.status(
            f"[{COLORS['secundario']}]Ping {i}/{repeticiones}...", spinner="dots"
        ):
            resultado, tiempo = network_scanner.ping_host(host)
            resultados.append((resultado, tiempo))

            if resultado:
                tiempo_total += tiempo
                intentos_exitosos += 1
            else:
                resultado_general = False
                
            estado = f"[{COLORS['exito']}]OK[/]" if resultado else f"[{COLORS['error']}]FAIL[/]"
            tiempo_str = f"{tiempo:.2f} ms" if resultado else "-"
            
            tabla.add_row(
                f"{i}",
                estado,
                tiempo_str
            )

    console_manager.console.print(tabla)
    console_manager.console.print()

    tiempo_promedio = tiempo_total / intentos_exitosos if intentos_exitosos > 0 else 0
    porcentaje_exito = (intentos_exitosos / repeticiones) * 100

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Paquetes:[/] "
        f"[{COLORS['texto']}]{intentos_exitosos} recibidos[/], "
        f"[{COLORS['texto_dim']}]{repeticiones - intentos_exitosos} perdidos[/], "
        f"[{COLORS['texto']}]{porcentaje_exito:.1f}% completado[/]"
    )
    
    if intentos_exitosos > 0:
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Tiempo promedio:[/] "
            f"[{COLORS['texto']}]{tiempo_promedio:.2f} ms[/]"
        )
    
    estado_texto = (
        "Conectividad correcta"
        if resultado_general
        else ("Conectividad intermitente" if intentos_exitosos > 0 else "Sin conectividad")
    )
    
    estado_color = (
        COLORS['exito']
        if resultado_general
        else (COLORS['advertencia'] if intentos_exitosos > 0 else COLORS['error'])
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Estado:[/] "
        f"[{estado_color}]{estado_texto}[/]"
    )