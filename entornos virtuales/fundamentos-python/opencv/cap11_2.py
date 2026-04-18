import sys
import cv2
import numpy as np
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class CuboARPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 AR Estable - UTNG")
        self.setGeometry(100, 100, 1100, 700)

        # 1. CARGAR IMAGEN (Marcador)
        ruta_script = os.path.dirname(os.path.abspath(__file__))
        self.ruta_imagen = os.path.join(ruta_script, "marcador.jpg")
        
        # Si no está en la raíz, buscar dentro de la carpeta 'opencv'
        if not os.path.exists(self.ruta_imagen):
            self.ruta_imagen = os.path.join(ruta_script, "opencv", "marcador.jpg")

        self.img_obj = cv2.imread(self.ruta_imagen, 0)
        
        if self.img_obj is None:
            print(f"❌ Error: No se encuentra 'marcador.jpg' en la ruta del script.")
            sys.exit()

        # 2. DETECTOR ORB
        self.orb = cv2.ORB_create(nfeatures=1500)
        self.kp_obj, self.des_obj = self.orb.detectAndCompute(self.img_obj, None)
        
        # Matcher FLANN (Específico para ORB)
        index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # 3. GEOMETRÍA
        self.h_obj, self.w_obj = self.img_obj.shape
        # Matriz de cámara intrínseca (estimada)
        self.matriz_cam = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)
        
        # Puntos del cubo 3D
        s = self.w_obj // 3 
        self.puntos_cubo = np.float32([
            [0,0,0], [s,0,0], [s,s,0], [0,s,0],       # Base (Z=0)
            [0,0,-s], [s,0,-s], [s,s,-s], [0,s,-s]    # Techo (Z=-s)
        ])

        self.rot_y = 0
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        l = QVBoxLayout(c)
        self.v = QLabel("Buscando marcador en cámara...")
        self.v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.v.setStyleSheet("background-color: black; color: white; font-size: 20px;")
        l.addWidget(self.v)

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_f, des_f = self.orb.detectAndCompute(gris, None)

        # Verificar que haya descriptores en el frame actual
        if des_f is not None and len(kp_f) > 20:
            matches = self.flann.knnMatch(self.des_obj, des_f, k=2)
            
            # --- LÍNEA CORREGIDA AQUÍ ---
            buenos = []
            for m_n in matches:
                if len(m_n) == 2:
                    m, n = m_n
                    if m.distance < 0.75 * n.distance:
                        buenos.append(m)

            if len(buenos) > 20:
                src_pts = np.float32([self.kp_obj[m.queryIdx].pt for m in buenos]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_f[m.trainIdx].pt for m in buenos]).reshape(-1, 1, 2)

                # Calcular Homografía
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                if M is not None:
                    pts = np.float32([[0, 0], [0, self.h_obj], [self.w_obj, self.h_obj], [self.w_obj, 0]]).reshape(-1, 1, 2)
                    
                    try:
                        dst = cv2.perspectiveTransform(pts, M)
                        area = cv2.contourArea(dst)
                        
                        # Validar tamaño y forma
                        if 3000 < area < (frame.shape[0] * frame.shape[1] * 0.9):
                            cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 2)
                            
                            self.rot_y = (self.rot_y + 5) % 360
                            obj_3d = np.float32([[0,0,0], [0,self.h_obj,0], [self.w_obj,self.h_obj,0], [self.w_obj,0,0]])
                            
                            ret_pnp, rvec, tvec = cv2.solvePnP(obj_3d, dst, self.matriz_cam, None)
                            
                            if ret_pnp:
                                # Crear rotación de animación
                                r_mat, _ = cv2.Rodrigues(rvec)
                                theta = np.radians(self.rot_y)
                                r_anim = np.array([[np.cos(theta), 0, np.sin(theta)],
                                                   [0, 1, 0],
                                                   [-np.sin(theta), 0, np.cos(theta)]], dtype=np.float32)
                                
                                r_final_mat = np.dot(r_mat, r_anim)
                                rvec_final, _ = cv2.Rodrigues(r_final_mat)

                                imgpts, _ = cv2.projectPoints(self.puntos_cubo, rvec_final, tvec, self.matriz_cam, None)
                                self.dibujar_cubo(frame, imgpts)
                    except:
                        pass

        self.mostrar(frame)

    def dibujar_cubo(self, img, pts):
        pts = np.int32(pts).reshape(-1, 2)
        # Base
        cv2.drawContours(img, [pts[:4]], -1, (255, 0, 0), 2)
        # Pilares
        for i in range(4): 
            cv2.line(img, tuple(pts[i]), tuple(pts[i+4]), (0, 0, 255), 2)
        # Techo
        cv2.drawContours(img, [pts[4:]], -1, (0, 255, 0), 2)

    def mostrar(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qi = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.v.setPixmap(QPixmap.fromImage(qi).scaled(self.v.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CuboARPro()
    win.show()
    sys.exit(app.exec())