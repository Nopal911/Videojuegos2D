import sys
import cv2
import numpy as np
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class CuboARPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 AR Estable - UTNG")
        self.setGeometry(100, 100, 1100, 700)

        # 1. CARGAR IMAGEN (Ruta absoluta)
        ruta_script = os.path.dirname(os.path.abspath(__file__))
        self.ruta_imagen = os.path.join(ruta_script, "marcador.jpg")
        self.img_obj = cv2.imread(self.ruta_imagen, 0)
        
        if self.img_obj is None:
            print(f"❌ Error: No se encuentra marcador.jpg en {ruta_script}")
            sys.exit()

        # 2. DETECTOR ORB (Configuración estable)
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.kp_obj, self.des_obj = self.orb.detectAndCompute(self.img_obj, None)
        
        # Matcher FLANN
        index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
        self.flann = cv2.FlannBasedMatcher(index_params, dict(checks=50))

        # 3. GEOMETRÍA
        h, w = self.img_obj.shape
        self.matriz_cam = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)
        
        # Cubo pequeño para que no tape todo
        s = w // 3 
        self.puntos_cubo = np.float32([
            [0,0,0], [s,0,0], [s,s,0], [0,s,0],
            [0,0,-s], [s,0,-s], [s,s,-s], [0,s,-s]
        ])

        self.rot_y = 0
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        l = QHBoxLayout(c)
        self.v = QLabel("Cargando...")
        l.addWidget(self.v, 3)
        self.setLayout(l)

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_f, des_f = self.orb.detectAndCompute(gris, None)

        if des_f is not None and len(kp_f) > 20:
            matches = self.flann.knnMatch(self.des_obj, des_f, k=2)
            buenos = [m for m_n in matches if len(m_n) == 2 and m_n[0].distance < 0.7 * m_n[1].distance]

            if len(buenos) > 30: # Necesitamos bastantes puntos para estabilidad
                src_pts = np.float32([self.kp_obj[m.queryIdx].pt for m in buenos]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_f[m.trainIdx].pt for m in buenos]).reshape(-1, 1, 2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if M is not None:
                    h, w = self.img_obj.shape
                    pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
                    
                    try:
                        dst = cv2.perspectiveTransform(pts, M)
                        
                        # --- EL FILTRO ANTI-ZOOM ---
                        # 1. El área no debe ser gigante (máximo 80% de la pantalla)
                        area = cv2.contourArea(dst)
                        # 2. Debe ser convexo (una forma cerrada, no cruzada)
                        es_convexo = cv2.isContourConvex(np.int32(dst))
                        
                        if 2000 < area < (frame.shape[0] * frame.shape[1] * 0.8) and es_convexo:
                            cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 2)
                            
                            self.rot_y = (self.rot_y + 4) % 360
                            obj_3d = np.float32([[0,0,0], [0,h,0], [w,h,0], [w,0,0]])
                            
                            ret, rvec, tvec = cv2.solvePnP(obj_3d, dst, self.matriz_cam, None)
                            
                            if ret:
                                # Matriz de rotación interna para el cubo
                                r_mat, _ = cv2.Rodrigues(rvec)
                                r_ext, _ = cv2.Rodrigues(np.array([0, self.rot_y*np.pi/180, 0], dtype=np.float32))
                                r_fin, _ = cv2.Rodrigues(np.dot(r_mat, r_ext))

                                imgpts, _ = cv2.projectPoints(self.puntos_cubo, r_fin, tvec, self.matriz_cam, None)
                                self.dibujar(frame, imgpts)
                    except: pass

        self.mostrar(frame)

    def dibujar(self, img, pts):
        pts = np.int32(pts).reshape(-1, 2)
        cv2.drawContours(img, [pts[:4]], -1, (255, 0, 0), 2)
        for i in range(4): cv2.line(img, tuple(pts[i]), tuple(pts[i+4]), (0, 0, 255), 2)
        cv2.drawContours(img, [pts[4:]], -1, (0, 255, 0), 2)

    def mostrar(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qi = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.v.setPixmap(QPixmap.fromImage(qi).scaled(self.v.size(), Qt.AspectRatioMode.KeepAspectRatio))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CuboARPro()
    win.show()
    sys.exit(app.exec())