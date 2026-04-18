import cv2
import os

def capturar():
    os.makedirs("calibracion", exist_ok=True)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    patron = (8, 5) # Esquinas internas
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret_c, esquinas = cv2.findChessboardCorners(gris, patron, None)
        
        vis = frame.copy()
        if ret_c:
            cv2.drawChessboardCorners(vis, patron, esquinas, ret_c)
            cv2.putText(vis, "Listo! Presiona 'C'", (10, 30), 2, 0.7, (0,255,0), 2)
            
        cv2.imshow("Captura", vis)
        k = cv2.waitKey(1)
        if k & 0xFF == ord('c') and ret_c:
            cv2.imwrite(f"calibracion/img_{count:02d}.png", frame)
            count += 1
            print(f"📸 Foto {count} guardada")
        elif k & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__": capturar()