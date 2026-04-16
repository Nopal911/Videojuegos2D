import cv2
import numpy as np
import time
import math

class RastreadorSencillo:
    """Rastrea objetos basándose en la distancia entre sus centros en frames consecutivos."""
    def __init__(self, max_desaparicion=10, distancia_max=50):
        self.centroides = {} # Formato: id: (centro_x, centro_y, frames_desaparecido)
        self.siguiente_id = 1
        self.max_desaparicion = max_desaparicion
        self.distancia_max = distancia_max

    def actualizar(self, rectangulos):
        if len(rectangulos) == 0:
            # Si no hay detecciones, aumentar el contador de desaparición de todos
            for obj_id in list(self.centroides.keys()):
                x, y, desap = self.centroides[obj_id]
                self.centroides[obj_id] = (x, y, desap + 1)
                if self.centroides[obj_id][2] > self.max_desaparicion:
                    del self.centroides[obj_id]
            return self.centroides

        # Calcular los nuevos centroides
        nuevos_centroides = []
        for (x1, y1, x2, y2) in rectangulos:
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            nuevos_centroides.append((cx, cy, x1, y1, x2, y2))

        centroides_actualizados = {}

        for nuevo_c in nuevos_centroides:
            cx, cy = nuevo_c[0], nuevo_c[1]
            obj_id_encontrado = None
            min_dist = self.distancia_max
            
            # Buscar el centroide anterior más cercano
            for obj_id, datos in self.centroides.items():
                distancia = math.hypot(cx - datos[0], cy - datos[1])
                if distancia < min_dist:
                    min_dist = distancia
                    obj_id_encontrado = obj_id
            
            if obj_id_encontrado is None:
                # Es una persona nueva
                centroides_actualizados[self.siguiente_id] = (cx, cy, 0)
                self.siguiente_id += 1
            else:
                # Es una persona conocida
                centroides_actualizados[obj_id_encontrado] = (cx, cy, 0)
                del self.centroides[obj_id_encontrado] # Lo quitamos de los viejos
        
        # Los que quedaron en self.centroides no fueron vistos en este frame
        for obj_id, datos in self.centroides.items():
            if datos[2] + 1 <= self.max_desaparicion:
                centroides_actualizados[obj_id] = (datos[0], datos[1], datos[2] + 1)
                
        self.centroides = centroides_actualizados
        return self.centroides

# --- INICIO DEL PROGRAMA PRINCIPAL ---

# Cargar modelo DNN
print("Cargando modelo DNN...")
prototxt = "deploy.prototxt"
modelo = "res10_300x300_ssd_iter_140000.caffemodel"
red_dnn = cv2.dnn.readNetFromCaffe(prototxt, modelo)

cap = cv2.VideoCapture(0)
rastreador = RastreadorSencillo()

# Configuración del reto
LIMITE_PERSONAS = 3

while True:
    ret, frame = cap.read()
    if not ret: break
    
    inicio_dnn = time.time()
    h, w = frame.shape[:2]
    
    # 1. Detección con DNN
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123])
    red_dnn.setInput(blob)
    detecciones = red_dnn.forward()
    
    cajas_detectadas = []
    
    for i in range(detecciones.shape[2]):
        confianza = detecciones[0, 0, i, 2]
        if confianza > 0.5:
            box = detecciones[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
            cajas_detectadas.append((x1, y1, x2, y2))

    # 2. Actualizar el rastreador con las cajas de este frame
    objetos_rastreados = rastreador.actualizar(cajas_detectadas)
    
    # Contar cuántas personas VISIBLES hay ahora (frames_desaparecido == 0)
    personas_actuales = sum(1 for datos in objetos_rastreados.values() if datos[2] == 0)
    total_historico = rastreador.siguiente_id - 1

    # 3. Dibujar detecciones e IDs
    for obj_id, datos in objetos_rastreados.items():
        cx, cy, desap = datos
        if desap == 0: # Solo dibujar si está visible
            cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
            cv2.putText(frame, f"ID: {obj_id}", (cx - 10, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # 4. Termómetro Visual (Barra de capacidad)
    alto_termometro = 200
    ancho_termometro = 30
    x_term, y_term = w - 50, h - 250
    
    # Calcular nivel (limitado al máximo de la barra)
    porcentaje_lleno = min(personas_actuales / LIMITE_PERSONAS, 1.0)
    nivel_pixel = int(alto_termometro * porcentaje_lleno)
    
    # Color cambia según la capacidad (Verde -> Amarillo -> Rojo)
    if personas_actuales < LIMITE_PERSONAS:
        color_term = (0, 255, 0)
    elif personas_actuales == LIMITE_PERSONAS:
        color_term = (0, 255, 255)
    else:
        color_term = (0, 0, 255)

    # Dibujar fondo, relleno y borde del termómetro
    cv2.rectangle(frame, (x_term, y_term), (x_term + ancho_termometro, y_term + alto_termometro), (50, 50, 50), -1)
    cv2.rectangle(frame, (x_term, y_term + alto_termometro - nivel_pixel), 
                 (x_term + ancho_termometro, y_term + alto_termometro), color_term, -1)
    cv2.rectangle(frame, (x_term, y_term), (x_term + ancho_termometro, y_term + alto_termometro), (255, 255, 255), 2)
    
    # 5. Interfaz y Alertas
    cv2.putText(frame, f"Personas en sala: {personas_actuales}/{LIMITE_PERSONAS}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(frame, f"Total visitantes hoy: {total_historico}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    if personas_actuales > LIMITE_PERSONAS:
        print('\a')  # Beep en terminal
        cv2.putText(frame, "¡ALERTA! AFORO SUPERADO", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        # Borde rojo intermitente
        if int(time.time() * 5) % 2 == 0: 
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), 10)

    cv2.imshow('Control de Aforo DNN', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()