import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QTextEdit, QVBoxLayout, QFileDialog, QMessageBox,
    QLabel, QTableWidget, QTableWidgetItem
)

# Librería pandas
import pandas as pd

#Crear ventana
class VentanaConTabla(QWidget):
    #creamos constructor
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pandas y PyQT6")
        #cambiar tamaño de la ventana
        self.resize(600, 400)
        
        #diseño y widgets
        self.layout = QVBoxLayout()
        #colocar tabla en la ventana
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
             """
        QTableWidget{
            background-color: white;
            alternate-background-color: #f3f4f6;
            border:2px solid #e5e7eb;
            border-radius: 6px;
            gridline-color: #d1d5db;
        }
        QHeaderView::section{
            background-color: #2563eb;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        """
        )
        self.boton_load = QPushButton("Cargar CSV")
        #Estilo al botón
        self.boton_load.setStyleSheet(
        """
        QPushButton{
            background-color: #2563eb;
            color: white;
            font-size: 14px;
            padding: 10px 20px;
            border-radius: 6px;
        }
        QPushButton:hover{
            background-color: #1d4ed8;
        }
        """
        )
        #conectamos el evento click con un metodo
        self.boton_load.clicked.connect(self.load_csv)
        
        #Colocar dentro de ventana
        self.layout.addWidget(self.boton_load)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
    #Metodo que carga el archivo
    def load_csv(self):
        #seleccionar archivo
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Abrir csv", "", "CSV files (*.csv)")
        #si seleccione un archivo valido
        if archivo:
            #leer archivo csv con pandas
            df = pd.read_csv(archivo)
            
            #configurar la tabla
            self.table.setColumnCount(len(df.columns))
            self.table.setRowCount(
                len(df.index)
            )
            self.table.setHorizontalHeaderLabels(
                df.columns
            )
            #llenar tabla
            #recorre cada fila
            for i in range(len(df.index)):
                #recorre cada columno
                for j in range(len(df.columns)):
                    #crea una celda en la tabla
                    #con los datos del dataframe
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i,j])))
            
        
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = VentanaConTabla()
    window.show()
    sys.exit(app.exec())