import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QPushButton, 
                             QGroupBox, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QImage, QPixmap

class SelectorColorMagico(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Selector de Color Mágico - Corregido")
        self.setGeometry(100, 100, 1300, 800)
        
        # Variables de captura
        self.cap = None
        self.camara_activa = False
        self.frame_actual = None
        self.datos_imagen = None 
        
        # Rango HSV inicial (Preservar todo por defecto)
        self.h_min, self.h_max = 0, 179
        self.s_min, self.s_max = 0, 255
        self.v_min, self.v_max = 0, 255
        
        # Colores predefinidos
        self.colores_preset = {
            "Personalizado": (0, 179, 0, 255, 0, 255),
            "Rojo": (0, 10, 100, 255, 100, 255),
            "Verde": (40, 80, 100, 255, 100, 255),
            "Azul": (100, 130, 100, 255, 100, 255),
            "Amarillo": (20, 30, 100, 255, 100, 255),
            "Naranja": (5, 15, 100, 255, 100, 255),
            "Rosa": (140, 160, 100, 255, 100, 255),
        }
        
        self.setup_ui()
        self.setup_camara()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # --- PANEL DE VIDEO ---
        panel_video = QWidget()
        layout_video = QVBoxLayout(panel_video)
        
        self.label_video = QLabel("Cargando cámara...")
        self.label_video.setMinimumSize(800, 600)
        self.label_video.setStyleSheet("border: 2px solid #333; background-color: #000;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_video.addWidget(self.label_video)
        
        layout.addWidget(panel_video, 3)
        
        # --- PANEL DE CONTROL ---
        panel_control = QWidget()
        panel_control.setMaximumWidth(350)
        layout_control = QVBoxLayout(panel_control)
        
        # Presets
        grupo_preset = QGroupBox("🎨 Presets de Color")
        lay_p = QVBoxLayout()
        self.combo_colores = QComboBox()
        self.combo_colores.addItems(self.colores_preset.keys())
        self.combo_colores.currentTextChanged.connect(self.cambiar_preset)
        lay_p.addWidget(self.combo_colores)
        grupo_preset.setLayout(lay_p)
        layout_control.addWidget(grupo_preset)
        
        # Sliders HSV
        grupo_hsv = QGroupBox("🎚️ Ajuste Manual HSV")
        lay_hsv = QVBoxLayout()
        
        self.sliders = {}
        for param, nombre, max_val in [
            ('h_min', 'Hue Mín', 179), ('h_max', 'Hue Máx', 179),
            ('s_min', 'Sat Mín', 255), ('s_max', 'Sat Máx', 255),
            ('v_min', 'Val Mín', 255), ('v_max', 'Val Máx', 255)
        ]:
            lay_hsv.addWidget(QLabel(nombre))
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(0, max_val)
            s.setValue(max_val if 'max' in param else 0)
            s.valueChanged.connect(lambda v, p=param: self.actualizar_hsv(p, v))
            lay_hsv.addWidget(s)
            self.sliders[param] = s
            
        grupo_hsv.setLayout(lay_hsv)
        layout_control.addWidget(grupo_hsv)
        
        # Info y Botón
        self.info_label = QLabel("H: [0, 179] S: [0, 255] V: [0, 255]")
        layout_control.addWidget(self.info_label)
        
        btn_foto = QPushButton("📸 Guardar Foto")
        btn_foto.setFixedHeight(40)
        btn_foto.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        btn_foto.clicked.connect(self.guardar_instantanea)
        layout_control.addWidget(btn_foto)
        
        layout_control.addStretch()
        layout.addWidget(panel_control, 1)

    def setup_camara(self):
        # CAP_DSHOW es vital para evitar bloqueos en Windows
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if self.cap.isOpened():
            # Configurar resolución antes de iniciar el timer
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            self.camara_activa = True
            self.timer = QTimer()
            self.timer.timeout.connect(self.actualizar_frame)
            self.timer.start(30)
        else:
            self.label_video.setText("❌ No se detectó la cámara")

    def actualizar_hsv(self, param, valor):
        setattr(self, param, valor)
        self.info_label.setText(f"H: [{self.h_min}, {self.h_max}] S: [{self.s_min}, {self.s_max}] V: [{self.v_min}, {self.v_max}]")

    def cambiar_preset(self, nombre):
        if nombre in self.colores_preset:
            v = self.colores_preset[nombre]
            params = ['h_min', 'h_max', 's_min', 's_max', 'v_min', 'v_max']
            for i, p in enumerate(params):
                self.sliders[p].setValue(v[i])

    def aplicar_efecto(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([self.h_min, self.s_min, self.v_min])
        upper = np.array([self.h_max, self.s_max, self.v_max])
        
        # Crear máscara
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Convertir a Escala de Grises y de vuelta a BGR para poder combinar
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # Mezclar: donde está la máscara, usar frame original; si no, el gris
        mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        resultado = (frame * mask_3d + gray_bgr * (1 - mask_3d)).astype(np.uint8)
        
        return resultado

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Procesar
            frame = cv2.flip(frame, 1) # Efecto espejo para comodidad
            self.frame_actual = self.aplicar_efecto(frame)
            
            # Convertir para Qt
            rgb = cv2.cvtColor(self.frame_actual, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            
            # tobytes() evita errores de punteros en PyQt6
            self.datos_imagen = rgb.tobytes()
            q_img = QImage(self.datos_imagen, w, h, ch * w, QImage.Format.Format_RGB888)
            
            pixmap = QPixmap.fromImage(q_img)
            self.label_video.setPixmap(pixmap.scaled(
                self.label_video.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))

    def guardar_instantanea(self):
        if self.frame_actual is not None:
            name = f"cine_{QDateTime.currentDateTime().toString('hhmmss')}.png"
            cv2.imwrite(name, self.frame_actual)
            print(f"✅ Guardado como: {name}")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SelectorColorMagico()
    window.show()
    sys.exit(app.exec())