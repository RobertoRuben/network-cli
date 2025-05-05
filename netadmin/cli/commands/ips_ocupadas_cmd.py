#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para listar las IPs ocupadas en una red.
"""

import typer
import subprocess
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress
from rich.table import Table

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import NetworkScanner, obtener_mac_desde_ip
from netadmin.config.settings import COLORS, NETWORK_CONFIG


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
    """Escanea una red en busca de direcciones IP ocupadas y muestra el resultado.

    Ejemplo: netadmin ips-ocupadas --red 192.168.1.0 --mascara 24
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
        f"IPs Ocupadas en la Red",
        f"Red: {network.network_address}/{network.prefixlen} ({network.num_addresses} direcciones)",
    )

    # Obtener lista total de IPs (exceptuando red y broadcast)
    direcciones = list(network.hosts())

    # Si es una red /31 o /32, incluir todas las direcciones
    if network.prefixlen >= 31:
        direcciones = list(network.hosts())
        if not direcciones:  # Si aún está vacío (en caso de /32)
            direcciones = [network.network_address]

    console_manager.console.print(
        f"[bold]Escaneando[/] [cyan]{len(direcciones)}[/] direcciones IP...\n"
    )

    # Función para verificar si una IP está activa
    def verificar_ip(ip):
        ip_str = str(ip)
        resultado, tiempo = scanner.ping_host(ip_str, timeout)
        hostname = ""
        mac = ""

        if resultado:
            # Obtener nombre de host
            try:
                hostname = socket.getfqdn(ip_str)
                if hostname == ip_str:
                    hostname = "Desconocido"
            except:
                hostname = "Desconocido"

            # Obtener dirección MAC
            mac = obtener_mac_desde_ip(ip_str)

        return {
            "ip": ip_str,
            "activa": resultado,
            "tiempo": tiempo,
            "hostname": hostname,
            "mac": mac,
        }

    # Escanear IPs en paralelo con barra de progreso
    resultados = []
    with Progress() as progress:
        tarea = progress.add_task(
            "[cyan]Escaneando direcciones...", total=len(direcciones)
        )

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for i, resultado in enumerate(executor.map(verificar_ip, direcciones)):
                resultados.append(resultado)
                progress.update(tarea, advance=1)

    # Filtrar resultados si no se ha pedido mostrar inactivas
    if not mostrar_inactivas:
        resultados = [r for r in resultados if r["activa"]]

    # Crear tabla para mostrar resultados
    columnas = [
        {"nombre": "IP", "estilo": "cyan"},
        {"nombre": "Estado", "estilo": "green"},
        {"nombre": "Tiempo (ms)", "estilo": "yellow"},
        {"nombre": "Hostname", "estilo": "blue"},
        {"nombre": "Dirección MAC", "estilo": "magenta"},
    ]

    tabla = console_manager.crear_tabla(f"Resultados del escaneo de red", columnas)

    # Agregar filas a la tabla
    ips_activas = 0
    for res in resultados:
        estado = "[green]Activa[/]" if res["activa"] else "[red]Inactiva[/]"
        tiempo = f"{res['tiempo']:.2f}" if res["activa"] else "-"
        hostname = res["hostname"] if res["hostname"] else "-"
        mac = res["mac"] if res["mac"] else "-"

        if res["activa"]:
            ips_activas += 1

        tabla.add_row(res["ip"], estado, tiempo, hostname, mac)

    # Mostrar tabla con resultados
    console_manager.console.print()
    console_manager.console.print(tabla)

    # Mostrar resumen
    console_manager.console.print(
        f"\n[bold]Resumen:[/] {ips_activas} IPs activas de {len(direcciones)} direcciones escaneadas"
    )

    if ips_activas > 0:
        console_manager.mostrar_exito(
            f"{ips_activas} IPs ocupadas encontradas en la red {network.network_address}/{network.prefixlen}"
        )
    else:
        console_manager.mostrar_advertencia(
            f"No se encontraron IPs ocupadas en la red {network.network_address}/{network.prefixlen}"
        )
