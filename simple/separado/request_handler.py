#!/usr/bin/env python3
"""
request_handler.py - Manejador de peticiones HTTP
"""

from http_utils import obtener_ip_cliente, parsear_peticion, parsear_formulario, enviar_respuesta
from html_templates import HTML_LOGIN, HTML_EXITO, HTML_ERROR, HTML_LOGOUT
from auth import validar_credenciales, registrar_sesion, cerrar_sesion
from firewall import autorizar_ip, desautorizar_ip
from config import sesiones_activas, sesiones_lock

# =========================================================
# FUNCIÓN: MANEJAR CLIENTE
# =========================================================

def manejar_cliente(socket_cliente, direccion):
    """Maneja una conexión de cliente (en un hilo)"""
    ip_cliente = obtener_ip_cliente(socket_cliente)
    print(f"\n➡️  Cliente: {ip_cliente}")
    
    try:
        datos = socket_cliente.recv(4096)
        if not datos:
            return
        
        metodo, ruta, body = parsear_peticion(datos)
        print(f"📨 {metodo} {ruta}")
        
        # RUTA: GET / (mostrar login)
        if metodo == "GET" and ruta == "/":
            print(f"   → Enviando login")
            enviar_respuesta(socket_cliente, "200 OK", HTML_LOGIN)
        
        # RUTA: POST /login (procesar login)
        elif metodo == "POST" and ruta == "/login":
            formulario = parsear_formulario(body)
            usuario = formulario.get('usuario', '')
            password = formulario.get('password', '')
            
            print(f"   → Usuario: '{usuario}'")
            
            if validar_credenciales(usuario, password):
                print(f"   ✅ VÁLIDO")
                registrar_sesion(ip_cliente)
                autorizar_ip(ip_cliente)
                enviar_respuesta(socket_cliente, "200 OK", HTML_EXITO)
            else:
                print(f"   ❌ INVÁLIDO")
                enviar_respuesta(socket_cliente, "401 Unauthorized", HTML_ERROR)
        
        # RUTA: GET /logout (cerrar sesión)
        elif metodo == "GET" and ruta == "/logout":
            print(f"   → Logout")
            cerrar_sesion(ip_cliente)
            desautorizar_ip(ip_cliente)
            enviar_respuesta(socket_cliente, "200 OK", HTML_LOGOUT)
        
        # RUTA: GET /status (ver sesiones)
        elif metodo == "GET" and ruta == "/status":
            print(f"   → Status")
            with sesiones_lock:
                html = f"<h1>Sesiones</h1><pre>{str(sesiones_activas)}</pre>"
            enviar_respuesta(socket_cliente, "200 OK", html)
        
        else:
            print(f"   → 404")
            enviar_respuesta(socket_cliente, "404 Not Found", "<h1>404</h1>")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    finally:
        socket_cliente.close()
        print(f"⬅️  Desconectado: {ip_cliente}")
