#!/usr/bin/env python3
"""
config.py - Configuración del Portal Cautivo
"""

import threading

# =========================================================
# CONFIGURACIÓN
# =========================================================

PUERTO = 80
HOST = '0.0.0.0'

# Cuentas de usuario
CUENTAS = {
    "admin": "123456",
    "user1": "pass1"
}

# IPs autenticadas
sesiones_activas = {}
sesiones_lock = threading.Lock()