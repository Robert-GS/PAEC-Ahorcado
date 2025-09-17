import random
import os
from flask import Flask, render_template, redirect, url_for, session

app = Flask(__name__)
#app.secret_key = "clave-secreta-ahorcado"  # Cambia esto en producción

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")


#def cargar_palabras():
#    with open("palabras.txt", "r", encoding="utf-8") as f:
#        return [linea.strip().upper() for linea in f if linea.strip()]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_palabras():
    with open(os.path.join(BASE_DIR, "palabras.txt"), "r", encoding="utf-8") as f:
        return [linea.strip().upper() for linea in f if linea.strip()]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/juego")
def juego():
    if "palabra" not in session:
        palabras = cargar_palabras()
        palabra = random.choice(palabras)
        session["palabra"] = palabra
        session["aciertos"] = []
        session["errores"] = []

    palabra = session.get("palabra")
    aciertos = session.get("aciertos", [])
    errores = session.get("errores", [])

    # Progreso para mostrar (lista de caracteres o '_')
    progreso = [letra if letra in aciertos else "_" for letra in palabra]

    # Estado del juego
    if set(palabra).issubset(set(aciertos)):
        mensaje = "🎉 Felicidades, ¡has ganado!"
        terminado = True
        progreso = list(palabra)  # mostrar la palabra completa si ganó
    elif len(errores) >= 6:
        mensaje = f"❌ Lo siento, has perdido. La palabra era: {palabra}"
        terminado = True
        progreso = list(palabra)  # mostrar la palabra completa si perdió
    else:
        mensaje = None
        terminado = False

    return render_template(
    "juego.html",
    palabra=progreso,
    aciertos=aciertos,
    errores=errores,
    terminado=terminado,
    mensaje=mensaje,
    imagen=f"ahorcado{len(errores)}.png" 
)


@app.route("/intento/<letra>")
def intento(letra):
    letra = letra.upper()
    if "palabra" in session:
        palabra = session["palabra"]
        # obtener copias locales para modificar
        aciertos = session.get("aciertos", [])
        errores = session.get("errores", [])

        if letra in palabra:
            if letra not in aciertos:
                aciertos.append(letra)
        else:
            if letra not in errores:
                errores.append(letra)

        # reasignar a session (importante para que Flask lo persista)
        session["aciertos"] = aciertos
        session["errores"] = errores
        # alternativa: session.modified = True

    return redirect(url_for("juego"))


@app.route("/reiniciar")
def reiniciar():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)