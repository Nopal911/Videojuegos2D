import cv2
import numpy as np

def crear_tablero_ajedrez(tamanio_cuadro=30, num_cuadros_x=9, num_cuadros_y=6):
    ancho = tamanio_cuadro * num_cuadros_x
    alto = tamanio_cuadro * num_cuadros_y
    tablero = np.ones((alto, ancho), dtype=np.uint8) * 255
    for i in range(num_cuadros_y):
        for j in range(num_cuadros_x):
            if (i + j) % 2 == 0:
                x1, y1 = j * tamanio_cuadro, i * tamanio_cuadro
                x2, y2 = x1 + tamanio_cuadro, y1 + tamanio_cuadro
                tablero[y1:y2, x1:x2] = 0
    tablero = cv2.copyMakeBorder(tablero, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)
    return tablero

tablero = crear_tablero_ajedrez()
cv2.imwrite("tablero_calibracion.png", tablero)
print("✅ Archivo 'tablero_calibracion.png' creado. ¡Imprímelo!")