import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QWidget, QFileDialog, QTableWidget,
    QTableWidgetItem, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicacion de datos")
        
        self.boton = QPushButton("Cargar csv")
        self.boton.clicked.connect(self.cargar_datos)
        
        self.label = QLabel("resultados")
        
        self.tabla = QTableWidget()
        
        self.figura = Figure()
        self.canvas = FigureCanvas(self.figura)
        
        layout = QVBoxLayout()
        layout.addWidget(self.boton)
        layout.addWidget(self.label)
        layout.addWidget(self.tabla)
        layout.addWidget(self.canvas)
        
        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)
        
    def cargar_datos(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir CSV",
                                                 "", "CSV (*.csv)")
        if archivo:
            df = pd.read_csv(archivo)
            
            #ejemplo numpy
            promedio = np.mean(df.iloc[:,1])
            self.label.setText(f"Promedio: {promedio}")
            
            #mostrar tabla
            self.tabla.setRowCount(len(df))
            self.tabla.setColumnCount(len(df.columns))
            self.tabla.setHorizontalHeaderLabels(df.columns)
            
            for i in range(len(df.columns)):
                for j in range(len(df.columns)):
                    self.tabla.setItem(i, j,
                                       QTableWidget(str(df.iat[i, j])))
                    
                #grafica
                self.figura.clear()
                ax = self.figura.add_subplot(111)
                ax.plot(df.iloc[:,1])
                self.canvas.draw()
                
app = QApplication(sys.argv)
ventana = Ventana()
ventana.show()
sys.exit(app.exec())