"""
Módulo CLI de NetAdmin.

Este módulo contiene la interfaz de línea de comandos de la aplicación:
- Comandos y subcomandos
- Procesamiento de argumentos
- Manejo de la interacción con el usuario
"""

import typer
from netadmin.config import APP_NAME, APP_VERSION, APP_DESCRIPTION

# Inicializar la aplicación Typer
app = typer.Typer(name="netadmin", help=APP_DESCRIPTION, add_completion=False)

# Importar comandos para registrarlos en la aplicación
from netadmin.cli.commands import (
    dispositivos_cmd,
    velocidad_cmd,
    trafico_cmd,
    info_cmd,
    ping_cmd,
    escanear_cmd,
    activos_cmd,
    monitor_cmd,
    puertos_cmd,
    servicios_cmd,
    vulnerabilidades_cmd,
    estadisticas_cmd,
    ips_ocupadas_cmd,
    ips_disponibles_cmd,
)


# Función principal de entrada para la CLI
def main():
    """Punto de entrada principal para la aplicación CLI."""
    app()


# Si se ejecuta como programa principal
if __name__ == "__main__":
    main()
