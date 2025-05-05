import typer
from rich import box
from rich.table import Table
from rich.text import Text

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
from netadmin.config.settings import COLORS


@app.command("servicios", help="Detectar servicios en ejecución en un host")
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host a escanear"),
    escaneo_profundo: bool = typer.Option(
        False, "--profundo", "-p", help="Realizar un escaneo más detallado de versiones"
    ),
):
    comando_str = f"servicios {host}"
    if escaneo_profundo:
        comando_str += " --profundo"
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
        console_manager.mostrar_error("Esta funcionalidad requiere nmap.")
        return

    console_manager.console.print()

    try:
        import nmap

        scanner = nmap.PortScanner()

        arguments = "-sV" if escaneo_profundo else "-sV --version-intensity 2"

        with console_manager.console.status(
            f"[{COLORS['secundario']}]Detectando servicios en {host}...", spinner="dots"
        ):
            scanner.scan(hosts=host, arguments=arguments)

        if host not in scanner.all_hosts():
            console_manager.mostrar_advertencia(f"No se pudo acceder al host {host}")
            return
        try:
            nombre_host = scanner[host].hostname()
            os_match = (
                scanner[host].get("osmatch", [{}])[0].get("name", "Desconocido")
                if "osmatch" in scanner[host]
                else "Desconocido"
            )
        except:
            nombre_host = "Desconocido"
            os_match = "Desconocido"

        console_manager.console.print(
            f"[bold {COLORS['primario']}]⟡ SERVICIOS EN HOST[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{host}[/]"
        )
        console_manager.console.print()

        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Host:[/] "
            f"[{COLORS['texto']}]{host}[/]"
            + (
                f" [{COLORS['texto_dim']}]({nombre_host})[/]"
                if nombre_host != "Desconocido"
                else ""
            )
        )

        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Estado:[/] "
            f"[{COLORS['texto']}]{scanner[host].state()}[/]"
        )

        if os_match != "Desconocido":
            console_manager.console.print(
                f"[{COLORS['secundario']}]•[/] "
                f"[bold {COLORS['texto']}]OS (estimado):[/] "
                f"[{COLORS['texto']}]{os_match}[/]"
            )

        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Tipo escaneo:[/] "
            f"[{COLORS['texto']}]{'Profundo' if escaneo_profundo else 'Estándar'}[/]"
        )

        console_manager.console.print()

        tabla = Table(
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style=f"bold {COLORS['primario']}",
            show_edge=False,
            padding=(0, 1),
        )

        tabla.add_column("PUERTO", style=f"{COLORS['secundario']}")
        tabla.add_column("SERVICIO", style=f"{COLORS['texto']}")
        tabla.add_column("VERSIÓN", style=f"{COLORS['texto']}")
        tabla.add_column("DETALLES", style=f"{COLORS['texto_dim']}")

        servicios_encontrados = 0
        puertos_abiertos = []
        servicios_riesgosos = {
            "ftp": [],
            "telnet": [],
            "smtp": [],
            "dns": [],
            "http": [],
            "pop3": [],
            "smb": [],
            "microsoft-ds": [],
            "netbios-ssn": [],
            "ms-sql": [],
        }

        for proto in scanner[host].all_protocols():
            puertos = sorted(scanner[host][proto].keys())

            for puerto in puertos:
                info = scanner[host][proto][puerto]
                estado = info["state"]

                if estado != "open":
                    continue

                servicios_encontrados += 1
                puertos_abiertos.append(f"{puerto}/{proto}")

                nombre = info.get("name", "desconocido")
                producto = info.get("product", "")
                version = info.get("version", "")
                extra = info.get("extrainfo", "")

                version_completa = f"{producto} {version}".strip()

                if nombre in servicios_riesgosos:
                    servicios_riesgosos[nombre].append(f"{puerto}/{proto}")

                tabla.add_row(
                    f"{puerto}/{proto}",
                    Text(nombre, style="bold"),
                    version_completa,
                    extra,
                )

        if servicios_encontrados == 0:
            console_manager.mostrar_advertencia(
                f"No se encontraron servicios en ejecución en {host}"
            )
            return

        console_manager.console.print(
            f"[{COLORS['secundario']}]•[/] "
            f"[bold {COLORS['texto']}]Servicios:[/] "
            f"[{COLORS['texto']}]{servicios_encontrados} encontrados[/]"
        )

        console_manager.console.print()

        console_manager.console.print(tabla)
        console_manager.console.print()

        servicios_encontrados_riesgosos = []
        for servicio, puertos in servicios_riesgosos.items():
            if puertos:
                servicios_encontrados_riesgosos.append(
                    f"{servicio} ({', '.join(puertos)})"
                )

        if servicios_encontrados_riesgosos:
            console_manager.console.print(
                f"[bold {COLORS['advertencia']}]⚠ SERVICIOS POTENCIALMENTE VULNERABLES[/]"
            )
            console_manager.console.print()

            for servicio in servicios_encontrados_riesgosos:
                console_manager.console.print(
                    f"[{COLORS['advertencia']}]•[/] [{COLORS['texto']}]{servicio}[/]"
                )

    except Exception as e:
        console_manager.mostrar_error(f"Error al detectar servicios en {host}", str(e))
