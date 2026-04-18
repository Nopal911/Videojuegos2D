import sys
import cv2
import numpy as np
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QListWidget, QListWidgetItem, QInputDialog,
                             QMessageBox, QLineEdit, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QImage, QPixmap

class DetectorAsistencia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("👥 Detector de Asistencia - Capítulo 5")
        self.setGeometry(100, 100, 1200, 700)
        
        # Variables de detección
        self.cap = cv2.VideoCapture(0)
        
        # Cargar modelo DNN
        self.cargar_modelo_dnn()
        
        # Base de datos de personas
        self.personas_conocidas = self.cargar_personas()
        
        # Configuración
        self.confianza_minima = 0.5
        
        self.setup_ui()
        
        # Timer de la cámara
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
    def cargar_modelo_dnn(self):
        """Carga el modelo pre-entrenado de detección de rostros"""
        # Rutas de los archivos (Asegúrate de que estén en la misma carpeta que el script)
        prototxt = "deploy.prototxt"
        modelo = "res10_300x300_ssd_iter_140000.caffemodel"
        
        if os.path.exists(prototxt) and os.path.exists(modelo):
            try:
                self.red_dnn = cv2.dnn.readNetFromCaffe(prototxt, modelo)
                self.usar_dnn = True
                print("✅ Modelo DNN cargado correctamente.")
            except Exception as e:
                print(f"❌ Error cargando DNN: {e}")
                self.activar_haar_fallback()
        else:
            print("⚠️ Archivos DNN no encontrados. Usando Haar Cascade.")
            self.activar_haar_fallback()

    def activar_haar_fallback(self):
        self.haar_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.usar_dnn = False

    def cargar_personas(self):
        if os.path.exists('personas.json'):
            try:
                with open('personas.json', 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def guardar_personas(self):
        with open('personas.json', 'w') as f:
            json.dump(self.personas_conocidas, f, indent=2)
            
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panel izquierdo: video
        panel_video = QWidget()
        layout_video = QVBoxLayout(panel_video)
        
        self.label_video = QLabel()
        self.label_video.setMinimumSize(700, 500)
        self.label_video.setStyleSheet("border: 2px solid #555; background-color: black;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_video.addWidget(self.label_video)
        
        self.info_label = QLabel("Esperando detecciones...")
        layout_video.addWidget(self.info_label)
        
        layout.addWidget(panel_video, 3)
        
        # Panel derecho: control
        panel_control = QWidget()
        panel_control.setFixedWidth(350)
        layout_control = QVBoxLayout(panel_control)
        
        grupo_asistencia = QGroupBox("📋 Asistencia en Pantalla")
        layout_asistencia = QVBoxLayout()
        self.lista_asistencia = QListWidget()
        layout_asistencia.addWidget(self.lista_asistencia)
        
        btn_registrar = QPushButton("➕ Registrar Rostro Actual")
        btn_registrar.clicked.connect(self.registrar_persona)
        layout_asistencia.addWidget(btn_registrar)
        grupo_asistencia.setLayout(layout_asistencia)
        layout_control.addWidget(grupo_asistencia)
        
        grupo_bd = QGroupBox("💾 Base de Datos")
        layout_bd = QVBoxLayout()
        self.lista_bd = QListWidget()
        self.actualizar_lista_bd()
        layout_bd.addWidget(self.lista_bd)
        
        btn_eliminar = QPushButton("🗑️ Eliminar seleccionado")
        btn_eliminar.clicked.connect(self.eliminar_persona)
        layout_bd.addWidget(btn_eliminar)
        grupo_bd.setLayout(layout_bd)
        layout_control.addWidget(grupo_bd)

        layout_control.addStretch()
        layout.addWidget(panel_control)

    def detectar_rostros(self, frame):
        rostros = []
        h, w = frame.shape[:2]
        
        if self.usar_dnn:
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                        (300, 300), (104.0, 177.0, 123.0))
            self.red_dnn.setInput(blob)
            detecciones = self.red_dnn.forward()
            
            for i in range(detecciones.shape[2]):
                confianza = detecciones[0, 0, i, 2]
                if confianza > self.confianza_minima:
                    box = detecciones[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x1, y1, x2, y2) = box.astype("int")
                    # Asegurar límites dentro del frame
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)
                    rostros.append((x1, y1, x2-x1, y2-y1, confianza))
        else:
            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detecciones_haar = self.haar_cascade.detectMultiScale(gris, 1.3, 5)
            for (x, y, w_h, h_h) in detecciones_haar:
                rostros.append((x, y, w_h, h_h, 0.8))
        return rostros

    def reconocer_persona(self, w_rostro, h_rostro):
        """Simplificación: Reconocimiento basado en proporciones (Solo para fines educativos)"""
        for nombre, datos in self.personas_conocidas.items():
            if abs(w_rostro - datos['ancho']) < 30 and abs(h_rostro - datos['alto']) < 30:
                return nombre
        return "Desconocido"

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        rostros = self.detectar_rostros(frame)
        nombres_detectados = []
        
        for (x, y, w, h, conf) in rostros:
            nombre = self.reconocer_persona(w, h)
            nombres_detectados.append(nombre)
            
            color = (0, 255, 0) if nombre != "Desconocido" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{nombre} {conf:.2f}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        self.actualizar_ui_asistencia(nombres_detectados)
        self.mostrar_imagen(frame)

    def actualizar_ui_asistencia(self, nombres):
        self.lista_asistencia.clear()
        for nombre in set(nombres):
            item = QListWidgetItem(f"• {nombre}")
            item.setForeground(Qt.GlobalColor.green if nombre != "Desconocido" else Qt.GlobalColor.red)
            self.lista_asistencia.addItem(item)
        self.info_label.setText(f"👥 Rostros detectados: {len(nombres)}")

    def registrar_persona(self):
        nombre, ok = QInputDialog.getText(self, "Registro", "Nombre del usuario:")
        if ok and nombre:
            ret, frame = self.cap.read()
            rostros = self.detectar_rostros(frame)
            if rostros:
                x, y, w, h, _ = rostros[0]
                self.personas_conocidas[nombre] = {
                    'ancho': int(w),
                    'alto': int(h),
                    'fecha': QDateTime.currentDateTime().toString()
                }
                self.guardar_personas()
                self.actualizar_lista_bd()
                QMessageBox.information(self, "Éxito", f"{nombre} registrado.")
            else:
                QMessageBox.warning(self, "Error", "No se detectó un rostro claro.")

    def actualizar_lista_bd(self):
        self.lista_bd.clear()
        self.lista_bd.addItems(self.personas_conocidas.keys())

    def eliminar_persona(self):
        item = self.lista_bd.currentItem()
        if item:
            nombre = item.text()
            del self.personas_conocidas[nombre]
            self.guardar_personas()
            self.actualizar_lista_bd()

    def mostrar_imagen(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.label_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = DetectorAsistencia()
    ventana.show()
    sys.exit(app.exec())