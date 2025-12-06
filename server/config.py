"""
config.py
Almacena todas las configuraciones del Portal Cautivo
"""

# =========================================================
# CONFIGURACIÓN DEL SERVIDOR
# =========================================================
PUERTO = 80
HOST = '0.0.0.0'

# =========================================================
# CUENTAS DE USUARIO
# =========================================================
CUENTAS_VALIDAS = {
    "admin": "123456",
    "user1": "pass1",
    "juan": "juan123"
}

# =========================================================
# MENSAJES
# =========================================================
MENSAJE_INICIO = """
🚀 Servidor Portal Cautivo iniciado
   Puerto: {}
   Abre: http://localhost
   (Presiona Ctrl+C para detener)
"""

MENSAJE_ERROR_PERMISOS = "❌ ERROR: Necesitas permisos de administrador (sudo) para puerto {}"
MENSAJE_DETENIDO = "🛑 Servidor detenido"