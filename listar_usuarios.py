import sqlite3

DB_FILE = "users.db"

def listar_usuarios():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT username, password FROM users")
        usuarios = cursor.fetchall()

        if len(usuarios) == 0:
            print("La tabla 'users' está vacía.")
        else:
            print("Usuarios en la base de datos:\n")
            for user in usuarios:
                print(f"Usuario: {user[0]} | Contraseña: {user[1]}")

        conn.close()

    except sqlite3.OperationalError as e:
        print("Error al acceder a la base de datos:")
        print(e)

if __name__ == "__main__":
    listar_usuarios()
