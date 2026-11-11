from base_datos.conexion_db import crear_tablas
from base_datos.consultas import (
    agregar_contacto,
    iniciar_sesion,
    obtener_contactos,
    registrar_usuario,
)


def probar_sistema():
    # 1. Asegurar que la BD y las tablas existan
    print("--- INICIALIZANDO BASE DE DATOS ---")
    crear_tablas()

    # 2. Registrar un usuario de prueba
    print("\n--- 1. PRUEBA DE REGISTRO ---")
    _exito, mensaje = registrar_usuario("Jean Perez", "jean@example.com", "1234")
    print(f"Resultado: {mensaje}")

    # 3. Intentar iniciar sesión
    print("\n--- 2. PRUEBA DE INICIO DE SESIÓN ---")
    usuario = iniciar_sesion("jean@example.com", "1234")

    if usuario:
        usuario_id, nombre, _correo = usuario
        print(f"¡Inicio de sesión exitoso! bienvenido {nombre} (ID: {usuario_id})")

        # 4. Agregar contactos vinculados al usuario autenticado
        print("\n--- 3. AGREGANDO CONTACTOS ---")
        agregar_contacto(
            usuario_id=usuario_id,
            nombre="Luis",
            telefono="56-5569-9386",
            correo="luis@example.com",
            categoria="Amigos",
        )
        agregar_contacto(
            usuario_id=usuario_id,
            nombre="Carlos",
            telefono="771-959-3289",
            correo="carlos@example.com",
            categoria="Trabajo",
        )
        print("Contactos agregados con éxito.")

        # 5. Consultar y mostrar la lista de contactos
        print("\n--- 4. LISTANDO CONTACTOS DE LA AGENDA ---")
        contactos = obtener_contactos(usuario_id)

        if contactos:
            for c in contactos:
                c_id, c_nombre, c_tel, c_correo, c_cat = c
                print(
                    f"ID: {c_id} | Nombre: {c_nombre} | Tel: {c_tel} | Correo: {c_correo} | Categoría: {c_cat}"
                )
        else:
            print("No hay contactos registrados en la agenda.")
    else:
        print("Error: Credenciales incorrectas.")


if __name__ == "__main__":
    probar_sistema()