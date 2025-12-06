"""
firewall.py
Maneja comandos iptables para abrir/cerrar acceso a IPs autenticadas
VERSIÓN CORREGIDA
"""

import subprocess
import os
import sys
import platform

# =========================================================
# VERIFICAR SI SE EJECUTA CON PERMISOS SUDO
# =========================================================

def tiene_permisos_sudo():
    """
    Verifica si el script se ejecuta como root (Linux/Mac) o admin (Windows)
    
    Retorna:
        bool: True si tiene permisos, False si no
    """
    # Si estamos en Windows
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell.IsUserAnAdmin() != 0
        except:
            return False
    
    # Si estamos en Linux/Mac
    else:
        try:
            return os.geteuid() == 0
        except:
            return False


# =========================================================
# EJECUTAR COMANDO EN LA TERMINAL
# =========================================================

def ejecutar_comando(comando):
    """
    Ejecuta un comando en la terminal de Linux
    
    Argumentos:
        comando (str): El comando a ejecutar (ej: "iptables -A FORWARD ...")
    
    Retorna:
        tuple: (exito, salida, error)
        - exito (bool): True si el comando funcionó
        - salida (str): Lo que imprimió el comando
        - error (str): Mensaje de error si falló
    """
    try:
        # Ejecutar el comando
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True
        )
        
        # Verificar si funcionó
        if resultado.returncode == 0:
            return True, resultado.stdout, ""
        else:
            return False, resultado.stdout, resultado.stderr
    
    except Exception as error:
        return False, "", str(error)


# =========================================================
# FUNCIÓN 1: ABRIR ACCESO A UNA IP
# =========================================================

def abrir_acceso_ip(ip_cliente):
    """
    Ejecuta comandos iptables para PERMITIR tráfico desde una IP
    
    Abre dos reglas:
    1. iptables -A FORWARD -s <IP> -j ACCEPT
    2. iptables -A FORWARD -d <IP> -m state --state ESTABLISHED,RELATED -j ACCEPT
    
    Esto permite que la IP acceda a Internet completamente
    
    Argumentos:
        ip_cliente (str): La IP a autorizar (ej: "192.168.1.100")
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print(f"   ❌ ERROR: Se necesita sudo para ejecutar iptables")
        return False
    
    # ⭐ REGLA 1: Permitir SALIDA desde la IP autenticada
    comando1 = f"iptables -A FORWARD -s {ip_cliente} -j ACCEPT"
    
    print(f"   🔓 Regla 1 (salida): {comando1}")
    exito1, _, error1 = ejecutar_comando(comando1)
    
    if not exito1:
        print(f"   ❌ Error en regla 1: {error1}")
        return False
    
    print(f"   ✅ Regla 1 aplicada")
    
    # ⭐ REGLA 2: Permitir RESPUESTAS de Internet hacia la IP
    # (conexiones establecidas y relacionadas)
    comando2 = f"iptables -A FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
    
    print(f"   🔓 Regla 2 (retorno): {comando2}")
    exito2, _, error2 = ejecutar_comando(comando2)
    
    if not exito2:
        print(f"   ⚠️  Error en regla 2: {error2}")
        print(f"   ℹ️  Pero la regla 1 sí se aplicó, intentando continuar...")
    else:
        print(f"   ✅ Regla 2 aplicada")
    
    print(f"   ✅ ACCESO ABIERTO para {ip_cliente}")
    return True


# =========================================================
# FUNCIÓN 2: CERRAR ACCESO A UNA IP
# =========================================================

def cerrar_acceso_ip(ip_cliente):
    """
    Ejecuta comandos iptables para DENEGAR tráfico desde una IP
    
    Elimina las dos reglas que permitían el acceso
    
    Argumentos:
        ip_cliente (str): La IP a bloquear (ej: "192.168.1.100")
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print(f"   ❌ ERROR: Se necesita sudo para ejecutar iptables")
        return False
    
    # Eliminar regla de salida
    comando1 = f"iptables -D FORWARD -s {ip_cliente} -j ACCEPT"
    
    print(f"   🔒 Eliminando regla 1: {comando1}")
    exito1, _, error1 = ejecutar_comando(comando1)
    
    if exito1:
        print(f"   ✅ Regla 1 eliminada")
    else:
        print(f"   ⚠️  No se pudo eliminar regla 1 (posiblemente no existe)")
    
    # Eliminar regla de retorno
    comando2 = f"iptables -D FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
    
    print(f"   🔒 Eliminando regla 2: {comando2}")
    exito2, _, error2 = ejecutar_comando(comando2)
    
    if exito2:
        print(f"   ✅ Regla 2 eliminada")
    else:
        print(f"   ⚠️  No se pudo eliminar regla 2 (posiblemente no existe)")
    
    print(f"   ✅ ACCESO CERRADO para {ip_cliente}")
    return True


# =========================================================
# FUNCIÓN 3: VER TODAS LAS REGLAS (DEBUG)
# =========================================================

def listar_reglas_firewall():
    """
    Muestra todas las reglas de iptables configuradas
    
    Retorna:
        str: El output de iptables
    """
    
    if not tiene_permisos_sudo():
        return "ERROR: Se necesita sudo para ver iptables"
    
    comando = "iptables -L -n -v"
    exito, salida, error = ejecutar_comando(comando)
    
    if exito:
        return salida
    else:
        return f"Error al listar reglas: {error}"


# =========================================================
# FUNCIÓN 4: RESETEAR FIREWALL (para testing)
# =========================================================

def resetear_firewall():
    """
    Elimina TODAS las reglas de iptables
    ¡CUIDADO! Solo usar para testing
    
    Retorna:
        bool: True si funcionó
    """
    
    if not tiene_permisos_sudo():
        print("❌ ERROR: Se necesita sudo")
        return False
    
    print(f"   🔄 Reseteando firewall...")
    
    # Flush de todas las cadenas
    ejecutar_comando("iptables -F INPUT")
    ejecutar_comando("iptables -F OUTPUT")
    ejecutar_comando("iptables -F FORWARD")
    ejecutar_comando("iptables -t nat -F POSTROUTING")
    
    print(f"   ✅ Firewall reseteado")
    return True