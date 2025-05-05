import typer
from rich import box
from rich.table import Table

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import NMAP_INFO
from netadmin.config.settings import COLORS, ANIMATION_STYLES


@app.command("puertos", help="Escanear puertos abiertos en un host específico")
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host a escanear"),
    inicio: int = typer.Option(1, "--inicio", "-i", help="Puerto inicial para escaneo"),
    fin: int = typer.Option(1024, "--fin", "-f", help="Puerto final para escaneo"),
    rapido: bool = typer.Option(
        False, "--rapido", "-r", help="Realizar un escaneo rápido de puertos comunes"
    ),
    todos: bool = typer.Option(
        False, "--todos", "-t", help="Escanear todos los puertos (1-65535)"
    ),
):
    comando_str = f"puertos {host}"
    if rapido:
        comando_str += " --rapido"
    elif todos:
        comando_str += " --todos"
    else:
        comando_str += f" --inicio {inicio} --fin {fin}"
    console_manager.mostrar_comando_ejecutado(comando_str)
    
    console_manager.console.print()

    if todos:
        inicio = 1
        fin = 65535
        titulo_adicional = "Todos los puertos (1-65535)"
    elif rapido:
        puertos_comunes = [
            21, 22, 23, 25, 53, 80, 110, 123, 143, 443, 465, 587, 993, 995,
            1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443
        ]
        titulo_adicional = "Puertos comunes"
    else:
        titulo_adicional = f"Rango {inicio}-{fin}"

    if NMAP_INFO["disponible"]:
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] [{COLORS['texto_dim']}]Usando Nmap {NMAP_INFO['version']}[/]"
        )
    else:
        console_manager.console.print(
            f"[{COLORS['advertencia']}]•[/] [{COLORS['texto_dim']}]{NMAP_INFO['mensaje']}[/]"
        )
        console_manager.mostrar_error("Esta funcionalidad requiere nmap.")
        return
    
    console_manager.console.print()

    try:
        import nmap
        scanner = nmap.PortScanner()

        if rapido:
            puertos = ",".join(str(puerto) for puerto in puertos_comunes)
            arguments = f"-sS -T4 -p {puertos}"
        else:
            arguments = f"-sS -p {inicio}-{fin}"

        with console_manager.console.status(
            f"[{COLORS['secundario']}]Escaneando puertos en {host}...", spinner="dots"
        ):
            scanner.scan(hosts=host, arguments=arguments)

        if host not in scanner.all_hosts():
            console_manager.mostrar_advertencia(f"No se pudo acceder al host {host}")
            return

        try:
            nombre_host = scanner[host].hostname()
        except:
            nombre_host = "Desconocido"

        info_escaner = f"{host}" + (f" ({nombre_host})" if nombre_host != "Desconocido" else "")
        console_manager.console.print(f"[bold {COLORS['primario']}]⟡ PUERTOS ABIERTOS[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{info_escaner}[/]")
        console_manager.console.print()

        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Tipo:[/] "
            f"[{COLORS['texto']}]{titulo_adicional}[/]"
        )
        
        tabla = Table(
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style=f"bold {COLORS['primario']}",
            show_edge=False,
            padding=(0, 1),
        )
        
        tabla.add_column("PUERTO", style=f"{COLORS['secundario']}")
        tabla.add_column("SERVICIO", style=f"{COLORS['texto']}")
        tabla.add_column("ESTADO", style=f"{COLORS['texto']}")
        tabla.add_column("VERSIÓN", style=f"{COLORS['texto_dim']}")

        puertos_abiertos = 0
        puertos_filtrados = 0

        for proto in scanner[host].all_protocols():
            puertos = sorted(scanner[host][proto].keys())

            for puerto in puertos:
                estado = scanner[host][proto][puerto]["state"]

                if estado not in ["open", "filtered"]:
                    continue

                if estado == "open":
                    puertos_abiertos += 1
                else:
                    puertos_filtrados += 1

                estado_formateado = (
                    f"[{COLORS['exito']}]abierto[/]"
                    if estado == "open"
                    else f"[{COLORS['texto_dim']}]filtrado[/]"
                )

                servicio = scanner[host][proto][puerto].get("name", "")
                if not servicio:
                    servicio = "desconocido"
                
                version = scanner[host][proto][puerto].get("product", "")
                if "version" in scanner[host][proto][puerto]:
                    version += f" {scanner[host][proto][puerto]['version']}"

                tabla.add_row(
                    f"{puerto}/{proto}",
                    servicio,
                    estado_formateado,
                    version
                )

        console_manager.console.print()
        
        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Total:[/] "
            f"[{COLORS['texto']}]{puertos_abiertos} abiertos[/]"
            + (f", [{COLORS['texto_dim']}]{puertos_filtrados} filtrados[/]" if puertos_filtrados > 0 else "")
        )
        
        console_manager.console.print()

        if puertos_abiertos == 0:
            console_manager.mostrar_advertencia(
                f"No se encontraron puertos abiertos en {host} ({titulo_adicional})"
            )
            return

        console_manager.console.print(tabla)

    except Exception as e:
        console_manager.mostrar_error(f"Error al escanear puertos en {host}", str(e))