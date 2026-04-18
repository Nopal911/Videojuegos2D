import sys
import cv2
import numpy as np
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QImage, QPixmap

class CuboFinal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 Cubo AR Profesional Calibrado")
        self.setGeometry(100, 100, 1200, 600)

        # Cargar calibración
        try:
            data = np.load('parametros_camara.npz')
            self.mtx, self.dist = data['matriz_camara'], data['dist_coefs']
        except:
            print("❌ Error: Ejecuta primero el paso 3."); sys.exit()

        # Config marcador
        self.img_obj = cv2.imread("marcador.jpg", 0)
        self.orb = cv2.ORB_create(1000)
        self.kp1, self.des1 = self.orb.detectAndCompute(self.img_obj, None)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        h, w = self.img_obj.shape
        s = w // 2
        self.pts_3d = np.float32([[0,0,0], [s,0,0], [s,s,0], [0,s,0], [0,0,-s], [s,0,-s], [s,s,-s], [0,s,-s]])

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

        c = QWidget(); self.setCentralWidget(c); l = QHBoxLayout(c)
        self.l1 = QLabel(); self.l2 = QLabel()
        l.addWidget(self.l1); l.addWidget(self.l2)

    def update(self):
        ret, frame = self.cap.read()
        if not ret: return

        # Corregir Distorsión
        frame_calib = cv2.undistort(frame, self.mtx, self.dist)
        
        # Procesar AR en la imagen calibrada
        gris = cv2.cvtColor(frame_calib, cv2.COLOR_BGR2GRAY)
        kp2, des2 = self.orb.detectAndCompute(gris, None)
        
        if des2 is not None:
            matches = sorted(self.bf.match(self.des1, des2), key=lambda x: x.distance)
            if len(matches) > 15:
                src = np.float32([self.kp1[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
                dst = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
                
                M, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
                if M is not None:
                    h, w = self.img_obj.shape
                    obj_c = np.float32([[0,0,0], [0,h,0], [w,h,0], [w,0,0]])
                    corn = cv2.perspectiveTransform(np.float32([[0,0],[0,h],[w,h],[w,0]]).reshape(-1,1,2), M)
                    
                    ret_p, rvec, tvec = cv2.solvePnP(obj_c, corn, self.mtx, self.dist)
                    if ret_p:
                        imgpts, _ = cv2.projectPoints(self.pts_3d, rvec, tvec, self.mtx, self.dist)
                        self.draw(frame_calib, imgpts)

        self.show_frame(self.l1, frame, "Original (Distorsionada)")
        self.show_frame(self.l2, frame_calib, "Calibrada (Líneas Rectas)")

    def draw(self, img, pts):
        pts = np.int32(pts).reshape(-1,2)
        cv2.drawContours(img, [pts[:4]], -1, (255,0,0), 2)
        for i in range(4): cv2.line(img, tuple(pts[i]), tuple(pts[i+4]), (0,0,255), 2)
        cv2.drawContours(img, [pts[4:]], -1, (0,255,0), 2)

    def show_frame(self, lbl, img, txt):
        cv2.putText(img, txt, (10,30), 1, 1.5, (0,255,0), 2)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        qi = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1]*3, QImage.Format.Format_RGB888)
        lbl.setPixmap(QPixmap.fromImage(qi).scaled(550, 400))

if __name__ == "__main__":
    app = QApplication([]); w = CuboFinal(); w.show(); app.exec()