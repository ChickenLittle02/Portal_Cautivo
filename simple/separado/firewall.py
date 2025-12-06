#!/usr/bin/env python3
"""
firewall.py - Gestión del firewall (iptables)
"""

import subprocess
import threading

# =========================================================
# FUNCIÓN: EJECUTAR COMANDO IPTABLES
# =========================================================

def ejecutar_iptables(comando):
    """Ejecuta un comando iptables"""
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return resultado.returncode == 0
    except:
        return False

# =========================================================
# FUNCIÓN: AUTORIZAR IP EN FIREWALL
# =========================================================

def autorizar_ip(ip_cliente):
    """
    Autoriza una IP en iptables con DOS reglas:
    1. Permite salida: FORWARD -s <IP> -j ACCEPT
    2. Permite respuesta: FORWARD -d <IP> -m state -j ACCEPT
    Se ejecuta en hilo separado para no bloquear
    """
    def _ejecutar():
        print(f"🔓 Autorizando {ip_cliente}...")
        
        # Regla 1: Salida
        cmd1 = f"sudo iptables -A FORWARD -s {ip_cliente} -j ACCEPT"
        if ejecutar_iptables(cmd1):
            print(f"   → Regla 1 OK")
        else:
            print(f"   → Regla 1 FALLO")
            return
        
        # Regla 2: Respuesta
        cmd2 = f"sudo iptables -A FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
        if ejecutar_iptables(cmd2):
            print(f"   → Regla 2 OK")
        else:
            print(f"   → Regla 2 FALLO")
        
        print(f"✅ {ip_cliente} AUTORIZADA")
    
    hilo = threading.Thread(target=_ejecutar, daemon=True)
    hilo.start()

# =========================================================
# FUNCIÓN: DESAUTORIZAR IP EN FIREWALL
# =========================================================

def desautorizar_ip(ip_cliente):
    """
    Desautoriza una IP en iptables (la elimina)
    Se ejecuta en hilo separado
    """
    def _ejecutar():
        print(f"🔒 Desautorizando {ip_cliente}...")
        
        # Regla 1: Salida
        cmd1 = f"sudo iptables -D FORWARD -s {ip_cliente} -j ACCEPT"
        ejecutar_iptables(cmd1)
        
        # Regla 2: Respuesta
        cmd2 = f"sudo iptables -D FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
        ejecutar_iptables(cmd2)
        
        print(f"✅ {ip_cliente} DESAUTORIZADA")
    
    hilo = threading.Thread(target=_ejecutar, daemon=True)
    hilo.start()
