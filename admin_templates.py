#!/usr/bin/env python3
"""
admin_templates.py - Plantillas HTML para panel de administración
"""

# =========================================================
# PÁGINA HTML: PANEL ADMIN
# =========================================================

def generar_panel_admin(usuarios, sesiones):
    """Genera el panel de administración con usuarios y sesiones"""
    
    # Generar tabla de usuarios
    filas_usuarios = ""
    for username, data in usuarios.items():
        estado = "✅ Activo" if data.get("active", True) else "❌ Inactivo"
        role = data.get("role", "user")
        created = data.get("created", "N/A")[:10]
        
        filas_usuarios += f"""
        <tr>
            <td>{username}</td>
            <td>{role}</td>
            <td>{estado}</td>
            <td>{created}</td>
            <td>
                <button onclick="eliminarUsuario('{username}')" 
                        style="background: #dc3545; padding: 5px 10px; border: none; 
                               border-radius: 4px; color: white; cursor: pointer;">
                    🗑️ Eliminar
                </button>
            </td>
        </tr>
        """
    
    # Generar tabla de sesiones
    filas_sesiones = ""
    for ip, info in sesiones.items():
        usuario = info.get("usuario", "desconocido")
        role = info.get("role", "user")
        
        filas_sesiones += f"""
        <tr>
            <td>{ip}</td>
            <td>{usuario}</td>
            <td>{role}</td>
            <td>
                <button onclick="desconectarIP('{ip}')" 
                        style="background: #ffc107; padding: 5px 10px; border: none; 
                               border-radius: 4px; color: black; cursor: pointer;">
                    ⛔ Desconectar
                </button>
            </td>
        </tr>
        """
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Panel de Administración</title>
    <meta charset="utf-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif; 
            background: #f5f5f5; 
            padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ 
            color: #333; 
            margin-bottom: 10px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{ 
            color: #555; 
            margin-top: 30px; 
            margin-bottom: 15px;
            border-left: 4px solid #28a745;
            padding-left: 10px;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        th {{ 
            background: #007bff; 
            color: white; 
            padding: 12px; 
            text-align: left;
        }}
        td {{ 
            padding: 12px; 
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .form-group {{ 
            margin: 20px 0; 
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .form-group label {{ 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold;
            color: #555;
        }}
        .form-group input, .form-group select {{ 
            width: 100%; 
            padding: 10px; 
            margin-bottom: 15px; 
            border: 1px solid #ddd; 
            border-radius: 4px;
            font-size: 14px;
        }}
        .btn {{ 
            padding: 12px 24px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 16px;
            transition: all 0.3s;
        }}
        .btn-primary {{ 
            background: #007bff; 
            color: white;
        }}
        .btn-primary:hover {{ 
            background: #0056b3;
            transform: translateY(-1px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        .btn-danger {{ 
            background: #dc3545; 
            color: white;
        }}
        .btn-danger:hover {{ 
            background: #c82333;
        }}
        .mensaje {{ 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 4px;
            display: none;
        }}
        .mensaje.exito {{ 
            background: #d4edda; 
            color: #155724; 
            border: 1px solid #c3e6cb;
            display: block;
        }}
        .mensaje.error {{ 
            background: #f8d7da; 
            color: #721c24; 
            border: 1px solid #f5c6cb;
            display: block;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            flex: 1;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            font-size: 36px;
            margin-bottom: 5px;
        }}
        .stat-card p {{
            opacity: 0.9;
        }}
        .logout-btn {{
            float: right;
            background: #6c757d;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            transition: all 0.3s;
        }}
        .logout-btn:hover {{
            background: #545b62;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout-btn">🚪 Cerrar Sesión</a>
        <h1>🔐 Panel de Administración - Portal Cautivo</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{len(usuarios)}</h3>
                <p>👥 Usuarios Registrados</p>
            </div>
            <div class="stat-card">
                <h3>{len(sesiones)}</h3>
                <p>🌐 Sesiones Activas</p>
            </div>
        </div>

        <div id="mensaje" class="mensaje"></div>

        <h2>➕ Agregar Nuevo Usuario</h2>
        <div class="form-group">
            <form id="formAgregar" onsubmit="agregarUsuario(event)">
                <label>Usuario:</label>
                <input type="text" id="nuevoUsuario" name="usuario" required>
                
                <label>Contraseña:</label>
                <input type="password" id="nuevoPassword" name="password" required>
                
                <label>Rol:</label>
                <select id="nuevoRole" name="role">
                    <option value="user">Usuario Normal</option>
                    <option value="admin">Administrador</option>
                </select>
                
                <button type="submit" class="btn btn-primary">✅ Crear Usuario</button>
            </form>
        </div>

        <h2>👥 Usuarios Registrados</h2>
        <table>
            <thead>
                <tr>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Creado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {filas_usuarios}
            </tbody>
        </table>

        <h2>🌐 Sesiones Activas</h2>
        <table>
            <thead>
                <tr>
                    <th>IP</th>
                    <th>Usuario</th>
                    <th>Rol</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {filas_sesiones}
            </tbody>
        </table>
    </div>


    <script>
    function mostrarMensaje(texto, tipo) {{
        const div = document.getElementById('mensaje');
        div.textContent = texto;
        div.className = 'mensaje ' + tipo;
        setTimeout(() => {{
            div.className = 'mensaje';
        }}, 5000);
    }}

    async function agregarUsuario(event) {{
        event.preventDefault();
        
        const usuario = document.getElementById('nuevoUsuario').value.trim();
        const password = document.getElementById('nuevoPassword').value.trim();
        const role = document.getElementById('nuevoRole').value.trim();
        
        if (!usuario || !password) {{
            mostrarMensaje('❌ Usuario y contraseña son requeridos', 'error');
            return;
        }}
        
        console.log('Enviando:', {{usuario, password: '***', role}});
        
        try {{
            const params = new URLSearchParams();
            params.append('usuario', usuario);
            params.append('password', password);
            params.append('role', role);
            
            const response = await fetch('/admin/add_user', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }},
                body: params.toString()
            }});
            
            console.log('Response status:', response.status);
            const text = await response.text();
            console.log('Response text:', text);
            
            let result;
            try {{
                result = JSON.parse(text);
            }} catch (e) {{
                console.error('Error parsing JSON:', e);
                mostrarMensaje('❌ Error al procesar respuesta del servidor', 'error');
                return;
            }}
            
            if (result.success) {{
                mostrarMensaje('✅ ' + result.message, 'exito');
                document.getElementById('formAgregar').reset();
                setTimeout(() => location.reload(), 1500);
            }} else {{
                mostrarMensaje('❌ ' + result.message, 'error');
            }}
        }} catch (error) {{
            console.error('Error:', error);
            mostrarMensaje('❌ Error al crear usuario: ' + error.message, 'error');
        }}
    }}

    async function eliminarUsuario(username) {{
        if (!confirm('¿Eliminar usuario \"' + username + '\"?')) return;
        
        console.log('Eliminando usuario:', username);
        
        try {{
            const params = new URLSearchParams();
            params.append('usuario', username);
            
            const response = await fetch('/admin/delete_user', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }},
                body: params.toString()
            }});
            
            console.log('Response status:', response.status);
            const text = await response.text();
            console.log('Response text:', text);
            
            let result;
            try {{
                result = JSON.parse(text);
            }} catch (e) {{
                console.error('Error parsing JSON:', e);
                mostrarMensaje('❌ Error al procesar respuesta del servidor', 'error');
                return;
            }}
            
            if (result.success) {{
                mostrarMensaje('✅ ' + result.message, 'exito');
                setTimeout(() => location.reload(), 1500);
            }} else {{
                mostrarMensaje('❌ ' + result.message, 'error');
            }}
        }} catch (error) {{
            console.error('Error:', error);
            mostrarMensaje('❌ Error al eliminar usuario: ' + error.message, 'error');
        }}
    }}

    async function desconectarIP(ip) {{
        if (!confirm('¿Desconectar IP \"' + ip + '\"?')) return;
        
        console.log('Desconectando IP:', ip);
        
        try {{
            const params = new URLSearchParams();
            params.append('ip', ip);
            
            const response = await fetch('/admin/disconnect_ip', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }},
                body: params.toString()
            }});
            
            console.log('Response status:', response.status);
            const text = await response.text();
            console.log('Response text:', text);
            
            let result;
            try {{
                result = JSON.parse(text);
            }} catch (e) {{
                console.error('Error parsing JSON:', e);
                mostrarMensaje('❌ Error al procesar respuesta del servidor', 'error');
                return;
            }}
            
            if (result.success) {{
                mostrarMensaje('✅ ' + result.message, 'exito');
                setTimeout(() => location.reload(), 1500);
            }} else {{
                mostrarMensaje('❌ ' + result.message, 'error');
            }}
        }} catch (error) {{
            console.error('Error:', error);
            mostrarMensaje('❌ Error al desconectar IP: ' + error.message, 'error');
        }}
    }}
</script>

</body>
</html>"""

# =========================================================
# PÁGINA HTML: ACCESO DENEGADO
# =========================================================

HTML_ACCESS_DENIED = """<!DOCTYPE html>
<html>
<head>
    <title>Acceso Denegado</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .caja { max-width: 400px; margin: 100px auto; background: white; 
                padding: 30px; border-radius: 8px; text-align: center; }
        h1 { color: #dc3545; }
    </style>
</head>
<body>
    <div class="caja">
        <h1>⛔ Acceso Denegado</h1>
        <p>Esta área es solo para administradores.</p>
        <p><a href="/logout">Cerrar Sesión</a></p>
    </div>
</body>
</html>"""