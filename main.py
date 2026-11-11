from flask import Flask, redirect, render_template, request, session, url_for

from base_datos.conexion_db import crear_tablas
from base_datos.consultas import (
    agregar_contacto,
    eliminar_contacto,
    iniciar_sesion,
    obtener_contactos,
    registrar_usuario,
)

app = Flask(__name__)
app.secret_key = "clave_secreta_agenda"

crear_tablas()


@app.route("/")
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
    correo = request.form["correo"]
    password = request.form["password"]

    usuario = iniciar_sesion(correo, password)

    if usuario:
        session["usuario_id"] = usuario[0]
        session["usuario_nombre"] = usuario[1]
        return redirect(url_for("vista_agenda"))
    else:
        return "Correo o contraseña incorrectos.", 401


@app.route("/agenda")
def vista_agenda():
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    contactos = obtener_contactos(session["usuario_id"])
    return render_template(
        "agenda.html", nombre=session["usuario_nombre"], contactos=contactos
    )


@app.route("/agregar_contacto", methods=["POST"])
def procesar_agregar_contacto():
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    nombre = request.form["nombre_contacto"]
    telefono = request.form["telefono"]
    correo = request.form["correo_contacto"]
    relacion = request.form["relacion"]

    agregar_contacto(session["usuario_id"], nombre, telefono, correo, relacion)
    return redirect(url_for("vista_agenda"))


@app.route("/eliminar_contacto/<int:contacto_id>")
def procesar_eliminar_contacto(contacto_id):
    if "usuario_id" not in session:
        return redirect(url_for("vista_login"))

    eliminar_contacto(contacto_id, session["usuario_id"])
    return redirect(url_for("vista_agenda"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("vista_login"))



if __name__ == "__main__":
    app.run(debug=True)