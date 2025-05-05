"""
Módulo de comandos de NetAdmin CLI.

Este módulo contiene los comandos disponibles en la aplicación:
- dispositivos: Muestra dispositivos conectados en la red
- velocidad: Mide velocidad de conexión a Internet
- trafico: Monitorea el tráfico de red
- info: Muestra información básica de red
- ping: Comprueba conectividad con un host
- escanear: Escanea una red específica mostrando detalles de consumo
- activos: Muestra solo los dispositivos activos en una red específica
- monitor: Monitorea el tráfico en tiempo real por dispositivo
- puertos: Escanea puertos abiertos en un host específico
- servicios: Detecta servicios en ejecución en un host
- vulnerabilidades: Realiza un escaneo básico de vulnerabilidades
- estadisticas: Muestra estadísticas de red en tiempo real
- ips-ocupadas: Lista las direcciones IP ocupadas en una red
- ips-disponibles: Lista las direcciones IP disponibles en una red con información detallada
"""

from netadmin.cli.commands.dispositivos_cmd import comando as dispositivos_cmd
from netadmin.cli.commands.velocidad_cmd import comando as velocidad_cmd
from netadmin.cli.commands.trafico_cmd import comando as trafico_cmd
from netadmin.cli.commands.info_cmd import comando as info_cmd
from netadmin.cli.commands.ping_cmd import comando as ping_cmd
from netadmin.cli.commands.escanear_cmd import (
    comando as escanear_cmd,
    activos as activos_cmd,
)
from netadmin.cli.commands.trafico_tiempo_real_cmd import comando as monitor_cmd
from netadmin.cli.commands.puertos_cmd import comando as puertos_cmd
from netadmin.cli.commands.servicios_cmd import comando as servicios_cmd
from netadmin.cli.commands.vulnerabilidades_cmd import comando as vulnerabilidades_cmd
from netadmin.cli.commands.estadisticas_cmd import comando as estadisticas_cmd
from netadmin.cli.commands.ips_ocupadas_cmd import comando as ips_ocupadas_cmd
from netadmin.cli.commands.ips_disponibles_cmd import comando as ips_disponibles_cmd
