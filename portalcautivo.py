#!/usr/bin/env python3
"""
Portal Cautivo - Servidor Web HTTP
Fase 1: Servidor básico + Lógica de usuarios
"""

import socket
import threading
import time
from datetime import datetime

# =====================================================================
# ESTRUCTURAS DE DATOS
# =====================================================================

# 1. CUENTAS DE USUARIO (nombre, contraseña)
VALID_ACCOUNTS = {
    "admin": "password123",
    "user1": "user123",
    "test": "test"
}

# 2. SESIONES ACTIVAS (IP -> {timestamp, estado})
active_sessions = {}
sessions_lock = threading.Lock()  # Para acceso seguro en hilos

# =====================================================================
# FUNCIONES DE UTILIDAD
# =====================================================================

def validate_credentials(username, password):
    """Valida credenciales contra VALID_ACCOUNTS"""
    if username in VALID_ACCOUNTS:
        return VALID_ACCOUNTS[username] == password
    return False

def get_client_ip(client_socket):
    """Extrae la IP del cliente del socket"""
    try:
        return client_socket.getpeername()[0]
    except:
        return "UNKNOWN"

def register_session(client_ip):
    """Registra una IP autenticada en sesiones activas"""
    with sessions_lock:
        active_sessions[client_ip] = {
            'timestamp': datetime.now().isoformat(),
            'estado': 'autenticado'
        }
    print(f"[SESSION] IP {client_ip} autenticada y registrada")

def is_session_active(client_ip):
    """Verifica si una IP tiene sesión activa"""
    with sessions_lock:
        return client_ip in active_sessions

def list_active_sessions():
    """Lista todas las sesiones activas"""
    with sessions_lock:
        return dict(active_sessions)

# =====================================================================
# PÁGINAS HTML
# =====================================================================

LOGIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Portal Cautivo - Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: red; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Portal Cautivo</h1>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Iniciar Sesión</button>
        </form>
        <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
            Cuentas de prueba:<br>
            admin / password123<br>
            user1 / user123
        </p>
    </div>
</body>
</html>"""

SUCCESS_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>¡Autenticado!</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 8px; text-align: center; }
        h1 { color: #28a745; }
        p { color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ ¡Autenticado!</h1>
        <p>Tu IP ha sido registrada y deberá ser desbloqueada en el firewall.</p>
        <p>Ahora puedes acceder a Internet.</p>
    </div>
</body>
</html>"""

# =====================================================================
# MANEJO DE CONEXIONES HTTP
# =====================================================================

def parse_http_request(data):
    """Parsea una petición HTTP básica"""
    try:
        lines = data.decode('utf-8').split('\r\n')
        first_line = lines[0].split()
        method = first_line[0]
        path = first_line[1]
        
        # Parsear body si es POST
        body = ""
        if method == "POST" and len(lines) > 0:
            # El body está después de una línea vacía
            for i, line in enumerate(lines):
                if line == "":
                    body = "\r\n".join(lines[i+1:])
                    break
        
        return method, path, body
    except:
        return None, None, None

def parse_post_data(body):
    """Parsea datos de formulario POST (application/x-www-form-urlencoded)"""
    data = {}
    if body:
        pairs = body.split('&')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                # Decodificar URL encoding básico
                value = value.replace('+', ' ')
                data[key] = value
    return data

def send_http_response(client_socket, status, content_type, body):
    """Envía una respuesta HTTP completa"""
    response = f"""HTTP/1.1 {status}
Content-Type: {content_type}
Content-Length: {len(body)}
Connection: close

{body}"""
    client_socket.sendall(response.encode('utf-8'))

def handle_client(client_socket, client_address):
    """Maneja una conexión de cliente (ejecutado en un hilo)"""
    client_ip = get_client_ip(client_socket)
    print(f"[CONEXION] Cliente conectado desde {client_ip}")
    
    try:
        # Recibir datos
        data = client_socket.recv(4096)
        if not data:
            return
        
        method, path, body = parse_http_request(data)
        print(f"[REQUEST] {method} {path} desde {client_ip}")
        
        # GET / -> Mostrar login
        if method == "GET" and path == "/":
            send_http_response(client_socket, "200 OK", "text/html", LOGIN_PAGE)
        
        # POST /login -> Procesar login
        elif method == "POST" and path == "/login":
            post_data = parse_post_data(body)
            username = post_data.get('username', '')
            password = post_data.get('password', '')
            
            print(f"[LOGIN] Intento de login: {username} desde {client_ip}")
            
            if validate_credentials(username, password):
                print(f"[AUTH] ✅ Credenciales válidas para {username} ({client_ip})")
                register_session(client_ip)
                send_http_response(client_socket, "200 OK", "text/html", SUCCESS_PAGE)
            else:
                print(f"[AUTH] ❌ Credenciales inválidas para {username} ({client_ip})")
                error_page = LOGIN_PAGE.replace("</form>", 
                    '<p class="error">❌ Usuario o contraseña incorrectos</p></form>')
                send_http_response(client_socket, "401 Unauthorized", "text/html", error_page)
        
        # GET /status -> Ver sesiones activas (para debug)
        elif method == "GET" and path == "/status":
            sessions = list_active_sessions()
            status_html = f"""<html><body>
            <h1>Estado del Portal</h1>
            <p>Sesiones activas: {len(sessions)}</p>
            <pre>{sessions}</pre>
            </body></html>"""
            send_http_response(client_socket, "200 OK", "text/html", status_html)
        
        else:
            send_http_response(client_socket, "404 Not Found", "text/html", 
                             "<html><body><h1>404</h1></body></html>")
    
    except Exception as e:
        print(f"[ERROR] {e}")
    
    finally:
        client_socket.close()
        print(f"[DESCONEXION] Cliente {client_ip} desconectado")

# =====================================================================
# SERVIDOR PRINCIPAL
# =====================================================================

def start_server(host='0.0.0.0', port=80):
    """Inicia el servidor HTTP en modo multihilo"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[SERVIDOR] Escuchando en {host}:{port}")
        print(f"[SERVIDOR] Abre http://localhost en tu navegador")
        print("[SERVIDOR] Presiona Ctrl+C para detener\n")
        
        while True:
            client_socket, client_address = server_socket.accept()
            # Crear un hilo para cada cliente
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Apagando...")
    except PermissionError:
        print(f"[ERROR] Necesitas permisos de administrador para usar puerto {port}")
        print("       En Linux/Mac: sudo python3 script.py")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()