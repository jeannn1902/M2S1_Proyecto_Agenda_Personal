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


def existe_telefono(usuario_id, telefono, contacto_id_excluir=None):
    """Verifica si un número de teléfono ya está registrado por el mismo usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    if contacto_id_excluir:
        cursor.execute(
            "SELECT id FROM contactos WHERE usuario_id = ? AND telefono = ?",
            (usuario_id, telefono),
        )
    existe = cursor.fetchone() is not None
    conexion.close()
    return existe


def obtener_contactos(usuario_id, busqueda=""):
    """Obtiene contactos del usuario con opción de filtrado por búsqueda."""
    conexion = conectar()
    cursor = conexion.cursor()
    if busqueda:
        patron = f"%{busqueda}%"
        cursor.execute(
            """
            SELECT id, nombre, telefono, correo, categoria
            FROM contactos
            WHERE usuario_id = ? AND (nombre LIKE ? OR categoria LIKE ? OR telefono LIKE ?)
            """,
            (usuario_id, patron, patron, patron)
        )
    else:
        cursor.execute(
            """
            SELECT id, nombre, telefono, correo, categoria
            FROM contactos
            WHERE usuario_id = ?
            ORDER BY nombre ASC
            """,
            (usuario_id,),
        )
    contactos = cursor.fetchall()
    conexion.close()
    return contactos


def obtener_contacto_por_id(contacto_id, usuario_id):
    """Obtiene un único contacto verificando la propiedad del usuario."""    
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre, telefono, correo, categoria FROM contactos WHERE id = ? AND usuario_id = ?",
        (contacto_id, usuario_id),
    )
    contacto = cursor.fetchone()
    conexion.close()
    return contacto


def actualizar_contacto(contacto_id, usuario_id, nombre, telefono, correo, categoria):
    """Actualiza la información de un contacto existente."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE contactos
        SET nombre = ?, telefono = ?, correo = ?, categoria = ?
        WHERE id = ? AND usuario_id = ?
        """,
        (nombre, telefono, correo, categoria, contacto_id, usuario_id),
    )
    conexion.commit()
    conexion.close()
    

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
