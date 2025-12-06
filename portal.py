import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

PORTAL_IP = "0.0.0.0"
PORT = 80

# ---------------------------
# Inicializar BD con un usuario admin
# ---------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    # Usuario admin por defecto
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", ("admin", "admin"))
    conn.commit()
    conn.close()


# ---------------------------
# Servidor HTTP
# ---------------------------
class LoginHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Página de login
        login_page = """
        <html>
        <body>
            <h2>Login</h2>
            <form method="POST" action="/">
                Usuario: <input type="text" name="username"><br><br>
                Contraseña: <input type="password" name="password"><br><br>
                <input type="submit" value="Ingresar">
            </form>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(login_page.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(length).decode("utf-8")
        data = parse_qs(post_data)

        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]

        # Validar contra BD
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        # Si usuario y contraseña son correctos
        if user:
            if username == "admin":
                # Página para agregar usuario
                response = """
                <html>
                <body>
                    <h2>Panel de Administrador</h2>
                    <h3>Agregar nuevo usuario</h3>
                    <form method="POST" action="/add_user">
                        Nuevo usuario: <input type="text" name="new_username"><br><br>
                        Nueva contraseña: <input type="password" name="new_password"><br><br>
                        <input type="submit" value="Agregar">
                    </form>
                </body>
                </html>
                """
            else:
                response = "<h2>Usted se ha logueado correctamente</h2>"
        else:
            response = "<h2>Credenciales inválidas</h2>"

        conn.close()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    # ---------------------------
    # Manejar ruta /add_user
    # ---------------------------
    def do_POST_add_user(self):
        length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(length).decode("utf-8")
        data = parse_qs(post_data)

        new_username = data.get("new_username", [""])[0]
        new_password = data.get("new_password", [""])[0]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            message = f"<h3>Usuario '{new_username}' agregado correctamente.</h3>"
        except sqlite3.IntegrityError:
            message = "<h3>Error: el usuario ya existe.</h3>"

        conn.close()

        response = f"""
        <html>
        <body>
            <h2>Panel de Administrador</h2>
            {message}
            <a href="/">Volver al login</a>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    # ---------------------------
    # Router manual para /add_user
    # ---------------------------
    def do_POST(self):
        if self.path == "/add_user":
            return self.do_POST_add_user()
        else:
            return self.login_post_handler()

    # Redefinir login POST separado para claridad
    def login_post_handler(self):
        length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(length).decode("utf-8")
        data = parse_qs(post_data)

        username = data.get("username", [""])[0]
        password = data.get("password", [""])[0]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            if username == "admin":
                response = """
                <html>
                <body>
                    <h2>Panel de Administrador</h2>
                    <h3>Agregar nuevo usuario</h3>
                    <form method="POST" action="/add_user">
                        Nuevo usuario: <input type="text" name="new_username"><br><br>
                        Nueva contraseña: <input type="password" name="new_password"><br><br>
                        <input type="submit" value="Agregar">
                    </form>
                </body>
                </html>
                """
            else:
                response = "<h2>Usted se ha logueado correctamente</h2>"
        else:
            response = "<h2>Credenciales inválidas</h2>"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))


# ---------------------------
# Iniciar servidor
# ---------------------------
if __name__ == "__main__":
    init_db()
    server = HTTPServer((PORTAL_IP, PORT), LoginHandler)
    print(f"Servidor escuchando en http://{PORTAL_IP}:{PORT}")
    server.serve_forever()
