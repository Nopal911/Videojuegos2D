import sys #propiedades de sistema
from PyQt6.QtWidgets import(
    QApplication, QMainWindow, QWidget,
    QPushButton, QVBoxLayout, QLabel)

from PyQt6.QtCore import Qt

#Plantilla para crear ventanas
class Ventana(QMainWindow):
    "ventana con un boton interactivo"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Botones y eventos")
        self.setGeometry(100,100,400,300)
        
        #contador entero
        self.contador = 0
        
        #creo el layout y los widgets
        self.iniciar_interfaz()

    def iniciar_interfaz(self):
        """
        configura todos los elementos visuales
        """
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        #caja vertical
        layout = QVBoxLayout()
        #asigno la caja al contenedor
        widget_central.setLayout(layout)
        
        #creo etiqueta para mostrar el contador
        self.etiqueta = QLabel("Haz hecho click 0 veces")
        self.etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.etiqueta.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                color: #2563eb;
                padding: 20px; 
            }
            """
        )
        
        layout.addWidget(self.etiqueta)
        
        #--- BOTÓN INCREMENTAR ---
        boton_incrementar = QPushButton("Incrementar (+)")
        boton_incrementar.setStyleSheet(
            """
            QPushButton {
                background-color: blue;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: red;
            }
            """
        )
        boton_incrementar.clicked.connect(self.incrementar_contador)
        layout.addWidget(boton_incrementar)

        #--- BOTÓN DECREMENTAR ---
        boton_decrementar = QPushButton("Decrementar (-)")
        boton_decrementar.setStyleSheet(
            """
            QPushButton {
                background-color: #f59e0b;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
            """
        )
        boton_decrementar.clicked.connect(self.decrementar_contador)
        layout.addWidget(boton_decrementar)
        
        #--- BOTÓN RESETEAR ---
        boton_resetear = QPushButton("Resetear contador")
        boton_resetear.setStyleSheet(
        """
        QPushButton {
            background-color: #10b981;
            color: white;
            font-size: 14px;
            padding: 10px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #059669;
        }
        """
        )
        boton_resetear.clicked.connect(self.resetear_contador)
        layout.addWidget(boton_resetear)
        
        layout.addStretch()

    def actualizar_texto(self):
        """Método auxiliar para manejar los mensajes de felicitación"""
        if self.contador == 10:
            self.etiqueta.setText(f"¡Felicidades! Llevas {self.contador} clicks")
        elif self.contador == 50:
            self.etiqueta.setText(f"¡Increíble! {self.contador} clicks alcanzados")
        else:
            self.etiqueta.setText(f"Haz hecho click {self.contador} veces")

    def incrementar_contador(self):
        self.contador += 1
        self.actualizar_texto()

    def decrementar_contador(self):
        if self.contador > 0:
            self.contador -= 1
            self.actualizar_texto()
        

    def resetear_contador(self):
        self.contador = 0
        self.etiqueta.setText("Haz hecho click 0 veces")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())