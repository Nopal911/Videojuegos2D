import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QPushButton, QLabel)

# Importamos el backend universal para que no suframos con las versiones de Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# --- TU CLASE DEL CANVAS ---
class MiCanvas(FigureCanvas):
    def __init__(self, parent=None):
        # Creamos la figura de Matplotlib
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.axes = self.fig.add_subplot(111)
        
        # Inicializamos el canvas con la figura
        super().__init__(self.fig)
        if parent:
            self.setParent(parent)

    def graficar(self, x, y):
        self.axes.clear()  # Limpiamos para que no se encimen las gráficas
        self.axes.plot(x, y, color='green', marker='o', linestyle='-')
        self.axes.set_title('Gráfica Dinámica')
        self.axes.grid(True, alpha=0.3)
        self.draw() # Refresca el canvas

# --- TU VENTANA PRINCIPAL ---
class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Aplicación con Gráficas")
        self.setGeometry(100, 100, 800, 600)

        # Widget central
        widget_central = QWidget()
        self.setCentralWidget(widget_central)

        # Layout
        layout = QVBoxLayout()
        widget_central.setLayout(layout)

        # Widgets
        self.label = QLabel("Presiona el botón para graficar")
        layout.addWidget(self.label)

        # --- INTEGRACIÓN DEL CANVAS ---
        self.canvas = MiCanvas(self)
        
        # Agregamos la barra de herramientas (zoom, guardar, etc)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Agregamos el canvas al diseño
        layout.addWidget(self.canvas)

        # Botón
        self.boton = QPushButton("Generar Gráfica")
        self.boton.clicked.connect(self.boton_presionado)
        layout.addWidget(self.boton)

    def boton_presionado(self):
        self.label.setText("¡Graficando función cuadrática!")
        
        # Generamos datos de prueba
        x = np.linspace(-10, 10, 20)
        y = x**2  # Una parábola simple
        
        # Mandamos los datos al canvas
        self.canvas.graficar(x, y)

# --- EJECUCIÓN ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec())