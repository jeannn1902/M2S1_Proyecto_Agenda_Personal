import sqlite3


def conectar():
    """Abre y devuelve la conexión con la base de datos."""
    conexion = sqlite3.connect("agenda.db")
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

def crear_tablas():
    """Crea las tablas de usuarios y contactos si no existen."""
    conexion = conectar()
    cursor = conexion.cursor()

    # ========== TABLA DE USUARIOS ==========
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # ========== TABLA DE CONTACTOS ==========
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contactos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            telefono TEXT,
            correo TEXT,
            categoria TEXT DEFAULT 'General',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    conexion.commit()
    conexion.close()
    print("¡Base de datos y tablas listas correctamente!")

if __name__ == "__main__":
    crear_tablas()