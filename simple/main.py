#!/usr/bin/env python3
"""
Portal Cautivo - Servidor Principal V2
Solo usa librerías estándar de Python
"""

import socket
import threading
import subprocess
import os

# =========================================================
# CONFIGURACIÓN
# =========================================================

PUERTO = 80
HOST = '0.0.0.0'

# Cuentas de usuario
CUENTAS = {
    "admin": "123456",
    "user1": "pass1"
}

# IPs autenticadas
sesiones_activas = {}
sesiones_lock = threading.Lock()

# =========================================================
# FUNCIÓN: OBTENER IP DEL CLIENTE
# =========================================================

def obtener_ip_cliente(socket_cliente):
    """Extrae la IP del cliente del socket"""
    try:
        return socket_cliente.getpeername()[0]
    except:
        return "DESCONOCIDA"

# =========================================================
# FUNCIÓN: EJECUTAR COMANDO IPTABLES
# =========================================================

def ejecutar_iptables(comando):
    """Ejecuta un comando iptables"""
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return resultado.returncode == 0
    except:
        return False

# =========================================================
# FUNCIÓN: VALIDAR CREDENCIALES
# =========================================================

def validar_credenciales(usuario, password):
    """Valida usuario y contraseña"""
    if usuario in CUENTAS:
        return CUENTAS[usuario] == password
    return False

# =========================================================
# FUNCIÓN: REGISTRAR SESIÓN
# =========================================================

def registrar_sesion(ip_cliente):
    """Registra una IP autenticada"""
    with sesiones_lock:
        sesiones_activas[ip_cliente] = "autenticado"
    print(f"✅ Sesión registrada: {ip_cliente}")

# =========================================================
# FUNCIÓN: AUTORIZAR IP EN FIREWALL
# =========================================================

def autorizar_ip(ip_cliente):
    """
    Autoriza una IP en iptables con DOS reglas:
    1. Permite salida: FORWARD -s <IP> -j ACCEPT
    2. Permite respuesta: FORWARD -d <IP> -m state -j ACCEPT
    Se ejecuta en hilo separado para no bloquear
    """
    def _ejecutar():
        print(f"🔓 Autorizando {ip_cliente}...")
        
        # Regla 1: Salida
        cmd1 = f"sudo iptables -A FORWARD -s {ip_cliente} -j ACCEPT"
        if ejecutar_iptables(cmd1):
            print(f"   → Regla 1 OK")
        else:
            print(f"   → Regla 1 FALLO")
            return
        
        # Regla 2: Respuesta
        cmd2 = f"sudo iptables -A FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
        if ejecutar_iptables(cmd2):
            print(f"   → Regla 2 OK")
        else:
            print(f"   → Regla 2 FALLO")
        
        print(f"✅ {ip_cliente} AUTORIZADA")
    
    hilo = threading.Thread(target=_ejecutar, daemon=True)
    hilo.start()

# =========================================================
# FUNCIÓN: DESAUTORIZAR IP EN FIREWALL
# =========================================================

def desautorizar_ip(ip_cliente):
    """
    Desautoriza una IP en iptables (la elimina)
    Se ejecuta en hilo separado
    """
    def _ejecutar():
        print(f"🔒 Desautorizando {ip_cliente}...")
        
        # Regla 1: Salida
        cmd1 = f"sudo iptables -D FORWARD -s {ip_cliente} -j ACCEPT"
        ejecutar_iptables(cmd1)
        
        # Regla 2: Respuesta
        cmd2 = f"sudo iptables -D FORWARD -d {ip_cliente} -m state --state ESTABLISHED,RELATED -j ACCEPT"
        ejecutar_iptables(cmd2)
        
        print(f"✅ {ip_cliente} DESAUTORIZADA")
    
    hilo = threading.Thread(target=_ejecutar, daemon=True)
    hilo.start()

# =========================================================
# FUNCIÓN: CERRAR SESIÓN
# =========================================================

def cerrar_sesion(ip_cliente):
    """Elimina sesión de IP"""
    with sesiones_lock:
        if ip_cliente in sesiones_activas:
            del sesiones_activas[ip_cliente]
    print(f"❌ Sesión cerrada: {ip_cliente}")

# =========================================================
# PÁGINA HTML: LOGIN
# =========================================================

HTML_LOGIN = """<!DOCTYPE html>
<html>
<head>
    <title>Portal Cautivo</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .caja { max-width: 350px; margin: 100px auto; background: white; 
                padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px #ccc; }
        h1 { text-align: center; color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; 
                border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; 
                 border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="caja">
        <h1>🔐 Portal Cautivo</h1>
        <form method="POST" action="/login">
            <input type="text" name="usuario" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Iniciar Sesión</button>
        </form>
        <p style="text-align: center; font-size: 12px; color: #666;">
            Prueba: admin / 123456
        </p>
    </div>
</body>
</html>"""

# =========================================================
# PÁGINA HTML: ÉXITO
# =========================================================

HTML_EXITO = """<!DOCTYPE html>
<html>
<head>
    <title>¡Autenticado!</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .caja { max-width: 350px; margin: 100px auto; background: white; 
                padding: 30px; border-radius: 8px; text-align: center; }
        h1 { color: #28a745; }
    </style>
</head>
<body>
    <div class="caja">
        <h1>✅ ¡Acceso Permitido!</h1>
        <p>Tu IP ha sido autorizada en el firewall.</p>
        <p>Ahora puedes acceder a Internet.</p>
        <p><a href="/logout">Cerrar Sesión</a></p>
    </div>
</body>
</html>"""

# =========================================================
# PÁGINA HTML: ERROR
# =========================================================

HTML_ERROR = """<!DOCTYPE html>
<html>
<body>
    <h1>❌ Error de Autenticación</h1>
    <p>Usuario o contraseña incorrectos</p>
    <p><a href="/">Volver</a></p>
</body>
</html>"""

# =========================================================
# PÁGINA HTML: LOGOUT
# =========================================================

HTML_LOGOUT = """<!DOCTYPE html>
<html>
<body>
    <h1>✅ Sesión Cerrada</h1>
    <p>Tu IP ha sido bloqueada.</p>
    <p><a href="/">Volver al login</a></p>
</body>
</html>"""

# =========================================================
# FUNCIÓN: PARSEAR PETICIÓN HTTP
# =========================================================

def parsear_peticion(datos):
    """Parsea una petición HTTP"""
    try:
        texto = datos.decode('utf-8')
        lineas = texto.split('\r\n')
        
        primera_linea = lineas[0].split()
        metodo = primera_linea[0]
        ruta = primera_linea[1]
        
        body = ""
        for i, linea in enumerate(lineas):
            if linea == "":
                if i + 1 < len(lineas):
                    body = lineas[i + 1]
                break
        
        return metodo, ruta, body
    except:
        return None, None, None

# =========================================================
# FUNCIÓN: PARSEAR FORMULARIO
# =========================================================

def parsear_formulario(body):
    """Parsea datos de formulario POST"""
    datos = {}
    if body:
        body = body.strip()
        for par in body.split('&'):
            if '=' in par:
                clave, valor = par.split('=', 1)
                datos[clave.strip()] = valor.strip()
    return datos

# =========================================================
# FUNCIÓN: ENVIAR RESPUESTA HTTP
# =========================================================

def enviar_respuesta(socket_cliente, codigo, contenido):
    """Envía respuesta HTTP"""
    respuesta = f"""HTTP/1.1 {codigo}
Content-Type: text/html; charset=utf-8
Content-Length: {len(contenido)}
Connection: close

{contenido}"""
    socket_cliente.sendall(respuesta.encode('utf-8'))

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

# =========================================================
# FUNCIÓN: INICIAR SERVIDOR
# =========================================================

def iniciar_servidor():
    """Inicia el servidor HTTP"""
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        socket_servidor.bind((HOST, PUERTO))
        socket_servidor.listen(5)
        print(f"\n🚀 Servidor Portal Cautivo")
        print(f"   Puerto: {PUERTO}")
        print(f"   Abre: http://localhost")
        print(f"   (Presiona Ctrl+C para detener)\n")
        
        while True:
            socket_cliente, direccion = socket_servidor.accept()
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(socket_cliente, direccion),
                daemon=True
            )
            hilo.start()
    
    except PermissionError:
        print(f"❌ Necesitas sudo para puerto {PUERTO}")
        print(f"   sudo python3 main.py")
    except KeyboardInterrupt:
        print(f"\n🛑 Servidor detenido")
    finally:
        socket_servidor.close()

# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    iniciar_servidor()