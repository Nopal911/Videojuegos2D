import cv2
import cv2.aruco as aruco
import os

def generar_marcadores():
    os.makedirs("marcadores", exist_ok=True)
    # Usamos el diccionario 6x6 con 250 variantes
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    
    for marker_id in range(10):
        # Generar la matriz de bits (400x400 px)
        imagen_marcador = aruco.generateImageMarker(diccionario, marker_id, 400)
        
        # Añadir un borde blanco para que la cámara lo detecte mejor
        imagen_final = cv2.copyMakeBorder(imagen_marcador, 50, 50, 50, 50, 
                                         cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        cv2.imwrite(f"marcadores/marcador_{marker_id}.png", imagen_final)
        print(f"✅ Guardado: marcadores/marcador_{marker_id}.png")

if __name__ == "__main__":
    generar_marcadores()