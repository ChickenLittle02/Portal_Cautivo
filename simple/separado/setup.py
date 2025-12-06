#!/usr/bin/env python3
"""
setup.py - Configura automáticamente el firewall para el Portal Cautivo
Ejecutar UNA SOLA VEZ:
    sudo python3 setup.py
"""

import sys
from setup_utils import verificar_sudo, obtener_interfaces
from firewall_config import aplicar_firewall

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
    aplicar_firewall(hotspot, internet)

# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    configurar()