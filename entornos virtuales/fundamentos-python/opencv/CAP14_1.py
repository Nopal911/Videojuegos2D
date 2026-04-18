import sys
import cv2
import numpy as np
import json
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QTableWidget, QTableWidgetItem, QComboBox, 
                             QMessageBox, QTabWidget, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

# --- 1. GENERADOR DE RECURSOS (Para evitar errores de archivos faltantes) ---
def generar_recursos_prueba():
    os.makedirs("assets", exist_ok=True)
    
    # 1. Crear JSON
    json_path = 'contenido_marcadores.json'
    if not os.path.exists(json_path):
        datos = {
            "0": {"tipo": "texto", "contenido": "Marcador 0: Texto", "color": [0, 255, 255]},
            "1": {"tipo": "imagen", "contenido": "assets/logo.png", "tamanio": [200, 200]},
            "2": {"tipo": "video", "contenido": "assets/video.avi", "loop": True},
            "3": {"tipo": "modelo_3d", "contenido": "Cubo 3D", "escala": 1.0}
        }
        with open(json_path, 'w') as f:
            json.dump(datos, f, indent=2)

    # 2. Crear Imagen Dummy
    if not os.path.exists("assets/logo.png"):
        img = np.zeros((200, 200, 4), dtype=np.uint8)
        cv2.circle(img, (100, 100), 80, (255, 0, 0, 255), -1)
        cv2.putText(img, "UTNG", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 255), 3)
        cv2.imwrite("assets/logo.png", img)

    # 3. Crear Video Dummy
    if not os.path.exists("assets/video.avi"):
        out = cv2.VideoWriter('assets/video.avi', cv2.VideoWriter_fourcc(*'XVID'), 10, (200, 200))
        for i in range(30):
            frame = np.zeros((200, 200, 3), dtype=np.uint8)
            cv2.circle(frame, (100, 100), i * 3, (0, 255, 0), -1)
            out.write(frame)
        out.release()

# --- 2. MOTOR DE REALIDAD AUMENTADA ---
class MotorAR:
    def __init__(self):
        # Configurar detector ArUco (Compatible con OpenCV 4.7+)
        self.diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        self.parametros = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.diccionario, self.parametros)
        
        self.cargar_base_datos()
        
        # Matriz genérica
        self.matriz_camara = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)
        self.dist_coefs = np.zeros((4, 1))
        self.tamanio_marcador = 0.05
        
        self.cache_contenido = {}
        self.estados_animacion = {}

    def cargar_base_datos(self):
        with open('contenido_marcadores.json', 'r') as f:
            self.base_datos = json.load(f)

    def cargar_contenido(self, id_str):
        if id_str in self.cache_contenido:
            return self.cache_contenido[id_str]
        
        if id_str not in self.base_datos:
            return None
            
        info = self.base_datos[id_str]
        contenido = None
        
        if info["tipo"] == "imagen" and os.path.exists(info["contenido"]):
            img = cv2.imread(info["contenido"], cv2.IMREAD_UNCHANGED)
            contenido = cv2.resize(img, tuple(info["tamanio"]))
            
        elif info["tipo"] == "video" and os.path.exists(info["contenido"]):
            contenido = {'cap': cv2.VideoCapture(info["contenido"]), 'loop': info.get('loop', True)}
            
        elif info["tipo"] == "texto":
            img = np.zeros((100, 300, 4), dtype=np.uint8)
            cv2.putText(img, info["contenido"], (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, info["color"]+[255], 2)
            contenido = img
            
        elif info["tipo"] == "modelo_3d":
            contenido = "cubo_3d" # Bandera para renderizar geometría

        self.cache_contenido[id_str] = contenido
        return contenido

    def procesar_frame(self, frame):
        esquinas, ids, _ = self.detector.detectMarkers(frame)
        
        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                esq = esquinas[i][0]
                id_str = str(marker_id)
                
                # 1. Lógica de Animación (Borde brillante)
                tiempo = time.time()
                grosor = int(3 + 2 * np.sin(tiempo * 5))
                color_borde = (0, 255, 255) if marker_id % 2 == 0 else (255, 0, 255)
                cv2.polylines(frame, [esq.astype(int)], True, color_borde, grosor)
                cv2.putText(frame, f"ID:{marker_id}", (int(esq[0][0]), int(esq[0][1])-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_borde, 2)

                # 2. Renderizado de Contenido
                contenido = self.cargar_contenido(id_str)
                if contenido is not None:
                    # Si es modelo 3D nativo
                    if contenido == "cubo_3d":
                        obj_pts = np.float32([[-0.025, 0.025, 0], [0.025, 0.025, 0], 
                                              [0.025, -0.025, 0], [-0.025, -0.025, 0]])
                        ret, rvec, tvec = cv2.solvePnP(obj_pts, esq, self.matriz_camara, self.dist_coefs)
                        if ret:
                            # Cubo animado rotando
                            rot_y = (tiempo * 50) % 360
                            theta = np.radians(rot_y)
                            r_anim = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]], dtype=np.float32)
                            r_mat, _ = cv2.Rodrigues(rvec)
                            rvec_final, _ = cv2.Rodrigues(np.dot(r_mat, r_anim))
                            
                            s = 0.025
                            puntos_cubo = np.float32([[0,0,0], [s,0,0], [s,s,0], [0,s,0], [0,0,-s], [s,0,-s], [s,s,-s], [0,s,-s]])
                            imgpts, _ = cv2.projectPoints(puntos_cubo, rvec_final, tvec, self.matriz_camara, self.dist_coefs)
                            pts = np.int32(imgpts).reshape(-1, 2)
                            cv2.drawContours(frame, [pts[:4]], -1, (255, 0, 0), 2)
                            for j in range(4): cv2.line(frame, tuple(pts[j]), tuple(pts[j+4]), (0, 0, 255), 2)
                            cv2.drawContours(frame, [pts[4:]], -1, (0, 255, 0), 2)

                    # Si es Video
                    elif isinstance(contenido, dict):
                        ret_v, f_video = contenido['cap'].read()
                        if not ret_v and contenido['loop']:
                            contenido['cap'].set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret_v, f_video = contenido['cap'].read()
                        if ret_v:
                            frame = self.superponer_homografia(frame, f_video, esq)
                    
                    # Si es Imagen/Texto
                    else:
                        frame = self.superponer_homografia(frame, contenido, esq)
                        
        return frame, ids

    def superponer_homografia(self, frame, img_overlay, esquina):
        h, w = img_overlay.shape[:2]
        pts_orig = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
        H, _ = cv2.findHomography(pts_orig, esquina.astype(np.float32))
        warped = cv2.warpPerspective(img_overlay, H, (frame.shape[1], frame.shape[0]))
        
        if img_overlay.shape[2] == 4:
            mask = warped[:,:,3] / 255.0
            for c in range(3):
                frame[:,:,c] = frame[:,:,c] * (1 - mask) + warped[:,:,c] * mask
        else:
            mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
            cv2.fillConvexPoly(mask, esquina.astype(int), 255)
            mask_inv = cv2.bitwise_not(mask)
            frame = cv2.add(cv2.bitwise_and(frame, frame, mask=mask_inv), warped)
        return frame

# --- 3. INTERFAZ DE USUARIO ---
class LibroARApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📖 Libro AR Interactivo - Master Final UTNG")
        self.setGeometry(100, 100, 1200, 700)
        
        generar_recursos_prueba() # Asegurar archivos
        self.ar_system = MotorAR()
        self.pagina_actual = 0
        
        self.paginas = {
            0: {"titulo": "Portada", "desc": "Muestra los marcadores 0 y 1"},
            1: {"titulo": "Capítulo 1", "desc": "Muestra los marcadores 2 y 3"}
        }
        
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.setup_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        self.timer.start(30)
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Panel Video
        self.label_video = QLabel()
        self.label_video.setStyleSheet("background-color: black; border: 2px solid #555;")
        layout.addWidget(self.label_video, 3)

        # Panel Control
        panel_ctrl = QFrame()
        panel_ctrl.setFixedWidth(350)
        v_lay = QVBoxLayout(panel_ctrl)
        
        v_lay.addWidget(QLabel("📖 NAVEGACIÓN DEL LIBRO"))
        self.combo = QComboBox()
        self.combo.addItems([f"Pág {i}: {p['titulo']}" for i, p in self.paginas.items()])
        self.combo.currentIndexChanged.connect(self.cambiar_pagina)
        v_lay.addWidget(self.combo)
        
        self.info_txt = QTextEdit()
        self.info_txt.setReadOnly(True)
        self.info_txt.setMaximumHeight(100)
        v_lay.addWidget(self.info_txt)
        
        btn_snap = QPushButton("📸 CAPTURAR AR")
        btn_snap.clicked.connect(self.capturar)
        btn_snap.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        v_lay.addWidget(btn_snap)
        
        self.lbl_stats = QLabel("Marcadores: 0")
        v_lay.addWidget(self.lbl_stats)
        
        v_lay.addStretch()
        layout.addWidget(panel_ctrl, 1)
        self.cambiar_pagina(0)

    def cambiar_pagina(self, idx):
        self.pagina_actual = idx
        p = self.paginas[idx]
        self.info_txt.setText(f"{p['titulo']}\n\n{p['desc']}")

    def capturar(self):
        if hasattr(self, 'frame_actual'):
            fname = f"Pagina_{self.pagina_actual}_{int(time.time())}.png"
            cv2.imwrite(fname, self.frame_actual)
            QMessageBox.information(self, "Éxito", f"Captura guardada: {fname}")

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame, ids = self.ar_system.procesar_frame(frame)
        self.frame_actual = frame
        
        num = len(ids) if ids is not None else 0
        self.lbl_stats.setText(f"Marcadores detectados: {num}")
        cv2.putText(frame, f"Pagina: {self.pagina_actual}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        
        # --- FIX: TAMAÑO FIJO PARA EVITAR EL BUCLE DE ZOOM ---
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(
            900, 600, # <-- Tamaño fijo en lugar de self.label_video.size()
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label_video.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = LibroARApp()
    win.show()
    sys.exit(app.exec())