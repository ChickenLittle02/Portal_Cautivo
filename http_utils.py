#!/usr/bin/env python3
"""
http_utils.py - Utilidades para manejo de HTTP
"""

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
# FUNCIÓN: ENVIAR RESPUESTA JSON
# =========================================================

def enviar_json(socket_cliente, data):
    """Envía respuesta JSON"""
    import json
    contenido = json.dumps(data)
    respuesta = f"""HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: {len(contenido)}
Connection: close

{contenido}"""
    socket_cliente.sendall(respuesta.encode('utf-8'))