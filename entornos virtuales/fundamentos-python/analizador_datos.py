import sys
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFileDialog,
    QMessageBox, QLabel, QComboBox, QSplitter
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class GestorDatos:
    """
    Clase responsable de manejar los datos
    Separamos la LÓGICA de la INTERFAZ
    """
    def __init__(self):
        self.df = None # DataFrame de pandas

    def cargar_csv(self, ruta):
        """Cargar archivo CSV"""
        try:
            self.df = pd.read_csv(ruta)
            return True, "Archivo cargado exitosamente"
        except Exception as e:
            return False, str(e)

    def generar_ejemplo(self):
        """Generar datos de ejemplo para probar"""
        self.df = pd.DataFrame({
            'Mes': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
            'Ventas': [15000, 18000, 16500, 19000, 21000, 17500],
            'Gastos': [12000, 13500, 12800, 14000, 15500, 13000],
            'Utilidad': [3000, 4500, 3700, 5000, 5500, 4500]
        })
        return True, "Datos de ejemplo generados"

    def obtener_columnas_numericas(self):
        """Obtener solo columnas con números"""
        if self.df is not None:
            return self.df.select_dtypes(include=[np.number]).columns.tolist()
        return []

    def calcular_estadisticas(self, columna):
        """Calcular estadísticas de una columna"""
        if self.df is None or columna not in self.df.columns:
            return None
        datos = self.df[columna].dropna() # Quitar valores nulos
        return {
            'Promedio': np.mean(datos),
            'Máximo': np.max(datos),
            'Mínimo': np.min(datos),
            'Total': np.sum(datos)
        }

class MiCanvas(FigureCanvas):
    """
    Clase responsable de crear gráficas
    Separamos la VISUALIZACIÓN de la LÓGICA
    """
    def __init__(self):
        # Crear figura de matplotlib
        self.figura = Figure(figsize=(6, 4))
        self.ejes = self.figura.add_subplot(111)
        super().__init__(self.figura)
        self.figura.tight_layout()

    def graficar_datos(self, datos, etiquetas, titulo='Gráfica'):
        """Crear gráfica de barras"""
        self.ejes.clear() # Limpiar gráfica anterior
        # Colores modernos
        colores = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
        # Crear barras
        self.ejes.bar(etiquetas, datos, color=colores[:len(datos)])
        # Configurar apariencia
        self.ejes.set_title(titulo, fontsize=12, fontweight='bold')
        self.ejes.set_ylabel('Valores')
        self.ejes.tick_params(axis='x', rotation=45)
        # Ajustar layout y redibujar
        self.figura.tight_layout()
        self.draw()

class VentanaAnalisis(QMainWindow):
    """
    Ventana principal que COORDINA todo
    No hace cálculos ni gráficas, solo coordina
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('📊 Analizador Simple de Datos')
        self.setGeometry(100, 100, 1200, 700)
        # Crear gestor de datos
        self.gestor = GestorDatos()
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        """Configurar la interfaz"""
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout()
        widget_central.setLayout(layout_principal)

        # BOTONES SUPERIORES
        layout_botones = QHBoxLayout()
        btn_cargar = QPushButton('📂 Cargar CSV')
        btn_cargar.clicked.connect(self.cargar_archivo)
        layout_botones.addWidget(btn_cargar)
        btn_ejemplo = QPushButton('🎲 Generar Ejemplo')
        btn_ejemplo.clicked.connect(self.generar_ejemplo)
        layout_botones.addWidget(btn_ejemplo)
        layout_botones.addStretch() 
        layout_principal.addLayout(layout_botones)

        # DIVISOR: TABLA | GRÁFICA
        divisor = QSplitter(Qt.Orientation.Horizontal)
        
        # PANEL IZQUIERDO: Tabla
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True) 
        divisor.addWidget(self.tabla)

        # PANEL DERECHO: Gráfica + Controles
        widget_derecho = QWidget()
        layout_derecho = QVBoxLayout()
        widget_derecho.setLayout(layout_derecho)

        # Selector de columna
        layout_control = QHBoxLayout()
        layout_control.addWidget(QLabel('📊 Columna:'))
        self.combo_columna = QComboBox()
        self.combo_columna.currentTextChanged.connect(self.actualizar_grafica)
        layout_control.addWidget(self.combo_columna)
        layout_derecho.addLayout(layout_control)

        # Canvas de gráfica
        self.canvas = MiCanvas()
        layout_derecho.addWidget(self.canvas)

        # Estadísticas
        self.label_stats = QLabel('Selecciona una columna para ver estadísticas')
        self.label_stats.setStyleSheet("""
            QLabel {
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 6px;
                font-size: 12px;
            }
        """)
        layout_derecho.addWidget(self.label_stats)
        divisor.addWidget(widget_derecho)
        divisor.setSizes([400, 800]) 
        layout_principal.addWidget(divisor)

        # Estilos CSS
        self.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9fafb;
                border: 1px solid #e5e7eb;
            }
            QHeaderView::section {
                background-color: #2563eb;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)

    def cargar_archivo(self):
        """Cargar archivo CSV"""
        ruta, _ = QFileDialog.getOpenFileName(self, 'Seleccionar CSV', '', 'CSV (*.csv)')
        if not ruta:
            return 
        exito, mensaje = self.gestor.cargar_csv(ruta)
        if exito:
            self.mostrar_tabla()
            self.actualizar_selector_columnas()
            QMessageBox.information(self, '✅ Éxito', mensaje)
        else:
            QMessageBox.critical(self, '❌ Error', mensaje)

    def generar_ejemplo(self):
        """Generar datos de ejemplo"""
        exito, mensaje = self.gestor.generar_ejemplo()
        if exito:
            self.mostrar_tabla()
            self.actualizar_selector_columnas()
            QMessageBox.information(self, '✅ Éxito', mensaje)

    def mostrar_tabla(self):
        """Mostrar DataFrame en la tabla"""
        df = self.gestor.df
        if df is None:
            return
        self.tabla.setRowCount(len(df))
        self.tabla.setColumnCount(len(df.columns))
        self.tabla.setHorizontalHeaderLabels(df.columns.tolist())
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(i, j, item)
        self.tabla.resizeColumnsToContents()

    def actualizar_selector_columnas(self):
        """Actualizar ComboBox con columnas numéricas"""
        self.combo_columna.clear()
        columnas = self.gestor.obtener_columnas_numericas()
        self.combo_columna.addItems(columnas)

    def actualizar_grafica(self):
        """Actualizar gráfica y estadísticas"""
        columna = self.combo_columna.currentText()
        if not columna or self.gestor.df is None:
            return
        df = self.gestor.df
        etiquetas = df.iloc[:, 0].tolist() 
        valores = df[columna].tolist()
        self.canvas.graficar_datos(valores, etiquetas, f'Gráfica de {columna}')
        stats = self.gestor.calcular_estadisticas(columna)
        if stats:
            texto = f"""
📊 ESTADÍSTICAS DE: {columna}
• Promedio: {stats['Promedio']:.2f}
• Máximo: {stats['Máximo']:.2f}
• Mínimo: {stats['Mínimo']:.2f}
• Total: {stats['Total']:.2f}
"""
            self.label_stats.setText(texto)

def main():
    app = QApplication(sys.argv)
    ventana = VentanaAnalisis()
    ventana.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()