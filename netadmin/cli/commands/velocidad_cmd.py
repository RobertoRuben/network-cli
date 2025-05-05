import typer
from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import speed_tester
from netadmin.config.settings import COLORS


@app.command("velocidad", help="Medir la velocidad de conexión a Internet")
def comando():
    console_manager.mostrar_comando_ejecutado("velocidad")
    console_manager.console.print()

    with console_manager.console.status(
        f"[{COLORS['secundario']}]Realizando prueba de velocidad...", spinner="dots"
    ):
        resultados = speed_tester.realizar_prueba()
        
    if resultados["download"] == 0 and resultados["upload"] == 0:
        console_manager.mostrar_error("No se pudo completar la prueba de velocidad")
        return

    console_manager.console.print(
        f"[bold {COLORS['primario']}]⟡ RESULTADOS DE VELOCIDAD[/]"
    )
    console_manager.console.print()

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Descarga:[/] "
        f"[{COLORS['texto']}]{resultados['download']:.2f} Mbps[/]"
    )

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Carga:[/] "
        f"[{COLORS['texto']}]{resultados['upload']:.2f} Mbps[/]"
    )

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Ping:[/] "
        f"[{COLORS['texto']}]{resultados['ping']:.2f} ms[/]"
    )

    console_manager.console.print()

    calidad = (
        "excelente"
        if resultados["download"] > 100
        else (
            "buena"
            if resultados["download"] > 30
            else "aceptable" if resultados["download"] > 10 else "baja"
        )
    )

    color_calidad = (
        COLORS["exito"]
        if calidad in ["excelente", "buena"]
        else COLORS["advertencia"] if calidad == "aceptable" else COLORS["error"]
    )

    console_manager.console.print(
        f"[{color_calidad}]• Calidad de conexión: {calidad}[/]"
    )
