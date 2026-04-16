import cv2

# Cargar los clasificadores pre-entrenados
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

cap = cv2.VideoCapture(0)

# Variables de control
contador_parpadeos = 0
estado_parpadeo = False # True si los ojos están cerrados

print("Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 1. Detectar rostros
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Region de Interés (ROI) para los ojos (solo buscamos en la mitad superior de la cara)
        roi_gray = gray[y:y + int(h*0.6), x:x+w]
        roi_color = frame[y:y + int(h*0.6), x:x+w]
        
        # 2. Detectar ojos dentro del rostro
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10, minSize=(30, 30))
        
        # 3. Lógica de parpadeo
        # Si detectamos la cara pero NO detectamos ojos, es posible que estén cerrados
        if len(eyes) == 0:
            if not estado_parpadeo:
                estado_parpadeo = True
                contador_parpadeos += 1
            cv2.putText(frame, "OJOS CERRADOS", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            estado_parpadeo = False
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    # Interfaz de usuario
    cv2.putText(frame, f"Parpadeos: {contador_parpadeos}", (30, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    cv2.imshow('Detector de Parpadeos (Haar Cascades)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()