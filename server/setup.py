#!/usr/bin/env python3
"""
setup.py
Configura automáticamente el firewall y NAT para el Portal Cautivo
Ejecutar ANTES de main.py:
    sudo python3 setup.py
"""

import subprocess
import os
import sys

# =========================================================
# VERIFICAR PERMISOS SUDO
# =========================================================

def verificar_sudo():
    """Verifica que se ejecute con sudo"""
    if os.geteuid() != 0:
        print("❌ ERROR: Este script debe ejecutarse con sudo")
        print("   sudo python3 setup.py")
        sys.exit(1)
    print("✅ Ejecutándose con permisos sudo")

# =========================================================
# EJECUTAR COMANDO EN TERMINAL
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
            text=True
        )
        
        if resultado.returncode == 0:
            print(f"   ✅ OK")
            return True
        else:
            print(f"   ❌ Error: {resultado.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False

# =========================================================
# DETECTAR INTERFACES DE RED
# =========================================================

def detectar_interfaces():
    """
    Detecta automáticamente:
    - Interfaz del WiFi hotspot (ej: wlo1)
    - Interfaz de Internet (ej: enx32d53edd8df7)
    """
    print("\n🔍 Detectando interfaces de red...")
    
    # Obtener lista de interfaces
    resultado = subprocess.run(
        "ip addr show | grep 'inet ' | grep -v '127.0.0.1'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    lineas = resultado.stdout.strip().split('\n')
    
    interfaces = {}
    for linea in lineas:
        if linea:
            # Parsear: "inet 10.42.0.1/24 brd 10.42.0.255 scope global noprefixroute wlo1"
            partes = linea.split()
            ip = partes[1].split('/')[0]
            interfaz = partes[-1]
            interfaces[interfaz] = ip
    
    print(f"\n📡 Interfaces detectadas:")
    for interfaz, ip in interfaces.items():
        print(f"   {interfaz}: {ip}")
    
    return interfaces

# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def configurar_firewall():
    """Configura todo automáticamente"""
    
    print("\n" + "="*60)
    print("🔥 CONFIGURADOR AUTOMÁTICO DEL PORTAL CAUTIVO")
    print("="*60)
    
    # 1. Verificar sudo
    verificar_sudo()
    
    # 2. Detectar interfaces
    interfaces = detectar_interfaces()
    
    if len(interfaces) < 2:
        print("\n❌ ERROR: Se necesitan AL MENOS 2 interfaces de red")
        print("   - Una para el WiFi hotspot")
        print("   - Una para Internet")
        sys.exit(1)
    
    # 3. Solicitar confirmación
    print("\n⚙️  CONFIGURACIÓN:")
    print("   Estas interfaces serán configuradas como router")
    
    # Crear lista de interfaces para seleccionar
    lista_interfaces = list(interfaces.items())
    
    interfaz_hotspot = None
    interfaz_internet = None
    
    print("\n" + "="*60)
    print("📡 SELECCIONA LAS INTERFACES DE RED")
    print("="*60)
    
    print("\n🔹 INTERFACES DISPONIBLES:")
    for i, (interfaz, ip) in enumerate(lista_interfaces, 1):
        print(f"\n   {i}. {interfaz}")
        print(f"      IP: {ip}")
    
    # Seleccionar HOTSPOT
    print("\n" + "-"*60)
    print("1️⃣  ¿CUÁL ES EL HOTSPOT?")
    print("   (La que Windows usa para conectarse)")
    print("   (Probablemente sea wlo1 o similar)")
    print("-"*60)
    
    while True:
        try:
            opcion = int(input("\n   Escribe el número: ").strip())
            if 1 <= opcion <= len(lista_interfaces):
                interfaz_hotspot = lista_interfaces[opcion - 1][0]
                print(f"   ✅ Hotspot seleccionado: {interfaz_hotspot}")
                break
            else:
                print(f"   ❌ Opción inválida (1-{len(lista_interfaces)})")
        except ValueError:
            print("   ❌ Ingresa un número válido")
    
    # Seleccionar INTERNET
    print("\n" + "-"*60)
    print("2️⃣  ¿CUÁL ES LA INTERFAZ DE INTERNET?")
    print("   (La que recibe Internet desde tu teléfono/router)")
    print("   (Probablemente sea enx... o eth0)")
    print("-"*60)
    
    print("\n   OPCIONES:")
    opciones_validas = []
    for i, (interfaz, ip) in enumerate(lista_interfaces, 1):
        if interfaz != interfaz_hotspot:  # No mostrar la que ya seleccionó
            opciones_validas.append((i, interfaz))
            print(f"   {i}. {interfaz} ({ip})")
    
    while True:
        try:
            opcion = int(input("\n   Escribe el número: ").strip())
            # Buscar en opciones válidas
            for num, interfaz in opciones_validas:
                if opcion == num:
                    interfaz_internet = interfaz
                    print(f"   ✅ Internet seleccionado: {interfaz_internet}")
                    break
            if interfaz_internet:
                break
            else:
                print(f"   ❌ Opción inválida")
        except ValueError:
            print("   ❌ Ingresa un número válido")
    
    # Resumen visual
    print("\n" + "="*60)
    print("✅ RESUMEN DE CONFIGURACIÓN")
    print("="*60)
    
    print(f"\n📡 INTERFACES SELECCIONADAS:")
    print(f"\n   🔹 HOTSPOT (Windows se conecta aquí):")
    print(f"      {interfaz_hotspot} ({interfaces[interfaz_hotspot]})")
    print(f"\n   🔹 INTERNET (Desde tu teléfono/router):")
    print(f"      {interfaz_internet} ({interfaces[interfaz_internet]})")
    
    print("\n📊 FLUJO DE DATOS:")
    print(f"\n   Windows")
    print(f"      ↓")
    print(f"   {interfaz_hotspot} (Hotspot)")
    print(f"      ↓ [NAT Router]")
    print(f"   {interfaz_internet} (Internet)")
    print(f"      ↓")
    print(f"   Tu teléfono / Router")
    
    print("\n" + "="*60)
    confirmacion = input("¿Confirmar esta configuración? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Cancelado")
        sys.exit(0)
    
    # 4. Aplicar configuración
    print("\n" + "="*60)
    print("🔧 APLICANDO CONFIGURACIÓN...")
    print("="*60)
    
    # Limpiar iptables anterior
    print("\n1️⃣  Limpiando configuración anterior...")
    ejecutar("sudo iptables -F", "Limpiando INPUT")
    ejecutar("sudo iptables -F FORWARD", "Limpiando FORWARD")
    ejecutar("sudo iptables -F OUTPUT", "Limpiando OUTPUT")
    ejecutar("sudo iptables -t nat -F", "Limpiando NAT")
    
    # Establecer políticas por defecto
    print("\n2️⃣  Estableciendo políticas por defecto (BLOQUEAR TODO)...")
    ejecutar("sudo iptables -P INPUT DROP", "Policy INPUT = DROP")
    ejecutar("sudo iptables -P OUTPUT DROP", "Policy OUTPUT = DROP")
    ejecutar("sudo iptables -P FORWARD DROP", "Policy FORWARD = DROP")
    
    # Permitir localhost
    print("\n3️⃣  Permitiendo localhost...")
    ejecutar("sudo iptables -A INPUT -i lo -j ACCEPT", "INPUT localhost")
    ejecutar("sudo iptables -A OUTPUT -o lo -j ACCEPT", "OUTPUT localhost")
    
    # Permitir PING desde hotspot
    print("\n4️⃣  Permitiendo PING desde WiFi...")
    ejecutar(f"sudo iptables -A INPUT -i {interfaz_hotspot} -p icmp -j ACCEPT", "INPUT PING")
    ejecutar(f"sudo iptables -A OUTPUT -o {interfaz_hotspot} -p icmp -j ACCEPT", "OUTPUT PING")
    
    # Permitir puerto 80 (LOGIN)
    print("\n5️⃣  Permitiendo puerto 80 (LOGIN)...")
    ejecutar(f"sudo iptables -A INPUT -i {interfaz_hotspot} -p tcp --dport 80 -j ACCEPT", "INPUT puerto 80")
    ejecutar(f"sudo iptables -A OUTPUT -o {interfaz_hotspot} -p tcp --sport 80 -j ACCEPT", "OUTPUT puerto 80")
    
    # Permitir DNS
    print("\n6️⃣  Permitiendo DNS...")
    ejecutar("sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT", "OUTPUT DNS")
    ejecutar("sudo iptables -A INPUT -p udp --sport 53 -j ACCEPT", "INPUT DNS")
    
    # Permitir OUTPUT hacia Internet (para que Linux tenga acceso)
    print("\n7️⃣  Permitiendo OUTPUT hacia Internet...")
    ejecutar(
        f"sudo iptables -A OUTPUT -o {interfaz_internet} -j ACCEPT",
        f"OUTPUT hacia {interfaz_internet} (Linux accede a Internet)"
    )
    ejecutar(
        f"sudo iptables -A INPUT -i {interfaz_internet} -m state --state ESTABLISHED,RELATED -j ACCEPT",
        f"INPUT desde {interfaz_internet} (respuestas para Linux)"
    )
    ejecutar("sudo sysctl -w net.ipv4.ip_forward=1", "IP Forward activado")
    
    # Configurar NAT
    print("\n8️⃣  Configurando NAT (Network Address Translation)...")
    ejecutar(
        f"sudo iptables -t nat -A POSTROUTING -o {interfaz_internet} -j MASQUERADE",
        "NAT MASQUERADE"
    )
    
    # Permitir FORWARD entre interfaces
    print("\n9️⃣  Permitiendo FORWARD entre interfaces...")
    
    # Obtener el rango de IP del hotspot
    ip_hotspot = interfaces[interfaz_hotspot]
    # Convertir 10.42.0.1 → 10.42.0.0/24
    partes_ip = ip_hotspot.split('.')
    ip_rango = f"{partes_ip[0]}.{partes_ip[1]}.{partes_ip[2]}.0/24"
    
    print(f"   (Rango del hotspot detectado: {ip_rango})")
    
    # FORWARD: Desde hotspot hacia Internet
    ejecutar(
        f"sudo iptables -A FORWARD -i {interfaz_hotspot} -o {interfaz_internet} -j ACCEPT",
        f"FORWARD {interfaz_hotspot} ({ip_rango}) → {interfaz_internet}"
    )
    
    # FORWARD: Respuestas desde Internet hacia hotspot
    ejecutar(
        f"sudo iptables -A FORWARD -i {interfaz_internet} -o {interfaz_hotspot} -m state --state ESTABLISHED,RELATED -j ACCEPT",
        f"FORWARD {interfaz_internet} → {interfaz_hotspot} (respuestas)"
    )
    
    # IMPORTANTE: Permitir que Linux SALGA hacia Internet (para su propio uso)
    print(f"\n🔟 Permitiendo que Linux acceda a Internet...")
    ejecutar(
        f"sudo iptables -A FORWARD -o {interfaz_internet} -j ACCEPT",
        f"FORWARD cualquier origen → {interfaz_internet} (para Linux)"
    )
    ejecutar(
        f"sudo iptables -A FORWARD -i {interfaz_internet} -m state --state ESTABLISHED,RELATED -j ACCEPT",
        f"FORWARD {interfaz_internet} → cualquier destino (respuestas)"
    )
    
    # 5. Mostrar resultado
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*60)
    
    print("\n📋 ESTADO ACTUAL:")
    print("\n🔹 INPUT:")
    subprocess.run("sudo iptables -L INPUT -n", shell=True)
    
    print("\n🔹 OUTPUT:")
    subprocess.run("sudo iptables -L OUTPUT -n", shell=True)
    
    print("\n🔹 FORWARD:")
    subprocess.run("sudo iptables -L FORWARD -n", shell=True)
    
    print("\n🔹 NAT:")
    subprocess.run("sudo iptables -t nat -L -n", shell=True)
    
    print("\n" + "="*60)
    print("✅ LISTO PARA EJECUTAR:")
    print("   sudo python3 main.py")
    print("="*60)

# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    configurar_firewall()