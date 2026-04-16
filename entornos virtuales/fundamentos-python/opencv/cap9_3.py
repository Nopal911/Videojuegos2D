import cv2
import cv2.aruco as aruco
import os

def generar_base_proyecto():
    os.makedirs("marcadores", exist_ok=True)
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    
    for i in range(2): # Generamos el 0 y el 1
        img = aruco.generateImageMarker(diccionario, i, 400)
        # Añadir borde blanco para mejor detección
        img_con_borde = cv2.copyMakeBorder(img, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        cv2.imwrite(f"marcadores/tarjeta_id_{i}.png", img_con_borde)
        print(f"✅ Marcador ID {i} guardado en carpeta /marcadores")

if __name__ == "__main__":
    generar_base_proyecto()