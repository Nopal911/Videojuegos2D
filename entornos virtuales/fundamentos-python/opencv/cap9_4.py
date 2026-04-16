import sys
import cv2
import cv2.aruco as aruco
import numpy as np
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QGroupBox,
                            QLineEdit, QColorDialog, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class TarjetaPresentacionAR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📇 Sistema de Tarjetas de Presentación AR")
        self.setGeometry(100, 100, 1200, 700)
        
        # 1. Configuración ArUco
        self.diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.parametros = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.diccionario, self.parametros)
        
        # 2. Base de Datos Temporal (Memoria)
        self.info_tarjetas = {
            0: {"nombre": "Ana García", "cargo": "Ingeniera AR", "empresa": "TechVision", "color": (255, 0, 0)},
            1: {"nombre": "Carlos López", "cargo": "Dev Senior", "empresa": "AR Solutions", "color": (0, 255, 0)}
        }
        
        # 3. Cámara
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QHBoxLayout(central)

        # --- PANEL IZQUIERDO: VIDEO ---
        self.label_video = QLabel()
        self.label_video.setStyleSheet("background-color: black; border: 2px solid #444;")
        self.label_video.setMinimumWidth(800)
        layout_principal.addWidget(self.label_video, 3)

        # --- PANEL DERECHO: EDICIÓN ---
        panel_control = QWidget()
        layout_ctrl = QVBoxLayout(panel_control)

        # Selector de ID
        grupo_id = QGroupBox("🎯 Selector de Marcador")
        ly_id = QHBoxLayout()
        self.label_id_actual = QLabel("ID: 0")
        btn_next = QPushButton("Siguiente ID")
        btn_next.clicked.connect(self.cambiar_id)
        ly_id.addWidget(self.label_id_actual)
        ly_id.addWidget(btn_next)
        grupo_id.setLayout(ly_id)
        layout_ctrl.addWidget(grupo_id)

        # Campos de texto
        self.in_nombre = QLineEdit(); self.in_nombre.setPlaceholderText("Nombre")
        self.in_cargo = QLineEdit(); self.in_cargo.setPlaceholderText("Cargo")
        
        layout_ctrl.addWidget(QLabel("Nombre:"))
        layout_ctrl.addWidget(self.in_nombre)
        layout_ctrl.addWidget(QLabel("Cargo:"))
        layout_ctrl.addWidget(self.in_cargo)
        
        btn_color = QPushButton("🎨 Cambiar Color")
        btn_color.clicked.connect(self.elegir_color)
        layout_ctrl.addWidget(btn_color)

        btn_save = QPushButton("💾 Guardar a JSON")
        btn_save.clicked.connect(self.exportar_json)
        layout_ctrl.addWidget(btn_save)

        layout_ctrl.addStretch()
        layout_principal.addWidget(panel_control, 1)

    def cambiar_id(self):
        id_actual = int(self.label_id_actual.text().split(":")[1])
        nuevo_id = (id_actual + 1) % 5
        self.label_id_actual.setText(f"ID: {nuevo_id}")

    def elegir_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            id_act = int(self.label_id_actual.text().split(":")[1])
            if id_act not in self.info_tarjetas: self.info_tarjetas[id_act] = {}
            self.info_tarjetas[id_act]["color"] = (color.blue(), color.green(), color.red())

    def exportar_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar", "", "JSON (*.json)")
        if path:
            with open(path, 'w') as f:
                json.dump(self.info_tarjetas, f)

    def dibujar_ar(self, frame, info, esquinas):
        pts = esquinas[0].astype(int)
        x_min, y_min = np.min(pts, axis=0)
        
        # Crear rectángulo flotante
        color = info.get("color", (0, 255, 0))
        overlay = frame.copy()
        cv2.rectangle(overlay, (x_min, y_min-120), (x_min+250, y_min), color, -1)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
        
        # Texto
        cv2.putText(frame, info.get("nombre", "Usuario"), (x_min+10, y_min-80), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, info.get("cargo", "Staff"), (x_min+10, y_min-40), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (200,200,200), 1)

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        esquinas, ids, _ = self.detector.detectMarkers(frame)
        if ids is not None:
            for i, m_id in enumerate(ids.flatten()):
                if m_id in self.info_tarjetas:
                    self.dibujar_ar(frame, self.info_tarjetas[m_id], esquinas[i])
        
        # Convertir a formato PyQt
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img_qt = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(img_qt).scaled(self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TarjetaPresentacionAR()
    window.show()
    sys.exit(app.exec())