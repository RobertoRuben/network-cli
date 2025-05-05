#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de entrada para la herramienta NetAdmin CLI.
"""

from netadmin.utils.console import console_manager
from netadmin.cli import app
from netadmin.config import APP_NAME, APP_VERSION

def main():
    """Punto de entrada principal para la aplicación NetAdmin CLI."""
    try:
        # Mostrar bienvenida
        console_manager.mostrar_titulo(
            f"{APP_NAME} v{APP_VERSION}",
            "Herramienta de administración de red con animaciones"
        )
        
        # Ejecutar la aplicación
        app()
        
    except KeyboardInterrupt:
        console_manager.console.print("\n[bold yellow]Operación cancelada por el usuario.[/]")
    except Exception as e:
        console_manager.mostrar_error(f"Error inesperado: {str(e)}")
        raise

if __name__ == "__main__":
    main()