#!/usr/bin/env python3
"""
request_handler.py - Manejador de peticiones HTTP
Ahora incluye panel de administración y gestión de usuarios
CON SOPORTE PARA DETECCIÓN AUTOMÁTICA DE PORTALES CAUTIVOS
"""

import json
from http_utils import obtener_ip_cliente, parsear_peticion, parsear_formulario, enviar_respuesta, enviar_json, enviar_redireccion
from html_templates import HTML_LOGIN, HTML_EXITO, HTML_ERROR, HTML_LOGOUT
from admin_templates import generar_panel_admin, HTML_ACCESS_DENIED
from auth import validar_credenciales, obtener_rol, registrar_sesion, cerrar_sesion, es_admin, obtener_usuario_ip
from firewall import autorizar_ip, desautorizar_ip
from config import sesiones_activas, sesiones_lock, PORTAL_IP
from user_manager import agregar_usuario, eliminar_usuario, listar_usuarios

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
        
        # Si no se pudo parsear (datos encriptados HTTPS), redirigir
        if metodo is None or ruta is None:
            print(f"⚠️  Datos encriptados detectados (HTTPS)")
            print(f"   → Cerrando conexión (el navegador reintentará con HTTP)")
            return
        
        print(f"📨 {metodo} {ruta}")
        
        # =====================================================
        # DETECCIÓN AUTOMÁTICA DE PORTALES CAUTIVOS
        # =====================================================
        
        # Android/Chrome: /generate_204
        if ruta == "/generate_204" or ruta == "/gen_204":
            print(f"   → Detección de portal (Android/Chrome)")
            # Verificar si ya está autenticado
            with sesiones_lock:
                autenticado = ip_cliente in sesiones_activas
            
            if autenticado:
                # Ya autenticado: responder 204 (sin portal)
                print(f"   ✅ Usuario autenticado, responder 204")
                enviar_respuesta(socket_cliente, "204 No Content", "")
            else:
                # No autenticado: redirigir al portal
                print(f"   🔀 Redirigir al portal de login")
                enviar_redireccion(socket_cliente, f"http://{PORTAL_IP}/")
            return
        
        # iOS: /hotspot-detect.html
        if ruta == "/hotspot-detect.html" or ruta == "/library/test/success.html":
            print(f"   → Detección de portal (iOS)")
            with sesiones_lock:
                autenticado = ip_cliente in sesiones_activas
            
            if autenticado:
                print(f"   ✅ Usuario autenticado, responder Success")
                enviar_respuesta(socket_cliente, "200 OK", "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>")
            else:
                print(f"   🔀 Redirigir al portal de login")
                enviar_redireccion(socket_cliente, f"http://{PORTAL_IP}/")
            return
        
        # Windows: /ncsi.txt, /connecttest.txt
        if ruta == "/ncsi.txt" or ruta == "/connecttest.txt":
            print(f"   → Detección de portal (Windows)")
            with sesiones_lock:
                autenticado = ip_cliente in sesiones_activas
            
            if autenticado:
                print(f"   ✅ Usuario autenticado, responder Microsoft NCSI")
                enviar_respuesta(socket_cliente, "200 OK", "Microsoft NCSI")
            else:
                print(f"   🔀 Redirigir al portal de login")
                enviar_redireccion(socket_cliente, f"http://{PORTAL_IP}/")
            return
        
        # =====================================================
        # RUTAS NORMALES DEL PORTAL
        # =====================================================
        
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
                role = obtener_rol(usuario, password)
                registrar_sesion(ip_cliente, usuario, role)
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
        
        # RUTA: GET /admin (panel de administración)
        elif metodo == "GET" and ruta == "/admin":
            print(f"   → Panel Admin")
            if es_admin(ip_cliente):
                usuarios = listar_usuarios()
                with sesiones_lock:
                    sesiones_copy = dict(sesiones_activas)
                html = generar_panel_admin(usuarios, sesiones_copy)
                enviar_respuesta(socket_cliente, "200 OK", html)
            else:
                print(f"   ❌ Acceso denegado")
                enviar_respuesta(socket_cliente, "403 Forbidden", HTML_ACCESS_DENIED)
        
        # RUTA: POST /admin/add_user (agregar usuario desde panel)
        elif metodo == "POST" and ruta == "/admin/add_user":
            print(f"   → Admin: Agregar usuario")
            if not es_admin(ip_cliente):
                print(f"   ❌ Acceso denegado (no es admin)")
                enviar_json(socket_cliente, {"success": False, "message": "Acceso denegado"})
                return
            
            formulario = parsear_formulario(body)
            usuario = formulario.get('usuario', '').strip()
            password = formulario.get('password', '').strip()
            role = formulario.get('role', 'user').strip()
            
            print(f"   → Datos: usuario='{usuario}', role='{role}'")
            
            if not usuario or not password:
                print(f"   ❌ Datos incompletos")
                enviar_json(socket_cliente, {"success": False, "message": "Usuario y contraseña son requeridos"})
                return
            
            exito, mensaje = agregar_usuario(usuario, password, role)
            print(f"   → Resultado: {exito} - {mensaje}")
            enviar_json(socket_cliente, {"success": exito, "message": mensaje})
        
        # RUTA: POST /admin/delete_user (eliminar usuario desde panel)
        elif metodo == "POST" and ruta == "/admin/delete_user":
            print(f"   → Admin: Eliminar usuario")
            if not es_admin(ip_cliente):
                print(f"   ❌ Acceso denegado (no es admin)")
                enviar_json(socket_cliente, {"success": False, "message": "Acceso denegado"})
                return
            
            formulario = parsear_formulario(body)
            usuario = formulario.get('usuario', '').strip()
            
            print(f"   → Usuario a eliminar: '{usuario}'")
            
            if not usuario:
                print(f"   ❌ Usuario vacío")
                enviar_json(socket_cliente, {"success": False, "message": "Usuario requerido"})
                return
            
            exito, mensaje = eliminar_usuario(usuario)
            print(f"   → Resultado: {exito} - {mensaje}")
            enviar_json(socket_cliente, {"success": exito, "message": mensaje})
        
        # RUTA: POST /admin/disconnect_ip (desconectar IP desde panel)
        elif metodo == "POST" and ruta == "/admin/disconnect_ip":
            print(f"   → Admin: Desconectar IP")
            if not es_admin(ip_cliente):
                print(f"   ❌ Acceso denegado (no es admin)")
                enviar_json(socket_cliente, {"success": False, "message": "Acceso denegado"})
                return
            
            formulario = parsear_formulario(body)
            ip = formulario.get('ip', '').strip()
            
            print(f"   → IP a desconectar: '{ip}'")
            
            if not ip:
                print(f"   ❌ IP vacía")
                enviar_json(socket_cliente, {"success": False, "message": "IP requerida"})
                return
            
            with sesiones_lock:
                existe = ip in sesiones_activas
            
            if existe:
                cerrar_sesion(ip)
                desautorizar_ip(ip)
                print(f"   ✅ IP desconectada")
                enviar_json(socket_cliente, {"success": True, "message": f"IP {ip} desconectada"})
            else:
                print(f"   ❌ IP no encontrada")
                enviar_json(socket_cliente, {"success": False, "message": "IP no encontrada"})
        
        # RUTA: GET /status (ver sesiones - debug)
        elif metodo == "GET" and ruta == "/status":
            print(f"   → Status")
            with sesiones_lock:
                html = f"<h1>Sesiones</h1><pre>{json.dumps(sesiones_activas, indent=2)}</pre>"
            enviar_respuesta(socket_cliente, "200 OK", html)
        
        else:
            print(f"   → Redirigir al login (ruta desconocida)")
            enviar_redireccion(socket_cliente, f"http://{PORTAL_IP}/")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    finally:
        socket_cliente.close()
        print(f"⬅️  Desconectado: {ip_cliente}")