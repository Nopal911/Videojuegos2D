import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QTextEdit, QVBoxLayout, QFileDialog, QMessageBox,
    QLabel
)

# crear ventana de carga de archivo
class VentanaCargaArchivo(QMainWindow):
    """
    Ventana para cargar y mostrar archivos de texto
    """
    # Crear el metodo constructor 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cargar Archivos")
        self.setGeometry(100, 100, 700, 500)
        
        # metodo para agregar componentes a la ventana
        self.iniciar_interfaz()

    def iniciar_interfaz(self):
        """
        configuramos la interfaz
        """
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout = QVBoxLayout()
        widget_central.setLayout(layout)
        
        # etiqueta para las instrucciones
        instrucciones = QLabel("Haz click en el botón para cargar el archivo de texto")
        instrucciones.setStyleSheet("""
                                    font-size: 14px;
                                    padding: 10px;
                                    """)
        layout.addWidget(instrucciones)
        
        # boton para cargar archivo
        self.boton_cargar = QPushButton("Seleccionar archivo")
        # CORRECCIÓN: QPushButton debe llevar la P mayúscula en el CSS
        self.boton_cargar.setStyleSheet("""
                                        QPushButton {
                                            background-color: #2563eb;
                                            color: white;
                                            font-size: 16px;
                                            padding: 12px;
                                            border-radius: 6px;
                                        }
                                        QPushButton:hover {
                                            background-color: #1d4ed8;
                                        }
                                        """)
        self.boton_cargar.clicked.connect(self.cargar_archivo)
        layout.addWidget(self.boton_cargar) # CORRECCIÓN: Faltaba añadir el botón al layout

        # Area de texto para mostrar el contenido
        self.area_texto = QTextEdit()
        self.area_texto.setPlaceholderText("El contenido del archivo se mostrará aquí")
        self.area_texto.setStyleSheet("""
                                      QTextEdit {
                                          font-family: 'Courier New', monospace;
                                          border: 2px solid #e5e7eb;
                                          border-radius: 6px;
                                          padding: 10px;
                                      }
                                      """)
        layout.addWidget(self.area_texto)
        
        # etiqueta de ruta de archivo
        self.etiqueta_ruta = QLabel("No hay archivo cargado")
        self.etiqueta_ruta.setStyleSheet("""
                                         QLabel {
                                             color: #6b7280;
                                             font-size: 11px;
                                             padding: 6px;
                                         }
                                         """)
        layout.addWidget(self.etiqueta_ruta)

    def cargar_archivo(self):
        """
        abre un cuadro de dialogo para seleccionar el archivo y lo carga
        """
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, 
            'Seleccionar archivo', 
            '', 
            'Archivos de texto (*.txt *.csv *.md);;Todos los archivos (*)' 
        )
        
        if not ruta_archivo:
            return

        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read()
                
                self.area_texto.setPlainText(contenido)
                self.etiqueta_ruta.setText(f"Archivo cargado: {ruta_archivo}")
                
                # CORRECCIÓN: QMessageBox.information requiere título y mensaje
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Archivo cargado correctamente\n\nLíneas: {len(contenido.splitlines())}\nCaracteres: {len(contenido)}"
                )

        except UnicodeDecodeError: # CORRECCIÓN: Especificamos el error de codificación
            QMessageBox.warning(
                self,
                'Error de codificación',
                "No se pudo leer el archivo. Asegúrate de que sea un archivo de texto válido (UTF-8)."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar el archivo: {str(e)}"
            )
            
def main():
    app = QApplication(sys.argv)
    ventana = VentanaCargaArchivo()
    ventana.show()
    sys.exit(app.exec())
    
if __name__ == '__main__':
    main()