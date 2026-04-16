import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class CorrectorSelfies(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📸 Corrector de Selfies (Distorsión Óptica) - Capítulo 4")
        self.setGeometry(100, 100, 1100, 700)
        
        # Cargar los modelos Haar Cascade pre-entrenados de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        
        # Variables de efecto
        self.fuerza_efecto = 0.0
        self.mostrar_guias = True
        
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panel de video
        panel_video = QWidget()
        layout_video = QVBoxLayout(panel_video)
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800, 600)
        self.label_video.setStyleSheet("background-color: #000;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_video.addWidget(self.label_video)
        layout.addWidget(panel_video, 3)
        
        # Panel de control
        panel_control = QWidget()
        panel_control.setMaximumWidth(300)
        layout_control = QVBoxLayout(panel_control)
        
        grupo_efecto = QGroupBox("👽 Corrector Focal")
        layout_efecto = QVBoxLayout()
        
        layout_efecto.addWidget(QLabel("Intensidad del 'Achatamiento':"))
        self.slider_efecto = QSlider(Qt.Orientation.Horizontal)
        self.slider_efecto.setRange(0, 100) # Se mapeará de 0.0 a 0.5
        self.slider_efecto.setValue(0)
        self.slider_efecto.valueChanged.connect(self.actualizar_fuerza)
        layout_efecto.addWidget(self.slider_efecto)
        
        self.cb_guias = QCheckBox("Mostrar guías de detección")
        self.cb_guias.setChecked(True)
        self.cb_guias.stateChanged.connect(lambda v: setattr(self, 'mostrar_guias', v))
        layout_efecto.addWidget(self.cb_guias)
        
        grupo_efecto.setLayout(layout_efecto)
        layout_control.addWidget(grupo_efecto)
        layout_control.addStretch()
        layout.addWidget(panel_control, 1)
        
    def actualizar_fuerza(self, valor):
        # Mapeamos el slider (0-100) a un factor k (0.0 - 0.5)
        self.fuerza_efecto = valor / 200.0 

    def aplicar_pinch(self, frame, x, y, w, h, cx, cy, k):
        """Aplica un efecto Pincushion suavizado en un ROI alrededor del rostro"""
        alto_frame, ancho_frame = frame.shape[:2]
        
        # Expandir la región de interés (ROI) para no cortar el efecto de golpe
        margen = int(w * 0.4)
        x1 = max(0, cx - margen - w//2)
        y1 = max(0, cy - margen - h//2)
        x2 = min(ancho_frame, cx + margen + w//2)
        y2 = min(alto_frame, cy + margen + h//2)
        
        roi = frame[y1:y2, x1:x2]
        h_roi, w_roi = roi.shape[:2]
        
        if h_roi == 0 or w_roi == 0: 
            return frame

        # Crear una cuadrícula de coordenadas (Meshgrid)
        map_x, map_y = np.meshgrid(np.arange(w_roi), np.arange(h_roi))
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)
        
        # Coordenadas relativas al centro del ROI
        cx_roi = cx - x1
        cy_roi = cy - y1
        
        dx = map_x - cx_roi
        dy = map_y - cy_roi
        r = np.sqrt(dx**2 + dy**2) # Distancia Euclidiana
        
        # Normalizar radio
        rmax = max(w_roi, h_roi) / 2.0
        r_norm = r / rmax
        
        # Factor de distorsión (suavizado hacia los bordes para transición limpia)
        mascara_borde = np.clip(1.0 - r_norm, 0, 1)
        factor = 1.0 + (k * (r_norm ** 2)) * mascara_borde
        
        # ---> AQUÍ ESTÁ LA CORRECCIÓN CLAVE <---
        # Forzamos los mapas a float32 para que cv2.remap no colapse
        map_x_dist = (cx_roi + dx * factor).astype(np.float32)
        map_y_dist = (cy_roi + dy * factor).astype(np.float32)
        
        # Aplicar el remapeo
        roi_dist = cv2.remap(roi, map_x_dist, map_y_dist, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        # Sustituir la región en el frame original
        resultado = frame.copy()
        resultado[y1:y2, x1:x2] = roi_dist
        return resultado

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = self.face_cascade.detectMultiScale(gris, scaleFactor=1.2, minNeighbors=6, minSize=(100, 100))
        
        # Solo procesamos la cara más grande para optimizar
        if len(caras) > 0:
            # Ordenar caras por área (w*h) descendente
            caras = sorted(caras, key=lambda c: c[2]*c[3], reverse=True)
            x, y, w, h = caras[0]
            
            # Centro aproximado de la cara
            cx = x + w // 2
            cy = y + h // 2
            
            # Afinar el centro usando los ojos (para ubicar el puente de la nariz)
            roi_gris = gris[y:y+h, x:x+w]
            ojos = self.eye_cascade.detectMultiScale(roi_gris, scaleFactor=1.1, minNeighbors=5)
            
            # Si encontramos al menos 2 ojos
            if len(ojos) >= 2:
                # Ordenar ojos de izquierda a derecha
                ojos = sorted(ojos, key=lambda o: o[0])
                o1, o2 = ojos[0], ojos[-1] # Tomamos los dos más separados
                
                # Centro x entre ambos ojos
                cx_ojos = x + (o1[0] + o1[2]//2 + o2[0] + o2[2]//2) // 2
                # Centro y ligeramente debajo de los ojos (puente nasal)
                cy_ojos = y + int(max(o1[1] + o1[3], o2[1] + o2[3]) * 1.1) 
                cx, cy = cx_ojos, cy_ojos

            # 1. Aplicar la distorsión
            if self.fuerza_efecto > 0:
                frame = self.aplicar_pinch(frame, x, y, w, h, cx, cy, self.fuerza_efecto)
                
            # 2. Dibujar guías
            if self.mostrar_guias:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1) # Punto focal

        # Mostrar en UI
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CorrectorSelfies()
    ventana.show()
    sys.exit(app.exec())