#Prueba de micro framework web de python
from flask import Flask, render_template, app

#Importar modulo de aleatoriedad
from random import choice

#Creo una lista 
valores = [1,2,3,4,5,6]

#Crear una app flask
app = Flask(__name__)

#Decoro una función que se ejecute en el explorador
@app.route("/")
def inicio():
    #selecciono de maner aletoria uno de los valores de la lista
    valor = choice(valores)
    #Va a la ruta del archivo index.html y le coloca el parametro valor
    return render_template("index.html", valor = valor)

##ejecutar la aplicacion
if __name__ == '__main__':
    app.run(debug=True)
    

