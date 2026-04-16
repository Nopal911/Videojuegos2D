import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QComboBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class ContadorEjercicios(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💪 Fitness AI - UTNG Pro")
        self.setGeometry(100, 100, 1300, 800)
        
        # MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
        # Variables de control
        self.ejercicio_actual = "sentadilla"
        self.contador = 0
        self.etapa = "arriba"
        
        # Umbrales por ejercicio (abajo, arriba)
        self.config_ejercicios = {
            "sentadilla": (90, 160),
            "flexion": (70, 160),
            "abdominal": (60, 130)
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panel de video
        self.label_video = QLabel()
        self.label_video.setMinimumSize(854, 480)
        self.label_video.setStyleSheet("border: 3px solid #2c3e50; background-color: #000; border-radius: 10px;")
        layout.addWidget(self.label_video, 3)
        
        # Panel de control
        panel_ctrl = QWidget()
        panel_ctrl.setFixedWidth(320)
        layout_ctrl = QVBoxLayout(panel_ctrl)
        
        # Grupo Ejercicio
        grp_exe = QGroupBox("🏋️ Seleccionar Rutina")
        lay_exe = QVBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems(list(self.config_ejercicios.keys()))
        self.combo.currentTextChanged.connect(self.cambiar_ejercicio)
        lay_exe.addWidget(self.combo)
        grp_exe.setLayout(lay_exe)
        layout_ctrl.addWidget(grp_exe)

        # Grupo Progreso
        grp_prog = QGroupBox("📊 Resultados")
        lay_prog = QVBoxLayout()
        self.lbl_cont = QLabel("0")
        self.lbl_cont.setStyleSheet("font-size: 80px; font-weight: bold; color: #27ae60;")
        self.lbl_cont.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_prog.addWidget(self.lbl_cont)
        
        self.prog_bar = QProgressBar()
        self.prog_bar.setRange(0, 10) # 10 reps para llenar la barra
        lay_prog.addWidget(self.prog_bar)
        grp_prog.setLayout(lay_prog)
        layout_ctrl.addWidget(grp_prog)

        # Feedback
        self.lbl_fase = QLabel("FASE: ESPERANDO")
        self.lbl_fase.setStyleSheet("font-size: 18px; font-weight: bold; color: #2980b9;")
        layout_ctrl.addWidget(self.lbl_fase)

        btn_reset = QPushButton("🔄 Reiniciar")
        btn_reset.clicked.connect(self.reiniciar_contador)
        btn_reset.setHeight(50)
        layout_ctrl.addWidget(btn_reset)

        layout_ctrl.addStretch()
        layout.addWidget(panel_ctrl, 1)

    def cambiar_ejercicio(self, exe):
        self.ejercicio_actual = exe
        self.reiniciar_contador()

    def reiniciar_contador(self):
        self.contador = 0
        self.etapa = "arriba"
        self.lbl_cont.setText("0")
        self.prog_bar.setValue(0)

    def calcular_angulo(self, a, b, c, landmarks, w, h):
        p1 = np.array([landmarks[a].x * w, landmarks[a].y * h])
        p2 = np.array([landmarks[b].x * w, landmarks[b].y * h])
        p3 = np.array([landmarks[c].x * w, landmarks[c].y * h])
        
        ba = p1 - p2
        bc = p3 - p2
        
        cos_angulo = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angulo = np.degrees(np.arccos(np.clip(cos_angulo, -1.0, 1.0)))
        return angulo, p1.astype(int), p2.astype(int), p3.astype(int)

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(rgb)

        if res.pose_landmarks:
            lms = res.pose_landmarks.landmark
            
            # Seleccionar puntos según ejercicio
            if self.ejercicio_actual == "sentadilla":
                ang, p1, p2, p3 = self.calcular_angulo(23, 25, 27, lms, w, h)
            elif self.ejercicio_actual == "flexion":
                ang, p1, p2, p3 = self.calcular_angulo(11, 13, 15, lms, w, h)
            else: # abdominal
                ang, p1, p2, p3 = self.calcular_angulo(11, 23, 25, lms, w, h)

            # Lógica de conteo
            u_abajo, u_arriba = self.config_ejercicios[self.ejercicio_actual]
            
            if ang < u_abajo and self.etapa == "arriba":
                self.etapa = "abajo"
                self.lbl_fase.setText("FASE: ABAJO ↓")
            elif ang > u_arriba and self.etapa == "abajo":
                self.etapa = "arriba"
                self.contador += 1
                self.lbl_fase.setText("FASE: ARRIBA ↑")
                self.lbl_cont.setText(str(self.contador))
                self.prog_bar.setValue(self.contador % 11)

            # Dibujar visualización en el frame
            cv2.line(frame, p1, p2, (255, 255, 255), 3)
            cv2.line(frame, p2, p3, (255, 255, 255), 3)
            for p in [p1, p2, p3]:
                cv2.circle(frame, p, 10, (46, 204, 113), -1)
            
            cv2.putText(frame, f"{int(ang)} deg", (p2[0]-50, p2[1]-20), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 0), 2)

        self.mostrar_imagen(frame)

    def mostrar_imagen(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        qimg = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg).scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        self.pose.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ContadorEjercicios()
    win.show()
    sys.exit(app.exec())