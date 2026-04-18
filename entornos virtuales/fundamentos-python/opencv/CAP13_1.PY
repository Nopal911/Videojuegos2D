import sys
import cv2
import numpy as np
import time
import os

# --- IMPORTACIÓN ESTÁNDAR CON PROTECCIÓN ---
try:
    import mediapipe as mp
    # Forzamos la carga de soluciones
    mp_face_mesh = mp.solutions.face_mesh
    print("✅ MediaPipe cargado correctamente.")
except (ImportError, AttributeError) as e:
    print(f"❌ Error: {e}")
    print("Sugerencia: Ejecuta 'pip install numpy<2.0.0'")
    sys.exit()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class FaceEngine:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def obtener_puntos(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        puntos = {}
        
        if results.multi_face_landmarks:
            coords = results.multi_face_landmarks[0].landmark
            # Puntos clave
            puntos['ojo_izq'] = (int(coords[468].x * w), int(coords[468].y * h))
            puntos['ojo_der'] = (int(coords[473].x * w), int(coords[473].y * h))
            puntos['nariz'] = (int(coords[1].x * w), int(coords[1].y * h))
            puntos['frente'] = (int(coords[10].x * w), int(coords[10].y * h))
            
            # Parpadeo
            dist_pardaos = abs(coords[159].y - coords[145].y)
            puntos['parpadeo'] = dist_pardaos < 0.012
            
        return puntos

    def overlay_alpha(self, fondo, img_overlay, x, y, w, h):
        if x < 0 or y < 0 or x + w > fondo.shape[1] or y + h > fondo.shape[0]:
            return fondo
        try:
            img_res = cv2.resize(img_overlay, (w, h))
            alpha = img_res[:, :, 3] / 255.0
            for c in range(3):
                fondo[y:y+h, x:x+w, c] = (fondo[y:y+h, x:x+w, c] * (1 - alpha) + 
                                          img_res[:, :, c] * alpha)
        except: pass
        return fondo

class SnapARApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎭 SnapAR Pro v1.0 - UTNG")
        self.setMinimumSize(1100, 700)
        
        self.engine = FaceEngine()
        self.filtro_actual = "Ninguno"
        
        # Crear assets si no existen
        self.preparar_recursos()
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.procesar)
        self.timer.start(30)

    def preparar_recursos(self):
        # Gafas dummy
        if not os.path.exists("gafas.png"):
            g = np.zeros((100, 200, 4), dtype=np.uint8)
            cv2.rectangle(g, (20, 30), (80, 70), (0, 0, 0, 255), -1)
            cv2.rectangle(g, (120, 30), (180, 70), (0, 0, 0, 255), -1)
            cv2.imwrite("gafas.png", g)
        # Bigote dummy
        if not os.path.exists("bigote.png"):
            b = np.zeros((60, 160, 4), dtype=np.uint8)
            cv2.ellipse(b, (80, 30), (60, 20), 0, 0, 360, (40, 40, 40, 255), -1)
            cv2.imwrite("bigote.png", b)

    def setup_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QHBoxLayout(widget)

        self.label_cam = QLabel()
        self.label_cam.setStyleSheet("background-color: black;")
        layout.addWidget(self.label_cam, 4)

        panel = QFrame()
        panel.setFixedWidth(280)
        v_lay = QVBoxLayout(panel)

        v_lay.addWidget(QLabel("💎 FILTROS:"))
        self.lista = QListWidget()
        self.lista.addItems(["Ninguno", "Gafas de Sol", "Bigote Pro", "Cyber Mode"])
        self.lista.currentTextChanged.connect(self.cambiar_filtro)
        v_lay.addWidget(self.lista)

        btn_snap = QPushButton("📸 SNAP")
        btn_snap.clicked.connect(self.guardar)
        v_lay.addWidget(btn_snap)

        v_lay.addStretch()
        layout.addWidget(panel)

    def cambiar_filtro(self, f): self.filtro_actual = f

    def guardar(self):
        if hasattr(self, 'frame_final'):
            cv2.imwrite(f"Snap_{int(time.time())}.png", self.frame_final)

    def procesar(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        puntos = self.engine.obtener_puntos(frame)
        
        if puntos:
            if self.filtro_actual == "Gafas de Sol":
                img = cv2.imread("gafas.png", cv2.IMREAD_UNCHANGED)
                dist = int(np.linalg.norm(np.array(puntos['ojo_izq']) - np.array(puntos['ojo_der'])))
                w_g, h_g = dist * 3, int(dist * 1.2)
                frame = self.engine.overlay_alpha(frame, img, puntos['ojo_izq'][0]-w_g//3, puntos['ojo_izq'][1]-h_g//2, w_g, h_g)

            elif self.filtro_actual == "Bigote Pro":
                img = cv2.imread("bigote.png", cv2.IMREAD_UNCHANGED)
                frame = self.engine.overlay_alpha(frame, img, puntos['nariz'][0]-80, puntos['nariz'][1]+10, 160, 60)

            elif self.filtro_actual == "Cyber Mode":
                color = (0, 255, 255) if not puntos['parpadeo'] else (0, 0, 255)
                cv2.circle(frame, puntos['ojo_izq'], 15, color, 2)
                cv2.circle(frame, puntos['ojo_der'], 15, color, 2)

        self.frame_final = frame
        self.mostrar(frame)

    def mostrar(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.label_cam.setPixmap(QPixmap.fromImage(qimg).scaled(self.label_cam.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SnapARApp()
    win.show()
    sys.exit(app.exec())