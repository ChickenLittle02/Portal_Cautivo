#!/usr/bin/env python3
"""
http_utils.py - Utilidades para manejo de HTTP
VERSIÓN CORREGIDA: Manejo correcto de URL-encoded y body multilinea
+ Soporte para redirecciones HTTP
"""

from urllib.parse import unquote

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
        
        # Buscar donde empieza el body (después de línea vacía)
        body = ""
        for i, linea in enumerate(lineas):
            if linea == "":
                # El body es todo lo que viene después
                if i + 1 < len(lineas):
                    # Unir todas las líneas del body (puede ser multilinea)
                    body = "\r\n".join(lineas[i + 1:])
                break
        
        return metodo, ruta, body
    
    except UnicodeDecodeError as e:
        # Datos encriptados (HTTPS) - no se pueden decodificar
        return None, None, None
    except Exception as e:
        print(f"Error en parsear_peticion: {e}")
        return None, None, None

# =========================================================
# FUNCIÓN: PARSEAR FORMULARIO
# =========================================================

def parsear_formulario(body):
    """Parsea datos de formulario POST (application/x-www-form-urlencoded)"""
    datos = {}
    
    if body:
        body = body.strip()
        # Dividir por &
        for par in body.split('&'):
            if '=' in par:
                clave, valor = par.split('=', 1)
                # IMPORTANTE: Decodificar URL-encoded values
                clave = unquote(clave.strip())
                valor = unquote(valor.strip())
                datos[clave] = valor
    
    return datos

# =========================================================
# FUNCIÓN: ENVIAR RESPUESTA HTTP
# =========================================================

def enviar_respuesta(socket_cliente, codigo, contenido):
    """Envía respuesta HTTP"""
    contenido_bytes = contenido.encode('utf-8')
    
    respuesta = f"""HTTP/1.1 {codigo}
Content-Type: text/html; charset=utf-8
Content-Length: {len(contenido_bytes)}
Connection: close

""".encode('utf-8')
    
    socket_cliente.sendall(respuesta + contenido_bytes)

# =========================================================
# FUNCIÓN: ENVIAR RESPUESTA JSON
# =========================================================

def enviar_json(socket_cliente, data):
    """Envía respuesta JSON"""
    import json
    
    contenido = json.dumps(data)
    contenido_bytes = contenido.encode('utf-8')
    
    respuesta = f"""HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: {len(contenido_bytes)}
Connection: close

""".encode('utf-8')
    
    socket_cliente.sendall(respuesta + contenido_bytes)

# =========================================================
# FUNCIÓN: ENVIAR REDIRECCIÓN HTTP
# =========================================================

def enviar_redireccion(socket_cliente, url_destino):
    """Envía una redirección HTTP 302"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={url_destino}">
    <title>Redirigiendo...</title>
</head>
<body>
    <h1>Redirigiendo al portal...</h1>
    <p>Si no eres redirigido automáticamente, <a href="{url_destino}">haz clic aquí</a>.</p>
</body>
</html>"""
    
    html_bytes = html.encode('utf-8')
    
    respuesta = f"""HTTP/1.1 302 Found
Location: {url_destino}
Content-Type: text/html; charset=utf-8
Content-Length: {len(html_bytes)}
Connection: close

""".encode('utf-8')
    
    socket_cliente.sendall(respuesta + html_bytes)