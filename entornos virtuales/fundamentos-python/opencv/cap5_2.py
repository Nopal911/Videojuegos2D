#DETECTOR FACIAL

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
        self.setGeometry(100, 100, 1400, 800)
        
        # Variables de detección
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
        # Cargar modelo DNN
        self.cargar_modelo_dnn()
        
        # Base de datos de personas
        self.personas_conocidas = self.cargar_personas()
        self.detecciones_previas = []  # Para tracking temporal
        
        # Configuración
        self.confianza_minima = 0.5
        self.tiempo_sin_deteccion = 5  # segundos para considerar salida
        
        self.setup_ui()
        
    def cargar_modelo_dnn(self):
        """Carga el modelo pre-entrenado de detección de rostros"""
        try:
            prototxt = "deploy.prototxt"
            modelo = "res10_300x300_ssd_iter_140000.caffemodel"
            
            # Verificar si existen los archivos, si no, advertir (asumimos que ya los descargaste en el cap anterior)
            if not os.path.exists(prototxt) or not os.path.exists(modelo):
                QMessageBox.warning(self, "Archivos faltantes",
                    "Faltan los archivos del modelo DNN. Usando Haar Cascade por defecto.")
                raise Exception("Archivos DNN no encontrados")
            
            self.red_dnn = cv2.dnn.readNetFromCaffe(prototxt, modelo)
            self.usar_dnn = True
        except Exception as e:
            print(f"Fallback a Haar Cascade: {e}")
            self.haar_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.usar_dnn = False
    
    def cargar_personas(self):
        """Carga la base de datos de personas conocidas"""
        if os.path.exists('personas.json'):
            try:
                with open('personas.json', 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def guardar_personas(self):
        """Guarda la base de datos de personas"""
        with open('personas.json', 'w') as f:
            json.dump(self.personas_conocidas, f, indent=2)
            
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        layout = QHBoxLayout(central)
        
        # Panel izquierdo: video
        panel_video = QWidget()
        layout_video = QVBoxLayout(panel_video)
        
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800, 600)
        self.label_video.setStyleSheet("border: 2px solid #333; background-color: #111;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_video.addWidget(self.label_video)
        
        # Información en tiempo real
        self.info_label = QLabel("Esperando detecciones...")
        self.info_label.setStyleSheet("font-size: 14px; padding: 5px;")
        layout_video.addWidget(self.info_label)
        
        layout.addWidget(panel_video, 3)
        
        # Panel derecho: control y lista
        panel_control = QWidget()
        panel_control.setMaximumWidth(400)
        layout_control = QVBoxLayout(panel_control)
        
        # Grupo: Asistencia actual
        grupo_asistencia = QGroupBox("📋 Asistencia Actual")
        layout_asistencia = QVBoxLayout()
        
        self.lista_asistencia = QListWidget()
        self.lista_asistencia.setMinimumHeight(300)
        layout_asistencia.addWidget(self.lista_asistencia)
        
        btn_registrar = QPushButton("➕ Registrar nueva persona")
        btn_registrar.clicked.connect(self.registrar_persona)
        layout_asistencia.addWidget(btn_registrar)
        
        grupo_asistencia.setLayout(layout_asistencia)
        layout_control.addWidget(grupo_asistencia)
        
        # Grupo: Base de datos
        grupo_bd = QGroupBox("💾 Base de Datos")
        layout_bd = QVBoxLayout()
        
        self.lista_bd = QListWidget()
        self.lista_bd.setMinimumHeight(150)
        layout_bd.addWidget(self.lista_bd)
        
        btn_eliminar = QPushButton("🗑️ Eliminar seleccionado")
        btn_eliminar.clicked.connect(self.eliminar_persona)
        layout_bd.addWidget(btn_eliminar)
        
        grupo_bd.setLayout(layout_bd)
        layout_control.addWidget(grupo_bd)
        
        # Grupo: Configuración
        grupo_config = QGroupBox("⚙️ Configuración")
        layout_config = QGridLayout()
        
        layout_config.addWidget(QLabel("Confianza mínima:"), 0, 0)
        self.confianza_input = QLineEdit(str(self.confianza_minima))
        self.confianza_input.textChanged.connect(self.actualizar_confianza)
        layout_config.addWidget(self.confianza_input, 0, 1)
        
        btn_guardar = QPushButton("💾 Guardar BD")
        btn_guardar.clicked.connect(self.guardar_personas_manual)
        layout_config.addWidget(btn_guardar, 1, 0, 1, 2)
        
        grupo_config.setLayout(layout_config)
        layout_control.addWidget(grupo_config)
        
        layout_control.addStretch()
        layout.addWidget(panel_control, 1)
        
        # Actualizar lista de BD
        self.actualizar_lista_bd()
        
    def actualizar_confianza(self):
        try:
            self.confianza_minima = float(self.confianza_input.text())
        except ValueError:
            pass # Ignorar si el usuario escribe texto no numérico
            
    def guardar_personas_manual(self):
        self.guardar_personas()
        QMessageBox.information(self, "Éxito", "Base de datos guardada correctamente.")
    
    def detectar_rostros(self, frame):
        """Detecta rostros usando DNN o Haar"""
        rostros = []
        if self.usar_dnn:
            blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
            self.red_dnn.setInput(blob)
            detecciones = self.red_dnn.forward()
            
            h, w = frame.shape[:2]
            for i in range(detecciones.shape[2]):
                confianza = detecciones[0, 0, i, 2]
                if confianza > self.confianza_minima:
                    box = detecciones[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x1, y1, x2, y2) = box.astype("int")
                    # Convertir a int nativos de Python para evitar errores JSON
                    rostros.append((int(x1), int(y1), int(x2-x1), int(y2-y1), float(confianza)))
        else:
            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detecciones_haar = self.haar_cascade.detectMultiScale(
                gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (x, y, w, h) in detecciones_haar:
                rostros.append((int(x), int(y), int(w), int(h), 0.8))
                
        return rostros
    
    def reconocer_persona(self, rostro_recortado):
        """Identifica a la persona comparando con la BD"""
        h, w = rostro_recortado.shape[:2]
        
        # Buscar coincidencia en BD (MUY simplificado)
        for nombre, datos in self.personas_conocidas.items():
            if abs(w - datos.get('ancho', 0)) < 50 and abs(h - datos.get('alto', 0)) < 50:
                return nombre
        return "Desconocido"
    
    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        rostros = self.detectar_rostros(frame)
        asistentes = []
        
        for (x, y, w, h, confianza) in rostros:
            # Validar que las coordenadas estén dentro de la imagen
            if x < 0 or y < 0 or x+w > frame.shape[1] or y+h > frame.shape[0]:
                continue
                
            rostro = frame[y:y+h, x:x+w]
            if rostro.size > 0:
                nombre = self.reconocer_persona(rostro)
                asistentes.append(nombre)
                
                color = (0, 255, 0) if nombre != "Desconocido" else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                label = f"{nombre} ({confianza:.2f})"
                cv2.putText(frame, label, (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        self.actualizar_lista_asistencia(asistentes)
        self.mostrar_imagen(frame)
    
    def actualizar_lista_asistencia(self, asistentes):
        """Actualiza la lista visual de asistentes"""
        self.lista_asistencia.clear()
        for nombre in set(asistentes):
            count = asistentes.count(nombre)
            item_text = f"{nombre} ({count})"
            item = QListWidgetItem(item_text)
            
            if nombre == "Desconocido":
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setForeground(Qt.GlobalColor.green)
            
            self.lista_asistencia.addItem(item)
            
        self.info_label.setText(f"👥 Personas detectadas en pantalla: {len(set(asistentes))}")
    
    def actualizar_lista_bd(self):
        """Actualiza la lista de la base de datos"""
        self.lista_bd.clear()
        for nombre in self.personas_conocidas.keys():
            self.lista_bd.addItem(nombre)
    
    def registrar_persona(self):
        """Registra una nueva persona en la BD"""
        nombre, ok = QInputDialog.getText(self, "Registrar persona", 
                                          "Nombre de la persona:")
        if ok and nombre:
            ret, frame = self.cap.read()
            if ret:
                rostros = self.detectar_rostros(frame)
                if rostros:
                    x, y, w, h, _ = rostros[0] # Toma el primer rostro que vea
                    
                    self.personas_conocidas[nombre] = {
                        'ancho': int(w),
                        'alto': int(h),
                        'fecha_registro': QDateTime.currentDateTime().toString()
                    }
                    self.guardar_personas()
                    self.actualizar_lista_bd()
                    QMessageBox.information(self, "Éxito", 
                        f"Persona '{nombre}' registrada correctamente")
                else:
                    QMessageBox.warning(self, "Error", 
                        "No se detectó ningún rostro para registrar. ¡Ponte frente a la cámara!")
    
    def eliminar_persona(self):
        """Elimina una persona de la BD"""
        current = self.lista_bd.currentItem()
        if current:
            nombre = current.text()
            reply = QMessageBox.question(self, "Confirmar", 
                f"¿Eliminar a {nombre} de la base de datos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                if nombre in self.personas_conocidas:
                    del self.personas_conocidas[nombre]
                    self.guardar_personas()
                    self.actualizar_lista_bd()
    
    def mostrar_imagen(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(
            self.label_video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label_video.setPixmap(pixmap)
    
    def closeEvent(self, event):
        self.cap.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    ventana = DetectorAsistencia()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()