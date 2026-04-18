import cv2
import numpy as np
import glob

def calibrar():
    patron = (8, 5)
    objp = np.zeros((8*5, 3), np.float32)
    objp[:,:2] = np.mgrid[0:8, 0:5].T.reshape(-1, 2) * 0.025 # 2.5cm por cuadro

    obj_pts, img_pts = [], []
    images = glob.glob('calibracion/*.png')

    for fname in images:
        img = cv2.imread(fname)
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, esquinas = cv2.findChessboardCorners(gris, patron, None)
        if ret:
            obj_pts.append(objp)
            img_pts.append(esquinas)

    if not img_pts:
        print("❌ No se detectaron tableros en las fotos."); return

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts, gris.shape[::-1], None, None)
    np.savez('parametros_camara.npz', matriz_camara=mtx, dist_coefs=dist)
    print(f"✅ Calibración Exitosa. Error: {ret:.4f}. Parámetros guardados.")

if __name__ == "__main__": calibrar()