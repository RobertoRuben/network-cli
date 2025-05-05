APP_NAME = "NetAdmin CLI"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Herramienta para administración de red"

COLORS = {
    "primario": "#38b2ac",  # Teal moderno
    "secundario": "#4fd1c5",  # Teal claro
    "advertencia": "#f6ad55",  # Naranja pastel
    "error": "#fc8181",  # Coral suave
    "info": "#63b3ed",  # Azul cielo
    "exito": "#68d391",  # Verde menta
    "texto": "#f7fafc",  # Blanco muy suave
    "texto_dim": "#cbd5e0",  # Gris claro
    "fondo": "#1a202c",  # Gris azulado oscuro
    "acento": "#9f7aea",  # Púrpura pastel
}

NETWORK_CONFIG = {
    "timeout_ping": 1.0,  
    "timeout_scan": 5.0,  
    "default_scan_range": "0/24",  
}

SPEEDTEST_CONFIG = {
    "force_json": True,
    "include_ping": True,
    "servers": [], 
}

ANIMATION_STYLES = {
    "carga": "arc",  
    "progreso": "line",  
    "ping": "dots",  
    "scan": "point",  
}

DEFAULTS = {
    "dispositivos_max": 10,
    "trafico_duracion": 10,  
}

TABLE_STYLES = {
    "box": "SIMPLE",  
    "header_style": f"bold {COLORS['primario']}",
    "row_styles": ["", "dim"],  
}
