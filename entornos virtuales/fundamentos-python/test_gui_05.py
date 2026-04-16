import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMessageBox

class JuegoBolita(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bolita en movimiento - Nivel 2")
        self.setGeometry(200, 200, 450, 350) # Aumenté un poco el alto
        
        self.x_inicial = 50
        self.y_inicial = 100
        self.x = self.x_inicial
        self.y = self.y_inicial
        
        self.crear_interfaz()

    def crear_interfaz(self):
        # Jugador (Bolita Roja)
        self.bolita = QLabel(self)
        self.bolita.setGeometry(self.x, self.y, 35, 35)
        self.bolita.setStyleSheet("background-color: red; border-radius: 17px;")
        
        # Enemigo 1 (Negro)
        self.enemigo1 = QLabel(self)
        self.enemigo1.setGeometry(180, 50, 40, 40)
        self.enemigo1.setStyleSheet("background-color: black; border-radius: 20px;")
        
        # Enemigo 2 (Azul oscuro o Negro)
        self.enemigo2 = QLabel(self)
        self.enemigo2.setGeometry(180, 200, 40, 40)
        self.enemigo2.setStyleSheet("background-color: #1a1a1a; border-radius: 20px;")
        
        # Botones de control
        self.btn_arriba = QPushButton("↑", self)
        self.btn_arriba.move(300, 50)
        self.btn_arriba.clicked.connect(self.arriba)
        
        self.btn_abajo = QPushButton("↓", self)
        self.btn_abajo.move(300, 130)
        self.btn_abajo.clicked.connect(self.abajo)
        
        self.btn_adelante = QPushButton("→", self)
        self.btn_adelante.move(340, 90)
        self.btn_adelante.clicked.connect(self.adelante)
        
        self.btn_atras = QPushButton("←", self)
        self.btn_atras.move(260, 90)
        self.btn_atras.clicked.connect(self.atras)

        # Botón de reiniciar
        self.btn_reiniciar = QPushButton("Reiniciar Juego", self)
        self.btn_reiniciar.setGeometry(150, 280, 150, 30)
        self.btn_reiniciar.clicked.connect(self.reiniciar_juego)
        self.btn_reiniciar.hide()

    def arriba(self):
        if self.y > 0:
            self.y -= 20
            self.actualizar()
    
    def abajo(self):
        if self.y < 260:
            self.y += 20
            self.actualizar()
            
    def adelante(self):
        if self.x < 410:
            self.x += 20
            self.actualizar()
            
    def atras(self):
        if self.x > 0:
            self.x -= 20
            self.actualizar()
            
    def actualizar(self):
        self.bolita.move(self.x, self.y)
        self.detectar_colision()
    
    def detectar_colision(self):
        # Ahora verificamos si choca con el enemigo 1 O con el enemigo 2
        colision1 = self.bolita.geometry().intersects(self.enemigo1.geometry())
        colision2 = self.bolita.geometry().intersects(self.enemigo2.geometry())
        
        if colision1 or colision2:
            self.bolita.hide()
            self.desactivar_controles(False)
            self.btn_reiniciar.show()
            QMessageBox.critical(self, "¡Perdiste!", "Un enemigo te ha alcanzado.")
            
    def desactivar_controles(self, estado):
        self.btn_arriba.setEnabled(estado)
        self.btn_abajo.setEnabled(estado)
        self.btn_atras.setEnabled(estado)
        self.btn_adelante.setEnabled(estado)

    def reiniciar_juego(self):
        self.x = self.x_inicial
        self.y = self.y_inicial
        self.bolita.move(self.x, self.y)
        self.bolita.show()
        self.desactivar_controles(True)
        self.btn_reiniciar.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = JuegoBolita()
    ventana.show()
    sys.exit(app.exec())
    