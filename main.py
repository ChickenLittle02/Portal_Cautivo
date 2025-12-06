#!/usr/bin/env python3
"""
Portal Cautivo - Servidor Principal V2 (Modularizado)
Solo usa librerías estándar de Python
"""

import socket
import threading
from config import PUERTO, HOST
from request_handler import manejar_cliente

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