#!/usr/bin/env python3
"""
html_templates.py - Plantillas HTML del Portal Cautivo
"""

# =========================================================
# PÁGINA HTML: LOGIN
# =========================================================

HTML_LOGIN = """<!DOCTYPE html>
<html>
<head>
    <title>Portal Cautivo</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .caja { max-width: 350px; margin: 100px auto; background: white; 
                padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px #ccc; }
        h1 { text-align: center; color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; 
                border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; 
                 border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="caja">
        <h1>🔐 Portal Cautivo</h1>
        <form method="POST" action="/login">
            <input type="text" name="usuario" placeholder="Usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Iniciar Sesión</button>
        </form>
        <p style="text-align: center; font-size: 12px; color: #666;">
            Usuario por defecto: admin / 123456
        </p>
        <p style="text-align: center; margin-top: 15px;">
            <a href="/admin" style="color: #007bff; text-decoration: none; font-size: 12px;">
                🔐 Panel de Administración
            </a>
        </p>
    </div>
</body>
</html>"""

# =========================================================
# PÁGINA HTML: ÉXITO
# =========================================================

HTML_EXITO = """<!DOCTYPE html>
<html>
<head>
    <title>¡Autenticado!</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .caja { max-width: 350px; margin: 100px auto; background: white; 
                padding: 30px; border-radius: 8px; text-align: center; }
        h1 { color: #28a745; }
    </style>
</head>
<body>
    <div class="caja">
        <h1>✅ ¡Acceso Permitido!</h1>
        <p>Tu IP ha sido autorizada en el firewall.</p>
        <p>Ahora puedes acceder a Internet.</p>
        <p style="margin-top: 20px;">
            <a href="/admin" style="display: inline-block; padding: 10px 20px; 
                                     background: #007bff; color: white; text-decoration: none; 
                                     border-radius: 4px; margin-right: 10px;">
                🔐 Panel Admin
            </a>
            <a href="/logout" style="display: inline-block; padding: 10px 20px; 
                                      background: #dc3545; color: white; text-decoration: none; 
                                      border-radius: 4px;">
                🚪 Cerrar Sesión
            </a>
        </p>
    </div>
</body>
</html>"""

# =========================================================
# PÁGINA HTML: ERROR
# =========================================================

HTML_ERROR = """<!DOCTYPE html>
<html>
<body>
    <h1>❌ Error de Autenticación</h1>
    <p>Usuario o contraseña incorrectos</p>
    <p><a href="/">Volver</a></p>
</body>
</html>"""

# =========================================================
# PÁGINA HTML: LOGOUT
# =========================================================

HTML_LOGOUT = """<!DOCTYPE html>
<html>
<body>
    <h1>✅ Sesión Cerrada</h1>
    <p>Tu IP ha sido bloqueada.</p>
    <p><a href="/">Volver al login</a></p>
</body>
</html>"""