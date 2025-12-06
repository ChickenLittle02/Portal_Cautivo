#!/usr/bin/env python3
"""
setup_utils.py - Utilidades para configuración del firewall
"""

import subprocess
import os
import sys

# =========================================================
# FUNCIÓN: EJECUTAR COMANDO
# =========================================================

def ejecutar(comando, descripcion=""):
    """Ejecuta un comando y muestra resultado"""
    try:
        if descripcion:
            print(f"   → {descripcion}")
        
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if resultado.returncode == 0:
            print(f"      ✅")
            return True
        else:
            print(f"      ❌ {resultado.stderr}")
            return False
    except Exception as e:
        print(f"      ❌ {e}")
        return False

# =========================================================
# FUNCIÓN: OBTENER INTERFACES
# =========================================================

def obtener_interfaces():
    """Detecta interfaces de red disponibles"""
    resultado = subprocess.run(
        "ip addr show | grep 'inet ' | grep -v '127.0.0.1'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    interfaces = {}
    for linea in resultado.stdout.strip().split('\n'):
        if linea:
            partes = linea.split()
            ip = partes[1].split('/')[0]
            interfaz = partes[-1]
            interfaces[interfaz] = ip
    
    return interfaces

# =========================================================
# FUNCIÓN: VERIFICAR PERMISOS SUDO
# =========================================================

def verificar_sudo():
    """Verifica que se ejecute con sudo"""
    if os.geteuid() != 0:
        print("❌ ERROR: Ejecuta con sudo")
        print("   sudo python3 setup.py")
        sys.exit(1)
    print("✅ Ejecutándose con sudo\n")