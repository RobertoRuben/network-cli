"""
Módulo core de NetAdmin CLI.

Este módulo contiene la funcionalidad principal de la aplicación:
- Escaneo de red
- Pruebas de velocidad
- Monitoreo de tráfico
- Informes y estadísticas
"""

from netadmin.core.network import (
    NetworkScanner, 
    SpeedTester, 
    NetworkMonitor,
    network_scanner,
    speed_tester,
    network_monitor
)