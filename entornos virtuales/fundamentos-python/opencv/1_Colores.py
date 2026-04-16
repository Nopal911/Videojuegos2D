import cv2
import numpy as np

def mostrar_valor_pixel(evento, x, y, flags, param):
    # 'param' contiene la imagen que enviamos desde el main
    imagen = param
    
    if evento == cv2.EVENT_MOUSEMOVE:
        if 0 <= y < imagen.shape[0] and 0 <= x < imagen.shape[1]:
            bgr = imagen[y, x]
            
            # 1. Creamos la copia para dibujar
            img_info = imagen.copy()
            
            # 2. Preparamos el texto (BGR)
            texto = f"B:{bgr[0]} G:{bgr[1]} R:{bgr[2]}"
            
            # 3. Dibujamos (Texto y Círculo)
            cv2.putText(img_info, texto, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.circle(img_info, (x, y), 6, (0, 255, 0), 2)
            
            # 4. ¡IMPORTANTE! Mostramos la copia AQUÍ
            cv2.imshow('Visor', img_info)

def main():
    # Cargar o crear gradiente (lo que ya tienes funcionando)
    imagen = cv2.imread('test.jpg')
    if imagen is None:
        imagen = np.zeros((400, 600, 3), dtype=np.uint8)
        for i in range(400):
            for j in range(600):
                imagen[i, j] = [j % 256, i % 256, (i+j) % 256]

    cv2.namedWindow('Visor')
    cv2.setMouseCallback('Visor', mostrar_valor_pixel, imagen)
    
    # Ejemplo para canal azul
    canal_azul = np.zeros_like(imagen)
    canal_azul[:, :, 0] = imagen[:, :, 0]  # Solo canal B
    
    #canal verde
    canal_verde = np.zeros_like(imagen)
    canal_verde[:,:,1] = imagen[:,:,1]
    
    #canal rojo
    canal_rojo = np.zeros_like(imagen)
    canal_rojo[:,:,2] = imagen[:,:,2]
    
    # Mostrar la imagen por primera vez
    cv2.imshow('Visor', imagen)

    while True:
        # Nota: Quitamos el cv2.imshow de aquí para que no borre lo que hace el mouse
        tecla = cv2.waitKey(1) & 0xFF
    
        
        if tecla == ord('1'):
           cv2.imshow('Visor',canal_azul)
        
        elif tecla == ord('2'):
            cv2.imshow('Visor', canal_verde)

        elif tecla == ord('3'):
            cv2.imshow('Visor', canal_rojo)
            
        elif tecla == ord('4'):
            cv2.imshow('Visor', imagen)
            
        elif tecla == ord('q') or tecla == 27:
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()