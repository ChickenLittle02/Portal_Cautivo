#!/usr/bin/env python3
"""
firewall_config.py - Configuración de reglas de firewall
"""

import subprocess
from setup_utils import ejecutar

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
