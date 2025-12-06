#!/usr/bin/env python3
"""
user_manager.py - Sistema de gestión de usuarios
Permite crear, listar, eliminar usuarios y cambiar contraseñas
"""

import json
import os
import hashlib
import getpass
from datetime import datetime

USERS_FILE = "users.json"
ADMIN_ROLE = "admin"
USER_ROLE = "user"

# =========================================================
# FUNCIÓN: HASH DE CONTRASEÑA
# =========================================================

def hash_password(password):
    """Genera hash SHA-256 de una contraseña"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# =========================================================
# FUNCIÓN: CARGAR USUARIOS
# =========================================================

def cargar_usuarios():
    """Carga usuarios desde archivo JSON"""
    if not os.path.exists(USERS_FILE):
        # Crear usuario admin por defecto
        usuarios_default = {
            "admin": {
                "password": hash_password("123456"),
                "role": ADMIN_ROLE,
                "created": datetime.now().isoformat(),
                "active": True
            }
        }
        guardar_usuarios(usuarios_default)
        return usuarios_default
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        print("❌ Error al cargar usuarios")
        return {}

# =========================================================
# FUNCIÓN: GUARDAR USUARIOS
# =========================================================

def guardar_usuarios(usuarios):
    """Guarda usuarios en archivo JSON"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(usuarios, f, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False

# =========================================================
# FUNCIÓN: VALIDAR CREDENCIALES
# =========================================================

def validar_credenciales(usuario, password):
    """Valida usuario y contraseña contra el sistema"""
    usuarios = cargar_usuarios()
    
    if usuario not in usuarios:
        return False, None
    
    user_data = usuarios[usuario]
    
    if not user_data.get("active", True):
        return False, None
    
    password_hash = hash_password(password)
    if user_data["password"] == password_hash:
        return True, user_data.get("role", USER_ROLE)
    
    return False, None

# =========================================================
# FUNCIÓN: AGREGAR USUARIO
# =========================================================

def agregar_usuario(username, password, role=USER_ROLE):
    """Agrega un nuevo usuario al sistema"""
    usuarios = cargar_usuarios()
    
    if username in usuarios:
        return False, "Usuario ya existe"
    
    if role not in [ADMIN_ROLE, USER_ROLE]:
        return False, "Rol inválido"
    
    usuarios[username] = {
        "password": hash_password(password),
        "role": role,
        "created": datetime.now().isoformat(),
        "active": True
    }
    
    if guardar_usuarios(usuarios):
        return True, "Usuario creado exitosamente"
    
    return False, "Error al guardar usuario"

# =========================================================
# FUNCIÓN: ELIMINAR USUARIO
# =========================================================

def eliminar_usuario(username):
    """Elimina un usuario del sistema"""
    usuarios = cargar_usuarios()
    
    if username not in usuarios:
        return False, "Usuario no existe"
    
    if username == "admin":
        return False, "No se puede eliminar al usuario admin"
    
    del usuarios[username]
    
    if guardar_usuarios(usuarios):
        return True, "Usuario eliminado"
    
    return False, "Error al eliminar usuario"

# =========================================================
# FUNCIÓN: LISTAR USUARIOS
# =========================================================

def listar_usuarios():
    """Retorna lista de todos los usuarios"""
    usuarios = cargar_usuarios()
    return usuarios

# =========================================================
# FUNCIÓN: CAMBIAR CONTRASEÑA
# =========================================================

def cambiar_password(username, nueva_password):
    """Cambia la contraseña de un usuario"""
    usuarios = cargar_usuarios()
    
    if username not in usuarios:
        return False, "Usuario no existe"
    
    usuarios[username]["password"] = hash_password(nueva_password)
    usuarios[username]["password_changed"] = datetime.now().isoformat()
    
    if guardar_usuarios(usuarios):
        return True, "Contraseña cambiada"
    
    return False, "Error al cambiar contraseña"

# =========================================================
# FUNCIÓN: ACTIVAR/DESACTIVAR USUARIO
# =========================================================

def toggle_usuario(username, estado):
    """Activa o desactiva un usuario"""
    usuarios = cargar_usuarios()
    
    if username not in usuarios:
        return False, "Usuario no existe"
    
    if username == "admin":
        return False, "No se puede desactivar al admin"
    
    usuarios[username]["active"] = estado
    
    if guardar_usuarios(usuarios):
        estado_text = "activado" if estado else "desactivado"
        return True, f"Usuario {estado_text}"
    
    return False, "Error al cambiar estado"

# =========================================================
# INTERFAZ DE LÍNEA DE COMANDOS
# =========================================================

def menu_principal():
    """Menú interactivo para gestión de usuarios"""
    print("\n" + "="*60)
    print("👥 GESTIÓN DE USUARIOS - PORTAL CAUTIVO")
    print("="*60)
    
    while True:
        print("\n📋 MENÚ:")
        print("  1. Listar usuarios")
        print("  2. Agregar usuario")
        print("  3. Eliminar usuario")
        print("  4. Cambiar contraseña")
        print("  5. Activar/Desactivar usuario")
        print("  0. Salir")
        
        opcion = input("\n➡️  Opción: ").strip()
        
        if opcion == "1":
            listar_usuarios_menu()
        elif opcion == "2":
            agregar_usuario_menu()
        elif opcion == "3":
            eliminar_usuario_menu()
        elif opcion == "4":
            cambiar_password_menu()
        elif opcion == "5":
            toggle_usuario_menu()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

def listar_usuarios_menu():
    """Muestra lista de usuarios"""
    usuarios = listar_usuarios()
    
    if not usuarios:
        print("\n📭 No hay usuarios registrados")
        return
    
    print("\n" + "="*60)
    print("👥 USUARIOS REGISTRADOS")
    print("="*60)
    
    for username, data in usuarios.items():
        estado = "✅ Activo" if data.get("active", True) else "❌ Inactivo"
        role = data.get("role", USER_ROLE)
        created = data.get("created", "N/A")[:10]
        
        print(f"\n🔹 Usuario: {username}")
        print(f"   Rol: {role}")
        print(f"   Estado: {estado}")
        print(f"   Creado: {created}")

def agregar_usuario_menu():
    """Agrega un nuevo usuario interactivamente"""
    print("\n" + "-"*60)
    print("➕ AGREGAR NUEVO USUARIO")
    print("-"*60)
    
    username = input("Usuario: ").strip()
    if not username:
        print("❌ Usuario no puede estar vacío")
        return
    
    password = getpass.getpass("Contraseña: ")
    if not password:
        print("❌ Contraseña no puede estar vacía")
        return
    
    password_confirm = getpass.getpass("Confirmar contraseña: ")
    if password != password_confirm:
        print("❌ Las contraseñas no coinciden")
        return
    
    print("\n¿Rol del usuario?")
    print("  1. Usuario normal")
    print("  2. Administrador")
    
    rol_opcion = input("Opción [1]: ").strip() or "1"
    role = ADMIN_ROLE if rol_opcion == "2" else USER_ROLE
    
    exito, mensaje = agregar_usuario(username, password, role)
    
    if exito:
        print(f"✅ {mensaje}")
        print(f"   Usuario: {username}")
        print(f"   Rol: {role}")
    else:
        print(f"❌ {mensaje}")

def eliminar_usuario_menu():
    """Elimina un usuario interactivamente"""
    print("\n" + "-"*60)
    print("🗑️  ELIMINAR USUARIO")
    print("-"*60)
    
    listar_usuarios_menu()
    
    username = input("\n➡️  Usuario a eliminar: ").strip()
    if not username:
        print("❌ Operación cancelada")
        return
    
    confirmar = input(f"⚠️  ¿Eliminar '{username}'? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Operación cancelada")
        return
    
    exito, mensaje = eliminar_usuario(username)
    print(f"{'✅' if exito else '❌'} {mensaje}")

def cambiar_password_menu():
    """Cambia contraseña de un usuario"""
    print("\n" + "-"*60)
    print("🔑 CAMBIAR CONTRASEÑA")
    print("-"*60)
    
    username = input("Usuario: ").strip()
    if not username:
        print("❌ Operación cancelada")
        return
    
    nueva_password = getpass.getpass("Nueva contraseña: ")
    if not nueva_password:
        print("❌ Contraseña no puede estar vacía")
        return
    
    confirmar_password = getpass.getpass("Confirmar contraseña: ")
    if nueva_password != confirmar_password:
        print("❌ Las contraseñas no coinciden")
        return
    
    exito, mensaje = cambiar_password(username, nueva_password)
    print(f"{'✅' if exito else '❌'} {mensaje}")

def toggle_usuario_menu():
    """Activa o desactiva un usuario"""
    print("\n" + "-"*60)
    print("🔄 ACTIVAR/DESACTIVAR USUARIO")
    print("-"*60)
    
    listar_usuarios_menu()
    
    username = input("\n➡️  Usuario: ").strip()
    if not username:
        print("❌ Operación cancelada")
        return
    
    print("\n¿Acción?")
    print("  1. Activar")
    print("  2. Desactivar")
    
    accion = input("Opción: ").strip()
    
    if accion == "1":
        estado = True
    elif accion == "2":
        estado = False
    else:
        print("❌ Opción inválida")
        return
    
    exito, mensaje = toggle_usuario(username, estado)
    print(f"{'✅' if exito else '❌'} {mensaje}")

# =========================================================
# EJECUTAR
# =========================================================

if __name__ == "__main__":
    menu_principal()