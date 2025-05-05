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
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import NetworkScanner
from netadmin.config.settings import COLORS, NETWORK_CONFIG


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
    """Escanea una red en busca de direcciones IP disponibles y muestra información detallada.

    Ejemplo: netadmin ips-disponibles --red 192.168.1.0 --mascara 24
    """
    # Inicializar el escáner de red
    scanner = NetworkScanner()

    # Si no se especifica una red, obtener la red actual
    if not red:
        ip_local = scanner.obtener_ip_local()
        red_base = scanner.obtener_red_desde_ip(ip_local)
        red = f"{red_base}.0"

    # Crear el objeto de red con la máscara
    try:
        network = ipaddress.IPv4Network(f"{red}/{mascara}", strict=False)
    except ValueError as e:
        console_manager.mostrar_error(f"Red inválida: {red}/{mascara}", str(e))
        return

    # Mostrar título
    console_manager.mostrar_titulo(
        f"IPs Disponibles en la Red",
        f"Red: {network.network_address}/{network.prefixlen} ({network.num_addresses} direcciones)",
    )

    # Mostrar información de la red
    info_red = obtener_informacion_red(network)
    panel_info = Panel(
        f"[bold]Network Address:[/] {info_red['network_address']}\n"
        f"[bold]Broadcast Address:[/] {info_red['broadcast_address']}\n"
        f"[bold]Netmask:[/] {info_red['netmask']} ({info_red['cidr']})\n"
        f"[bold]Gateway (estimado):[/] {info_red['gateway']}\n"
        f"[bold]DNS Servers:[/] {', '.join(info_red['dns_servers'])}\n"
        f"[bold]Total IPs:[/] {info_red['total_ips']}\n",
        title="Información de la Red",
        border_style=COLORS["primario"],
    )
    console_manager.console.print(panel_info)

    # Obtener lista total de IPs (exceptuando red y broadcast)
    direcciones = list(network.hosts())

    # Si es una red /31 o /32, incluir todas las direcciones
    if network.prefixlen >= 31:
        direcciones = list(network.hosts())
        if not direcciones:  # Si aún está vacío (en caso de /32)
            direcciones = [network.network_address]

    console_manager.console.print(
        f"[bold]Escaneando[/] [cyan]{len(direcciones)}[/] direcciones IP en busca de IPs disponibles...\n"
    )

    # Función para verificar si una IP está disponible (inactiva)
    def verificar_ip_disponible(ip):
        ip_str = str(ip)
        resultado, tiempo = scanner.ping_host(ip_str, timeout)

        # Si hay respuesta, la IP está ocupada (no disponible)
        esta_disponible = not resultado

        if esta_disponible:
            try:
                # Intentar obtener información DNS inversa
                hostname = socket.getfqdn(ip_str)
                if hostname == ip_str:
                    hostname = ""
            except:
                hostname = ""

            return {"ip": ip_str, "disponible": esta_disponible, "hostname": hostname}
        return None

    # Escanear IPs en paralelo con barra de progreso
    ips_disponibles = []
    with Progress() as progress:
        tarea = progress.add_task(
            "[cyan]Verificando IPs disponibles...", total=len(direcciones)
        )

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for resultado in executor.map(verificar_ip_disponible, direcciones):
                if resultado:  # Solo considerar las IPs disponibles
                    ips_disponibles.append(resultado)
                progress.update(tarea, advance=1)

    # Ordenar por IP
    ips_disponibles.sort(key=lambda x: [int(i) for i in x["ip"].split(".")])

    # Limitar la cantidad si se ha especificado un límite
    if limite > 0 and len(ips_disponibles) > limite:
        ips_disponibles = ips_disponibles[:limite]
        console_manager.console.print(
            f"\n[italic]Mostrando las primeras {limite} IPs disponibles de un total de {len(ips_disponibles)}...[/]"
        )

    # Crear tabla para mostrar resultados
    columnas = [
        {"nombre": "IP", "estilo": "cyan"},
        {"nombre": "Estado", "estilo": "green"},
        {"nombre": "Hostname", "estilo": "blue"},
        {"nombre": "Máscara", "estilo": "yellow"},
        {"nombre": "Gateway", "estilo": "magenta"},
        {"nombre": "DNS", "estilo": "red"},
    ]

    tabla = console_manager.crear_tabla(f"IPs Disponibles en la Red", columnas)

    # Agregar filas a la tabla
    for res in ips_disponibles:
        hostname = res["hostname"] if res["hostname"] else "-"

        tabla.add_row(
            res["ip"],
            "[green]Disponible[/]",
            hostname,
            str(info_red["netmask"]),
            info_red["gateway"],
            info_red["dns_servers"][0] if info_red["dns_servers"] else "-",
        )

    # Mostrar tabla con resultados
    console_manager.console.print()
    console_manager.console.print(tabla)

    # Mostrar resumen
    console_manager.console.print(
        f"\n[bold]Resumen:[/] {len(ips_disponibles)} IPs disponibles de {len(direcciones)} direcciones escaneadas"
    )

    if len(ips_disponibles) > 0:
        console_manager.mostrar_exito(
            f"{len(ips_disponibles)} IPs disponibles encontradas en la red {network.network_address}/{network.prefixlen}"
        )
    else:
        console_manager.mostrar_advertencia(
            f"No se encontraron IPs disponibles en la red {network.network_address}/{network.prefixlen}"
        )


def obtener_informacion_red(network):
    """Obtiene información detallada sobre la red.

    Args:
        network: Objeto de red de ipaddress

    Returns:
        Dict con información de la red
    """
    # Información básica de la red
    info = {
        "network_address": str(network.network_address),
        "broadcast_address": str(network.broadcast_address),
        "netmask": str(network.netmask),
        "cidr": f"/{network.prefixlen}",
        "total_ips": network.num_addresses,
        "gateway": "",
        "dns_servers": [],
    }

    # Estimar el gateway (normalmente .1 o .254)
    if network.num_addresses > 2:
        gateway_candidates = [
            str(network.network_address + 1),  # Típicamente .1
            str(network.broadcast_address - 1),  # Típicamente .254
        ]
        for candidate in gateway_candidates:
            # Verificar si el gateway responde
            try:
                resultado, _ = NetworkScanner().ping_host(candidate, timeout=0.2)
                if resultado:
                    info["gateway"] = candidate
                    break
            except:
                pass

        # Si no responde ninguno, asumir .1
        if not info["gateway"]:
            info["gateway"] = gateway_candidates[0]
    else:
        info["gateway"] = str(network.network_address)

    # Obtener servidores DNS
    info["dns_servers"] = obtener_dns_servers()

    return info


def obtener_dns_servers():
    """Obtiene la lista de servidores DNS configurados en el sistema.

    Returns:
        Lista de IPs de servidores DNS
    """
    dns_servers = []

    # Intentar obtener servidores DNS del sistema
    try:
        if platform.system() == "Windows":
            # En Windows, usar el comando ipconfig /all
            output = subprocess.check_output(
                ["ipconfig", "/all"], universal_newlines=True
            )
            for line in output.split("\n"):
                if "DNS Servers" in line or "Servidores DNS" in line:
                    # Extraer la IP del servidor DNS
                    ip_part = line.split(":")[-1].strip()
                    if ip_part and ip_part not in ("", "None"):
                        dns_servers.append(ip_part)
        else:
            # En Linux/Mac, leer /etc/resolv.conf
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

    # Si no se encontró ninguno, usar los DNS públicos de Google como respaldo
    if not dns_servers:
        dns_servers = ["8.8.8.8", "8.8.4.4"]

    return dns_servers
