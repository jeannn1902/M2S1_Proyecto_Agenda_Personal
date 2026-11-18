import logging
import re
import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from base_datos.conexion_db import conectar, conexion_segura

logger = logging.getLogger(__name__)

PATRON_CORREO = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
PATRON_TELEFONO = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def validar_datos_usuario(nombre, correo, password):
    """Valida los campos del registro de usuario. Devuelve (es_valido, mensaje_error)."""

    nombre = nombre.strip() if nombre else ""
    correo = correo.strip() if correo else ""

    if not 2 <= len(nombre) <= 50:
        return False, "El nombre debe tener entre 2 y 50 caracteres."
    
    if not correo or len(correo) > 120 or not PATRON_CORREO.match(correo):
        return False, "Ingresa un correo válido de máximo 120 caracteres."
    
    if not password or len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    
    return True, ""


def validar_datos_contacto(nombre, telefono, correo=""):
    """Valida los campos al crear o editar un contacto. Devuelve (es_valido, mensaje_error)."""

    nombre = nombre.strip() if nombre else ""
    telefono = telefono.strip() if telefono else ""
    correo = correo.strip() if correo else ""

    if not 2 <= len(nombre) <= 80:
        return False, "El nombre debe tener entre 2 y 80 caracteres."

    digitos = sum(caracter.isdigit() for caracter in telefono)
    
    if not 7 <= digitos <= 15:
        return False, "El teléfono debe contener entre 7 y 15 dígitos."

    if not all(
        caracter.isdigit() or caracter in "+()- ."
        for caracter in telefono
    ):
        return False, "El teléfono contiene caracteres no permitidos."
    
    if correo and (
        len(correo) > 120 or not PATRON_CORREO.match(correo)
    ):
        return False, "El correo del contacto no es válido o supera los 120 caracteres."
    
    return True, ""


# ==========================================
# FUNCIONES DE USUARIOS
# ==========================================
def registrar_usuario(nombre, correo, password):
    """Registra un nuevo usuario en la base de datos con contraseña hasheada."""
    nombre_limpio = nombre.strip()
    correo_limpio = correo.strip().lower()

    es_valido, error = validar_datos_usuario(nombre_limpio, correo_limpio, password)
    if not es_valido:
        return False, error

    conexion = conectar()
    cursor = conexion.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
            (nombre_limpio, correo_limpio, password_hash)
        )
        conexion.commit()
        return True, "Usuario registrado con éxito."
    except sqlite3.IntegrityError:
        return False, "Este correo electrónico ya está registrado."
    except Exception:
        logger.exception("Error inesperado al registrar usuario")
        return False, "Ocurrió un error interno al crear la cuenta. Inténtalo más tarde."
    finally:
        conexion.close()


def iniciar_sesion(correo, password):
    """Verifica las credenciales utilizando exclusivamente contraseñas hasheadas."""
    correo_limpio = correo.strip().lower()

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, nombre, correo, password FROM usuarios WHERE correo = ?",
            (correo_limpio,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return None

        password_almacenado = usuario[3]

        if not check_password_hash(password_almacenado, password):
            return None

        return (usuario[0], usuario[1], usuario[2])

    finally:
        conexion.close()

# ==========================================
# FUNCIONES DE CONTACTOS
# ==========================================
def agregar_contacto(usuario_id, nombre, telefono="", correo="", categoria="General"):
    """Agrega un nuevo contacto ligado al id del usuario autenticado."""

    with conexion_segura() as conexion:
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO contactos (usuario_id, nombre, telefono, correo, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario_id, nombre, telefono, correo, categoria)
        )

        conexion.commit()


def existe_telefono(usuario_id, telefono, contacto_id_excluir=None):
    """Verifica si un número de teléfono ya está registrado por el mismo usuario."""
    conexion = conectar()
    cursor = conexion.cursor()
    if contacto_id_excluir:
        cursor.execute(
            "SELECT id FROM contactos WHERE usuario_id = ? AND telefono = ? AND id != ?",
            (usuario_id, telefono, contacto_id_excluir),
        )
    else:
        cursor.execute(
            "SELECT id FROM contactos WHERE usuario_id = ? AND telefono = ?",
            (usuario_id, telefono),
        )
    existe = cursor.fetchone() is not None
    conexion.close()
    return existe


def obtener_contactos(usuario_id, busqueda=""):
    """Obtiene contactos con opción de filtro por búsqueda."""
    conexion = conectar()
    cursor = conexion.cursor()
    if busqueda:
        patron = f"%{busqueda}%"
        cursor.execute(
            """
            SELECT id, nombre, telefono, correo, categoria 
            FROM contactos 
            WHERE usuario_id = ? AND (nombre LIKE ? OR categoria LIKE ? OR telefono LIKE ?)
            ORDER BY nombre ASC
            """,
            (usuario_id, patron, patron, patron),
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
