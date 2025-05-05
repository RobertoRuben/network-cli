#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comando para hacer ping a un host para comprobar conectividad.
"""

import typer
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from netadmin.cli import app
from netadmin.utils.console import console_manager
from netadmin.core.network import network_scanner
from netadmin.config.settings import COLORS, NETWORK_CONFIG

@app.command("ping", help="Hacer ping a un host para comprobar conectividad")
def comando(
    host: str = typer.Argument(..., help="Dirección IP o nombre del host"),
    repeticiones: int = typer.Option(4, help="Número de veces a realizar el ping")
):
    """Hace ping a un host para comprobar la conectividad."""
    console_manager.mostrar_titulo(
        "Ping a Host",
        f"Verificando conectividad con {host}"
    )
    
    resultados = []
    resultado_general = True
    tiempo_total = 0
    intentos_exitosos = 0
    
    # Realizar ping el número de veces indicado
    for i in range(1, repeticiones + 1):
        with console_manager.console.status(
            f"[bold {COLORS['primario']}]Haciendo ping a {host} ({i}/{repeticiones})...", 
            spinner="dots12"
        ):
            resultado, tiempo = network_scanner.ping_host(host)
            resultados.append((resultado, tiempo))
            
            # Actualizar estadísticas
            if resultado:
                tiempo_total += tiempo
                intentos_exitosos += 1
            else:
                resultado_general = False
    
    # Mostrar resultados detallados
    console_manager.console.print("\n[bold]Resultados del Ping:[/]")
    
    for i, (resultado, tiempo) in enumerate(resultados, 1):
        estado = "Exitoso" if resultado else "Fallido"
        color = COLORS["exito"] if resultado else COLORS["error"]
        tiempo_str = f"{tiempo:.2f} ms" if resultado else "N/A"
        
        console_manager.console.print(
            f"  Intento {i}: [{color}]{estado}[/] - Tiempo: {tiempo_str}"
        )
    
    # Mostrar resumen
    tiempo_promedio = tiempo_total / intentos_exitosos if intentos_exitosos > 0 else 0
    porcentaje_exito = (intentos_exitosos / repeticiones) * 100
    
    # Panel de resumen
    texto_resumen = Text()
    texto_resumen.append(f"Host: ", style="bold")
    texto_resumen.append(f"{host}\n")
    
    texto_resumen.append(f"Intentos: ", style="bold")
    texto_resumen.append(f"{repeticiones}\n")
    
    texto_resumen.append(f"Exitosos: ", style="bold")
    texto_resumen.append(f"{intentos_exitosos} ({porcentaje_exito:.1f}%)\n")
    
    texto_resumen.append(f"Tiempo promedio: ", style="bold")
    if tiempo_promedio > 0:
        texto_resumen.append(f"{tiempo_promedio:.2f} ms\n")
    else:
        texto_resumen.append("N/A\n")
    
    texto_resumen.append(f"Estado general: ", style="bold")
    if resultado_general:
        texto_resumen.append("Conectividad correcta", style=f"bold {COLORS['exito']}")
    else:
        if intentos_exitosos > 0:
            texto_resumen.append("Conectividad intermitente", style=f"bold {COLORS['advertencia']}")
        else:
            texto_resumen.append("Sin conectividad", style=f"bold {COLORS['error']}")
    
    console_manager.console.print("\n")
    console_manager.console.print(
        Panel(
            texto_resumen,
            title="Resumen de Ping",
            border_style=COLORS["primario"]
        )
    )
    
    if resultado_general:
        console_manager.mostrar_exito(f"Ping a {host} completado con éxito.")
    elif intentos_exitosos > 0:
        console_manager.mostrar_advertencia(f"Conectividad intermitente con {host}.")
    else:
        console_manager.mostrar_error(f"No se pudo conectar con {host}.")