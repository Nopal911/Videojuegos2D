import cv2
import numpy as np
import time
import math

cap = cv2.VideoCapture(0)

# Variables para el cronómetro
tiempo_mala_postura = 0
alerta_limite = 5  # segundos

while True:
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # 1. Preprocesamiento: Convertir a gris y desenfocar
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (25, 25), 0)
    
    # 2. Umbralización (Ajusta el 100 si tu fondo es oscuro o claro)
    # Buscamos separar tu silueta del fondo
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 3. Encontrar el contorno más grande (Tú)
    contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contornos:
        c = max(contornos, key=cv2.contourArea)
        
        if cv2.contourArea(c) > 10000: # Evitar ruido pequeño
            # 4. Obtener el rectángulo delimitador y momentos
            x, y, ancho, alto = cv2.boundingRect(c)
            M = cv2.moments(c)
            
            if M["m00"] != 0:
                # Centro de masa (Torso aproximado)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Punto superior (Cabeza aproximada)
                top_head = tuple(c[c[:, :, 1].argmin()][0])
                
                # 5. Calcular ángulo de inclinación respecto a la vertical
                # Si cx y top_head[0] están alineados, el ángulo es 0 (derecho)
                dx = top_head[0] - cx
                dy = cy - top_head[1]
                angulo = math.degrees(math.atan2(dx, dy))
                
                # Lógica de postura: Si te inclinas más de 25 grados
                if abs(angulo) > 25:
                    if tiempo_mala_postura == 0:
                        tiempo_mala_postura = time.time()
                    
                    duracion = time.time() - tiempo_mala_postura
                    color = (0, 0, 255) # Rojo
                    
                    if duracion >= alerta_limite:
                        cv2.putText(frame, "¡SIENTATE DERECHO! 😊", (50, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                else:
                    tiempo_mala_postura = 0
                    color = (0, 255, 0) # Verde

                # Dibujar visualización
                cv2.rectangle(frame, (x, y), (x + ancho, y + alto), color, 2)
                cv2.line(frame, (cx, cy), top_head, color, 3)
                cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)
                cv2.putText(frame, f"Inclinacion: {abs(int(angulo))} deg", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow('Detector de Postura (CV Tradicional)', frame)
    # cv2.imshow('Mascara Binaria', thresh) # Descomenta para ver qué ve el algoritmo
    
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()