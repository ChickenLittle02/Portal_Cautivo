#!/usr/bin/env python3
"""
test_firewall.py
Script para probar los comandos de firewall ANTES de usarlos en main.py

Úsalo así:
    sudo python3 test_firewall.py
"""

from firewall import (
    abrir_acceso_ip, 
    cerrar_acceso_ip, 
    listar_reglas_firewall, 
    resetear_firewall,
    tiene_permisos_sudo
)

def menu_principal():
    """Muestra un menú interactivo para probar el firewall"""
    
    print("\n" + "="*50)
    print("  PORTAL CAUTIVO - TESTING DE FIREWALL")
    print("="*50)
    
    # Verificar permisos
    if not tiene_permisos_sudo():
        print("❌ ERROR: Este script DEBE ejecutarse con sudo")
        print("   sudo python3 test_firewall.py")
        return
    
    print("✅ Ejecutándose con permisos sudo\n")
    
    while True:
        print("\n📋 OPCIONES:")
        print("  1. Ver todas las reglas de firewall")
        print("  2. Abrir acceso a una IP")
        print("  3. Cerrar acceso a una IP")
        print("  4. Resetear firewall (eliminar todas las reglas)")
        print("  5. Prueba rápida (abrir y cerrar 192.168.1.100)")
        print("  6. Salir")
        
        opcion = input("\n¿Qué deseas hacer? (1-6): ").strip()
        
        if opcion == "1":
            print("\n" + "-"*50)
            print("REGLAS DE FIREWALL:")
            print("-"*50)
            reglas = listar_reglas_firewall()
            print(reglas)
        
        elif opcion == "2":
            ip = input("  Ingresa la IP a autorizar (ej: 192.168.1.100): ").strip()
            abrir_acceso_ip(ip)
        
        elif opcion == "3":
            ip = input("  Ingresa la IP a bloquear (ej: 192.168.1.100): ").strip()
            cerrar_acceso_ip(ip)
        
        elif opcion == "4":
            confirmacion = input("  ⚠️  ¿Estás seguro? Esto eliminará TODAS las reglas (s/n): ").strip()
            if confirmacion.lower() == 's':
                resetear_firewall()
            else:
                print("  Cancelado")
        
        elif opcion == "5":
            print("\n  Prueba rápida con 192.168.1.100:")
            print("  1. Abriendo acceso...")
            abrir_acceso_ip("192.168.1.100")
            
            print("\n  Esperando 2 segundos...")
            import time
            time.sleep(2)
            
            print("\n  2. Viendo reglas...")
            print(listar_reglas_firewall())
            
            print("\n  3. Cerrando acceso...")
            cerrar_acceso_ip("192.168.1.100")
            
            print("\n  ✅ Prueba completada")
        
        elif opcion == "6":
            print("\n👋 Saliendo...")
            break
        
        else:
            print("❌ Opción no válida")


if __name__ == "__main__":
    menu_principal()