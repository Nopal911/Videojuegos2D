import sys
import cv2
import mediapipe as mp
import numpy as np
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSpinBox, QColorDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class PinturaDedos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖌️ Pintura con Dedos - UTNG Pro")
        self.setGeometry(100, 100, 1200, 800)
        
        # 1. Inicializar MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.7
        )
        
        # 2. Configuración de Video y Lienzo
        self.cap = cv2.VideoCapture(0)
        self.ancho_cam = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.alto_cam = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.lienzo = np.zeros((self.alto_cam, self.ancho_cam, 3), dtype=np.uint8)
        
        # 3. Variables de Estado
        self.color_actual = (0, 255, 0)  # Verde BGR
        self.grosor_actual = 5
        self.pos_anterior = None
        self.modo_borrador = False
        
        # 4. Timer para la cámara
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QHBoxLayout(central)

        # --- PANEL DE VIDEO ---
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(800, 600)
        self.lbl_video.setStyleSheet("background-color: black; border: 2px solid #2c3e50;")
        layout_principal.addWidget(self.lbl_video, 3)

        # --- PANEL DE CONTROL ---
        panel_ctrl = QWidget()
        panel_ctrl.setFixedWidth(300)
        v_ctrl = QVBoxLayout(panel_ctrl)

        # Herramientas
        grp_tools = QGroupBox("🛠️ Herramientas")
        l_tools = QVBoxLayout()
        
        btn_col = QPushButton("🎨 Elegir Color")
        btn_col.clicked.connect(self.cambiar_color)
        l_tools.addWidget(btn_col)

        self.btn_borrar = QPushButton("🧼 Modo Borrador")
        self.btn_borrar.setCheckable(True)
        self.btn_borrar.toggled.connect(self.set_borrador)
        l_tools.addWidget(self.btn_borrar)
        
        l_tools.addWidget(QLabel("Grosor del trazo:"))
        self.spn_grosor = QSpinBox()
        self.spn_grosor.setRange(2, 30)
        self.spn_grosor.setValue(5)
        self.spn_grosor.valueChanged.connect(self.set_grosor)
        l_tools.addWidget(self.spn_grosor)
        
        grp_tools.setLayout(l_tools)
        v_ctrl.addWidget(grp_tools)

        # Acciones
        grp_acc = QGroupBox("💾 Sistema")
        l_acc = QVBoxLayout()
        
        btn_clear = QPushButton("🧹 Limpiar Todo")
        btn_clear.clicked.connect(self.limpiar_lienzo)
        l_acc.addWidget(btn_clear)

        btn_save = QPushButton("💾 Guardar Obra")
        btn_save.clicked.connect(self.guardar_imagen)
        l_acc.addWidget(btn_save)
        
        grp_acc.setLayout(l_acc)
        v_ctrl.addWidget(grp_acc)

        v_ctrl.addStretch()
        layout_principal.addWidget(panel_ctrl, 1)

    # --- LÓGICA DE CONTROL ---
    def cambiar_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.color_actual = (col.blue(), col.green(), col.red())
            self.modo_borrador = False
            self.btn_borrar.setChecked(False)

    def set_borrador(self, state): self.modo_borrador = state
    def set_grosor(self, v): self.grosor_actual = v
    def limpiar_lienzo(self): self.lienzo[:] = 0

    def guardar_imagen(self):
        nombre = f"dibujo_utng_{int(time.time())}.png"
        cv2.imwrite(nombre, self.lienzo)
        QMessageBox.information(self, "Éxito", f"Dibujo guardado como: {nombre}")

    # --- PROCESAMIENTO ---
    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1) # Espejo
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        
        gesto = "ninguno"
        pos_dedo = None

        if res.multi_hand_landmarks:
            for lms in res.multi_hand_landmarks:
                # 1. Obtener puntos clave
                idx_punta = lms.landmark[8]  # Índice
                med_punta = lms.landmark[12] # Medio
                idx_base = lms.landmark[6]
                med_base = lms.landmark[10]
                
                x, y = int(idx_punta.x * self.ancho_cam), int(idx_punta.y * self.alto_cam)
                pos_dedo = (x, y)

                # 2. Detectar Gestos
                dedo_idx = idx_punta.y < idx_base.y
                dedo_med = med_punta.y < med_base.y

                if dedo_idx and not dedo_med:
                    gesto = "dibujar"
                elif dedo_idx and dedo_med:
                    gesto = "mover"
                    self.pos_anterior = None # Reset para no crear líneas largas al saltar
                
                # Dibujar esqueleto de la mano
                mp.solutions.drawing_utils.draw_landmarks(frame, lms, self.mp_hands.HAND_CONNECTIONS)

        # 3. Dibujar en el lienzo
        if gesto == "dibujar" and pos_dedo:
            color = (0, 0, 0) if self.modo_borrador else self.color_actual
            size = self.grosor_actual * 2 if self.modo_borrador else self.grosor_actual
            
            if self.pos_anterior is not None:
                cv2.line(self.lienzo, self.pos_anterior, pos_dedo, color, size)
            self.pos_anterior = pos_dedo
            cv2.circle(frame, pos_dedo, 10, (255, 255, 255), 2) # Puntero visual
        else:
            self.pos_anterior = None

        # 4. Fusionar Lienzo con Cámara
        # Solo mostramos el dibujo donde no sea negro
        img_gris = cv2.cvtColor(self.lienzo, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(img_gris, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        fondo = cv2.bitwise_and(frame, frame, mask=mask_inv)
        dibujo = cv2.bitwise_and(self.lienzo, self.lienzo, mask=mask)
        res_final = cv2.add(fondo, dibujo)

        self.mostrar_en_ui(res_final)

    def mostrar_en_ui(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        qimg = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.lbl_video.setPixmap(QPixmap.fromImage(qimg).scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        self.hands.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = PinturaDedos()
    win.show()
    sys.exit(app.exec())