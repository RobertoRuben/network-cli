#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para realizar un escaneo básico de vulnerabilidades en un host.
"""

import typer
from datetime import datetime
import json
import os

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner, NMAP_INFO
from netadmin.config.settings import COLORS, ANIMATION_STYLES


@app.command(
    "vulnerabilidades", help="Realizar un escaneo básico de vulnerabilidades en un host"
)
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host a escanear"),
    intensidad: int = typer.Option(
        3,
        "--intensidad",
        "-i",
        help="Nivel de intensidad del escaneo (1-5, donde 5 es el más agresivo)",
    ),
    guardar: bool = typer.Option(
        False, "--guardar", "-g", help="Guardar resultados en un archivo"
    ),
):
    """Realiza un escaneo básico de vulnerabilidades en un host y muestra los resultados.

    Ejemplo: netadmin vulnerabilidades 192.168.1.1 --intensidad 4
    """
    # Mostrar comando que se está ejecutando
    comando_str = f"vulnerabilidades {host} --intensidad {intensidad}"
    if guardar:
        comando_str += " --guardar"
    console_manager.mostrar_comando_ejecutado(comando_str)

    # Validar la intensidad del escaneo
    if intensidad < 1 or intensidad > 5:
        console_manager.mostrar_error("El nivel de intensidad debe estar entre 1 y 5")
        return

    # Verificar si nmap está disponible
    console_manager.mostrar_estado_nmap(NMAP_INFO)

    if not NMAP_INFO["disponible"]:
        console_manager.mostrar_error("Esta funcionalidad requiere nmap.")
        return

    # Advertencia sobre privilegios y permisos (más concisa)
    console_manager.console.print(
        f"[{COLORS['advertencia']}]Nota:[/] Escaneo puede requerir permisos y ser detectado."
    )

    try:
        import nmap

        scanner = nmap.PortScanner()

        # Configurar los scripts de Nmap según la intensidad
        if intensidad == 1:
            scripts = "auth,default,discovery,version"
        elif intensidad == 2:
            scripts = "auth,default,discovery,version,safe"
        elif intensidad == 3:
            scripts = "auth,default,discovery,version,safe,vuln"
        elif intensidad == 4:
            scripts = "auth,default,discovery,version,safe,vuln,exploit"
        else:  # intensidad == 5
            scripts = "auth,default,discovery,version,safe,vuln,exploit,intrusive"

        arguments = f"-sV -sC --script={scripts}"

        # Realizar el escaneo con animación
        with console_manager.console.status(
            f"[bold {COLORS['primario']}]Analizando vulnerabilidades (Intensidad {intensidad}/5) en {host}...",
            spinner=ANIMATION_STYLES["carga"],
        ):
            scanner.scan(hosts=host, arguments=arguments)

        # Verificar si el host se encontró en los resultados
        if host not in scanner.all_hosts():
            console_manager.mostrar_advertencia(f"No se pudo acceder al host {host}")
            return

        # Crear tabla para los resultados
        columnas = [
            {"nombre": "Puerto/Servicio", "estilo": "cyan"},
            {"nombre": "Vulnerabilidad", "estilo": "yellow"},
            {"nombre": "Severidad", "estilo": "magenta"},
            {"nombre": "Detalles", "estilo": "green"},
        ]

        tabla = console_manager.crear_tabla(
            f"Vulnerabilidades Detectadas en {host}", columnas
        )

        # Contador de vulnerabilidades encontradas
        vuln_encontradas = 0
        vulnerabilidades = []

        # Extraer información de vulnerabilidades de los resultados del escaneo
        for proto in scanner[host].all_protocols():
            puertos = scanner[host][proto].keys()

            for puerto in puertos:
                info_puerto = scanner[host][proto][puerto]

                # Buscar scripts relacionados con vulnerabilidades
                if 'script' in info_puerto:
                    for script_name, data in info_puerto['script'].items():
                        vuln_encontradas += 1

                        # Analizar severidad basada en palabras clave
                        severidad = "Baja"
                        detalles = str(data)

                        # Palabras clave para determinar la severidad
                        if any(kw in detalles.lower() for kw in ["critical", "crítico", "remote code execution", "rce"]):
                            severidad = "[bold red]Crítica[/]"
                        elif any(kw in detalles.lower() for kw in ["high", "alta", "bypass", "overflow"]):
                            severidad = "[bold orange]Alta[/]"
                        elif any(kw in detalles.lower() for kw in ["medium", "media", "information disclosure"]):
                            severidad = "[yellow]Media[/]"

                        # Agregar a la tabla
                        servicio = info_puerto.get("name", "desconocido")
                        tabla.add_row(
                            f"{puerto}/{proto} ({servicio})",
                            script_name,
                            severidad,
                            detalles[:100] + "..." if len(detalles) > 100 else detalles,
                        )

                        # Guardar para el reporte
                        vulnerabilidades.append(
                            {
                                "puerto": puerto,
                                "protocolo": proto,
                                "servicio": servicio,
                                "vulnerabilidad": script_name,
                                "severidad": severidad.replace("[bold red]", "")
                                .replace("[bold orange]", "")
                                .replace("[yellow]", "")
                                .replace("[/]", ""),
                                "detalles": detalles,
                            }
                        )

        if vuln_encontradas == 0:
            console_manager.mostrar_exito(
                f"Análisis completado: No se detectaron vulnerabilidades en {host}"
            )
        else:
            # Mostrar tabla con las vulnerabilidades encontradas
            console_manager.console.print(tabla)

            # Mostrar resumen conciso
            console_manager.mostrar_exito(
                f"Análisis completado: {vuln_encontradas} vulnerabilidades potenciales detectadas en {host}."
            )

            # Mostrar recomendaciones concisas
            console_manager.console.print(
                f"[{COLORS['info']}]Recomendaciones:[/] Actualizar servicios, aplicar parches, revisar configuración."
            )

            # Si se solicita guardar el reporte
            if guardar and vulnerabilidades:
                fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
                directorio = "reportes"

                # Crear directorio si no existe
                if not os.path.exists(directorio):
                    os.makedirs(directorio)

                # Crear el nombre del archivo
                nombre_archivo = f"{directorio}/vulnerabilidades_{host.replace('.', '_')}_{fecha_actual}.json"

                # Crear el informe
                reporte = {
                    "host": host,
                    "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "intensidad_escaneo": intensidad,
                    "total_vulnerabilidades": vuln_encontradas,
                    "vulnerabilidades": vulnerabilidades,
                }

                # Guardar el informe
                try:
                    with open(nombre_archivo, "w", encoding="utf-8") as f:
                        json.dump(reporte, f, indent=4, ensure_ascii=False)
                    console_manager.mostrar_exito(
                        f"Reporte guardado en: {nombre_archivo}"
                    )
                except Exception as e:
                    console_manager.mostrar_error(
                        f"Error al guardar el reporte: {str(e)}"
                    )

    except Exception as e:
        console_manager.mostrar_error(
            f"Error al analizar vulnerabilidades en {host}", str(e)
        )
