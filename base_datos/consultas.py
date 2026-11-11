from base_datos.conexion_db import conectar


# ==========================================
# FUNCIONES DE USUARIOS
# ==========================================
def registrar_usuario(nombre, correo, password):
    """Registra un nuevo usuario en la base de datos."""
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
            (nombre, correo, password)
        )
        conexion.commit()
        return True, "Usuario registrado con éxito."
    except Exception as e:  # noqa: BLE001
        return False, f"Error al registrar: {e}"
    finally:
        conexion.close()

def iniciar_sesion(correo, password):
    """Verifica credenciales y regresa los datos del usuario si son correctos."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, correo FROM usuarios WHERE correo = ? AND password = ?",
        (correo, password)
    )
    usuario = cursor.fetchone()
    conexion.close()
    return usuario

# ==========================================
# FUNCIONES DE CONTACTOS
# ==========================================
def agregar_contacto(usuario_id, nombre, telefono="", correo="", categoria="General"):
    """Agrega un nuevo contacto ligado al id del usuario autenticado."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        INSERT INTO contactos (usuario_id, nombre, telefono, correo, categoria)
        VALUES (?, ?, ?, ?, ?)
        """,
        (usuario_id, nombre, telefono, correo, categoria)
    )
    conexion.commit()
    conexion.close()

def obtener_contactos(usuario_id):
    """Obtiene todos los contactos pertenecientes a un usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, telefono, correo, categoria FROM contactos WHERE usuario_id = ?",
        (usuario_id,)
    )
    contactos = cursor.fetchall()
    conexion.close()
    return contactos

def eliminar_contacto(contacto_id, usuario_id):
    """Elimina un contacto asegurando que pertenezca al usuario activo."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "DELETE FROM contactos WHERE id = ? AND usuario_id = ?",
        (contacto_id, usuario_id)
    )
    conexion.commit()
    conexion.close()