#!/usr/bin/env python3
"""
firewall.py - Gestión del firewall (iptables)
SOLUCIÓN DEFINITIVA: Excluir IPs autenticadas de la redirección NAT
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
    Autoriza una IP completamente:
    
    1. En NAT PREROUTING: Excluir de redirección (ACCEPT antes de CAPTIVE_PORTAL)
    2. En FORWARD: Permitir todo el tráfico
    
    Esto asegura que el tráfico de IPs autenticadas NO sea redirigido al portal.
    """
    def _ejecutar():
        print(f"🔓 Autorizando {ip_cliente}...")
        
        # PASO 1: Excluir de la redirección NAT
        # -I PREROUTING 1: Insertar en PRIMERA posición
        # Esto hace que el tráfico de esta IP SALTE la cadena CAPTIVE_PORTAL
        cmd_nat = f"sudo iptables -t nat -I PREROUTING 1 -s {ip_cliente} -j ACCEPT"
        if ejecutar_iptables(cmd_nat):
            print(f"   ✅ NAT: IP excluida de redirección")
        else:
            print(f"   ❌ NAT: FALLO al excluir")
            return
        
        # PASO 2: Permitir FORWARD (salida)
        cmd_forward = f"sudo iptables -I FORWARD 1 -s {ip_cliente} -j ACCEPT"
        if ejecutar_iptables(cmd_forward):
            print(f"   ✅ FORWARD: Salida permitida")
        else:
            print(f"   ❌ FORWARD: FALLO")
            return
        
        print(f"✅ {ip_cliente} AUTORIZADA - ACCESO COMPLETO A INTERNET")
    
    hilo = threading.Thread(target=_ejecutar, daemon=True)
    hilo.start()

# =========================================================
# FUNCIÓN: DESAUTORIZAR IP EN FIREWALL
# =========================================================

def desautorizar_ip(ip_cliente):
    """
    Desautoriza una IP:
    1. Eliminar de NAT PREROUTING (vuelve a redirigir al portal)
    2. Eliminar de FORWARD (bloquea el tráfico)
    """
    def _ejecutar():
        print(f"🔒 Desautorizando {ip_cliente}...")
        
        # Eliminar de NAT
        cmd_nat = f"sudo iptables -t nat -D PREROUTING -s {ip_cliente} -j ACCEPT"
        ejecutar_iptables(cmd_nat)
        
        # Eliminar de FORWARD
        cmd_forward = f"sudo iptables -D FORWARD -s {ip_cliente} -j ACCEPT"
        ejecutar_iptables(cmd_forward)
        
        print(f"✅ {ip_cliente} DESAUTORIZADA")
    
    hilo = threading.Thread(target=_ejecutar, daemon=True)
    hilo.start()

# =========================================================
# FUNCIÓN: LISTAR REGLAS (DEBUG)
# =========================================================

def listar_reglas():
    """Muestra las reglas actuales para debug"""
    try:
        print("\n" + "="*60)
        print("📋 REGLAS NAT PREROUTING")
        print("="*60)
        subprocess.run("sudo iptables -t nat -L PREROUTING -n -v --line-numbers", shell=True)
        
        print("\n" + "="*60)
        print("📋 REGLAS FORWARD")
        print("="*60)
        subprocess.run("sudo iptables -L FORWARD -n -v --line-numbers", shell=True)
        print("="*60 + "\n")
    except Exception as e:
        print(f"❌ Error listando reglas: {e}")