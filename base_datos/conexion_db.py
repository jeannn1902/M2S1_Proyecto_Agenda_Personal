import sqlite3
from contextlib import contextmanager
from pathlib import Path

RUTA_BD = Path(__file__).resolve().parent.parent / "agenda.db"

def conectar():
    """Abre y devuelve la conexión con la base de datos."""
    conexion = sqlite3.connect(str(RUTA_BD), timeout=10)

    try:
        conexion.execute("PRAGMA foreign_keys = ON")
    except sqlite3.Error:
        conexion.close()
        raise

    return conexion

@contextmanager
def conexion_segura():
    """Administra la conexión y garantiza su cierre."""
    conexion = conectar()

    try:
        yield conexion
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def crear_tablas():
    """Crea las tablas de usuarios y contactos si no existen."""

    with conexion_segura() as conexion:
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

    print("¡Base de datos y tablas listas correctamente!")

if __name__ == "__main__":
    crear_tablas()