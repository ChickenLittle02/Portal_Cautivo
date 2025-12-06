"""
paginas.py
Almacena todas las páginas HTML del Portal Cautivo
"""

# =========================================================
# PÁGINA 1: LOGIN
# =========================================================

PAGINA_LOGIN = """
<!DOCTYPE html>
<html>
<head>
    <title>Portal Cautivo - Login</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #f5f5f5; 
            margin: 0;
        }
        .caja {
            max-width: 350px;
            margin: 100px auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px #ccc;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 14px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        button:hover {
            background: #0056b3;
        }
        .info {
            text-align: center;
            font-size: 12px;
            color: #666;
            margin-top: 20px;
        }
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
        <div class="info">
            <p><strong>Credenciales de prueba:</strong></p>
            admin / 123456<br>
            user1 / pass1
        </div>
    </div>
</body>
</html>
"""

# =========================================================
# PÁGINA 2: ÉXITO EN LOGIN
# =========================================================

PAGINA_EXITO = """
<!DOCTYPE html>
<html>
<head>
    <title>¡Autenticado!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
        }
        .caja {
            max-width: 350px;
            margin: 100px auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px #ccc;
        }
        h1 {
            color: #28a745;
        }
        p {
            color: #666;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="caja">
        <h1>✅ ¡Acceso Permitido!</h1>
        <p>Tu IP ha sido registrada correctamente.</p>
        <p>El firewall será actualizado para permitirte acceso a Internet.</p>
        <p style="margin-top: 30px; font-size: 14px; color: #999;">
            Puedes cerrar esta página
        </p>
    </div>
</body>
</html>
"""

# =========================================================
# PÁGINA 3: ERROR EN LOGIN
# =========================================================

PAGINA_ERROR = """
<!DOCTYPE html>
<html>
<head>
    <title>Error de Autenticación</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
        }
        .caja {
            max-width: 350px;
            margin: 100px auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px #ccc;
        }
        h1 {
            color: #dc3545;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        a:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="caja">
        <h1>❌ Error de Autenticación</h1>
        <p>Usuario o contraseña incorrectos</p>
        <a href="/">Volver a intentar</a>
    </div>
</body>
</html>
"""

# =========================================================
# PÁGINA 4: 404 NO ENCONTRADO
# =========================================================

PAGINA_404 = """
<!DOCTYPE html>
<html>
<head>
    <title>404 - No Encontrado</title>
</head>
<body>
    <h1>404 - Página no encontrada</h1>
    <p><a href="/">Volver al login</a></p>
</body>
</html>
"""

# =========================================================
# PÁGINA 5: ESTADO (DEBUG)
# =========================================================

def PAGINA_ESTADO(sesiones):
    """
    Genera una página HTML con el estado de las sesiones
    
    Argumentos:
        sesiones (dict): Diccionario de sesiones activas
    
    Retorna:
        str: HTML generado dinámicamente
    """
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Estado del Portal</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .caja { max-width: 500px; margin: 50px auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        pre { background: #f0f0f0; padding: 15px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="caja">
        <h1>Estado del Portal Cautivo</h1>
        <p><strong>Sesiones Activas: {}</strong></p>
        <pre>{}</pre>
        <p><a href="/">Volver</a></p>
    </div>
</body>
</html>
"""
    return html.format(len(sesiones), str(sesiones))