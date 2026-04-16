#importo caracteristicas de sistema
import sys
#importo componentes gráficos
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

#cambiar color
def cambiar_color(is_checked):
    if is_checked:
        ventana.setStyleSheet("background-color: red; color:blue;")
    else:
        ventana.setStyleSheet("background-color: blue; color:red")
#función para calcular una suma
def calcular():
    try:
        a = float(caja1.text())
        b = float(caja2.text())
        resultado.setText(str(round(a+b, 2)))
    except ValueError:
        resultado.setText("error")
   
#crear aplicación 
app = QApplication(sys.argv)
#crear ventana
ventana = QWidget()
ventana.setGeometry(200, 200, 300,220)
ventana.setWindowTitle("Mini Calculadora")

#cajas de texto
caja1 = QLineEdit(ventana) #colocamos como argumento el contenedor
caja1.move(50,40)

caja2 = QLineEdit(ventana)
caja2.move(50,80)

#boton
boton = QPushButton("Sumar", ventana)
boton.move(50,120)
boton.clicked.connect(calcular)

#botón de cambiar color
btn_cambiar = QPushButton("Cambiar color", ventana)
btn_cambiar.setCheckable(True)
btn_cambiar.move(50, 160)
btn_cambiar.clicked.connect(cambiar_color)
#etiqueta de resultado
resultado = QLabel("resultado", ventana)
resultado.move(180, 70)

#mostramos ventana
ventana.show()
sys.exit(app.exec())
