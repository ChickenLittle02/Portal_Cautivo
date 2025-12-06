#!/usr/bin/env python3
"""
auth.py - Gestión de autenticación y sesiones
Ahora integrado con user_manager para gestión avanzada de usuarios
"""

from config import sesiones_activas, sesiones_lock
from user_manager import validar_credenciales as validar_user_manager

# =========================================================
# FUNCIÓN: VALIDAR CREDENCIALES
# =========================================================

def validar_credenciales(usuario, password):
    """Valida usuario y contraseña usando el sistema de gestión de usuarios"""
    valido, role = validar_user_manager(usuario, password)
    return valido

# =========================================================
# FUNCIÓN: OBTENER ROL DE USUARIO
# =========================================================

def obtener_rol(usuario, password):
    """Obtiene el rol del usuario (admin o user)"""
    valido, role = validar_user_manager(usuario, password)
    return role if valido else None

# =========================================================
# FUNCIÓN: REGISTRAR SESIÓN
# =========================================================

def registrar_sesion(ip_cliente, usuario="", role="user"):
    """Registra una IP autenticada con información del usuario"""
    with sesiones_lock:
        sesiones_activas[ip_cliente] = {
            "autenticado": True,
            "usuario": usuario,
            "role": role
        }
    print(f"✅ Sesión registrada: {ip_cliente} ({usuario} - {role})")

# =========================================================
# FUNCIÓN: CERRAR SESIÓN
# =========================================================

def cerrar_sesion(ip_cliente):
    """Elimina sesión de IP"""
    with sesiones_lock:
        if ip_cliente in sesiones_activas:
            usuario = sesiones_activas[ip_cliente].get("usuario", "desconocido")
            del sesiones_activas[ip_cliente]
            print(f"❌ Sesión cerrada: {ip_cliente} ({usuario})")
        else:
            print(f"❌ Sesión cerrada: {ip_cliente}")

# =========================================================
# FUNCIÓN: VERIFICAR SI ES ADMIN
# =========================================================

def es_admin(ip_cliente):
    """Verifica si la IP actual tiene rol de admin"""
    with sesiones_lock:
        if ip_cliente in sesiones_activas:
            return sesiones_activas[ip_cliente].get("role") == "admin"
    return False

# =========================================================
# FUNCIÓN: OBTENER USUARIO DE IP
# =========================================================

def obtener_usuario_ip(ip_cliente):
    """Obtiene el nombre de usuario asociado a una IP"""
    with sesiones_lock:
        if ip_cliente in sesiones_activas:
            return sesiones_activas[ip_cliente].get("usuario", "desconocido")
    return None