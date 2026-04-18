import sys
import cv2
import numpy as np
import math
import time
from datetime import datetime

# --- BLOQUE DE IMPORTACIÓN ANTI-ERROR ---
try:
    import mediapipe as mp
    from mediapipe.python.solutions import selfie_segmentation as mp_selfie
    from mediapipe.python.solutions import pose as mp_pose
    from mediapipe.python.solutions import face_mesh as mp_face_mesh
    print("✅ MediaPipe cargado correctamente.")
except Exception as e:
    print(f"❌ Error de instalación de MediaPipe: {e}")
    sys.exit()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QComboBox, QGridLayout, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

# --- 1. MOTOR DE SEGMENTACIÓN Y ALINEACIÓN ---
class AlineadorObjetos:
    def __init__(self):
        # 1.1 Segmentación de Fondo
        self.segmentador = mp_selfie.SelfieSegmentation(model_selection=0)
        
        # 1.2 Detección Corporal (Pose)
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True
        )
        
        # 1.3 Detección Facial (Malla)
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True
        )
        
        self.catalogo = self.cargar_catalogo()

    def cargar_catalogo(self):
        """Genera los objetos virtuales (assets dummy)"""
        cat = {}
        
        # Gafas de sol
        gafas = np.zeros((150, 300, 4), dtype=np.uint8)
        cv2.rectangle(gafas, (30, 40), (120, 80), (0, 0, 0, 200), -1)
        cv2.rectangle(gafas, (170, 40), (260, 80), (0, 0, 0, 200), -1)
        cv2.rectangle(gafas, (120, 50), (170, 70), (0, 0, 0, 255), -1)
        cv2.line(gafas, (30, 60), (0, 80), (0, 0, 0, 255), 5)
        cv2.line(gafas, (260, 60), (290, 80), (0, 0, 0, 255), 5)
        cat['gafas'] = gafas
        
        # Sombrero
        sombrero = np.zeros((200, 300, 4), dtype=np.uint8)
        cv2.rectangle(sombrero, (120, 20), (170, 100), (139, 69, 19, 255), -1)
        cv2.ellipse(sombrero, (145, 100), (80, 30), 0, 0, 360, (139, 69, 19, 255), -1)
        cv2.rectangle(sombrero, (110, 70), (180, 90), (255, 215, 0, 255), -1)
        cat['sombrero'] = sombrero
        
        # Corbata
        corbata = np.zeros((200, 100, 4), dtype=np.uint8)
        pts = np.array([[50, 20], [20, 150], [80, 150]], np.int32)
        cv2.fillPoly(corbata, [pts], (200, 50, 50, 255))
        cv2.rectangle(corbata, (30, 150), (70, 180), (200, 50, 50, 255), -1)
        cat['corbata'] = corbata
        
        # Bigote
        bigote = np.zeros((60, 150, 4), dtype=np.uint8)
        cv2.ellipse(bigote, (40, 30), (30, 15), 0, 0, 360, (30, 30, 30, 255), -1)
        cv2.ellipse(bigote, (110, 30), (30, 15), 0, 0, 360, (30, 30, 30, 255), -1)
        cat['bigote'] = bigote
        
        return cat

    def procesar_frame(self, frame):
        """Extrae puntos clave del cuerpo y la cara"""
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        res_pose = self.pose.process(rgb)
        res_face = self.face_mesh.process(rgb)
        
        puntos = {}
        
        # Puntos del cuerpo
        if res_pose.pose_landmarks:
            lm = res_pose.pose_landmarks.landmark
            puntos['hombro_izq'] = (int(lm[11].x * w), int(lm[11].y * h))
            puntos['hombro_der'] = (int(lm[12].x * w), int(lm[12].y * h))
            
        # Puntos de la cara
        if res_face.multi_face_landmarks:
            lm = res_face.multi_face_landmarks[0].landmark
            puntos['ojo_izq'] = (int(lm[33].x * w), int(lm[33].y * h))
            puntos['ojo_der'] = (int(lm[362].x * w), int(lm[362].y * h))
            puntos['nariz'] = (int(lm[1].x * w), int(lm[1].y * h))
            puntos['boca_izq'] = (int(lm[61].x * w), int(lm[61].y * h))
            puntos['boca_der'] = (int(lm[291].x * w), int(lm[291].y * h))
            puntos['frente'] = (int(lm[10].x * w), int(lm[10].y * h))
            
        return puntos

    def superponer_imagen(self, fondo, overlay, x, y):
        """Aplica Alpha Blending seguro"""
        h_f, w_f = fondo.shape[:2]
        h_o, w_o = overlay.shape[:2]
        
        # Recortar si se sale de la pantalla
        y1, y2 = max(0, y), min(h_f, y + h_o)
        x1, x2 = max(0, x), min(w_f, x + w_o)
        
        y1_o, y2_o = max(0, -y), h_o - max(0, (y + h_o) - h_f)
        x1_o, x2_o = max(0, -x), w_o - max(0, (x + w_o) - w_f)
        
        if y1 >= y2 or x1 >= x2 or y1_o >= y2_o or x1_o >= x2_o:
            return fondo
            
        overlay_recorte = overlay[y1_o:y2_o, x1_o:x2_o]
        alpha = overlay_recorte[:, :, 3] / 255.0
        
        for c in range(3):
            fondo[y1:y2, x1:x2, c] = (fondo[y1:y2, x1:x2, c] * (1 - alpha) + 
                                      overlay_recorte[:, :, c] * alpha)
        return fondo

    def aplicar_objeto(self, frame, puntos, tipo):
        if not puntos: return frame
        
        if tipo == 'gafas' and 'ojo_izq' in puntos and 'ojo_der' in puntos:
            cx = (puntos['ojo_izq'][0] + puntos['ojo_der'][0]) // 2
            cy = (puntos['ojo_izq'][1] + puntos['ojo_der'][1]) // 2
            dist = math.hypot(puntos['ojo_der'][0] - puntos['ojo_izq'][0], 
                              puntos['ojo_der'][1] - puntos['ojo_izq'][1])
            angulo = math.degrees(math.atan2(puntos['ojo_der'][1] - puntos['ojo_izq'][1], 
                                             puntos['ojo_der'][0] - puntos['ojo_izq'][0]))
            
            gafas = self.catalogo['gafas']
            escala = dist / gafas.shape[1] * 2.5
            n_w, n_h = int(gafas.shape[1] * escala), int(gafas.shape[0] * escala)
            if n_w > 0 and n_h > 0:
                g_redim = cv2.resize(gafas, (n_w, n_h))
                M = cv2.getRotationMatrix2D((n_w//2, n_h//2), -angulo, 1)
                g_rot = cv2.warpAffine(g_redim, M, (n_w, n_h))
                return self.superponer_imagen(frame, g_rot, cx - n_w//2, cy - n_h//2 - int(n_h*0.2))
                
        elif tipo == 'sombrero' and 'frente' in puntos:
            cx, cy = puntos['frente']
            ancho_cab = abs(puntos.get('hombro_der', (cx+100,0))[0] - puntos.get('hombro_izq', (cx-100,0))[0]) * 0.4
            
            sombrero = self.catalogo['sombrero']
            escala = max(0.1, ancho_cab / sombrero.shape[1] * 1.5)
            n_w, n_h = int(sombrero.shape[1] * escala), int(sombrero.shape[0] * escala)
            if n_w > 0 and n_h > 0:
                s_redim = cv2.resize(sombrero, (n_w, n_h))
                return self.superponer_imagen(frame, s_redim, cx - n_w//2, cy - n_h + int(n_h*0.3))
                
        elif tipo == 'corbata' and 'hombro_izq' in puntos and 'hombro_der' in puntos:
            cx = (puntos['hombro_izq'][0] + puntos['hombro_der'][0]) // 2
            cy = (puntos['hombro_izq'][1] + puntos['hombro_der'][1]) // 2
            ancho = abs(puntos['hombro_der'][0] - puntos['hombro_izq'][0])
            
            corbata = self.catalogo['corbata']
            escala = max(0.1, ancho / corbata.shape[1] * 0.4)
            n_w, n_h = int(corbata.shape[1] * escala), int(corbata.shape[0] * escala)
            if n_w > 0 and n_h > 0:
                c_redim = cv2.resize(corbata, (n_w, n_h))
                return self.superponer_imagen(frame, c_redim, cx - n_w//2, cy)
                
        elif tipo == 'bigote' and 'nariz' in puntos and 'boca_izq' in puntos:
            cx = puntos['nariz'][0]
            cy = (puntos['nariz'][1] + (puntos['boca_izq'][1] + puntos['boca_der'][1])//2) // 2
            ancho = abs(puntos['boca_der'][0] - puntos['boca_izq'][0])
            
            bigote = self.catalogo['bigote']
            escala = max(0.1, ancho / bigote.shape[1] * 1.5)
            n_w, n_h = int(bigote.shape[1] * escala), int(bigote.shape[0] * escala)
            if n_w > 0 and n_h > 0:
                b_redim = cv2.resize(bigote, (n_w, n_h))
                return self.superponer_imagen(frame, b_redim, cx - n_w//2, cy - n_h//2)
                
        return frame

# --- 2. INTERFAZ DE USUARIO ---
class CatalogoVirtualApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("👗 Probador Virtual - UTNG Master")
        self.setGeometry(100, 100, 1200, 700)
        
        self.alineador = AlineadorObjetos()
        self.objeto_activo = 'gafas'
        
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
        self.label_video.setStyleSheet("background-color: black; border-radius: 10px;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_video, 3)
        
        # Panel Catálogo
        panel_cat = QWidget()
        panel_cat.setMaximumWidth(350)
        v_lay = QVBoxLayout(panel_cat)
        
        v_lay.addWidget(QLabel("🛍️ CATÁLOGO VIRTUAL", alignment=Qt.AlignmentFlag.AlignCenter))
        
        # Selector de Categoría
        v_lay.addWidget(QLabel("Selecciona un artículo:"))
        self.combo = QComboBox()
        self.combo.addItems(["Gafas de Sol", "Sombrero Clásico", "Corbata Formal", "Bigote Retro"])
        self.combo.currentTextChanged.connect(self.cambiar_articulo)
        v_lay.addWidget(self.combo)
        
        # Preview
        grupo_prev = QGroupBox("Vista Previa")
        l_prev = QVBoxLayout(grupo_prev)
        self.lbl_preview = QLabel()
        self.lbl_preview.setMinimumHeight(150)
        self.lbl_preview.setStyleSheet("background-color: #222;")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l_prev.addWidget(self.lbl_preview)
        v_lay.addWidget(grupo_prev)
        
        # Botones
        btn_foto = QPushButton("📸 Tomar Foto con Estilo")
        btn_foto.setStyleSheet("background-color: #E91E63; color: white; padding: 15px; font-weight: bold;")
        btn_foto.clicked.connect(self.tomar_foto)
        v_lay.addWidget(btn_foto)
        
        v_lay.addStretch()
        layout.addWidget(panel_cat, 1)
        
        self.cambiar_articulo("Gafas de Sol")

    def cambiar_articulo(self, nombre):
        mapeo = {
            "Gafas de Sol": "gafas",
            "Sombrero Clásico": "sombrero",
            "Corbata Formal": "corbata",
            "Bigote Retro": "bigote"
        }
        self.objeto_activo = mapeo.get(nombre, "gafas")
        self.actualizar_preview()

    def actualizar_preview(self):
        """Muestra una miniatura del objeto seleccionado"""
        img = self.alineador.catalogo[self.objeto_activo]
        # Crear un fondo gris para que resalte
        fondo = np.ones((150, 250, 3), dtype=np.uint8) * 50
        
        h_o, w_o = img.shape[:2]
        escala = min(150/h_o, 250/w_o) * 0.8
        n_w, n_h = int(w_o * escala), int(h_o * escala)
        img_redim = cv2.resize(img, (n_w, n_h))
        
        x = (250 - n_w) // 2
        y = (150 - n_h) // 2
        
        alpha = img_redim[:, :, 3] / 255.0
        for c in range(3):
            fondo[y:y+n_h, x:x+n_w, c] = (fondo[y:y+n_h, x:x+n_w, c] * (1 - alpha) + 
                                          img_redim[:, :, c] * alpha)
        
        rgb = cv2.cvtColor(fondo, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, 250, 150, 255*3, QImage.Format.Format_RGB888)
        self.lbl_preview.setPixmap(QPixmap.fromImage(qimg))

    def tomar_foto(self):
        if hasattr(self, 'frame_limpio'):
            frame = self.frame_limpio.copy()
            h, w = frame.shape[:2]
            
            # Aplicar Estilo (Marco y Fecha)
            cv2.rectangle(frame, (15, 15), (w-15, h-15), (255, 255, 255), 4)
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, f"UTNG Probador Virtual - {fecha}", (30, h-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            fname = f"Probador_{datetime.now().strftime('%H%M%S')}.png"
            cv2.imwrite(fname, frame)
            QMessageBox.information(self, "¡Foto Guardada!", f"Tu foto con estilo se guardó como:\n{fname}")

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        puntos = self.alineador.procesar_frame(frame)
        
        # Aplicar el objeto activo
        frame_procesado = self.alineador.aplicar_objeto(frame, puntos, self.objeto_activo)
        self.frame_limpio = frame_procesado.copy()
        
        # Mostrar en UI (con tamaño estricto para evitar el Resize Loop)
        rgb = cv2.cvtColor(frame_procesado, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qimg).scaled(
            800, 600, # FIX: TAMAÑO FIJO
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
    win = CatalogoVirtualApp()
    win.show()
    sys.exit(app.exec())