#!/usr/bin/env python3
"""
dns_server.py - Servidor DNS que redirige todo a la IP del portal
Responde a TODAS las consultas DNS con la IP del servidor portal
"""

import socket
import struct
import threading
from config import sesiones_activas, sesiones_lock, PORTAL_IP

DNS_PORT = 53

# =========================================================
# FUNCIÓN: PARSEAR CONSULTA DNS
# =========================================================

def parsear_dns_query(data):
    """Extrae el dominio consultado de una query DNS"""
    try:
        # Saltar header (12 bytes)
        pos = 12
        domain_parts = []
        
        while True:
            length = data[pos]
            if length == 0:
                break
            pos += 1
            domain_parts.append(data[pos:pos+length].decode('utf-8'))
            pos += length
        
        domain = '.'.join(domain_parts)
        return domain
    except:
        return "unknown"

# =========================================================
# FUNCIÓN: CREAR RESPUESTA DNS
# =========================================================

def crear_respuesta_dns(data, ip_destino):
    """Crea una respuesta DNS apuntando al portal"""
    try:
        # Copiar Transaction ID (primeros 2 bytes)
        transaction_id = data[0:2]
        
        # Flags: Standard query response, No error
        flags = b'\x81\x80'
        
        # Questions: 1, Answers: 1, Authority: 0, Additional: 0
        counts = b'\x00\x01\x00\x01\x00\x00\x00\x00'
        
        # Question section (copiar desde la query original)
        # Encontrar donde termina el nombre de dominio
        pos = 12
        while data[pos] != 0:
            pos += data[pos] + 1
        pos += 5  # Incluir null byte + type + class
        
        question = data[12:pos]
        
        # Answer section
        # Name pointer (apunta al nombre en la question)
        name_pointer = b'\xc0\x0c'
        
        # Type A (IPv4)
        answer_type = b'\x00\x01'
        
        # Class IN
        answer_class = b'\x00\x01'
        
        # TTL (60 segundos)
        ttl = b'\x00\x00\x00\x3c'
        
        # Data length (4 bytes para IPv4)
        data_length = b'\x00\x04'
        
        # IP address
        ip_bytes = socket.inet_aton(ip_destino)
        
        answer = name_pointer + answer_type + answer_class + ttl + data_length + ip_bytes
        
        # Construir respuesta completa
        response = transaction_id + flags + counts + question + answer
        
        return response
    except Exception as e:
        print(f"❌ Error creando respuesta DNS: {e}")
        return None

# =========================================================
# FUNCIÓN: VERIFICAR SI IP ESTÁ AUTENTICADA
# =========================================================

def ip_autenticada(ip_cliente):
    """Verifica si una IP ya está autenticada"""
    with sesiones_lock:
        return ip_cliente in sesiones_activas and sesiones_activas[ip_cliente].get("autenticado", False)

# =========================================================
# FUNCIÓN: MANEJAR CONSULTA DNS
# =========================================================

def manejar_consulta_dns(data, addr, sock):
    """Procesa una consulta DNS y envía respuesta"""
    ip_cliente = addr[0]
    dominio = parsear_dns_query(data)
    
    # Si la IP ya está autenticada, dejar pasar (no responder)
    if ip_autenticada(ip_cliente):
        print(f"🌐 DNS: {ip_cliente} -> {dominio} [AUTENTICADO - SIN RESPUESTA]")
        return
    
    # Si NO está autenticada, redirigir al portal
    print(f"🔀 DNS: {ip_cliente} -> {dominio} [REDIRIGIR A PORTAL]")
    
    respuesta = crear_respuesta_dns(data, PORTAL_IP)
    
    if respuesta:
        try:
            sock.sendto(respuesta, addr)
            print(f"   ✅ Redirigido a {PORTAL_IP}")
        except Exception as e:
            print(f"   ❌ Error enviando respuesta: {e}")

# =========================================================
# FUNCIÓN: INICIAR SERVIDOR DNS
# =========================================================

def iniciar_servidor_dns():
    """Inicia el servidor DNS en el puerto 53"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('0.0.0.0', DNS_PORT))
        print(f"🌐 Servidor DNS activo en puerto {DNS_PORT}")
        print(f"   Redirigiendo a: {PORTAL_IP}\n")
        
        while True:
            data, addr = sock.recvfrom(512)
            
            # Procesar en hilo separado para no bloquear
            threading.Thread(
                target=manejar_consulta_dns,
                args=(data, addr, sock),
                daemon=True
            ).start()
            
    except PermissionError:
        print(f"❌ Necesitas sudo para puerto {DNS_PORT}")
        print(f"   sudo python3 main.py")
    except Exception as e:
        print(f"❌ Error en servidor DNS: {e}")
    finally:
        sock.close()

# =========================================================
# EJECUTAR (SOLO PARA PRUEBAS)
# =========================================================

if __name__ == "__main__":
    iniciar_servidor_dns()