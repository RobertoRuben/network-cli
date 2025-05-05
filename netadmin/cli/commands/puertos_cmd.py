#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para escanear puertos abiertos en un host específico.
"""

import typer
from rich.progress import Progress
from rich import box

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
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
    """Escanea puertos abiertos en un host específico y muestra los resultados.

    Ejemplo: netadmin puertos 192.168.1.1 --rapido
    """
    # Construir string del comando ejecutado
    comando_str = f"puertos {host}"
    if rapido:
        comando_str += " --rapido"
    elif todos:
        comando_str += " --todos"
    else:
        comando_str += f" --inicio {inicio} --fin {fin}"
    console_manager.mostrar_comando_ejecutado(comando_str)

    # Ajustar los puertos según las opciones
    if todos:
        inicio = 1
        fin = 65535
        titulo_adicional = "Todos los puertos (1-65535)"
    elif rapido:
        puertos_comunes = [
            21,
            22,
            23,
            25,
            53,
            80,
            110,
            123,
            143,
            443,
            465,
            587,
            993,
            995,
            1433,
            1521,
            3306,
            3389,
            5432,
            5900,
            8080,
            8443,
        ]
        titulo_adicional = "Puertos comunes"
    else:
        titulo_adicional = f"Rango {inicio}-{fin}"

    # Verificar si nmap está disponible
    console_manager.mostrar_estado_nmap(NMAP_INFO)

    if not NMAP_INFO["disponible"]:
        console_manager.mostrar_error("Esta funcionalidad requiere nmap.")
        return

    try:
        import nmap

        scanner = nmap.PortScanner()

        # Preparar argumentos de escaneo
        if rapido:
            puertos = ",".join(str(puerto) for puerto in puertos_comunes)
            arguments = f"-sS -T4 -p {puertos}"
        else:
            arguments = f"-sS -p {inicio}-{fin}"

        # Realizar el escaneo con barra de progreso
        with console_manager.console.status(
            f"[bold {COLORS['primario']}]Escaneando puertos en {host} ({titulo_adicional})...",
            spinner=ANIMATION_STYLES["carga"],
        ):
            scanner.scan(hosts=host, arguments=arguments)

        # Verificar si el host se encontró en los resultados
        if host not in scanner.all_hosts():
            console_manager.mostrar_advertencia(f"No se pudo acceder al host {host}")
            return

        # Obtener información del host
        try:
            nombre_host = scanner[host].hostname()
        except:
            nombre_host = "Desconocido"

        # Crear tabla para los resultados
        columnas = [
            {"nombre": "Puerto", "estilo": "cyan"},
            {"nombre": "Estado", "estilo": "green"},
            {"nombre": "Servicio", "estilo": "yellow"},
            {"nombre": "Versión", "estilo": "magenta"},
        ]

        tabla = console_manager.crear_tabla(
            f"Puertos en {host} ({nombre_host})", columnas
        )

        # Contador de puertos abiertos
        puertos_abiertos = 0

        # Agregar información de puertos a la tabla
        for proto in scanner[host].all_protocols():
            puertos = sorted(scanner[host][proto].keys())

            for puerto in puertos:
                estado = scanner[host][proto][puerto]["state"]

                # Solo mostrar puertos abiertos o filtrados
                if estado not in ["open", "filtered"]:
                    continue

                puertos_abiertos += 1 if estado == "open" else 0

                # Estilo según estado
                estado_estilo = (
                    f"[green]abierto[/]"
                    if estado == "open"
                    else f"[{COLORS['advertencia']}]filtrado[/]"
                )

                # Obtener información del servicio
                servicio = scanner[host][proto][puerto].get("name", "desconocido")
                version = scanner[host][proto][puerto].get("product", "")
                if "version" in scanner[host][proto][puerto]:
                    version += f" {scanner[host][proto][puerto]['version']}"

                tabla.add_row(f"{puerto}/{proto}", estado_estilo, servicio, version)

        if puertos_abiertos == 0:
            console_manager.mostrar_advertencia(
                f"No se encontraron puertos abiertos en {host} ({titulo_adicional})"
            )
            return

        # Mostrar tabla con resultados
        console_manager.console.print(tabla)

        # Mostrar resumen conciso
        console_manager.mostrar_exito(
            f"Escaneo completado: {puertos_abiertos} puertos abiertos encontrados en {host}."
        )

    except Exception as e:
        console_manager.mostrar_error(f"Error al escanear puertos en {host}", str(e))
