import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton

puntos = 0

# Función para sumar
def sumar():
    global puntos 
    puntos += 1
    etiqueta.setText(f"Puntos: {puntos}")

# Función para restar
def restar():
    global puntos 
    puntos -= 1
    etiqueta.setText(f"Puntos: {puntos}")
    
app = QApplication(sys.argv)

ventana = QWidget()
ventana.setWindowTitle("Botones")
ventana.setGeometry(200, 200, 300, 200)

etiqueta = QLabel(f"Puntos: 0            ", ventana)
etiqueta.move(120, 30)

# --- Botón de Sumar ---
boton_sumar = QPushButton("Sumar +1      ", ventana) 
boton_sumar.move(50, 100) # Lo movemos a la izquierda
boton_sumar.clicked.connect(sumar)

# --- Botón de Restar ---
boton_restar = QPushButton("Restar -1     ", ventana) 
boton_restar.move(160, 100) # Lo movemos a la derecha
boton_restar.clicked.connect(restar)

ventana.show()
sys.exit(app.exec())