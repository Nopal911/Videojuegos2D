import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QComboBox, QColorDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class MallaFacialArtistica(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Malla Facial Artística Pro - UTNG")
        self.setGeometry(100, 100, 1200, 800)
        
        # 1. Inicializar MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 2. Configuración inicial
        self.estilo = "contorno"
        self.color = (0, 255, 0)  # Verde (BGR)
        self.grosor = 2
        self.efecto_arcoiris = False
        
        # 3. Captura de video
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30) # ~30 FPS
        
        self.setup_ui()

    def setup_ui(self):
        """Crea la interfaz gráfica"""
        ventana_principal = QWidget()
        self.setCentralWidget(ventana_principal)
        layout_principal = QHBoxLayout(ventana_principal)
        
        # --- PANEL IZQUIERDO: VIDEO ---
        panel_video = QWidget()
        layout_v = QVBoxLayout(panel_video)
        
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800, 600)
        self.label_video.setStyleSheet("border: 3px solid #444; background-color: black;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_v.addWidget(self.label_video)
        
        self.expresion_label = QLabel("🎭 Expresión: --")
        self.expresion_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078d7;")
        layout_v.addWidget(self.expresion_label)
        
        layout_principal.addWidget(panel_video, 3)
        
        # --- PANEL DERECHO: CONTROLES ---
        panel_control = QWidget()
        panel_control.setMaximumWidth(300)
        layout_c = QVBoxLayout(panel_control)
        
        # Estilo
        grupo_estilo = QGroupBox("🎭 Estilo de Dibujo")
        lay_estilo = QVBoxLayout()
        self.combo_estilo = QComboBox()
        self.combo_estilo.addItems(["contorno", "puntos", "malla_completa", "solo_ojos", "solo_boca"])
        self.combo_estilo.currentTextChanged.connect(self.cambiar_estilo)
        lay_estilo.addWidget(self.combo_estilo)
        grupo_estilo.setLayout(lay_estilo)
        layout_c.addWidget(grupo_estilo)
        
        # Color
        grupo_color = QGroupBox("🎨 Personalización")
        lay_color = QVBoxLayout()
        btn_color = QPushButton("Elegir Color")
        btn_color.clicked.connect(self.seleccionar_color)
        lay_color.addWidget(btn_color)
        
        self.btn_arcoiris = QPushButton("🌈 Modo Arcoíris")
        self.btn_arcoiris.setCheckable(True)
        self.btn_arcoiris.toggled.connect(self.toggle_arcoiris)
        lay_color.addWidget(self.btn_arcoiris)
        grupo_color.setLayout(lay_color)
        layout_c.addWidget(grupo_color)
        
        # Grosor
        grupo_grosor = QGroupBox("✏️ Grosor de Línea")
        lay_grosor = QVBoxLayout()
        self.sld_grosor = QSlider(Qt.Orientation.Horizontal)
        self.sld_grosor.setRange(1, 5)
        self.sld_grosor.valueChanged.connect(self.cambiar_grosor)
        lay_grosor.addWidget(self.sld_grosor)
        grupo_grosor.setLayout(lay_grosor)
        layout_c.addWidget(grupo_grosor)

        layout_c.addStretch()
        layout_principal.addWidget(panel_control, 1)

    # --- LÓGICA DE CONTROL ---
    def seleccionar_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = (color.blue(), color.green(), color.red())

    def toggle_arcoiris(self, valor): self.efecto_arcoiris = valor
    def cambiar_estilo(self, st): self.estilo = st
    def cambiar_grosor(self, v): self.grosor = v

    def calcular_ear(self, landmarks, indices, w, h):
        p = [np.array([landmarks[i].x * w, landmarks[i].y * h]) for i in indices]
        # Fórmula EAR simplificada para 6 u 8 puntos
        v_dist = np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])
        h_dist = np.linalg.norm(p[0] - p[3]) * 2
        return v_dist / h_dist

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1) # Efecto espejo
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.face_mesh.process(rgb)
        
        if res.multi_face_landmarks:
            for face_lms in res.multi_face_landmarks:
                # Detección de Expresión
                ojo_izq = [33, 160, 158, 133, 153, 144]
                ear = self.calcular_ear(face_lms.landmark, ojo_izq, w, h)
                
                # Sonrisa (distancia entre comisuras 61 y 291)
                dist_boca = np.linalg.norm(
                    np.array([face_lms.landmark[61].x * w, face_lms.landmark[61].y * h]) -
                    np.array([face_lms.landmark[291].x * w, face_lms.landmark[291].y * h])
                )
                
                exp = "😐 Neutral"
                if ear < 0.21: exp = "😉 Parpadeo"
                elif dist_boca > (w * 0.15): exp = "😊 Sonrisa"
                self.expresion_label.setText(f"🎭 Expresión: {exp}")
                
                # Dibujo Artístico
                self.dibujar_artes(frame, face_lms, w, h)
        
        self.mostrar_en_label(frame)

    def dibujar_artes(self, frame, lms, w, h):
        if self.estilo == "contorno":
            idx_contorno = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
            pts = np.array([[(int(lms.landmark[i].x * w), int(lms.landmark[i].y * h))] for i in idx_contorno], np.int32)
            cv2.polylines(frame, [pts], True, self.color, self.grosor)
            
        elif self.estilo == "puntos":
            for lm in lms.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                c = (cx % 255, cy % 255, 255) if self.efecto_arcoiris else self.color
                cv2.circle(frame, (cx, cy), self.grosor, c, -1)
                
        elif self.estilo == "malla_completa":
            mp.solutions.drawing_utils.draw_landmarks(
                frame, lms, self.mp_face_mesh.FACEMESH_TESSELATION,
                None, mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())

        elif self.estilo == "solo_ojos":
            for i in [33, 133, 159, 145, 362, 263, 386, 374]:
                cv2.circle(frame, (int(lms.landmark[i].x*w), int(lms.landmark[i].y*h)), 3, self.color, -1)

    def mostrar_en_label(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        img_qt = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(img_qt).scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Estilo moderno
    ex = MallaFacialArtistica()
    ex.show()
    sys.exit(app.exec())