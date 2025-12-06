#!/bin/bash

# =============================================
# FIREWALL PARA PORTAL CAUTIVO
#   Hotspot: wlo1
#   Internet: enx32d53edd8df7
# =============================================

HOTSPOT="wlo1"
WAN="enx32d53edd8df7"

echo "=============================================="
echo "🔥 Iniciando configuración de firewall"
echo "=============================================="

# 0. Verificar root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Debes ejecutar como root: sudo bash firewall_cautivo.sh"
   exit 1
fi

# ---------------------------------------------------
# 1. LIMPIAR CONFIGURACIÓN ANTERIOR
# ---------------------------------------------------
echo "🔹 Limpiando reglas anteriores..."
iptables -F
iptables -F INPUT
iptables -F OUTPUT
iptables -F FORWARD
iptables -t nat -F


#para verificar los cambios

#ver reglas actuales de la tabla filter
# sudo iptables -L -n -v

#ver reglas actuales de la tabla nat
# sudo iptables -t nat -L -n -v

# ver politicas por defecto
# sudo iptables -S






# ---------------------------------------------------
# 2. ACEPTAR LOOPBACK
# ---------------------------------------------------
echo "🔹 Permitiendo loopback..."
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# ---------------------------------------------------
# 3. ACEPTAR TRÁFICO ESTABLECIDO (conntrack)
# ---------------------------------------------------
echo "🔹 Permitiendo tráfico ESTABLISHED,RELATED..."
iptables -A INPUT  -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# ---------------------------------------------------
# 4. PERMITIR SSH (importante si usas remoto)
# ---------------------------------------------------
echo "🔹 Permitiendo SSH (tcp/22) para evitar bloqueo propio..."
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT

# ---------------------------------------------------
# 5. PERMITIR PING (ICMP) DESDE EL HOTSPOT
# ---------------------------------------------------
echo "🔹 Permitiendo ICMP (ping) desde hotspot..."
iptables -A INPUT  -i $HOTSPOT -p icmp -m limit --limit 5/second -j ACCEPT
iptables -A OUTPUT -o $HOTSPOT -p icmp -j ACCEPT

# ---------------------------------------------------
# 6. PERMITIR EL PORTAL HTTP (puerto 80)
# ---------------------------------------------------
echo "🔹 Permitiendo acceso al portal cautivo (HTTP 80)..."
iptables -A INPUT -i $HOTSPOT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT

# ---------------------------------------------------
# 7. PERMITIR DNS (para el HOST)
# ---------------------------------------------------
echo "🔹 Permitiendo DNS para el sistema..."
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT  -p udp --sport 53 -j ACCEPT

# ---------------------------------------------------
# 8. HABILITAR IP FORWARDING
# ---------------------------------------------------
echo "🔹 Activando IP Forward..."
sysctl -w net.ipv4.ip_forward=1 >/dev/null

# ---------------------------------------------------
# 9. CONFIGURAR NAT (MASCARADE)
# ---------------------------------------------------
echo "🔹 Configurando NAT MASQUERADE..."
iptables -t nat -A POSTROUTING -o $WAN -j MASQUERADE

# ---------------------------------------------------
# 10. PERMITIR FORWARDING CLIENTE→INTERNET
# ---------------------------------------------------
echo "🔹 Permitiendo forwarding del hotspot hacia Internet..."
iptables -A FORWARD -i $HOTSPOT -o $WAN -j ACCEPT

# (las respuestas ya están permitidas por ESTABLISHED,RELATED)

# ---------------------------------------------------
# 11. PREPARAR SISTEMA PARA USUARIOS AUTENTICADOS
# ---------------------------------------------------
echo "🔹 Creando conjunto de IPs autorizadas (ipset)..."

ipset destroy clientes_auth 2>/dev/null
ipset create clientes_auth hash:ip

# regla para que IPs autenticadas tengan internet completo
iptables -I FORWARD 1 -m set --match-set clientes_auth src -j ACCEPT

echo "   ✔ Cuando un usuario se autentique:"
echo "       sudo ipset add clientes_auth <IP_DEL_CLIENTE>"
echo "   ✔ Cuando un usuario cierre sesión:"
echo "       sudo ipset del clientes_auth <IP_DEL_CLIENTE>"

# ---------------------------------------------------
# 12. POLÍTICAS POR DEFECTO (BLOQUEAR TODO)
# ---------------------------------------------------
echo "🔹 Estableciendo políticas por defecto (DROP)..."
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

echo "=============================================="
echo "✅ Firewall configurado correctamente"
echo "=============================================="

echo "📌 Para ver las reglas:"
echo "    iptables -L -n"
echo "    iptables -t nat -L -n"
echo "    ipset list clientes_auth"

exit 0
