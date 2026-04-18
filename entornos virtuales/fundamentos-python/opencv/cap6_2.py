import sys
import cv2
import numpy as np
import mediapipe as mp  # Importación estándar
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QComboBox, QColorDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class MallaFacialArtistica(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Malla Facial Artística - UTNG Fix")
        self.setGeometry(100, 100, 1100, 700)
        
        # 1. Configuración de MediaPipe
        # Usamos mp.solutions que es la forma oficial documentada
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 2. Variables de estilo
        self.estilo = "contorno"
        self.color = (0, 255, 0) # Verde BGR
        self.grosor = 2
        
        # 3. Cámara
        self.cap = cv2.VideoCapture(0)
        
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Video
        self.label_video = QLabel()
        self.label_video.setMinimumSize(700, 500)
        self.label_video.setStyleSheet("background-color: black; border: 2px solid #333;")
        layout.addWidget(self.label_video, 3)
        
        # Controles
        panel = QWidget()
        panel.setFixedWidth(250)
        lay_p = QVBoxLayout(panel)
        
        self.combo = QComboBox()
        self.combo.addItems(["contorno", "puntos", "malla_completa"])
        self.combo.currentTextChanged.connect(lambda t: setattr(self, 'estilo', t))
        lay_p.addWidget(QLabel("Seleccionar Estilo:"))
        lay_p.addWidget(self.combo)
        
        btn_col = QPushButton("🎨 Cambiar Color")
        btn_col.clicked.connect(self.cambiar_color)
        lay_p.addWidget(btn_col)
        
        lay_p.addStretch()
        layout.addWidget(panel)

    def cambiar_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = (color.blue(), color.green(), color.red())

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = self.face_mesh.process(rgb)
        
        if resultados.multi_face_landmarks:
            for face_lms in resultados.multi_face_landmarks:
                self.dibujar(frame, face_lms)
        
        self.mostrar(frame)

    def dibujar(self, frame, lms):
        h, w, _ = frame.shape
        if self.estilo == "contorno":
            # Puntos simplificados del óvalo facial
            puntos_idx = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
            pts = np.array([[int(lms.landmark[i].x * w), int(lms.landmark[i].y * h)] for i in puntos_idx], np.int32)
            cv2.polylines(frame, [pts], True, self.color, self.grosor)
        
        elif self.estilo == "puntos":
            for lm in lms.landmark:
                cv2.circle(frame, (int(lm.x*w), int(lm.y*h)), 1, self.color, -1)
        
        elif self.estilo == "malla_completa":
            self.mp_drawing.draw_landmarks(
                frame, lms, self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )

    def mostrar(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_qt = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1]*3, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(img_qt).scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MallaFacialArtistica()
    win.show()
    sys.exit(app.exec())