import sys
import cv2
import cv2.aruco as aruco
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QListWidget, QFileDialog, QSlider, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class ARPortalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌌 AR Portal & Designer Pro - UTNG 2026")
        self.setGeometry(100, 100, 1400, 850)
        
        # --- Configuración ArUco ---
        self.diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.parametros = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.diccionario, self.parametros)
        
        # --- Estado y Recursos ---
        self.modo_portal = False
        self.escala = 1.0
        self.opacidad = 0.8
        self.img_ar = self.generar_placeholder()
        self.fondo_portal = self.generar_fondo_espacial()
        
        # --- Cámara ---
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.run_logic)
        self.timer.start(30)
        
        self.init_ui()

    def generar_placeholder(self):
        """Crea una imagen inicial decorativa"""
        img = np.zeros((500, 500, 4), dtype=np.uint8)
        cv2.rectangle(img, (10, 10), (490, 490), (0, 255, 0, 255), 10)
        cv2.putText(img, "UTNG AR", (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255, 255), 3)
        return img

    def generar_fondo_espacial(self):
        """Crea una imagen que se verá dentro del portal"""
        bg = np.zeros((720, 1280, 3), dtype=np.uint8)
        for _ in range(200): # Estrellas
            x, y = np.random.randint(0, 1280), np.random.randint(0, 720)
            cv2.circle(bg, (x, y), np.random.randint(1, 3), (255, 255, 255), -1)
        return bg

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Panel de Video
        self.lbl_video = QLabel()
        self.lbl_video.setStyleSheet("background: #000; border-radius: 10px;")
        layout.addWidget(self.lbl_video, 3)

        # Panel de Control
        controls = QWidget()
        controls.setFixedWidth(350)
        v_lay = QVBoxLayout(controls)

        # Grupo: Modos
        grp_modo = QGroupBox("🚀 Modo de Visualización")
        l_modo = QVBoxLayout()
        self.chk_portal = QCheckBox("Activar Efecto Portal")
        self.chk_portal.stateChanged.connect(lambda v: setattr(self, 'modo_portal', v == 2))
        l_modo.addWidget(self.chk_portal)
        grp_modo.setLayout(l_modo)
        v_lay.addWidget(grp_modo)

        # Grupo: Ajustes
        grp_adj = QGroupBox("⚙️ Ajustes del Objeto")
        l_adj = QVBoxLayout()
        l_adj.addWidget(QLabel("Tamaño del Marco:"))
        sl_size = QSlider(Qt.Orientation.Horizontal)
        sl_size.setRange(5, 30) # Multiplicador
        sl_size.setValue(10)
        sl_size.valueChanged.connect(lambda v: setattr(self, 'escala', v/10.0))
        l_adj.addWidget(sl_size)
        
        l_adj.addWidget(QLabel("Opacidad:"))
        sl_alpha = QSlider(Qt.Orientation.Horizontal)
        sl_alpha.setRange(0, 100)
        sl_alpha.setValue(80)
        sl_alpha.valueChanged.connect(lambda v: setattr(self, 'opacidad', v/100.0))
        l_adj.addWidget(sl_alpha)
        grp_adj.setLayout(l_adj)
        v_lay.addWidget(grp_adj)

        # Botones
        btn_img = QPushButton("📂 Cargar Imagen AR (.png)")
        btn_img.clicked.connect(self.load_image)
        v_lay.addWidget(btn_img)
        
        btn_bg = QPushButton("🌌 Cambiar Fondo Portal")
        btn_bg.clicked.connect(self.load_portal_bg)
        v_lay.addWidget(btn_bg)

        v_lay.addStretch()
        layout.addWidget(controls, 1)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Imagen PNG", "", "PNG Files (*.png)")
        if path:
            self.img_ar = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    def load_portal_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, "Imagen Fondo", "", "Images (*.jpg *.png)")
        if path:
            self.fondo_portal = cv2.imread(path)

    def process_ar(self, frame, corners):
        pts_dst = corners[0].astype(np.float32)
        
        if self.modo_portal:
            # --- Lógica de Portal ---
            h_f, w_f = frame.shape[:2]
            # Mapeamos el fondo a las esquinas del marcador
            pts_src = np.array([[0,0], [self.fondo_portal.shape[1], 0], 
                                [self.fondo_portal.shape[1], self.fondo_portal.shape[0]], 
                                [0, self.fondo_portal.shape[0]]], dtype=np.float32)
            M = cv2.getPerspectiveTransform(pts_src, pts_dst)
            warped_portal = cv2.warpPerspective(self.fondo_portal, M, (w_f, h_f))
            
            # Máscara para el hueco
            mask = np.zeros((h_f, w_f), dtype=np.uint8)
            cv2.fillConvexPoly(mask, pts_dst.astype(int), 255)
            
            # Combinar
            frame_inv = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
            portal_cut = cv2.bitwise_and(warped_portal, warped_portal, mask=mask)
            return cv2.add(frame_inv, portal_cut)
        
        else:
            # --- Lógica de Marco/Imagen AR ---
            h_i, w_i = self.img_ar.shape[:2]
            pts_src = np.array([[0,0], [w_i, 0], [w_i, h_i], [0, h_i]], dtype=np.float32)
            
            # Aplicar Escala
            if self.escala != 1.0:
                centro = np.mean(pts_dst, axis=0)
                pts_dst = centro + (pts_dst - centro) * self.escala

            M = cv2.getPerspectiveTransform(pts_src, pts_dst)
            warped_img = cv2.warpPerspective(self.img_ar, M, (frame.shape[1], frame.shape[0]))
            
            # Blending con Alpha
            if warped_img.shape[2] == 4:
                alpha = (warped_img[:,:,3] / 255.0) * self.opacidad
                for c in range(3):
                    frame[:,:,c] = frame[:,:,c] * (1 - alpha) + warped_img[:,:,c] * alpha
            return frame

    def run_logic(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        corners, ids, _ = self.detector.detectMarkers(frame)
        
        if ids is not None:
            frame = self.process_ar(frame, corners)
            aruco.drawDetectedMarkers(frame, corners, ids)

        # Renderizar en PyQt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.lbl_video.setPixmap(QPixmap.fromImage(qimg).scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ARPortalApp()
    win.show()
    sys.exit(app.exec())