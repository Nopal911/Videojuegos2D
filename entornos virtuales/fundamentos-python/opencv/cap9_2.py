import cv2
import cv2.aruco as aruco
import numpy as np
from datetime import datetime
import os

def app_personalizada(target_id=5):
    cap = cv2.VideoCapture(0)
    detector = aruco.ArucoDetector(aruco.getPredefinedDictionary(aruco.DICT_6X6_250))
    os.makedirs("capturas", exist_ok=True)
    foto_tomada = False

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        esquinas, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            for i, m_id in enumerate(ids):
                if m_id[0] == target_id:
                    # EFECTO: Borde Neón (Magenta)
                    pts = esquinas[i].astype(int)
                    cv2.polylines(frame, [pts], True, (255, 0, 255), 5)
                    
                    # TEXTO FLOTANTE
                    centro = np.mean(pts[0], axis=0).astype(int)
                    cv2.putText(frame, "ID VIP DETECTADO", (centro[0]-100, centro[1]-50), 
                                cv2.FONT_HERSHEY_TRIPLEX, 0.8, (255, 255, 255), 2)

                    # AUTO-SAVE (Una sola vez por detección)
                    if not foto_tomada:
                        filename = f"capturas/user_{target_id}_{datetime.now().strftime('%H%M%S')}.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"📸 Foto guardada como: {filename}")
                        foto_tomada = True
                else:
                    aruco.drawDetectedMarkers(frame, [esquinas[i]], [m_id])

        cv2.imshow("Mi App AR", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('r'): foto_tomada = False # Reset con la tecla 'r'

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    app_personalizada(target_id=5) # <--- Cambia este número por el tuyo