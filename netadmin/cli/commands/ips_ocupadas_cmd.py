import typer
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor
from rich import box
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import NetworkScanner, obtener_mac_desde_ip
from netadmin.config.settings import COLORS


@app.command("ips-ocupadas", help="Listar las direcciones IP ocupadas en una red")
def comando(
    red: str = typer.Option(
        "",
        "--red",
        "-r",
        help="Dirección IP de red (ej: 192.168.1.0). Si no se especifica, se utiliza la red actual",
    ),
    mascara: str = typer.Option(
        "24", "--mascara", "-m", help="Máscara de red en formato CIDR (ej: 24 para /24)"
    ),
    timeout: float = typer.Option(
        0.5, "--timeout", "-t", help="Tiempo máximo de espera por IP (segundos)"
    ),
    num_workers: int = typer.Option(
        50, "--workers", "-w", help="Número de hilos paralelos para el escaneo"
    ),
    mostrar_inactivas: bool = typer.Option(
        False, "--inactivas", "-i", help="Mostrar también las IPs inactivas"
    ),
):
    scanner = NetworkScanner()

    if not red:
        ip_local = scanner.obtener_ip_local()
        red_base = scanner.obtener_red_desde_ip(ip_local)
        red = f"{red_base}.0"

    comando_str = f"ips-ocupadas --red {red} --mascara {mascara} --timeout {timeout} --workers {num_workers}"
    if mostrar_inactivas:
        comando_str += " --inactivas"
    console_manager.mostrar_comando_ejecutado(comando_str)
    
    console_manager.console.print()

    try:
        network = ipaddress.IPv4Network(f"{red}/{mascara}", strict=False)
    except ValueError as e:
        console_manager.mostrar_error(f"Red inválida: {red}/{mascara}", str(e))
        return

    direcciones = list(network.hosts())

    if network.prefixlen >= 31:
        direcciones = list(network.hosts())
        if not direcciones:  
            direcciones = [network.network_address]

    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ DIRECCIONES IP EN RED[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{network.network_address}/{network.prefixlen}[/]")
    console_manager.console.print()

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Escaneando:[/] "
        f"[{COLORS['texto']}]{len(direcciones)} direcciones[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Configuración:[/] "
        f"[{COLORS['texto']}]timeout: {timeout}s[/], "
        f"[{COLORS['texto']}]workers: {num_workers}[/]"
    )
    
    console_manager.console.print()

    def verificar_ip(ip):
        ip_str = str(ip)
        resultado, tiempo = scanner.ping_host(ip_str, timeout)
        hostname = ""
        mac = ""

        if resultado:
            try:
                hostname = socket.getfqdn(ip_str)
                if hostname == ip_str:
                    hostname = "Desconocido"
            except:
                hostname = "Desconocido"

            mac = obtener_mac_desde_ip(ip_str)

        return {
            "ip": ip_str,
            "activa": resultado,
            "tiempo": tiempo,
            "hostname": hostname,
            "mac": mac,
        }

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[{task.description}]"),
        BarColumn(complete_style=COLORS["secundario"]),
    )

    resultados = []
    with progress:
        tarea = progress.add_task(f"[{COLORS['secundario']}]Escaneando", total=len(direcciones))

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for i, resultado in enumerate(executor.map(verificar_ip, direcciones)):
                resultados.append(resultado)
                progress.update(tarea, advance=1)
                
    console_manager.console.print()
    
    ips_activas_filtradas = [r for r in resultados if r["activa"]]
    if not mostrar_inactivas:
        resultados_mostrados = ips_activas_filtradas
    else:
        resultados_mostrados = resultados

    if not ips_activas_filtradas:
        console_manager.mostrar_advertencia(
            f"No se encontraron IPs ocupadas en {network.network_address}/{network.prefixlen}."
        )
        return

    tabla = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style=f"bold {COLORS['primario']}",
        show_edge=False,
        padding=(0, 1),
    )
    
    tabla.add_column("IP", style=f"{COLORS['secundario']}")
    tabla.add_column("ESTADO", style=f"{COLORS['texto']}")
    tabla.add_column("TIEMPO", style=f"{COLORS['texto']}", justify="right")
    tabla.add_column("HOSTNAME", style=f"{COLORS['texto']}")
    tabla.add_column("MAC", style=f"{COLORS['texto_dim']}")

    for res in resultados_mostrados:
        estado_formateado = (
            f"[{COLORS['exito']}]activa[/]"
            if res["activa"]
            else f"[{COLORS['texto_dim']}]inactiva[/]"
        )
        
        tiempo = f"{res['tiempo']:.2f} ms" if res["activa"] else "-"
        hostname = res["hostname"] if res["hostname"] else "-"
        mac = res["mac"] if res["mac"] else "-"

        tabla.add_row(res["ip"], estado_formateado, tiempo, hostname, mac)

    dispositivos_activos = len(ips_activas_filtradas)
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Resultados:[/] "
        f"[{COLORS['texto']}]{dispositivos_activos} IPs activas[/] "
        f"[{COLORS['texto_dim']}]de {len(direcciones)} escaneadas[/]"
    )
    
    console_manager.console.print()
    
    console_manager.console.print(tabla)