import cv2
import cv2.aruco as aruco
import numpy as np

def crear_geometria_iniciales():
    """Define los puntos 3D y las conexiones para las letras 'A' y 'R'"""
    # Escala: 1 unidad = 1 metro. Altura = 4cm (0.04m)
    z_alto = 0.04
    z_medio = 0.02
    
    # 1. Definir los VÉRTICES (Puntos [X, Y, Z])
    # Consideramos Y=0 para que las letras estén "de pie" sobre el marcador
    vertices = np.float32([
        # --- Puntos para la letra 'A' ---
        [-0.03, 0, 0],         # 0: Base izquierda
        [-0.02, 0, z_alto],    # 1: Pico superior
        [-0.01, 0, 0],         # 2: Base derecha
        [-0.025, 0, z_medio],  # 3: Barra central izquierda
        [-0.015, 0, z_medio],  # 4: Barra central derecha
        
        # --- Puntos para la letra 'R' ---
        [0.01, 0, 0],          # 5: Base palo izquierdo
        [0.01, 0, z_alto],     # 6: Tope palo izquierdo
        [0.03, 0, z_alto],     # 7: Esquina superior derecha (curva/cuadrada)
        [0.03, 0, z_medio],    # 8: Esquina inferior derecha curva
        [0.01, 0, z_medio],    # 9: Intersección central
        [0.03, 0, 0]           # 10: Pie derecho
    ])
    
    # 2. Definir las ARISTAS (Conexiones entre puntos)
    conexiones = [
        # Trazos de la 'A'
        (0, 1), (1, 2), (3, 4),
        # Trazos de la 'R'
        (5, 6), (6, 7), (7, 8), (8, 9), (9, 10)
    ]
    
    return vertices, conexiones

def calcular_color_por_distancia(tvec):
    """Cambia de Verde (cerca) a Rojo (lejos)"""
    # tvec es la distancia desde la cámara al marcador
    distancia = np.linalg.norm(tvec)
    
    # Supongamos que 20cm (0.2m) es cerca y 80cm (0.8m) es lejos
    rango_min = 0.2
    rango_max = 0.8
    
    # Normalizar distancia entre 0 y 1
    norm_dist = np.clip((distancia - rango_min) / (rango_max - rango_min), 0, 1)
    
    # Interpolar: Cerca = Verde (0, 255, 0), Lejos = Rojo (0, 0, 255)
    rojo = int(255 * norm_dist)
    verde = int(255 * (1 - norm_dist))
    azul = 255  # Agregamos azul constante para que parezca un holograma
    
    return (azul, verde, rojo) # Formato BGR

def main():
    cap = cv2.VideoCapture(0)
    
    # Matriz de cámara genérica
    matriz_camara = np.array([[1000, 0, 640],
                              [0, 1000, 360],
                              [0, 0, 1]], dtype=np.float32)
    dist_coefs = np.zeros((4, 1))
    
    tamanio_marcador = 0.05
    vertices_3d, conexiones = crear_geometria_iniciales()
    
    # Detector ArUco
    diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    parametros = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(diccionario, parametros)
    
    angulo_rotacion = 0.0

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Animación: Aumentar ángulo 3 grados por frame
        angulo_rotacion += 3.0
        if angulo_rotacion >= 360:
            angulo_rotacion = 0
            
        esquinas, ids, _ = detector.detectMarkers(frame)
        
        if ids is not None:
            for i in range(len(ids)):
                # 1. Estimar la pose del marcador
                obj_points = np.array([[-tamanio_marcador/2, tamanio_marcador/2, 0],
                                       [tamanio_marcador/2, tamanio_marcador/2, 0],
                                       [tamanio_marcador/2, -tamanio_marcador/2, 0],
                                       [-tamanio_marcador/2, -tamanio_marcador/2, 0]], dtype=np.float32)
                
                success, rvec, tvec = cv2.solvePnP(obj_points, esquinas[i][0], matriz_camara, dist_coefs)
                
                if success:
                    # 2. Calcular color dinámico
                    color_holograma = calcular_color_por_distancia(tvec)
                    
                    # 3. Aplicar matriz de rotación sobre el eje Z (para que giren como un tocadiscos)
                    # El eje Z sale disparado hacia arriba desde el marcador
                    R_animacion = cv2.Rodrigues(np.array([0, 0, angulo_rotacion * np.pi / 180.0]))[0]
                    vertices_rotados = np.dot(vertices_3d, R_animacion.T)
                    
                    # 4. Proyectar los puntos 3D al mundo 2D de la pantalla
                    imgpts, _ = cv2.projectPoints(vertices_rotados, rvec, tvec, matriz_camara, dist_coefs)
                    imgpts = np.int32(imgpts).reshape(-1, 2)
                    
                    # 5. Dibujar las líneas conectando los puntos proyectados
                    for inicio, fin in conexiones:
                        pt1 = tuple(imgpts[inicio])
                        pt2 = tuple(imgpts[fin])
                        cv2.line(frame, pt1, pt2, color_holograma, 4)
                        
                    # 6. Mostrar métricas en pantalla
                    distancia_real = np.linalg.norm(tvec)
                    cv2.putText(frame, f"Distancia: {distancia_real:.2f}m", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_holograma, 2)
        
        cv2.imshow('Holograma 3D - UTNG', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()