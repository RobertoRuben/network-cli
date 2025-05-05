#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades de consola para la CLI de NetAdmin.
Encapsula la funcionalidad de visualización y animaciones.
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live

from netadmin.config.settings import COLORS, ANIMATION_STYLES, TABLE_STYLES


class ConsoleManager:
    """Gestor centralizado para la visualización en consola."""

    def __init__(self):
        """Inicializa el gestor de consola con una instancia de Rich Console."""
        self.console = Console()

    def mostrar_titulo(self, titulo, subtitulo=None):
        """Muestra un título con estilo moderno y minimalista con emojis."""
        # Estilo inspirado en CLIs modernas con emojis
        self.console.print()

        # Determinar emoji según el título
        emoji = "🌐"  # Emoji por defecto para red
        if "Velocidad" in titulo:
            emoji = "⚡"
        elif "Ping" in titulo:
            emoji = "📡"
        elif "Dispositivos" in titulo or "Activos" in titulo:
            emoji = "🖥️"
        elif "Puertos" in titulo:
            emoji = "🔌"
        elif "Tráfico" in titulo or "Monitor" in titulo:
            emoji = "📊"
        elif "Servicio" in titulo:
            emoji = "🔧"
        elif "Vulnerabilidades" in titulo:
            emoji = "🔒"
        elif "IP" in titulo:
            emoji = "📝"
        elif "Escanear" in titulo:
            emoji = "🔍"
        elif "Estadísticas" in titulo:
            emoji = "📈"

        # Verificar si estamos en el título principal de la aplicación
        if "NetAdmin CLI" in titulo:
            emoji = "🚀"
            # Título principal con emoji y formato moderno
            self.console.print(
                f"  [{COLORS['primario']}]┃[/] [bold white]{emoji} {titulo}[/]"
            )
        else:
            # Otros títulos con emoji correspondiente
            self.console.print(
                f"  [{COLORS['primario']}]┃[/] [bold white]{emoji} {titulo}[/]"
            )

        # Subtítulo con estilo tenue si existe
        if subtitulo:
            self.console.print(f"  [{COLORS['primario']}]┃[/] [dim]{subtitulo}[/]")

        # Separador minimalista
        self.console.print()

    def mostrar_estado_nmap(self, info_nmap):
        """Muestra el estado de nmap con iconos visuales."""
        if info_nmap["disponible"]:
            self.console.print(
                f"[bold {COLORS['exito']}]✓[/] Nmap disponible: {info_nmap['version']}"
            )
        else:
            self.console.print(
                f"[bold {COLORS['advertencia']}]⚠[/] {info_nmap['mensaje']} Algunas funcionalidades estarán limitadas."
            )

    def mostrar_animacion_carga(self, mensaje, duracion=2, estilo=None):
        """Muestra una animación de carga con el mensaje especificado."""
        estilo = estilo or ANIMATION_STYLES["carga"]
        with self.console.status(
            f"[bold {COLORS['primario']}]{mensaje}...", spinner=estilo
        ):
            time.sleep(duracion)

    def crear_tabla(self, titulo, columnas):
        """Crea una tabla con estilo moderno y minimalista."""
        # Usar SIMPLE como estilo de tabla para un aspecto más limpio y moderno
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
        """Crea una barra de progreso con animación para múltiples tareas.

        Args:
            tareas: Lista de diccionarios con la estructura:
                   {"descripcion": "Texto descriptivo", "total": 100}
                   Si total es None, será una tarea indeterminada.

        Returns:
            Objeto Progress y lista de IDs de tareas generadas.
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn(
                "[bold {color}]{{task.description}}".format(color=COLORS["primario"])
            ),
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
        """Muestra un mensaje de error formateado."""
        self.console.print(f"[bold {COLORS['error']}]✖[/] {mensaje}")
        if detalle:
            self.console.print(f"  [dim]{detalle}[/]")

    def mostrar_advertencia(self, mensaje):
        """Muestra un mensaje de advertencia formateado."""
        self.console.print(f"[bold {COLORS['advertencia']}]⚠[/] {mensaje}")

    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito formateado."""
        self.console.print(f"[bold {COLORS['exito']}]✓[/] {mensaje}")

    def datos_formateados(self, titulo, datos, estilo="grid"):
        """Muestra datos en formato clave-valor de manera atractiva.

        Args:
            titulo: Título de la sección de datos
            datos: Diccionario con datos clave-valor
            estilo: Estilo de visualización ("grid" o "lista")
        """
        if estilo == "grid":
            # Usar box.SIMPLE para mantener consistencia con el estilo moderno
            tabla = Table(
                title=titulo,
                box=box.SIMPLE,
                show_header=False,
                title_style=f"bold {COLORS['primario']}",
            )
            tabla.add_column("Clave", style=f"bold {COLORS['primario']}")
            tabla.add_column("Valor", style=COLORS["secundario"])

            for clave, valor in datos.items():
                tabla.add_row(clave, str(valor))

            self.console.print(tabla)
        else:
            # Estilo de lista con iconos modernos
            self.console.print(f"\n[bold {COLORS['primario']}]{titulo}[/]")
            for clave, valor in datos.items():
                self.console.print(
                    f"  [{COLORS['info']}]•[/] [bold]{clave}:[/] {valor}"
                )

    def mostrar_comando_ejecutado(self, comando):
        """Muestra el nombre del comando que se está ejecutando actualmente."""
        self.console.print(
            f"[bold {COLORS['primario']}]⟩[/] [bold]Ejecutando[/]: [bold white]{comando}[/]"
        )
        self.console.print()


# Instancia global para uso en toda la aplicación
console_manager = ConsoleManager()
