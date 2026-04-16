import sys
import numpy as np  # Faltaba esta importación
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt

# Importar componentes de matplotlib para PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class CanvasMatplotlib(FigureCanvas):
    """
    Clase que contiene un lienzo de matplotlib.
    """
    def __init__(self, parent=None):
        # Creamos la figura de matplotlib
        self.figura = Figure(figsize=(8, 5), dpi=100)
        
        # Crear ejes de la figura (Corregido: add_subplot)
        self.ejes = self.figura.add_subplot(111)
        
        # Iniciar lienzo (Corregido: sintaxis de super)
        super().__init__(self.figura)
        self.setParent(parent)
        
        # Configuración inicial
        self.figura.tight_layout()
        
    def graficar_linea(self, x, y, titulo="Gráfica de Línea"):
        self.ejes.clear()
        self.ejes.plot(x, y, 'b-', linewidth=2, marker='o')
        self.configurar_ejes(titulo, 'Eje X', 'Eje Y')
        self.draw()
        
    def graficar_barras(self, categorias, valores, titulo="Gráfica de Barras"):
        self.ejes.clear()
        colores = ["#2563eb", "#10b981", "#f59e0b", "#f43f5e", "#8b5cf6"]
        
        barras = self.ejes.bar(categorias, valores, color=colores[:len(valores)])
        
        self.configurar_ejes(titulo, 'Categorías', 'Valores')

        # Agregar etiquetas de valor sobre las barras
        for barra in barras:
            altura = barra.get_height()
            self.ejes.text(
                barra.get_x() + barra.get_width()/2,
                altura,
                f'{altura:.1f}',
                ha='center', va='bottom'
            )
        self.draw()

    def graficar_dispersion(self, x, y, titulo='Gráfica de Dispersión'):
        self.ejes.clear()
        self.ejes.scatter(x, y, s=100, alpha=0.6, color='#2563eb')
        self.configurar_ejes(titulo, 'Eje X', 'Eje Y')
        self.draw()

    def configurar_ejes(self, titulo, xlabel, ylabel):
        """Método auxiliar para evitar repetición de código"""
        self.ejes.set_title(titulo, fontsize=14, fontweight='bold')
        self.ejes.set_xlabel(xlabel, fontsize=12)
        self.ejes.set_ylabel(ylabel, fontsize=12)
        self.ejes.grid(True, alpha=0.3)


class VentanaGraficas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('📈 Gráficas con Matplotlib')
        self.setGeometry(100, 100, 1000, 700)
        self.inicializar_interfaz()
    
    def inicializar_interfaz(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        
        # --- SECCIÓN 1: Controles ---
        grupo_controles = QGroupBox('⚙️ Controles')
        layout_controles = QHBoxLayout(grupo_controles)
        
        layout_controles.addWidget(QLabel('Tipo:'))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(['Línea', 'Barras', 'Dispersión'])
        self.combo_tipo.currentTextChanged.connect(self.actualizar_grafica)
        layout_controles.addWidget(self.combo_tipo)
        
        layout_controles.addWidget(QLabel('Puntos:'))
        self.slider_puntos = QSlider(Qt.Orientation.Horizontal)
        self.slider_puntos.setMinimum(5)
        self.slider_puntos.setMaximum(50)
        self.slider_puntos.setValue(10)
        self.slider_puntos.valueChanged.connect(self.actualizar_grafica)
        layout_controles.addWidget(self.slider_puntos)
        
        self.label_puntos = QLabel('10')
        layout_controles.addWidget(self.label_puntos)
        
        boton_actualizar = QPushButton('🔄 Actualizar')
        boton_actualizar.setStyleSheet("background-color: #10b981; color: white; padding: 8px; border-radius: 5px;")
        boton_actualizar.clicked.connect(self.actualizar_grafica)
        layout_controles.addWidget(boton_actualizar)
        
        layout_principal.addWidget(grupo_controles)
        
        # --- SECCIÓN 2: Canvas ---
        grupo_grafica = QGroupBox('📊 Visualización')
        layout_grafica = QVBoxLayout(grupo_grafica)
        
        self.canvas = CanvasMatplotlib(self) # Ahora acepta 'self'
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout_grafica.addWidget(self.toolbar)
        layout_grafica.addWidget(self.canvas)
        layout_principal.addWidget(grupo_grafica)
        
        self.actualizar_grafica()
    
    def actualizar_grafica(self):
        n_puntos = self.slider_puntos.value()
        self.label_puntos.setText(str(n_puntos))
        tipo = self.combo_tipo.currentText()
        
        # Generar datos
        x = np.linspace(0, 10, n_puntos)
        y = np.sin(x) * 2 + np.random.randn(n_puntos) * 0.3
        
        if tipo == 'Línea':
            self.canvas.graficar_linea(x, y, f'Línea ({n_puntos} pts)')
        elif tipo == 'Barras':
            categorias = [f'C{i+1}' for i in range(min(n_puntos, 8))]
            valores = np.abs(y[:len(categorias)])
            self.canvas.graficar_barras(categorias, valores, 'Barras')
        elif tipo == 'Dispersión':
            self.canvas.graficar_dispersion(x, y, f'Dispersión ({n_puntos} pts)')

def main():
    app = QApplication(sys.argv)
    ventana = VentanaGraficas()
    ventana.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    