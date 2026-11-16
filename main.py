import os
import secrets
from datetime import timedelta

from flask import Flask, redirect, render_template, request, session, url_for

from base_datos.conexion_db import crear_tablas
from base_datos.consultas import (
    actualizar_contacto,
    agregar_contacto,
    eliminar_contacto,
    existe_telefono,
    iniciar_sesion,
    obtener_contacto_por_id,
    obtener_contactos,
    registrar_usuario,
)


def cargar_variables_entorno(ruta=".env"):
    """Lee el archivo .env local si existe y carga sus claves en os.environ."""
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())


cargar_variables_entorno()

app = Flask(__name__)

# Clave secreta leída desde entorno
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Configuración segura de cookies de sesión
modo_debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=not modo_debug,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
)

crear_tablas()


@app.route("/")
def vista_inicio():
    return render_template("inicio.html")


@app.route("/login")
def vista_login():
    return render_template("login.html")


@app.route("/registro")
def vista_registro():
    return render_template("registro.html")


@app.route("/registro", methods=["POST"])
def procesar_registro():
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    password = request.form["password"]

    exito, mensaje = registrar_usuario(nombre, correo, password)

    if exito:
        return redirect(url_for("vista_login"))
    else:
        return f"Error: {mensaje}", 400


@app.route("/login", methods=["POST"])
def procesar_login():
    correo = request.form["correo"].strip()
    password = request.form["password"]

    usuario = iniciar_sesion(correo, password)

    if usuario:
        session.clear()
        session.permanent = True
        session["usuario_id"] = usuario[0]
        session["usuario_nombre"] = usuario[1]
        return redirect(url_for("vista_agenda"))
    else:
        return "Correo o contraseña incorrectos.", 401


@app.route("/agenda")
def vista_agenda():
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    busqueda = request.args.get("q", "").strip()
    mensaje_error = request.args.get("error", "")
    contactos = obtener_contactos(session["usuario_id"], busqueda)

    return render_template(
        "agenda.html",
        nombre=session["usuario_nombre"],
        contactos=contactos,
        busqueda=busqueda,
        error=mensaje_error,
    )


@app.route("/agregar_contacto", methods=["POST"])
def procesar_agregar_contacto():
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    nombre = request.form["nombre_contacto"].strip()
    telefono = request.form["telefono"].strip()
    correo = request.form["correo_contacto"].strip()
    relacion = request.form["relacion"].strip()
    usuario_id = session["usuario_id"]

    # Validación de número telefónico duplicado
    if existe_telefono(usuario_id, telefono):
        return redirect(
            url_for("vista_agenda", error="El número de teléfono ya está en tu agenda.")
        )

    agregar_contacto(usuario_id, nombre, telefono, correo, relacion)
    return redirect(url_for("vista_agenda"))


@app.route("/editar_contacto/<int:contacto_id>", methods=["GET", "POST"])
def editar_contacto(contacto_id):
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    usuario_id = session["usuario_id"]
    contacto = obtener_contacto_por_id(contacto_id, usuario_id)

    if not contacto:
        return redirect(url_for("vista_agenda"))

    if request.method == "POST":
        nombre = request.form["nombre_contacto"].strip()
        telefono = request.form["telefono"].strip()
        correo = request.form["correo_contacto"].strip()
        relacion = request.form["relacion"].strip()

        # Validar teléfono duplicado excluyendo el registro actual
        if existe_telefono(usuario_id, telefono, contacto_id_excluir=contacto_id):
            return render_template(
                "editar.html",
                contacto=contacto,
                error="Este número de teléfono ya pertenece a otro contacto.",
            )

        actualizar_contacto(contacto_id, usuario_id, nombre, telefono, correo, relacion)
        return redirect(url_for("vista_agenda"))

    return render_template("editar.html", contacto=contacto)


@app.route("/eliminar_contacto/<int:contacto_id>")
def procesar_eliminar_contacto(contacto_id):
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    eliminar_contacto(contacto_id, session["usuario_id"])
    return redirect(url_for("vista_agenda"))


@app.after_request
def evitar_cache_rutas_privadas(response):
    """Evita que el navegador guarde en caché vistas privadas mientras hay sesión activa."""
    if "usuario_id" in session:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("vista_login"))


if __name__ == "__main__":
    app.run(debug=modo_debug)