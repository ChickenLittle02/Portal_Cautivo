#!/usr/bin/env python3
"""
firewall_config.py - Configuración de reglas de firewall
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
    ejecutar(
        f"iptables -P FORWARD DROP",
        f"Politica predeterminada de portal cautivo"
    )
    ejecutar(
        f"iptables -F FORWARD",
        f"Elimina toda ruta de compartir internet"
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
    
    # Obtener IP del servidor (interfaz hotspot)
    ip_servidor = obtener_ip_interfaz(hotspot)
    
    # 9. REDIRECCIÓN HTTP (captura de tráfico web)
    print("\n9️⃣  Configurando redirección HTTP al portal...")
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p tcp --dport 80 -j DNAT --to-destination {ip_servidor}:80",
        f"Redirigir HTTP al portal ({ip_servidor}:80)"
    )
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p tcp --dport 443 -j DNAT --to-destination {ip_servidor}:80",
        f"Redirigir HTTPS al portal ({ip_servidor}:80)"
    )
    
    # 10. REDIRECCIÓN DNS (captura de consultas DNS)
    print("\n🔟 Configurando redirección DNS al servidor local...")
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p udp --dport 53 -j DNAT --to-destination {ip_servidor}:53",
        f"Redirigir DNS UDP al servidor ({ip_servidor}:53)"
    )
    ejecutar(
        f"iptables -t nat -A PREROUTING -i {hotspot} -p tcp --dport 53 -j DNAT --to-destination {ip_servidor}:53",
        f"Redirigir DNS TCP al servidor ({ip_servidor}:53)"
    )
    
    # VERIFICAR
    print("\n" + "="*60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print(f"\n📍 IP del portal: {ip_servidor}")
    print("   ⚠️  IMPORTANTE: Actualiza esta IP en config.py:")
    print(f"   PORTAL_IP = \"{ip_servidor}\"")
    print("\n📋 REGLAS ACTUALES:")
    subprocess.run("echo '🔹 NAT PREROUTING:' && iptables -t nat -L PREROUTING -n", shell=True)
    subprocess.run("echo '\n🔹 FORWARD:' && iptables -L FORWARD -n", shell=True)
    
    print("\n" + "="*60)
    print("✅ LISTO PARA EJECUTAR:")
    print("   sudo python3 main.py")
    print("="*60 + "\n")