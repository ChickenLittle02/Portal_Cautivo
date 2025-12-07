#!/usr/bin/env python3
"""
firewall_config.py - Configuración de reglas de firewall
SOLUCIÓN DEFINITIVA: NO usar redirección NAT, sino reglas condicionales
"""

import subprocess
from setup_utils import ejecutar

# =========================================================
# FUNCIÓN: OBTENER IP DE INTERFAZ
# =========================================================

def obtener_ip_interfaz(interfaz):
    """Obtiene la IP de una interfaz de red"""
    try:
        resultado = subprocess.run(
            f"ip addr show {interfaz} | grep 'inet ' | awk '{{print $2}}' | cut -d'/' -f1",
            shell=True,
            capture_output=True,
            text=True
        )
        ip = resultado.stdout.strip()
        return ip if ip else "192.168.12.1"
    except:
        return "192.168.12.1"

# =========================================================
# FUNCIÓN: APLICAR CONFIGURACIÓN DE FIREWALL
# =========================================================

def aplicar_firewall(hotspot, internet):
    """Aplica toda la configuración de firewall"""
    
    print("\n" + "="*60)
    print("🔧 APLICANDO CONFIGURACIÓN...")
    print("="*60)
    
    # 1. Limpiar TODO
    print("\n1️⃣  Limpiando reglas anteriores...")
    ejecutar("iptables -F", "Limpiando filtros")
    ejecutar("iptables -X", "Limpiando cadenas personalizadas")
    ejecutar("iptables -t nat -F", "Limpiando NAT")
    ejecutar("iptables -t nat -X", "Limpiando cadenas NAT")
    ejecutar("iptables -t mangle -F", "Limpiando MANGLE")
    ejecutar("iptables -t mangle -X", "Limpiando cadenas MANGLE")
    
    # 2. Políticas por defecto
    print("\n2️⃣  Estableciendo políticas por defecto...")
    ejecutar("iptables -P INPUT ACCEPT", "INPUT ACCEPT")
    ejecutar("iptables -P OUTPUT ACCEPT", "OUTPUT ACCEPT")
    ejecutar("iptables -P FORWARD DROP", "FORWARD DROP")
    
    # 3. IP Forward
    print("\n3️⃣  Habilitando IP Forward...")
    ejecutar("sysctl -w net.ipv4.ip_forward=1", "ip_forward = 1")
    
    # 4. NAT para internet (MASQUERADE)
    print("\n4️⃣  Configurando NAT...")
    ejecutar(
        f"iptables -t nat -A POSTROUTING -o {internet} -j MASQUERADE",
        f"NAT MASQUERADE en {internet}"
    )
    
    # 5. Obtener IP del servidor
    ip_servidor = obtener_ip_interfaz(hotspot)
    
    # 6. Crear cadena personalizada para portal cautivo
    print("\n5️⃣  Creando cadena personalizada para portal...")
    ejecutar("iptables -t nat -N CAPTIVE_PORTAL", "Crear cadena CAPTIVE_PORTAL")
    
    # 7. En la cadena CAPTIVE_PORTAL: Redirigir HTTP/HTTPS al portal
    print("\n6️⃣  Configurando redirecciones en cadena CAPTIVE_PORTAL...")
    ejecutar(
        f"iptables -t nat -A CAPTIVE_PORTAL -p tcp --dport 80 -j DNAT --to-destination {ip_servidor}:80",
        f"Redirigir HTTP → portal"
    )
    ejecutar(
        f"iptables -t nat -A CAPTIVE_PORTAL -p tcp --dport 443 -j DNAT --to-destination {ip_servidor}:80",
        f"Redirigir HTTPS → portal"
    )
    
    # 8. DNS siempre al servidor local (para todos)
    print("\n7️⃣  Redirigiendo DNS al servidor local...")
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p udp --dport 53 -j DNAT --to-destination {ip_servidor}:53",
        f"Redirigir DNS UDP"
    )
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p tcp --dport 53 -j DNAT --to-destination {ip_servidor}:53",
        f"Redirigir DNS TCP"
    )
    
    # 9. Por defecto, enviar a la cadena CAPTIVE_PORTAL
    print("\n8️⃣  Enviando tráfico no autenticado a CAPTIVE_PORTAL...")
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p tcp -m multiport --dports 80,443 -j CAPTIVE_PORTAL",
        f"Tráfico web → CAPTIVE_PORTAL"
    )
    
    # 10. FORWARD: Permitir conexiones establecidas
    print("\n9️⃣  Permitiendo respuestas (ESTABLISHED/RELATED)...")
    ejecutar(
        f"iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT",
        f"Permitir respuestas"
    )
    
    # 11. FORWARD: Permitir acceso al portal (todos)
    print("\n🔟 Permitiendo acceso al servidor portal...")
    ejecutar(
        f"iptables -A FORWARD -i {hotspot} -d {ip_servidor} -j ACCEPT",
        f"Permitir acceso al portal"
    )
    
    # 12. Localhost
    print("\n1️⃣1️⃣  Permitiendo localhost...")
    ejecutar("iptables -A INPUT -i lo -j ACCEPT", "INPUT localhost")
    ejecutar("iptables -A OUTPUT -o lo -j ACCEPT", "OUTPUT localhost")
    
    # 13. Las IPs autenticadas se agregarán dinámicamente AQUÍ
    print("\n1️⃣2️⃣  Espacio para IPs autenticadas (dinámico)...")
    print("   → Las IPs autenticadas se agregarán con:")
    print("   → iptables -t nat -I PREROUTING 1 -s [IP] -j ACCEPT")
    print("   → iptables -I FORWARD 1 -s [IP] -j ACCEPT")
    
    # VERIFICAR
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print(f"\n📍 IP del portal: {ip_servidor}")
    print("   ⚠️  Actualiza esta IP en config.py:")
    print(f"   PORTAL_IP = \"{ip_servidor}\"")
    
    print("\n📋 REGLAS NAT:")
    subprocess.run("iptables -t nat -L -n -v --line-numbers", shell=True)
    
    print("\n📋 REGLAS FORWARD:")
    subprocess.run("iptables -L FORWARD -n -v --line-numbers", shell=True)
    
    print("\n" + "="*60)
    print("🔑 FUNCIONAMIENTO:")
    print("   1. Usuario NO autenticado:")
    print("      → HTTP/HTTPS → Cadena CAPTIVE_PORTAL → Portal")
    print("   2. Usuario autenticado:")
    print("      → Regla en PREROUTING -s [IP] -j ACCEPT")
    print("      → SALTA la cadena CAPTIVE_PORTAL")
    print("      → Acceso directo a internet")
    print("="*60)
    
    print("\n✅ LISTO PARA EJECUTAR:")
    print("   sudo python3 main.py")
    print("="*60 + "\n")