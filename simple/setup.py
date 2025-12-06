#!/usr/bin/env python3
"""
setup.py - Configura automáticamente el firewall para el Portal Cautivo
Ejecutar UNA SOLA VEZ:
    sudo python3 setup.py
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

# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================

def configurar():
    """Configura el firewall automáticamente"""
    
    print("\n" + "="*60)
    print("🔥 CONFIGURADOR AUTOMÁTICO - PORTAL CAUTIVO")
    print("="*60)
    
    # Verificar sudo
    verificar_sudo()
    
    # Obtener interfaces
    print("📡 Detectando interfaces de red...")
    interfaces = obtener_interfaces()
    
    if len(interfaces) < 2:
        print("❌ ERROR: Se necesitan 2 interfaces")
        sys.exit(1)
    
    print("\n🔹 INTERFACES DISPONIBLES:")
    for i, (iface, ip) in enumerate(interfaces.items(), 1):
        print(f"   {i}. {iface}: {ip}")
    
    # Seleccionar HOTSPOT
    print("\n" + "-"*60)
    print("1️⃣  ¿CUÁL ES LA INTERFAZ DEL HOTSPOT?")
    print("   (La que Windows usa para conectarse)")
    print("-"*60)
    
    lista = list(interfaces.items())
    
    while True:
        try:
            opcion = int(input("   Número: ").strip())
            if 1 <= opcion <= len(lista):
                hotspot = lista[opcion - 1][0]
                print(f"   ✅ Hotspot: {hotspot}")
                break
        except:
            pass
        print("   ❌ Opción inválida")
    
    # Seleccionar INTERNET
    print("\n" + "-"*60)
    print("2️⃣  ¿CUÁL ES LA INTERFAZ DE INTERNET?")
    print("   (La que lleva Internet desde tu teléfono)")
    print("-"*60)
    
    while True:
        try:
            opcion = int(input("   Número: ").strip())
            if 1 <= opcion <= len(lista):
                internet = lista[opcion - 1][0]
                if internet != hotspot:
                    print(f"   ✅ Internet: {internet}")
                    break
        except:
            pass
        print("   ❌ Opción inválida (debe ser diferente al hotspot)")
    
    # Confirmación
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN:")
    print(f"   Hotspot:  {hotspot} ({interfaces[hotspot]})")
    print(f"   Internet: {internet} ({interfaces[internet]})")
    print("="*60)
    
    confirmar = input("\n¿Confirmar? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Cancelado")
        sys.exit(0)
    
    # APLICAR CONFIGURACIÓN
    print("\n" + "="*60)
    print("🔧 APLICANDO CONFIGURACIÓN...")
    print("="*60)
    
    # 1. Limpiar
    print("\n1️⃣  Limpiando reglas anteriores...")
    ejecutar("iptables -F", "Limpiando INPUT/OUTPUT/FORWARD")
    ejecutar("iptables -F INPUT")
    ejecutar("iptables -F OUTPUT")
    ejecutar("iptables -F FORWARD")
    ejecutar("iptables -t nat -F", "Limpiando NAT")
    
    # 2. Políticas ACCEPT (abierto)
    print("\n2️⃣  Estableciendo políticas (ACCEPT)...")
    ejecutar("iptables -P INPUT ACCEPT", "INPUT ACCEPT")
    ejecutar("iptables -P OUTPUT ACCEPT", "OUTPUT ACCEPT")
    ejecutar("iptables -P FORWARD ACCEPT", "FORWARD ACCEPT")
    
    # 3. IP Forward
    print("\n3️⃣  Habilitando IP Forward...")
    ejecutar("sysctl -w net.ipv4.ip_forward=1", "ip_forward = 1")
    
    # 4. NAT
    print("\n4️⃣  Configurando NAT...")
    ejecutar(
        f"iptables -t nat -A POSTROUTING -o {internet} -j MASQUERADE",
        f"NAT MASQUERADE en {internet}"
    )
    
    # 5. FORWARD entre interfaces
    print("\n5️⃣  Configurando FORWARD entre interfaces...")
    ejecutar(
        f"iptables -A FORWARD -i {hotspot} -o {internet} -j ACCEPT",
        f"FORWARD {hotspot} → {internet}"
    )
    ejecutar(
        f"iptables -A FORWARD -i {internet} -o {hotspot} -m state --state ESTABLISHED,RELATED -j ACCEPT",
        f"FORWARD {internet} → {hotspot} (retorno)"
    )
    
    # 6. Puertos (HTTP + DNS)
    print("\n6️⃣  Abriendo puertos (HTTP + DNS)...")
    ejecutar("iptables -A FORWARD -p tcp --dport 80 -j ACCEPT", "TCP puerto 80 (salida)")
    ejecutar("iptables -A FORWARD -p tcp --sport 80 -j ACCEPT", "TCP puerto 80 (respuesta)")
    ejecutar("iptables -A FORWARD -p udp --dport 53 -j ACCEPT", "UDP puerto 53 (salida)")
    ejecutar("iptables -A FORWARD -p udp --sport 53 -j ACCEPT", "UDP puerto 53 (respuesta)")
    ejecutar("iptables -A FORWARD -p tcp --dport 53 -j ACCEPT", "TCP puerto 53 (salida)")
    ejecutar("iptables -A FORWARD -p tcp --sport 53 -j ACCEPT", "TCP puerto 53 (respuesta)")
    
    # 7. Localhost
    print("\n7️⃣  Permitiendo localhost...")
    ejecutar("iptables -A INPUT -i lo -j ACCEPT", "INPUT localhost")
    ejecutar("iptables -A OUTPUT -o lo -j ACCEPT", "OUTPUT localhost")
    
    # 8. Bloquear por defecto
    print("\n8️⃣  Estableciendo política por defecto (DROP)...")
    ejecutar("iptables -P FORWARD DROP", "FORWARD policy = DROP")
    
    # VERIFICAR
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*60)
    
    print("\n📋 REGLAS ACTUALES:")
    subprocess.run("echo '🔹 FORWARD:' && iptables -L FORWARD -n", shell=True)
    
    print("\n" + "="*60)
    print("✅ LISTO PARA EJECUTAR:")
    print("   sudo python3 main.py")
    print("="*60 + "\n")

# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    configurar()