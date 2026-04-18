import sys
import cv2
import numpy as np
import time
import mediapipe as mp
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSpinBox, QColorDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class PinturaDedos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖌️ Pintura con Dedos - UTNG Fix")
        self.setGeometry(100, 100, 1100, 700)
        
        # 1. Inicialización de MediaPipe con manejo de errores
        try:
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                model_complexity=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            print("✅ MediaPipe cargado correctamente.")
        except AttributeError:
            QMessageBox.critical(self, "Error de Librería", 
                "MediaPipe no se cargó bien. Reinstala con: pip install mediapipe")
            sys.exit()

        # 2. Configuración de Video y Lienzo
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.ancho_cam = 640
        self.alto_cam = 480
        self.cap.set(3, self.ancho_cam)
        self.cap.set(4, self.alto_cam)
        
        # Lienzo transparente (donde dibujamos)
        self.lienzo = np.zeros((self.alto_cam, self.ancho_cam, 3), dtype=np.uint8)
        
        # 3. Estado
        self.color_actual = (0, 255, 0) # Verde
        self.grosor = 5
        self.pos_anterior = None
        self.modo_borrador = False
        
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Pantalla de video
        self.lbl_video = QLabel()
        self.lbl_video.setStyleSheet("background-color: black; border: 2px solid #333;")
        layout.addWidget(self.lbl_video, 3)
        
        # Panel de control
        panel = QWidget()
        panel.setFixedWidth(250)
        v_lay = QVBoxLayout(panel)
        
        btn_col = QPushButton("🎨 Color")
        btn_col.clicked.connect(self.escoger_color)
        v_lay.addWidget(btn_col)
        
        self.btn_borrar = QPushButton("🧼 Borrador")
        self.btn_borrar.setCheckable(True)
        self.btn_borrar.toggled.connect(self.toggle_borrador)
        v_lay.addWidget(self.btn_borrar)
        
        self.spn_grosor = QSpinBox()
        self.spn_grosor.setRange(2, 50)
        self.spn_grosor.setValue(5)
        self.spn_grosor.valueChanged.connect(self.cambiar_grosor)
        v_lay.addWidget(QLabel("Grosor:"))
        v_lay.addWidget(self.spn_grosor)
        
        btn_clear = QPushButton("🧹 Limpiar")
        btn_clear.clicked.connect(lambda: self.lienzo.fill(0))
        v_lay.addWidget(btn_clear)
        
        v_lay.addStretch()
        layout.addWidget(panel)

    def escoger_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.color_actual = (col.blue(), col.green(), col.red())
            self.modo_borrador = False
            self.btn_borrar.setChecked(False)

    def toggle_borrador(self, state): self.modo_borrador = state
    def cambiar_grosor(self, v): self.grosor = v

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        
        pos_dedo = None
        dibujando = False

        if res.multi_hand_landmarks:
            for lms in res.multi_hand_landmarks:
                # Detección de dedos: 8 (Índice) y 12 (Medio)
                idx_y = lms.landmark[8].y
                med_y = lms.landmark[12].y
                base_y = lms.landmark[6].y
                
                cx = int(lms.landmark[8].x * self.ancho_cam)
                cy = int(lms.landmark[8].y * self.alto_cam)
                pos_dedo = (cx, cy)

                # Gesto: Solo índice arriba = Dibujar
                if idx_y < base_y and med_y > base_y:
                    dibujando = True
                
                self.mp_drawing.draw_landmarks(frame, lms, self.mp_hands.HAND_CONNECTIONS)

        # Lógica de dibujo
        if dibujando and pos_dedo:
            color = (0,0,0) if self.modo_borrador else self.color_actual
            if self.pos_anterior:
                cv2.line(self.lienzo, self.pos_anterior, pos_dedo, color, self.grosor)
            self.pos_anterior = pos_dedo
        else:
            self.pos_anterior = None

        # Combinar dibujo y cámara
        gris = cv2.cvtColor(self.lienzo, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gris, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        img_fondo = cv2.bitwise_and(frame, frame, mask=mask_inv)
        img_dibujo = cv2.bitwise_and(self.lienzo, self.lienzo, mask=mask)
        final = cv2.add(img_fondo, img_dibujo)

        self.mostrar(final)

    def mostrar(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qimg = QImage(img.data, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format.Format_RGB888)
        self.lbl_video.setPixmap(QPixmap.fromImage(qimg).scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        self.hands.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PinturaDedos()
    win.show()
    sys.exit(app.exec())