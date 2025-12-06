"""
firewall.py
Maneja comandos iptables para abrir/cerrar acceso a IPs autenticadas
"""

import subprocess
import os

# =========================================================
# VERIFICAR SI SE EJECUTA CON PERMISOS SUDO
# =========================================================

def tiene_permisos_sudo():
    """
    Verifica si el script se ejecuta como root (necesario para iptables)
    
    Retorna:
        bool: True si es root, False si no
    """
    return os.geteuid() == 0


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
    Ejecuta comando iptables para PERMITIR tráfico desde una IP
    
    Comando que ejecuta:
    iptables -A FORWARD -s <IP> -j ACCEPT
    
    Esto permite que la IP acceda a Internet
    
    Argumentos:
        ip_cliente (str): La IP a autorizar (ej: "192.168.1.100")
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print(f"   ❌ ERROR: Se necesita sudo para ejecutar iptables")
        return False
    
    # Comando a ejecutar
    # -A = Agregar regla
    # FORWARD = Cadena de reenvío (tráfico entre redes)
    # -s = Source (IP origen)
    # -j ACCEPT = Jump to ACCEPT (permitir tráfico)
    comando = f"iptables -A FORWARD -s {ip_cliente} -j ACCEPT"
    
    print(f"   🔓 Ejecutando: {comando}")
    
    exito, salida, error = ejecutar_comando(comando)
    
    if exito:
        print(f"   ✅ Acceso abierto para {ip_cliente}")
        return True
    else:
        print(f"   ❌ Error al abrir acceso: {error}")
        return False


# =========================================================
# FUNCIÓN 2: CERRAR ACCESO A UNA IP
# =========================================================

def cerrar_acceso_ip(ip_cliente):
    """
    Ejecuta comando iptables para DENEGAR tráfico desde una IP
    
    Comando que ejecuta:
    iptables -D FORWARD -s <IP> -j ACCEPT
    
    Esto cierra el acceso a Internet para esa IP
    
    Argumentos:
        ip_cliente (str): La IP a bloquear (ej: "192.168.1.100")
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print(f"   ❌ ERROR: Se necesita sudo para ejecutar iptables")
        return False
    
    # Comando a ejecutar
    # -D = Eliminar regla
    # FORWARD = Cadena de reenvío
    # -s = Source (IP origen)
    # -j ACCEPT = Que antes permitía
    comando = f"iptables -D FORWARD -s {ip_cliente} -j ACCEPT"
    
    print(f"   🔒 Ejecutando: {comando}")
    
    exito, salida, error = ejecutar_comando(comando)
    
    if exito:
        print(f"   ✅ Acceso cerrado para {ip_cliente}")
        return True
    else:
        print(f"   ⚠️  No se pudo cerrar acceso (posiblemente no existe): {error}")
        return False


# =========================================================
# FUNCIÓN 3: VER TODAS LAS REGLAS (DEBUG)
# =========================================================

def listar_reglas_firewall():
    """
    Muestra todas las reglas de iptables configuradas
    
    Comando que ejecuta:
    iptables -L -n
    
    Retorna:
        str: El output de iptables (todas las reglas)
    """
    
    if not tiene_permisos_sudo():
        return "ERROR: Se necesita sudo para ver iptables"
    
    comando = "iptables -L -n"
    exito, salida, error = ejecutar_comando(comando)
    
    if exito:
        return salida
    else:
        return f"Error al listar reglas: {error}"


# =========================================================
# FUNCIÓN 4: BLOQUEAR TODO EL TRÁFICO (INICIAL)
# =========================================================

def bloquear_todo_trafico():
    """
    Configura iptables para bloquear TODO el tráfico de la red local
    (excepto al puerto 80 del gateway, que maneja tu compañero)
    
    Comandos que ejecuta:
    1. iptables -A FORWARD -j DROP  (bloquear todo)
    2. iptables -A FORWARD -d <gateway_port_80> -j ACCEPT (permitir login)
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    if not tiene_permisos_sudo():
        print("❌ ERROR: Se necesita sudo")
        return False
    
    # Bloquear todo por defecto
    comando1 = "iptables -A FORWARD -j DROP"
    
    print(f"   🚫 Bloqueando todo tráfico...")
    exito1, _, error1 = ejecutar_comando(comando1)
    
    if exito1:
        print(f"   ✅ Tráfico bloqueado por defecto")
        return True
    else:
        print(f"   ❌ Error: {error1}")
        return False


# =========================================================
# FUNCIÓN 5: RESETEAR FIREWALL (para testing)
# =========================================================

def resetear_firewall():
    """
    Elimina TODAS las reglas de iptables
    ¡CUIDADO! Solo usar para testing
    
    Comando que ejecuta:
    iptables -F FORWARD (flush/limpiar cadena FORWARD)
    
    Retorna:
        bool: True si funcionó
    """
    
    if not tiene_permisos_sudo():
        print("❌ ERROR: Se necesita sudo")
        return False
    
    comando = "iptables -F FORWARD"
    
    print(f"   🔄 Reseteando firewall...")
    exito, _, error = ejecutar_comando(comando)
    
    if exito:
        print(f"   ✅ Firewall reseteado")
        return True
    else:
        print(f"   ❌ Error: {error}")
        return False