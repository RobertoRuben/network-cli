#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para listar las IPs disponibles en una red con información detallada.
"""

import typer
import ipaddress
import socket
import subprocess
import platform
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from rich import box
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import NetworkScanner
from netadmin.config.settings import COLORS


@app.command(
    "ips-disponibles",
    help="Listar las direcciones IP disponibles en una red con información detallada",
)
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
        0.3, "--timeout", "-t", help="Tiempo máximo de espera por IP (segundos)"
    ),
    num_workers: int = typer.Option(
        50, "--workers", "-w", help="Número de hilos paralelos para el escaneo"
    ),
    limite: int = typer.Option(
        0, "--limite", "-l", help="Límite de IPs a mostrar (0 para mostrar todas)"
    ),
):
    scanner = NetworkScanner()

    if not red:
        ip_local = scanner.obtener_ip_local()
        red_base = scanner.obtener_red_desde_ip(ip_local)
        red = f"{red_base}.0"

    comando_str = f"ips-disponibles --red {red} --mascara {mascara} --timeout {timeout} --workers {num_workers}"
    if limite > 0:
        comando_str += f" --limite {limite}"
    console_manager.mostrar_comando_ejecutado(comando_str)
    
    console_manager.console.print()

    try:
        network = ipaddress.IPv4Network(f"{red}/{mascara}", strict=False)
    except ValueError as e:
        console_manager.mostrar_error(f"Red inválida: {red}/{mascara}", str(e))
        return

    info_red = obtener_informacion_red(network)
    
    console_manager.console.print(f"[bold {COLORS['primario']}]⟡ IPS DISPONIBLES EN RED[/] [dim {COLORS['texto_dim']}]•[/] [bold {COLORS['secundario']}]{network.network_address}/{network.prefixlen}[/]")
    console_manager.console.print()
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Red:[/] "
        f"[{COLORS['texto']}]{info_red['network_address']}{info_red['cidr']}[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Gateway:[/] "
        f"[{COLORS['texto']}]{info_red['gateway']}[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]DNS:[/] "
        f"[{COLORS['texto']}]{', '.join(info_red['dns_servers'])}[/]"
    )
    
    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Total IPs:[/] "
        f"[{COLORS['texto']}]{info_red['total_ips']}[/]"
    )
    
    console_manager.console.print()

    direcciones = list(network.hosts())

    if network.prefixlen >= 31:
        direcciones = list(network.hosts())
        if not direcciones:  # Si aún está vacío (en caso de /32)
            direcciones = [network.network_address]

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
        + (f", [{COLORS['texto']}]límite: {limite}[/]" if limite > 0 else "")
    )
    
    console_manager.console.print()

    def verificar_ip_disponible(ip):
        ip_str = str(ip)
        resultado, tiempo = scanner.ping_host(ip_str, timeout)

        esta_disponible = not resultado

        if esta_disponible:
            try:
                hostname = socket.getfqdn(ip_str)
                if hostname == ip_str:
                    hostname = ""
            except:
                hostname = ""

            return {"ip": ip_str, "disponible": esta_disponible, "hostname": hostname}
        return None

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[{task.description}]"),
        BarColumn(complete_style=COLORS["secundario"]),
    )

    ips_disponibles = []
    with progress:
        tarea = progress.add_task(f"[{COLORS['secundario']}]Escaneando", total=len(direcciones))

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for resultado in executor.map(verificar_ip_disponible, direcciones):
                if resultado:  
                    ips_disponibles.append(resultado)
                progress.update(tarea, advance=1)
    
    console_manager.console.print()

    ips_disponibles.sort(key=lambda x: [int(i) for i in x["ip"].split(".")])

    total_disponibles_encontradas = len(ips_disponibles)
    if limite > 0 and total_disponibles_encontradas > limite:
        ips_disponibles = ips_disponibles[:limite]
        nota_limite = f" (mostrando primeras {limite})"
    else:
        nota_limite = ""

    console_manager.console.print(
        f"[{COLORS['secundario']}]•[/] "
        f"[bold {COLORS['texto']}]Resultados:[/] "
        f"[{COLORS['texto']}]{total_disponibles_encontradas} IPs disponibles[/]"
        f"[{COLORS['texto_dim']}]{nota_limite}[/]"
    )
    
    console_manager.console.print()

    if not ips_disponibles:
        console_manager.mostrar_advertencia(
            f"No se encontraron IPs disponibles en {network.network_address}/{network.prefixlen}."
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
    tabla.add_column("HOSTNAME", style=f"{COLORS['texto_dim']}")

    for res in ips_disponibles:
        hostname = res["hostname"] if res["hostname"] else "-"

        tabla.add_row(
            res["ip"],
            f"[{COLORS['exito']}]disponible[/]",
            hostname,
        )

    console_manager.console.print(tabla)


def obtener_informacion_red(network):
    info = {
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "netmask": str(network.netmask),
        "cidr": f"/{network.prefixlen}",
        "total_ips": network.num_addresses,
        "gateway": "",
        "dns_servers": [],
    }

    if network.num_addresses > 2:
        gateway_candidates = [
            str(network.network_address + 1),  # Típicamente .1
            str(network.broadcast_address - 1),  # Típicamente .254
        ]
        for candidate in gateway_candidates:
            try:
                resultado, _ = NetworkScanner().ping_host(candidate, timeout=0.2)
                if resultado:
                    info["gateway"] = candidate
                    break
            except:
                pass

        if not info["gateway"]:
            info["gateway"] = gateway_candidates[0]
    else:
        info["gateway"] = str(network.network_address)

    info["dns_servers"] = obtener_dns_servers()

    return info


def obtener_dns_servers():
    dns_servers = []

    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["ipconfig", "/all"], universal_newlines=True
            )
            for line in output.split("\n"):
                if "DNS Servers" in line or "Servidores DNS" in line:
                    ip_part = line.split(":")[-1].strip()
                    if ip_part and ip_part not in ("", "None"):
                        dns_servers.append(ip_part)
        else:
            try:
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        if line.startswith("nameserver"):
                            ip = line.split()[1].strip()
                            dns_servers.append(ip)
            except:
                pass
    except:
        pass
    
    if not dns_servers:
        dns_servers = ["8.8.8.8", "8.8.4.4"]

    return dns_servers