#!/usr/bin/env python3
"""
auth.py - Gestión de autenticación y sesiones
"""

from config import CUENTAS, sesiones_activas, sesiones_lock

# =========================================================
# FUNCIÓN: VALIDAR CREDENCIALES
# =========================================================

def validar_credenciales(usuario, password):
    """Valida usuario y contraseña"""
    if usuario in CUENTAS:
        return CUENTAS[usuario] == password
    return False

# =========================================================
# FUNCIÓN: REGISTRAR SESIÓN
# =========================================================

def registrar_sesion(ip_cliente):
    """Registra una IP autenticada"""
    with sesiones_lock:
        sesiones_activas[ip_cliente] = "autenticado"
    print(f"✅ Sesión registrada: {ip_cliente}")

# =========================================================
# FUNCIÓN: CERRAR SESIÓN
# =========================================================

def cerrar_sesion(ip_cliente):
    """Elimina sesión de IP"""
    with sesiones_lock:
        if ip_cliente in sesiones_activas:
            del sesiones_activas[ip_cliente]
    print(f"❌ Sesión cerrada: {ip_cliente}")
