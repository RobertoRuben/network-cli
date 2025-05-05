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
        """Muestra un título atractivo con bordes."""
        texto = Text(titulo, justify="center")
        if subtitulo:
            texto.append("\n")
            texto.append(subtitulo, style=f"italic {COLORS['info']}")
        
        self.console.print(Panel.fit(
            texto,
            style=f"bold {COLORS['primario']}"
        ))
    
    def mostrar_estado_nmap(self, info_nmap):
        """Muestra el estado de nmap con iconos visuales.
        
        Args:
            info_nmap: Diccionario con información de nmap
        """
        if info_nmap["disponible"]:
            self.console.print(f"[bold green]✓[/] Nmap disponible: {info_nmap['version']}")
        else:
            self.console.print(f"[bold {COLORS['advertencia']}]⚠[/] {info_nmap['mensaje']} Algunas funcionalidades estarán limitadas.")
    
    def mostrar_animacion_carga(self, mensaje, duracion=2, estilo=None):
        """Muestra una animación de carga con el mensaje especificado."""
        estilo = estilo or ANIMATION_STYLES["carga"]
        with self.console.status(f"[bold {COLORS['primario']}]{mensaje}...", spinner=estilo):
            time.sleep(duracion)
    
    def crear_tabla(self, titulo, columnas):
        """Crea una tabla con el estilo definido en la configuración."""
        tabla = Table(title=titulo, box=getattr(box, TABLE_STYLES["box"]))
        
        for columna in columnas:
            nombre = columna["nombre"]
            estilo = columna.get("estilo", TABLE_STYLES["header_style"])
            ancho = columna.get("ancho", None)
            alineacion = columna.get("alineacion", "left")
            no_wrap = columna.get("no_wrap", False)
            
            tabla.add_column(
                nombre, 
                style=estilo, 
                width=ancho, 
                justify=alineacion, 
                no_wrap=no_wrap
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
            TextColumn("[bold {color}]{{task.description}}".format(color=COLORS["primario"])),
            BarColumn(complete_style=COLORS["secundario"]),
            console=self.console,
            transient=True
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
        self.console.print(f"[bold {COLORS['error']}]Error:[/] {mensaje}")
        if detalle:
            self.console.print(f"[{COLORS['info']}]Detalle: {detalle}[/]")
    
    def mostrar_advertencia(self, mensaje):
        """Muestra un mensaje de advertencia formateado."""
        self.console.print(f"[bold {COLORS['advertencia']}]Advertencia:[/] {mensaje}")
    
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
            tabla = Table(title=titulo, box=getattr(box, TABLE_STYLES["box"]), show_header=False)
            tabla.add_column("Clave", style=f"bold {COLORS['primario']}")
            tabla.add_column("Valor", style=COLORS["secundario"])
            
            for clave, valor in datos.items():
                tabla.add_row(clave, str(valor))
                
            self.console.print(tabla)
        else:
            self.console.print(f"\n[bold {COLORS['primario']}]{titulo}[/]")
            for clave, valor in datos.items():
                self.console.print(f"  [bold]{clave}:[/] [{COLORS['secundario']}]{valor}[/]")

# Instancia global para uso en toda la aplicación
console_manager = ConsoleManager()