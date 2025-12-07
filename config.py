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
PORTAL_IP = "192.168.12.1"  # ⚠️ CAMBIAR POR LA IP REAL DEL HOTSPOT

# Cuentas de usuario
CUENTAS = {
    "admin": "123456",
    "user1": "pass1"
}

# IPs autenticadas
sesiones_activas = {}
sesiones_lock = threading.Lock()