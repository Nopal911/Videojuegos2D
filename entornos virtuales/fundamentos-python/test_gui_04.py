import sys 
# Importar elementos visuales
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton

# Función para cambiar el color de fondo
def cambiar_color(hex_color):
    # Corregido: Se quitó el ":" extra al final y se puso ";"
    ventana.setStyleSheet(f"background-color: {hex_color};")
    
# Creamos la aplicación
app = QApplication(sys.argv)

ventana = QWidget() # Creamos la ventana
ventana.setWindowTitle("Selector de Colores") # Título 
ventana.setGeometry(200, 200, 400, 200)

# Diccionario de colores
colores = {
    "Rojo": "#ff4d4d",
    "Azul": "#4da6ff",
    "Verde": "#4dff88",
    "Negro": "#1c1c1c"
}

# Variable x para la posición inicial de los botones
x_pos = 20

# Bucle para crear los botones dinámicamente
for nombre, hex_color in colores.items():
    boton = QPushButton(nombre, ventana)
    boton.setGeometry(x_pos, 80, 75, 40) # Definimos posición y tamaño (x, y, ancho, alto)
    
    # Usamos el valor por defecto en lambda para capturar el color actual del bucle
    boton.clicked.connect(lambda _, c=hex_color: cambiar_color(c))
    
    x_pos += 95 # Aumentamos el espacio para el siguiente botón

# Mostrar ventana
ventana.show()

# Ejecutar app
sys.exit(app.exec())