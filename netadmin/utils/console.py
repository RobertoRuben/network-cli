#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades de consola para la CLI de NetAdmin.
Encapsula la funcionalidad de visualización y animaciones.
"""

import time
import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

from netadmin.config.settings import COLORS, ANIMATION_STYLES, TABLE_STYLES


class ConsoleManager:
    def __init__(self):
        self.console = Console()
        self.terminal_width = shutil.get_terminal_size().columns

    def mostrar_titulo(self, titulo, subtitulo=None):
        self.console.print()

        # Calcular longitudes
        ancho_titulo = len(titulo)
        ancho_subtitulo = len(subtitulo) if subtitulo else 0
        ancho_contenido = max(ancho_titulo, ancho_subtitulo)

        padding = 10
        ancho_total = ancho_contenido + padding

        linea_superior = f"╭{'─' * ancho_total}╮"

        espacio_titulo = (ancho_total - ancho_titulo) // 2
        linea_titulo = f"│{' ' * espacio_titulo}{titulo}{' ' * (ancho_total - ancho_titulo - espacio_titulo)}│"

        if subtitulo:
            espacio_subtitulo = (ancho_total - ancho_subtitulo) // 2
            linea_subtitulo = f"│{' ' * espacio_subtitulo}{subtitulo}{' ' * (ancho_total - ancho_subtitulo - espacio_subtitulo)}│"

        linea_inferior = f"╰{'─' * ancho_total}╯"

        self.console.print(f"[bold {COLORS['primario']}]{linea_superior}[/]")
        self.console.print(f"[bold {COLORS['primario']}]{linea_titulo}[/]")

        if subtitulo:
            self.console.print(f"[bold {COLORS['primario']}]{linea_subtitulo}[/]")

        self.console.print(f"[bold {COLORS['primario']}]{linea_inferior}[/]")

        self.console.print()

    def mostrar_estado_nmap(self, info_nmap):
        if info_nmap["disponible"]:
            self.console.print(
                f"[bold {COLORS['exito']}]✓[/] Nmap disponible: {info_nmap['version']}"
            )
        else:
            self.console.print(
                f"[bold {COLORS['advertencia']}]⚠[/] {info_nmap['mensaje']} Algunas funcionalidades estarán limitadas."
            )

    def mostrar_animacion_carga(self, mensaje, duracion=2, estilo=None):
        estilo = estilo or ANIMATION_STYLES["carga"]
        with self.console.status(f"[{COLORS['texto']}]{mensaje}...[/]", spinner=estilo):
            time.sleep(duracion)

    def crear_tabla(self, titulo, columnas):
        tabla = Table(
            title=titulo, box=box.SIMPLE, title_style=f"bold {COLORS['primario']}"
        )

        for columna in columnas:
            nombre = columna["nombre"]
            estilo = columna.get("estilo", TABLE_STYLES["header_style"])
            ancho = columna.get("ancho", None)
            alineacion = columna.get("alineacion", "left")
            no_wrap = columna.get("no_wrap", False)

            tabla.add_column(
                nombre, style=estilo, width=ancho, justify=alineacion, no_wrap=no_wrap
            )

        return tabla

    def progreso_con_animacion(self, tareas):
        """Crea una barra de progreso con animación para múltiples tareas."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[{color}]{{task.description}}".format(color=COLORS["texto"])),
            BarColumn(complete_style=COLORS["secundario"]),
            console=self.console,
            transient=True,
        )

        task_ids = []
        for tarea in tareas:
            descripcion = tarea["descripcion"]
            total = tarea.get("total", None)
            task_id = progress.add_task(f"[{COLORS['info']}]{descripcion}", total=total)
            task_ids.append(task_id)

        return progress, task_ids

    def mostrar_error(self, mensaje, detalle=None):
        self.console.print(f"[bold {COLORS['error']}]●[/] {mensaje}")
        if detalle:
            self.console.print(f"  [dim {COLORS['texto_dim']}]{detalle}[/]")

    def mostrar_advertencia(self, mensaje):
        self.console.print(f"[bold {COLORS['advertencia']}]●[/] {mensaje}")

    def mostrar_exito(self, mensaje):
        self.console.print(f"[bold {COLORS['exito']}]●[/] {mensaje}")

    def datos_formateados(self, titulo, datos, estilo="grid"):
        if estilo == "grid":
            tabla = Table(
                title=titulo,
                box=box.SIMPLE,
                show_header=False,
                title_style=f"bold {COLORS['primario']}",
                padding=(0, 1),
            )
            tabla.add_column("Clave", style=f"bold {COLORS['texto']}")
            tabla.add_column("Valor", style=f"{COLORS['texto_dim']}")

            for clave, valor in datos.items():
                tabla.add_row(clave, str(valor))

            self.console.print(tabla)
        else:
            self.console.print(f"\n[bold {COLORS['primario']}]{titulo}[/]")
            for clave, valor in datos.items():
                self.console.print(
                    f"  [{COLORS['info']}]•[/] [bold {COLORS['texto']}]{clave}:[/] [{COLORS['texto_dim']}]{valor}[/]"
                )

    def mostrar_comando_ejecutado(self, comando):
        """Muestra el nombre del comando que se está ejecutando actualmente con estilo minimalista."""
        self.console.print()

        partes_comando = comando.split()
        nombre_comando = partes_comando[0] if partes_comando else ""
        argumentos = " ".join(partes_comando[1:]) if len(partes_comando) > 1 else ""

        self.console.print(
            f"[bold {COLORS['primario']}]❯[/] "
            f"[bold {COLORS['secundario']}]{nombre_comando}[/] "
            f"[{COLORS['texto_dim']}]{argumentos}[/]"
        )

console_manager = ConsoleManager()
