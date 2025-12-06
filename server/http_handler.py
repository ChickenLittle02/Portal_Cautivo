"""
http_handler.py
Funciones para parsear HTTP y enviar respuestas
"""

# =========================================================
# FUNCIÓN 1: OBTENER IP DEL CLIENTE
# =========================================================

def obtener_ip_cliente(socket_cliente):
    """
    Extrae la dirección IP de quién se conectó
    
    Argumentos:
        socket_cliente: El socket de conexión del cliente
    
    Retorna:
        str: IP del cliente (ej: "192.168.1.100")
    """
    try:
        return socket_cliente.getpeername()[0]
    except:
        return "DESCONOCIDA"


# =========================================================
# FUNCIÓN 2: PARSEAR PETICIÓN HTTP
# =========================================================

def parsear_peticion_http(datos):
    """
    Convierte los bytes recibidos en información legible
    
    Una petición HTTP se ve así:
    ---
    GET / HTTP/1.1
    Host: localhost
    ...
    ---
    
    O para POST:
    ---
    POST /login HTTP/1.1
    Host: localhost
    Content-Length: 30
    
    usuario=admin&password=123456
    ---
    
    Argumentos:
        datos (bytes): Los datos crudos recibidos del socket
    
    Retorna:
        tuple: (metodo, ruta, body)
        Ejemplo: ("POST", "/login", "usuario=admin&password=123456")
    """
    try:
        # Convertir bytes a texto
        texto = datos.decode('utf-8')
        lineas = texto.split('\r\n')
        
        # Primera línea contiene el método y la ruta
        primera_linea = lineas[0].split()
        metodo = primera_linea[0]      # GET, POST, etc.
        ruta = primera_linea[1]        # /, /login, etc.
        
        # El body viene después de una línea vacía
        body = ""
        for i, linea in enumerate(lineas):
            if linea == "":
                # Hay datos después de la línea vacía
                if i + 1 < len(lineas):
                    body = lineas[i + 1]
                break
        
        return metodo, ruta, body
    
    except Exception as error:
        print(f"   ❌ Error al parsear HTTP: {error}")
        return None, None, None


# =========================================================
# FUNCIÓN 3: PARSEAR DATOS DEL FORMULARIO
# =========================================================

def parsear_formulario(body):
    """
    Convierte datos de formulario HTML a un diccionario
    
    Ejemplo entrada: "usuario=admin&password=123456"
    Ejemplo salida: {"usuario": "admin", "password": "123456"}
    
    Argumentos:
        body (str): Los datos del formulario
    
    Retorna:
        dict: Datos parseados {clave: valor}
    """
    datos = {}
    
    if not body:
        return datos
    
    # Limpiar espacios en blanco
    body = body.strip()
    
    if not body:
        return datos
    
    # Separar por &
    try:
        pares = body.split('&')
        
        for par in pares:
            if '=' in par:
                # Separar clave y valor
                clave, valor = par.split('=', 1)
                # Limpiar espacios
                clave = clave.strip()
                valor = valor.strip()
                datos[clave] = valor
    except Exception as e:
        print(f"   ⚠️  Error parseando formulario: {e}")
    
    return datos


# =========================================================
# FUNCIÓN 4: ENVIAR RESPUESTA HTTP
# =========================================================

def enviar_respuesta_http(socket_cliente, codigo, tipo_contenido, cuerpo):
    """
    Construye y envía una respuesta HTTP completa
    
    Una respuesta HTTP se ve así:
    ---
    HTTP/1.1 200 OK
    Content-Type: text/html
    Content-Length: 150
    Connection: close
    
    <html>...</html>
    ---
    
    Argumentos:
        socket_cliente: Socket donde enviar
        codigo (str): Código HTTP (ej: "200 OK", "404 Not Found")
        tipo_contenido (str): MIME type (ej: "text/html")
        cuerpo (str): El contenido HTML a enviar
    """
    # Construir la respuesta completa
    respuesta = f"""HTTP/1.1 {codigo}
Content-Type: {tipo_contenido}
Content-Length: {len(cuerpo)}
Connection: close

{cuerpo}"""
    
    # Enviar al cliente
    socket_cliente.sendall(respuesta.encode('utf-8'))