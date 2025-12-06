"""
config.py
Configuración centralizada del Portal Cautivo
"""

# =========================================================
# CUENTAS VÁLIDAS (usuario -> contraseña)
# =========================================================
CUENTAS_VALIDAS = {
    "admin": "123456",
    "user1": "pass1",
    "usuario": "password"
}

# =========================================================
# CONFIGURACIÓN DEL SERVIDOR
# =========================================================

# Puerto donde escucha el servidor HTTP
PUERTO_HTTP = 80

# Interfaz donde escuchar (0.0.0.0 = todas)
HOST = "0.0.0.0"

# Máximo de conexiones simultáneas
MAX_CONEXIONES = 5

# =========================================================
# CONFIGURACIÓN DEL FIREWALL
# =========================================================

# IP de la puerta de enlace (gateway)
# Si no lo sabes, puedes dejarlo vacío y auto-detectar
GATEWAY = ""

# Interfaz del hotspot (se auto-detecta en setup.py)
INTERFAZ_HOTSPOT = "wlo1"

# Interfaz de Internet (se auto-detecta en setup.py)
INTERFAZ_INTERNET = "eth0"

# =========================================================
# CONFIGURACIÓN DE LOGGING
# =========================================================

# Nivel de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

# Archivo de log
LOG_FILE = "/tmp/portal_cautivo.log"