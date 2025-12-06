"""
usuarios.py
Maneja las cuentas de usuario, validación y sesiones activas
"""

import threading
from config import CUENTAS_VALIDAS

# =========================================================
# DICCIONARIO GLOBAL DE SESIONES ACTIVAS
# =========================================================
# IP -> "autenticado"
sesiones_activas = {}
sesiones_lock = threading.Lock()  # Protege acceso desde múltiples hilos


# =========================================================
# FUNCIÓN 1: VALIDAR CREDENCIALES
# =========================================================

def validar_credenciales(usuario, password):
    """
    Compara usuario y contraseña con CUENTAS_VALIDAS
    
    Argumentos:
        usuario (str): Nombre de usuario
        password (str): Contraseña
    
    Retorna:
        bool: True si son válidos, False si no
    """
    if usuario in CUENTAS_VALIDAS:
        if CUENTAS_VALIDAS[usuario] == password:
            return True
    return False


# =========================================================
# FUNCIÓN 2: REGISTRAR UNA SESIÓN
# =========================================================

def registrar_sesion(ip_cliente):
    """
    Guarda una IP en sesiones_activas cuando el usuario
    inicia sesión exitosamente
    
    Argumentos:
        ip_cliente (str): IP del cliente autenticado
    """
    with sesiones_lock:
        sesiones_activas[ip_cliente] = "autenticado"
    
    print(f"✅ IP {ip_cliente} autenticada y registrada")


# =========================================================
# FUNCIÓN 3: VERIFICAR SI UNA IP ESTÁ ACTIVA
# =========================================================

def verificar_sesion_activa(ip_cliente):
    """
    Comprueba si una IP ya tiene sesión activa
    
    Argumentos:
        ip_cliente (str): IP a verificar
    
    Retorna:
        bool: True si está autenticada, False si no
    """
    with sesiones_lock:
        return ip_cliente in sesiones_activas


# =========================================================
# FUNCIÓN 4: OBTENER TODAS LAS SESIONES (para debug)
# =========================================================

def obtener_sesiones_activas():
    """
    Retorna un diccionario con todas las sesiones activas
    (usado para la ruta /status)
    
    Retorna:
        dict: Copia de sesiones_activas
    """
    with sesiones_lock:
        return dict(sesiones_activas)
# =========================================================
# FUNCIÓN 5: ELIMINAR UNA SESIÓN
# =========================================================

def cerrar_sesion(ip_cliente):
    """
    Elimina una IP de sesiones_activas
    (útil para logout o timeout)
    
    Argumentos:
        ip_cliente (str): IP a eliminar
    """
    with sesiones_lock:
        if ip_cliente in sesiones_activas:
            del sesiones_activas[ip_cliente]
            print(f"🔴 Sesión cerrada para {ip_cliente}")
        else:
            print(f"⚠️  {ip_cliente} no tenía sesión activa")