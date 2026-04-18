import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QCheckBox, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QImage, QPixmap

class DetectorFiguras(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📐 Detector de Figuras Geométricas - UC3")
        self.setGeometry(100, 100, 1200, 700)
        
        # Inicialización de Cámara
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: No se pudo acceder a la cámara.")
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
        self.frame_procesado = None
        
        # Parámetros por defecto
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150
        self.min_area = 500
        self.detectar_circulos = True
        self.detectar_poligonos = True
        self.mostrar_bordes = False
        
        self.contadores = {
            "Triángulo": 0, "Cuadrado": 0, "Rectángulo": 0,
            "Círculo": 0, "Pentágono": 0, "Hexágono": 0, "Desconocido": 0
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # --- Panel de Video ---
        panel_video = QWidget()
        layout_video = QVBoxLayout(panel_video)
        
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800, 500)
        self.label_video.setStyleSheet("border: 2px solid #555; background-color: black;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_video.addWidget(self.label_video)
        
        self.cb_bordes = QCheckBox("Modo Depuración (Bordes Canny)")
        self.cb_bordes.stateChanged.connect(self.toggle_bordes)
        layout_video.addWidget(self.cb_bordes)
        
        layout.addWidget(panel_video, 3)
        
        # --- Panel de Control ---
        panel_control = QWidget()
        panel_control.setFixedWidth(300)
        layout_control = QVBoxLayout(panel_control)
        
        # Sliders Canny
        grupo_canny = QGroupBox("🎚️ Umbrales Canny")
        l_canny = QVBoxLayout()
        self.s_c1 = QSlider(Qt.Orientation.Horizontal)
        self.s_c1.setRange(0, 255); self.s_c1.setValue(50)
        self.s_c1.valueChanged.connect(lambda v: setattr(self, 'canny_threshold1', v))
        l_canny.addWidget(QLabel("Umbral Inferior:"))
        l_canny.addWidget(self.s_c1)
        
        self.s_c2 = QSlider(Qt.Orientation.Horizontal)
        self.s_c2.setRange(0, 255); self.s_c2.setValue(150)
        self.s_c2.valueChanged.connect(lambda v: setattr(self, 'canny_threshold2', v))
        l_canny.addWidget(QLabel("Umbral Superior:"))
        l_canny.addWidget(self.s_c2)
        grupo_canny.setLayout(l_canny)
        layout_control.addWidget(grupo_canny)

        # Área Mínima
        grupo_area = QGroupBox("📏 Tamaño Mínimo")
        l_area = QVBoxLayout()
        self.s_area = QSlider(Qt.Orientation.Horizontal)
        self.s_area.setRange(100, 5000); self.s_area.setValue(500)
        self.s_area.valueChanged.connect(self.update_area_label)
        l_area.addWidget(self.s_area)
        self.label_area_val = QLabel("500 px²")
        l_area.addWidget(self.label_area_val)
        grupo_area.setLayout(l_area)
        layout_control.addWidget(grupo_area)

        # Tabla de Conteo
        self.tabla_stats = QTableWidget(7, 2)
        self.tabla_stats.setHorizontalHeaderLabels(["Forma", "Cant."])
        self.tabla_stats.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i, forma in enumerate(self.contadores.keys()):
            self.tabla_stats.setItem(i, 0, QTableWidgetItem(forma))
            self.tabla_stats.setItem(i, 1, QTableWidgetItem("0"))
        layout_control.addWidget(self.tabla_stats)
        
        btn_captura = QPushButton("📸 Guardar Captura")
        btn_captura.clicked.connect(self.guardar_captura)
        btn_captura.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px;")
        layout_control.addWidget(btn_captura)
        
        layout.addWidget(panel_control)

    def toggle_bordes(self, state):
        self.mostrar_bordes = bool(state)

    def update_area_label(self, v):
        self.min_area = v
        self.label_area_val.setText(f"{v} px²")

    def detectar_forma(self, contorno):
        peri = cv2.arcLength(contorno, True)
        aprox = cv2.approxPolyDP(contorno, 0.04 * peri, True)
        v = len(aprox)
        
        if v == 3: return "Triángulo"
        if v == 4:
            x, y, w, h = cv2.boundingRect(aprox)
            aspecto = w / float(h)
            return "Cuadrado" if 0.9 <= aspecto <= 1.1 else "Rectángulo"
        if v == 5: return "Pentágono"
        if v == 6: return "Hexágono"
        
        # Lógica circular basada en circularidad (Area vs Perímetro)
        area = cv2.contourArea(contorno)
        if area > 0:
            circularidad = (4 * np.pi * area) / (peri ** 2)
            if circularidad > 0.8: return "Círculo"
            
        return "Desconocido"

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame_vis = frame.copy()
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gris, (7, 7), 0)
        bordes = cv2.Canny(blur, self.canny_threshold1, self.canny_threshold2)
        
        temp_counts = {k: 0 for k in self.contadores.keys()}
        
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contornos:
            area = cv2.contourArea(cnt)
            if area < self.min_area: continue
            
            forma = self.detectar_forma(cnt)
            temp_counts[forma] += 1
            
            # Dibujo
            color = self.get_color(forma)
            cv2.drawContours(frame_vis, [cnt], -1, color, 3)
            
            # Etiqueta
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(frame_vis, forma, (cx-20, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # Actualizar tabla
        for i, forma in enumerate(self.contadores.keys()):
            self.tabla_stats.setItem(i, 1, QTableWidgetItem(str(temp_counts[forma])))
            
        self.frame_procesado = frame_vis
        
        if self.mostrar_bordes:
            res = cv2.cvtColor(bordes, cv2.COLOR_GRAY2RGB)
        else:
            res = cv2.cvtColor(frame_vis, cv2.COLOR_BGR2RGB)
            
        self.mostrar_en_label(res)

    def get_color(self, forma):
        colores = {
            "Triángulo": (0, 255, 0), "Cuadrado": (255, 0, 0),
            "Rectángulo": (255, 255, 0), "Círculo": (0, 0, 255),
            "Pentágono": (255, 0, 255), "Hexágono": (0, 255, 255)
        }
        return colores.get(forma, (150, 150, 150))

    def mostrar_en_label(self, img):
        h, w, c = img.shape
        qimg = QImage(img.data, w, h, w*c, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        self.label_video.setPixmap(pix.scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def guardar_captura(self):
        if self.frame_procesado is not None:
            fname = f"captura_{QDateTime.currentDateTime().toString('hhmmss')}.png"
            cv2.imwrite(fname, self.frame_procesado)
            print(f"Imagen guardada como: {fname}")

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DetectorFiguras()
    window.show()
    sys.exit(app.exec())