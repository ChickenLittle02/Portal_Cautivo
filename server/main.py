#!/usr/bin/env python3
"""
main.py
Servidor Principal del Portal Cautivo
Coordina todos los módulos
"""

import socket
import threading

# Importar funciones de otros archivos
from config import PUERTO, HOST, CUENTAS_VALIDAS, MENSAJE_INICIO, MENSAJE_ERROR_PERMISOS, MENSAJE_DETENIDO
from usuarios import validar_credenciales, registrar_sesion, obtener_sesiones_activas, cerrar_sesion
from paginas import PAGINA_LOGIN, PAGINA_EXITO, PAGINA_ERROR, PAGINA_404, PAGINA_ESTADO
from http_handler import obtener_ip_cliente, parsear_peticion_http, parsear_formulario, enviar_respuesta_http
from firewall import abrir_acceso_ip, cerrar_acceso_ip, listar_reglas_firewall, resetear_firewall


# =========================================================
# FUNCIÓN PRINCIPAL: MANEJAR UN CLIENTE
# =========================================================

def manejar_cliente(socket_cliente, direccion_cliente):
    """
    Esta función se ejecuta en un HILO separado para cada cliente
    que se conecta al servidor
    
    Argumentos:
        socket_cliente: Socket de conexión del cliente
        direccion_cliente: Tupla con (IP, puerto)
    """
    
    # Obtener IP del cliente
    ip_cliente = obtener_ip_cliente(socket_cliente)
    print(f"\n➡️  Cliente conectado desde {ip_cliente}")
    
    try:
        # ===== PASO 1: RECIBIR DATOS =====
        datos_recibidos = socket_cliente.recv(4096)
        
        if not datos_recibidos:
            return
        
        # ===== PASO 2: PARSEAR PETICIÓN HTTP =====
        metodo, ruta, body = parsear_peticion_http(datos_recibidos)
        print(f"📨 {metodo} {ruta}")
        
        # ===== PASO 3: PROCESAR SEGÚN LA RUTA =====
        
        # RUTA 1: GET / -> Mostrar página de login
        if metodo == "GET" and ruta == "/":
            print(f"   → Enviando página de login")
            enviar_respuesta_http(socket_cliente, "200 OK", "text/html", PAGINA_LOGIN)
        
        # RUTA 2: POST /login -> Procesar inicio de sesión
        elif metodo == "POST" and ruta == "/login":
            # Parsear datos del formulario
            formulario = parsear_formulario(body)
            usuario = formulario.get('usuario', '')
            password = formulario.get('password', '')
            
            print(f"   → Intento de login: usuario='{usuario}'")
            
            # Validar credenciales
            if validar_credenciales(usuario, password):
                print(f"   ✅ VÁLIDO - Registrando sesión de {ip_cliente}")
                registrar_sesion(ip_cliente)
                
                # NUEVO: Abrir acceso en firewall
                print(f"   🔓 Abriendo acceso en firewall para {ip_cliente}")
                abrir_acceso_ip(ip_cliente)
                
                enviar_respuesta_http(socket_cliente, "200 OK", "text/html", PAGINA_EXITO)
            else:
                print(f"   ❌ INVÁLIDO - Credenciales rechazadas")
                enviar_respuesta_http(socket_cliente, "401 Unauthorized", "text/html", PAGINA_ERROR)
        
        # RUTA 3: GET /status -> Ver sesiones activas (para DEBUG)
        elif metodo == "GET" and ruta == "/status":
            print(f"   → Mostrando estado de sesiones")
            sesiones = obtener_sesiones_activas()
            contenido = PAGINA_ESTADO(sesiones)
            enviar_respuesta_http(socket_cliente, "200 OK", "text/html", contenido)
        
        # RUTA 4 (NUEVA): GET /firewall -> Ver reglas de iptables
        elif metodo == "GET" and ruta == "/firewall":
            print(f"   → Mostrando reglas de firewall")
            reglas = listar_reglas_firewall()
            contenido = f"""<html><body>
            <h1>Reglas de Firewall (iptables)</h1>
            <pre>{reglas}</pre>
            <p><a href="/">Volver</a></p>
            </body></html>"""
            enviar_respuesta_http(socket_cliente, "200 OK", "text/html", contenido)
        
        # RUTA 4: Cualquier otra ruta no existe
        else:
            print(f"   → Ruta no encontrada (404)")
            enviar_respuesta_http(socket_cliente, "404 Not Found", "text/html", PAGINA_404)
    
    except Exception as error:
        print(f"   ❌ ERROR: {error}")
    
    finally:
        # Cerrar conexión
        socket_cliente.close()
        print(f"⬅️  Cliente {ip_cliente} desconectado")


# =========================================================
# FUNCIÓN: INICIAR SERVIDOR
# =========================================================

def iniciar_servidor(puerto=PUERTO):
    """
    Crea un socket servidor que:
    1. Escucha en el puerto especificado
    2. Acepta conexiones de clientes
    3. Crea un hilo para cada cliente
    
    Argumentos:
        puerto (int): Puerto donde escuchar
    """
    
    # Crear socket servidor
    socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Vincular a puerto
        socket_servidor.bind((HOST, puerto))
        print(MENSAJE_INICIO.format(puerto))
        
        # Escuchar conexiones
        socket_servidor.listen(5)
        
        # Loop infinito: aceptar clientes
        while True:
            # Esperar a que se conecte un cliente
            socket_cliente, direccion = socket_servidor.accept()
            
            # Crear un hilo para manejar este cliente
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(socket_cliente, direccion)
            )
            hilo.daemon = True      # Termina cuando el programa termina
            hilo.start()            # Inicia el hilo
    
    except PermissionError:
        print(MENSAJE_ERROR_PERMISOS.format(puerto))
    except KeyboardInterrupt:
        print(f"\n{MENSAJE_DETENIDO}")
    finally:
        socket_servidor.close()


# =========================================================
# EJECUTAR PROGRAMA
# =========================================================

if __name__ == "__main__":
    print("\n=== PORTAL CAUTIVO ===\n")
    iniciar_servidor()