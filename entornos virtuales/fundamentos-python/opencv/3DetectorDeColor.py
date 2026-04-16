import cv2
import numpy as np
import os

def nada(x):
    pass

# 1. Configuración de ventanas
cv2.namedWindow('Control')
cv2.namedWindow('Original')
cv2.namedWindow('Resultado')

# Crear sliders para controlar el rango HSV
cv2.createTrackbar('H Min', 'Control', 0, 179, nada)
cv2.createTrackbar('H Max', 'Control', 179, 179, nada)
cv2.createTrackbar('S Min', 'Control', 0, 255, nada)
cv2.createTrackbar('S Max', 'Control', 255, 255, nada)
cv2.createTrackbar('V Min', 'Control', 0, 255, nada)
cv2.createTrackbar('V Max', 'Control', 255, 255, nada)

def actualizar_sliders(valores):
    # valores[0] son los minimos y valores[1] los maximos
    cv2.setTrackbarPos('H Min', 'Control', valores[0][0])
    cv2.setTrackbarPos('S Min', 'Control', valores[0][1])
    cv2.setTrackbarPos('V Min', 'Control', valores[0][2])
    cv2.setTrackbarPos('H Max', 'Control', valores[1][0])
    cv2.setTrackbarPos('S Max', 'Control', valores[1][1])
    cv2.setTrackbarPos('V Max', 'Control', valores[1][2])

# Captura de video
cap = cv2.VideoCapture(0)

print("Comandos: 'g': Guardar | 'c': Cargar | 'r': Reset | 'q': Salir")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Convertir a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Obtener valores actuales de los sliders
    h_min = cv2.getTrackbarPos('H Min', 'Control')
    h_max = cv2.getTrackbarPos('H Max', 'Control')
    s_min = cv2.getTrackbarPos('S Min', 'Control')
    s_max = cv2.getTrackbarPos('S Max', 'Control')
    v_min = cv2.getTrackbarPos('V Min', 'Control')
    v_max = cv2.getTrackbarPos('V Max', 'Control')
    
    # Definir rangos y crear mascara
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mascara = cv2.inRange(hsv, lower, upper)
    
    # Limpiar mascara (Morfologia)
    kernel = np.ones((5,5), np.uint8)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
    
    # --- DETECCION DE CONTORNOS ---
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area > 1000: # Filtrar objetos pequenos
            x, y, w, h = cv2.boundingRect(contorno)
            # Dibujar rectangulo sobre el frame original
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Objeto Detectado", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Aplicar mascara para visualizacion
    resultado = cv2.bitwise_and(frame, frame, mask=mascara)
    
    # Mostrar ventanas
    cv2.imshow('Original', frame)
    cv2.imshow('Mascara', mascara)
    cv2.imshow('Resultado', resultado)
    
    # Logica de teclado
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
        
    elif key == ord('g'):
        # Guardar valores actuales
        datos_a_guardar = np.array([lower, upper])
        np.save('color_favorito.npy', datos_a_guardar)
        print("Valores guardados en color_favorito.npy")
        
    elif key == ord('c'):
        # Cargar valores si el archivo existe
        if os.path.exists('color_favorito.npy'):
            datos_cargados = np.load('color_favorito.npy')
            actualizar_sliders(datos_cargados)
            print("Valores cargados desde archivo")
        else:
            print("Error: No se encontro el archivo color_favorito.npy")
            
    elif key == ord('r'):
        # Resetear sliders al rango completo
        rango_total = np.array([[0, 0, 0], [179, 255, 255]])
        actualizar_sliders(rango_total)
        print("Valores restablecidos")

cap.release()
cv2.destroyAllWindows()