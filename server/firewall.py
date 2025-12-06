"""
firewall.py
Maneja comandos iptables para abrir/cerrar acceso a IPs autenticadas
"""

import subprocess
import os
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
# FUNCIÓN: VERIFICAR SI UNA IP YA ESTÁ AUTORIZADA
# =========================================================

def ip_ya_autorizada(ip_cliente):
    """
    Verifica si la IP ya tiene una regla en FORWARD
    
    Argumentos:
        ip_cliente (str): IP a verificar
    
    Retorna:
        bool: True si ya está autorizada, False si no
    """
    # Ejecutar: iptables -L FORWARD -n | grep <IP>
    comando = f"iptables -L FORWARD -n | grep '{ip_cliente}'"
    exito, salida, _ = ejecutar_comando(comando)
    
    # Si grep encuentra algo, retorna True
    return exito and salida.strip() != ""


# =========================================================
# FUNCIÓN 1: ABRIR ACCESO A UNA IP
# =========================================================

def abrir_acceso_ip(ip_cliente):
    """
    Ejecuta comando iptables para PERMITIR tráfico desde una IP
    
    Agrega DOS reglas:
    1. iptables -A FORWARD -s <IP> -j ACCEPT
       (Permite que la IP salga hacia Internet)
    
    2. iptables -A FORWARD -d <IP> -m state --state ESTABLISHED,RELATED -j ACCEPT
       (Permite que las respuestas regresen)
    
    Argumentos:
        ip_cliente (str): La IP a autorizar (ej: "192.168.1.100")
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print(f"   ❌ ERROR: Se necesita sudo para ejecutar iptables")
        return False
    
    # IMPORTANTE: Verificar que la IP no esté ya autorizada
    if ip_ya_autorizada(ip_cliente):
        print(f"   ⚠️  IP {ip_cliente} YA ESTÁ AUTORIZADA (evitando duplicado)")
        return True
    
    print(f"   🔓 Autorizando IP {ip_cliente}...")
    
    # REGLA 1: Permitir salida (IP → Internet)
    comando1 = f"iptables -A FORWARD -s {ip_cliente} -j ACCEPT"
    print(f"      → {comando1}")
    
    exito1, _, error1 = ejecutar_comando(comando1)
    
    if not exito1:
        print(f"   ❌ Error al abrir acceso de salida: {error1}")
        return False
    
    # REGLA 2: Permitir respuestas (Internet → IP)
    comando2 = f"iptables -A FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
    print(f"      → {comando2}")
    
    exito2, _, error2 = ejecutar_comando(comando2)
    
    if not exito2:
        print(f"   ⚠️  Error al permitir respuestas (continuando): {error2}")
        # No retornamos False aquí porque la regla 1 ya funcionó
    
    print(f"   ✅ IP {ip_cliente} AUTORIZADA")
    return True


# =========================================================
# FUNCIÓN 2: CERRAR ACCESO A UNA IP
# =========================================================

def cerrar_acceso_ip(ip_cliente):
    """
    Ejecuta comando iptables para DENEGAR tráfico desde una IP
    
    Elimina DOS reglas:
    1. iptables -D FORWARD -s <IP> -j ACCEPT
    2. iptables -D FORWARD -d <IP> -m state --state ESTABLISHED,RELATED -j ACCEPT
    
    Argumentos:
        ip_cliente (str): La IP a bloquear (ej: "192.168.1.100")
    
    Retorna:
        bool: True si funcionó, False si falló
    """
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print(f"   ❌ ERROR: Se necesita sudo para ejecutar iptables")
        return False
    
    # IMPORTANTE: Verificar que la IP esté autorizada
    if not ip_ya_autorizada(ip_cliente):
        print(f"   ⚠️  IP {ip_cliente} NO está autorizada (nada que borrar)")
        return True
    
    print(f"   🔒 Bloqueando IP {ip_cliente}...")
    
    # REGLA 1: Eliminar salida (IP → Internet)
    comando1 = f"iptables -D FORWARD -s {ip_cliente} -j ACCEPT"
    print(f"      → {comando1}")
    
    exito1, _, error1 = ejecutar_comando(comando1)
    
    if not exito1:
        print(f"   ⚠️  Error al eliminar regla de salida: {error1}")
    
    # REGLA 2: Eliminar respuestas (Internet → IP)
    comando2 = f"iptables -D FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
    print(f"      → {comando2}")
    
    exito2, _, error2 = ejecutar_comando(comando2)
    
    if not exito2:
        print(f"   ⚠️  Error al eliminar regla de respuestas: {error2}")
    
    print(f"   ✅ IP {ip_cliente} BLOQUEADA")
    return True


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