#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para detectar servicios en ejecución en un host.
"""

import typer
from rich.panel import Panel

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
from netadmin.config.settings import COLORS, ANIMATION_STYLES


@app.command("servicios", help="Detectar servicios en ejecución en un host")
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host a escanear"),
    escaneo_profundo: bool = typer.Option(
        False, "--profundo", "-p", help="Realizar un escaneo más detallado de versiones"
    ),
):
    """Detecta servicios en ejecución en un host y muestra información detallada.

    Ejemplo: netadmin servicios 192.168.1.1 --profundo
    """
    # Mostrar comando que se está ejecutando
    comando_str = f"servicios {host}"
    if escaneo_profundo:
        comando_str += " --profundo"
    console_manager.mostrar_comando_ejecutado(comando_str)

    # Verificar si nmap está disponible
    console_manager.mostrar_estado_nmap(NMAP_INFO)

    if not NMAP_INFO["disponible"]:
        console_manager.mostrar_error("Esta funcionalidad requiere nmap.")
        return

    try:
        import nmap

        scanner = nmap.PortScanner()

        # Determinar los argumentos según el tipo de escaneo
        arguments = "-sV" if escaneo_profundo else "-sV --version-intensity 2"

        # Realizar el escaneo con animación
        with console_manager.console.status(
            f"[bold {COLORS['primario']}]Detectando servicios en {host}...",
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
            os_match = (
                scanner[host].get("osmatch", [{}])[0].get("name", "Desconocido")
                if "osmatch" in scanner[host]
                else "Desconocido"
            )
        except:
            nombre_host = "Desconocido"
            os_match = "Desconocido"

        # Mostrar información general del host (simplificado)
        console_manager.datos_formateados(
            "Información del Host",
            {
                "Nombre": nombre_host,
                "IP": host,
                "OS (estimado)": os_match,
                "Estado": scanner[host].state(),
            },
            estilo="lista"
        )

        # Crear tabla para los servicios detectados
        columnas = [
            {"nombre": "Puerto", "estilo": "cyan"},
            {"nombre": "Servicio", "estilo": "green"},
            {"nombre": "Versión", "estilo": "yellow"},
            {"nombre": "Detalles", "estilo": "magenta"},
        ]

        tabla = console_manager.crear_tabla("Servicios Detectados", columnas)

        # Contador de servicios encontrados
        servicios_encontrados = 0

        # Agregar servicios a la tabla
        for proto in scanner[host].all_protocols():
            puertos = sorted(scanner[host][proto].keys())

            for puerto in puertos:
                info = scanner[host][proto][puerto]
                estado = info["state"]

                # Solo mostrar puertos abiertos
                if estado != "open":
                    continue

                servicios_encontrados += 1

                # Obtener información del servicio
                nombre = info.get("name", "desconocido")
                producto = info.get("product", "")
                version = info.get("version", "")
                extra = info.get("extrainfo", "")

                # Formatear versión
                version_completa = f"{producto} {version}".strip()

                tabla.add_row(f"{puerto}/{proto}", nombre, version_completa, extra)

        if servicios_encontrados == 0:
            console_manager.mostrar_advertencia(
                f"No se encontraron servicios en ejecución en {host}"
            )
            return

        # Mostrar tabla con los servicios encontrados
        console_manager.console.print(tabla)

        # Mostrar resumen conciso
        console_manager.mostrar_exito(
            f"Detección completada: {servicios_encontrados} servicios encontrados en {host}."
        )

        # Mostrar información sobre servicios potencialmente vulnerables (simplificado)
        servicios_riesgosos = [
            "ftp", "telnet", "smtp", "dns", "http", "pop3", "smb",
            "microsoft-ds", "netbios-ssn", "ms-sql",
        ]
        servicios_encontrados_riesgosos = []

        for proto in scanner[host].all_protocols():
            for puerto in scanner[host][proto].keys():
                servicio = scanner[host][proto][puerto].get("name", "").lower()
                if (
                    servicio in servicios_riesgosos
                    and scanner[host][proto][puerto]["state"] == "open"
                ):
                    servicios_encontrados_riesgosos.append(
                        f"{servicio} ({puerto}/{proto})"
                    )

        if servicios_encontrados_riesgosos:
            console_manager.console.print(
                f"[{COLORS['advertencia']}]Servicios potencialmente vulnerables:[/] {', '.join(servicios_encontrados_riesgosos)}"
            )

    except Exception as e:
        console_manager.mostrar_error(f"Error al detectar servicios en {host}", str(e))
