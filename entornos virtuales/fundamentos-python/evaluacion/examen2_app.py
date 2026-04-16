import sys
import pandas as pd
import matplotlib.pyplot as plt
# Importamos los componentes necesarios de PyQt6 para crear la ventana y los controles
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QHeaderView
)
from PyQt6.QtGui import QColor

# Definimos la clase principal que heredará de QMainWindow (la ventana de la app)
class AnalizadorVentas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador basico de ventas")
        self.resize(1100, 800)

        # Esta variable empezará vacía y guardará nuestros datos de Pandas después
        self.df = None

        
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        
        self.layout_principal = QVBoxLayout(self.widget_central)

        # 1. BOTÓN DE CARGA
        self.btn_cargar = QPushButton("1. Cargar Datos")
        self.btn_cargar.clicked.connect(self.cargar_datos)
        self.layout_principal.addWidget(self.btn_cargar)

        # 2. TABLA DE DATOS (QTableWidget)
        self.tabla = QTableWidget()
        self.estilizar_tabla() 
        self.layout_principal.addWidget(self.tabla)


        layout_botones = QHBoxLayout() 
        
        self.btn_graficar = QPushButton(" Generar Gráfica")
        self.btn_graficar.clicked.connect(self.mostrar_graficas)
                
        layout_botones.addWidget(self.btn_graficar)
        
        self.layout_principal.addLayout(layout_botones)

    def estilizar_tabla(self):
        """Aplica los requisitos visuales: encabezado azul y filas alternadas"""
        
        estilo_header = "QHeaderView::section { background-color: #3498db; color: white; font-weight: bold; }"
        self.tabla.horizontalHeader().setStyleSheet(estilo_header)
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("alternate-background-color: purple; background-color: green;")
        
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def cargar_datos(self):
        """Lee el archivo CSV, valida y llena la tabla"""
        try:
            self.df = pd.read_csv('examen5.csv')
            
            columnas_requeridas = ['Producto', 'Cantidad', 'Precio']
            
            if not all(col in self.df.columns for col in columnas_requeridas):
                QMessageBox.critical(self, "Error de Columnas", "Faltan columnas obligatorias en el CSV.")
                return

            # Si pasa la validación, llenamos la tabla visual
            self.rellenar_tabla_visual()
            
            
            QMessageBox.information(self, "Carga Exitosa", f"Se cargaron {len(self.df)} registros.")

        except FileNotFoundError:
            QMessageBox.warning(self, "Archivo no encontrado", "Asegúrate de ejecutar el generador de CSV primero.")

    def rellenar_tabla_visual(self):
        """Copia los datos del DataFrame (memoria) a la QTableWidget (pantalla)"""
        
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                # Extraemos el valor de la celda usando .iloc de Pandas
                valor = str(self.df.iloc[i, j])
                # Creamos el objeto celda y lo ponemos en la tabla
                self.tabla.setItem(i, j, QTableWidgetItem(valor))

    def mostrar_graficas(self):
        """Crea una ventana de Matplotlib con 3 gráficos distintos"""
        if self.df is None: 
            QMessageBox.warning(self, "Sin datos", "Carga el CSV primero.")
            return

        plt.figure("Visualización de Datos", figsize=(10, 7))

        # GRÁFICA 1: Barras (Cantidad por Producto)
        plt.subplot(2, 2, 1)
        # Agrupacion de la grafica por producto y cantidad vendida
        self.df.groupby('Producto')['Cantidad'].sum().plot(kind='bar', color='darkblue')
        plt.title('Cantidad Totales por Producto')
        plt.ylabel('Total ()')

        # Ajustamos el espacio entre gráficas para que no se amontonen los títulos
        plt.tight_layout()
        plt.show()

    def exportar_reporte(self):
        """Genera un resumen de texto y lo guarda en disco"""
        if self.df is None: return

        
if __name__ == "__main__":
    # Creamos la aplicación
    app = QApplication(sys.argv)
    # Creamos nuestra ventana
    ventana = AnalizadorVentas()
    # La mostramos
    ventana.show()
    # Ejecutamos el bucle de la app
    sys.exit(app.exec())
    