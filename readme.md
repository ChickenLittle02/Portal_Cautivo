# 🔐 Portal Cautivo - Documentación Completa

Sistema de Portal Cautivo para control de acceso a Internet mediante autenticación web con firewall iptables y **gestión avanzada de usuarios**.

---

## 📋 Tabla de Contenidos

1. [Descripción](#-descripción)
2. [Características Nuevas](#-características-nuevas)
3. [Requisitos](#-requisitos)
4. [Estructura del Proyecto](#-estructura-del-proyecto)
5. [Instalación](#-instalación)
6. [Configuración Inicial](#-configuración-inicial)
7. [Gestión de Usuarios](#-gestión-de-usuarios)
8. [Ejecución](#-ejecución)
9. [Uso del Sistema](#-uso-del-sistema)
10. [Panel de Administración Web](#-panel-de-administración-web)
11. [Arquitectura](#-arquitectura)
12. [Endpoints Disponibles](#-endpoints-disponibles)
13. [Troubleshooting](#-troubleshooting)
14. [Seguridad](#-seguridad)

---

## 🎯 Descripción

Portal Cautivo es un sistema de autenticación web que controla el acceso a Internet mediante:
- Servidor HTTP ligero (solo librerías estándar de Python)
- Firewall iptables para control de tráfico
- **Sistema de gestión de usuarios con roles (admin/user)**
- **Panel web de administración**
- Gestión de sesiones por IP
- **Contraseñas cifradas con SHA-256**
- Interfaz web para login/logout

**Caso de uso típico:** Crear un hotspot WiFi en Linux que requiera autenticación antes de permitir acceso a Internet, con capacidad de gestionar usuarios desde la web.

---

## ✨ Características Nuevas

### 🆕 Sistema de Gestión de Usuarios
- ✅ **Almacenamiento persistente** en archivo JSON (`users.json`)
- ✅ **Contraseñas cifradas** con hash SHA-256
- ✅ **Sistema de roles**: Admin y Usuario normal
- ✅ **CRUD completo**: Crear, listar, eliminar usuarios
- ✅ **Cambio de contraseñas**
- ✅ **Activar/Desactivar usuarios**

### 🌐 Panel de Administración Web
- ✅ **Interfaz web moderna** para administradores
- ✅ **Agregar usuarios** directamente desde el navegador
- ✅ **Eliminar usuarios** con un click
- ✅ **Ver sesiones activas** en tiempo real
- ✅ **Desconectar usuarios** remotamente
- ✅ **Estadísticas** del sistema

### 🔧 Herramienta CLI
- ✅ **Gestión desde terminal** con `user_manager.py`
- ✅ **Menú interactivo** para todas las operaciones
- ✅ **Confirmaciones de seguridad**

---

## 💻 Requisitos

### Sistema Operativo
- Linux (Ubuntu, Debian, CentOS, etc.)
- Kernel con soporte para iptables
- Permisos de root/sudo

### Software
- Python 3.6 o superior (solo librerías estándar)
- iptables instalado
- 2 interfaces de red:
  - Una para el hotspot WiFi
  - Una con conexión a Internet

### Verificar requisitos:
```bash
# Verificar Python
python3 --version

# Verificar iptables
sudo iptables --version

# Verificar interfaces
ip addr show
```

---

## 📁 Estructura del Proyecto

```
portal_cautivo/
│
├── main.py                  # Servidor principal (ejecutar esto)
├── setup.py                 # Configurador de firewall (ejecutar una vez)
├── user_manager.py          # Gestión de usuarios CLI (NUEVO)
│
├── config.py                # Configuración (puertos, cuentas)
├── auth.py                  # Autenticación y sesiones (ACTUALIZADO)
├── firewall.py              # Gestión de iptables
├── http_utils.py            # Utilidades HTTP
├── html_templates.py        # Plantillas HTML (ACTUALIZADO)
├── admin_templates.py       # Panel de admin (NUEVO)
├── request_handler.py       # Manejador de peticiones (ACTUALIZADO)
│
├── setup_utils.py           # Utilidades de setup
├── firewall_config.py       # Configuración de firewall
│
├── users.json              # Base de datos de usuarios (generado automáticamente)
└── README.md               # Esta documentación
```

### Descripción de módulos:

| Archivo | Responsabilidad | Estado |
|---------|----------------|--------|
| `config.py` | Configuración global (puerto, host) | Sin cambios |
| `auth.py` | Validación de credenciales, sesiones con roles | ✨ Actualizado |
| `user_manager.py` | CRUD de usuarios, CLI interactiva | 🆕 Nuevo |
| `admin_templates.py` | Panel web de administración | 🆕 Nuevo |
| `firewall.py` | Autorizar/desautorizar IPs en iptables | Sin cambios |
| `http_utils.py` | Parsear peticiones HTTP, enviar respuestas | Sin cambios |
| `html_templates.py` | Páginas HTML (login, éxito, error, logout) | ✨ Actualizado |
| `request_handler.py` | Manejo de rutas, lógica con endpoints admin | ✨ Actualizado |
| `main.py` | Servidor HTTP principal | Sin cambios |
| `setup_utils.py` | Funciones auxiliares para setup | Sin cambios |
| `firewall_config.py` | Aplicación de reglas de firewall | Sin cambios |
| `setup.py` | Configurador interactivo del firewall | Sin cambios |

---

## 🚀 Instalación

### 1. Descargar el proyecto
```bash
# Clonar o descargar todos los archivos en un directorio
mkdir portal_cautivo
cd portal_cautivo

# Copiar todos los archivos .py al directorio
```

### 2. Verificar permisos
```bash
# Dar permisos de ejecución
chmod +x main.py setup.py user_manager.py
```

### 3. El sistema creará automáticamente:
- **`users.json`**: Base de datos de usuarios (primera ejecución)
- **Usuario admin por defecto**: `admin` / `123456`

---

## ⚙️ Configuración Inicial

### Paso 1: Ejecutar setup (SOLO UNA VEZ)

```bash
sudo python3 setup.py
```

**El configurador te pedirá:**

1. **Seleccionar interfaz del HOTSPOT**
   - La interfaz donde los clientes se conectan (ej: `wlan0`, `ap0`)
   
2. **Seleccionar interfaz de INTERNET**
   - La interfaz con conexión a Internet (ej: `eth0`, `wlan1`, `usb0`)

### Ejemplo de configuración:

```
🔹 INTERFACES DISPONIBLES:
   1. wlan0: 192.168.50.1
   2. wlan1: 192.168.1.100

1️⃣  ¿CUÁL ES LA INTERFAZ DEL HOTSPOT?
   Número: 1
   ✅ Hotspot: wlan0

2️⃣  ¿CUÁL ES LA INTERFAZ DE INTERNET?
   Número: 2
   ✅ Internet: wlan1

⚙️  CONFIGURACIÓN:
   Hotspot:  wlan0 (192.168.50.1)
   Internet: wlan1 (192.168.1.100)

¿Confirmar? (s/n): s
```

---

## 👥 Gestión de Usuarios

### Método 1: Herramienta CLI (Terminal)

```bash
python3 user_manager.py
```

**Menú interactivo:**

```
👥 GESTIÓN DE USUARIOS - PORTAL CAUTIVO

📋 MENÚ:
  1. Listar usuarios
  2. Agregar usuario
  3. Eliminar usuario
  4. Cambiar contraseña
  5. Activar/Desactivar usuario
  0. Salir

➡️  Opción:
```

#### Ejemplos de uso CLI:

**Agregar usuario:**
```bash
python3 user_manager.py
# Seleccionar opción 2
# Ingresar: usuario, contraseña, rol
```

**Listar usuarios:**
```bash
python3 user_manager.py
# Seleccionar opción 1
```

**Cambiar contraseña:**
```bash
python3 user_manager.py
# Seleccionar opción 4
# Ingresar: usuario, nueva contraseña
```

### Método 2: Panel Web (Requiere ser admin)

1. Iniciar sesión como admin
2. Acceder a: `http://192.168.50.1/admin`
3. Usar la interfaz gráfica

---

## 🎮 Ejecución

### Iniciar el servidor:

```bash
sudo python3 main.py
```

**Salida esperada:**
```
🚀 Servidor Portal Cautivo
   Puerto: 80
   Abre: http://localhost
   (Presiona Ctrl+C para detener)
```

### ¿Por qué sudo?
- Puerto 80 requiere permisos de root
- Modificación de reglas iptables requiere sudo

### Detener el servidor:
Presiona `Ctrl+C`

---

## 📱 Uso del Sistema

### Flujo de usuario normal:

1. **Cliente se conecta al WiFi**
   - El dispositivo obtiene IP automáticamente

2. **Cliente abre navegador**
   - Intenta acceder a cualquier sitio (ej: google.com)
   - Es redirigido al portal de login: `http://192.168.50.1`

3. **Autenticación**
   - Usuario ingresa credenciales
   - Si son correctas → IP autorizada en firewall
   - Si son incorrectas → Mensaje de error

4. **Acceso a Internet**
   - Usuario puede navegar libremente
   - Sesión permanece activa

5. **Cerrar sesión**
   - Acceder a `http://192.168.50.1/logout`
   - IP bloqueada automáticamente

### Flujo de administrador:

1. **Login como admin**
   - Usuario: `admin`
   - Contraseña: `123456` (cambiar después)

2. **Acceder al panel**
   - Click en "Panel de Administración"
   - O ir a: `http://192.168.50.1/admin`

3. **Gestionar el sistema**
   - Ver usuarios y sesiones
   - Agregar/eliminar usuarios
   - Desconectar IPs

---

## 🌐 Panel de Administración Web

### Acceso
- **URL**: `http://192.168.50.1/admin`
- **Requisito**: Sesión iniciada con rol de administrador

### Funcionalidades:

#### 📊 Dashboard
- **Estadísticas en tiempo real**:
  - Total de usuarios registrados
  - Sesiones activas

#### ➕ Agregar Usuario
```
Formulario web:
- Usuario: [texto]
- Contraseña: [password]
- Rol: [Usuario Normal / Administrador]
- Botón: [✅ Crear Usuario]
```

#### 👥 Tabla de Usuarios
| Usuario | Rol | Estado | Creado | Acciones |
|---------|-----|--------|--------|----------|
| admin | admin | ✅ Activo | 2024-12-01 | 🗑️ Eliminar |
| user1 | user | ✅ Activo | 2024-12-02 | 🗑️ Eliminar |

#### 🌐 Tabla de Sesiones Activas
| IP | Usuario | Rol | Acciones |
|----|---------|-----|----------|
| 192.168.50.100 | user1 | user | ⛔ Desconectar |
| 192.168.50.101 | admin | admin | ⛔ Desconectar |

### Características del Panel:
- ✅ **Diseño moderno** con CSS profesional
- ✅ **Operaciones AJAX** (sin recargar página)
- ✅ **Mensajes de confirmación**
- ✅ **Feedback visual** (éxito/error)
- ✅ **Responsive** (se adapta a móviles)

---

## 🏗️ Arquitectura

### Flujo de autenticación con roles:

```
1. Cliente → POST /login (user/pass) → Servidor
              ↓
2. Validar en users.json
              ↓
         ┌────┴────┐
         ↓         ↓
    ✅ VÁLIDO   ❌ INVÁLIDO
         ↓         ↓
3. Obtener    Envía
   rol        HTML_ERROR
   (admin/user)
         ↓
4. Registra sesión
   con rol
         ↓
5. Autoriza IP
   en iptables
         ↓
6. HTML_EXITO
```

### Sistema de usuarios (users.json):

```json
{
  "admin": {
    "password": "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
    "role": "admin",
    "created": "2024-12-06T10:30:00",
    "active": true
  },
  "user1": {
    "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
    "role": "user",
    "created": "2024-12-06T11:00:00",
    "active": true
  }
}
```

### Control de acceso por roles:

```
Ruta /admin → Verificar sesión activa
              ↓
         ¿Es admin?
         /        \
      SÍ          NO
       ↓           ↓
  Panel Admin   403 Forbidden
```

---

## 🌐 Endpoints Disponibles

| Ruta | Método | Descripción | Requiere Auth | Solo Admin |
|------|--------|-------------|---------------|------------|
| `/` | GET | Página de login | No | No |
| `/login` | POST | Procesa autenticación | No | No |
| `/logout` | GET | Cierra sesión y bloquea IP | No | No |
| `/admin` | GET | Panel de administración | Sí | Sí |
| `/admin/add_user` | POST | Agregar usuario (JSON) | Sí | Sí |
| `/admin/delete_user` | POST | Eliminar usuario (JSON) | Sí | Sí |
| `/admin/disconnect_ip` | POST | Desconectar IP (JSON) | Sí | Sí |
| `/status` | GET | Ver sesiones (debug) | No | No |

### Ejemplos de uso:

**Agregar usuario desde terminal:**
```bash
curl -X POST http://192.168.50.1/admin/add_user \
  -H "X-Forwarded-For: IP_ADMIN" \
  -d "usuario=nuevo&password=pass123&role=user"
```

**Respuesta JSON:**
```json
{
  "success": true,
  "message": "Usuario creado exitosamente"
}
```

---

## 🔧 Troubleshooting

### Problema: No puedo acceder a /admin
**Verificar:**
```bash
# 1. ¿Has iniciado sesión?
# 2. ¿Tu usuario es admin?

# Ver tu sesión actual en /status
curl http://192.168.50.1/status
```

### Problema: Error al crear usuario desde panel
**Solución:**
```bash
# Verificar permisos del archivo
ls -l users.json

# Debe ser escribible por el usuario que ejecuta main.py
chmod 644 users.json
```

### Problema: Olvidé la contraseña de admin
**Solución:**
```bash
# Eliminar archivo de usuarios (se recreará con admin/123456)
rm users.json
sudo python3 main.py
```

### Problema: "Permission denied" al iniciar
**Solución:**
```bash
# Usar sudo
sudo python3 main.py
```

### Problema: Cliente no puede conectarse a Internet después de autenticarse
**Verificar:**
```bash
# 1. IP forwarding está habilitado
cat /proc/sys/net/ipv4/ip_forward
# Debe devolver: 1

# 2. Ver reglas de iptables
sudo iptables -L FORWARD -n -v

# 3. Re-ejecutar setup
sudo python3 setup.py
```

---

## 🔒 Seguridad

### ✅ Mejoras implementadas:

1. **✅ Contraseñas cifradas**
   - Hash SHA-256 en `users.json`
   - Nunca se almacenan en texto plano

2. **✅ Sistema de roles**
   - Separación admin/usuario
   - Control de acceso granular

3. **✅ Validación de sesiones**
   - Verificación por IP
   - Control de permisos por ruta

### ⚠️ Advertencias de seguridad:

1. **HTTP sin cifrado**
   - Las credenciales viajan sin cifrar
   - Para producción: implementar HTTPS

2. **Sin límite de intentos**
   - No hay protección contra fuerza bruta
   - Agregar rate limiting para producción

3. **Sin timeout de sesión**
   - Las sesiones no expiran automáticamente
   - Implementar timeout para producción

4. **SHA-256 sin salt**
   - Para producción: usar bcrypt o argon2

### 🔐 Mejoras recomendadas para producción:

```python
# Usar bcrypt en lugar de SHA-256
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verificar_password(password, hash):
    return bcrypt.checkpw(password.encode(), hash)
```

```python
# Implementar rate limiting
import time
from collections import defaultdict

intentos_login = defaultdict(list)

def rate_limit(ip):
    ahora = time.time()
    intentos_login[ip] = [t for t in intentos_login[ip] if ahora - t < 300]
    
    if len(intentos_login[ip]) >= 5:
        return False  # Bloqueado
    
    intentos_login[ip].append(ahora)
    return True
```

### Primeros pasos de seguridad:

**1. Cambiar contraseña de admin:**
```bash
python3 user_manager.py
# Opción 4: Cambiar contraseña
# Usuario: admin
# Nueva contraseña: [contraseña segura]
```

**2. Crear usuarios específicos:**
```bash
# No usar cuenta admin para usuarios normales
# Crear cuentas individuales
```

**3. Revisar logs:**
```bash
# Monitorear el output de main.py
# Ver intentos de login fallidos
```

---

## 📊 Monitoreo

### Ver sesiones activas:
```bash
# Desde navegador (requiere admin)
http://192.168.50.1/admin

# Ver status en JSON
curl http://192.168.50.1/status
```

### Ver usuarios registrados:
```bash
# Desde CLI
python3 user_manager.py
# Opción 1: Listar usuarios

# Ver archivo directamente
cat users.json | python3 -m json.tool
```

### Ver logs en tiempo real:
```bash
# Los logs aparecen en la terminal donde ejecutas main.py
# Ejemplo de salida:

➡️  Cliente: 192.168.50.100
📨 POST /login
   → Usuario: 'user1'
   ✅ VÁLIDO
✅ Sesión registrada: 192.168.50.100 (user1 - user)
🔓 Autorizando 192.168.50.100...
   → Regla 1 OK
   → Regla 2 OK
✅ 192.168.50.100 AUTORIZADA
⬅️  Desconectado: 192.168.50.100
```

---

## 🚀 Inicio Rápido (Resumen)

```bash
# 1. Configurar firewall (solo una vez)
sudo python3 setup.py

# 2. (Opcional) Gestionar usuarios
python3 user_manager.py

# 3. Iniciar servidor
sudo python3 main.py

# 4. Desde cliente WiFi:
# Abrir navegador → http://192.168.50.1
# Login: admin / 123456

# 5. Acceder al panel admin:
# http://192.168.50.1/admin

# 6. ¡Gestionar usuarios y sesiones desde la web!
```

---

## 📞 Soporte

Para problemas o preguntas:
- Revisar sección [Troubleshooting](#-troubleshooting)
- Verificar logs del servidor
- Comprobar `users.json` existe y tiene permisos
- Verificar reglas de iptables

---

## 📝 Changelog

### Versión 2.0 (Actual)
- ✅ Sistema de gestión de usuarios
- ✅ Panel de administración web
- ✅ Contraseñas cifradas (SHA-256)
- ✅ Sistema de roles (admin/user)
- ✅ Herramienta CLI para gestión
- ✅ Almacenamiento persistente (JSON)

### Versión 1.0
- Servidor HTTP básico
- Autenticación simple
- Firewall iptables

---

**Última actualización:** Diciembre 2024  
**Versión:** 2.0 (Con gestión de usuarios)  
**Licencia:** Código abierto para fines educativos