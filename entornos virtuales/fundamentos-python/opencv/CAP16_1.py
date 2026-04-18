import sys
import cv2
import numpy as np
import random
import time
import json
import os
from datetime import datetime

# --- BLOQUE DE IMPORTACIÓN ANTI-ERROR ---
try:
    import mediapipe as mp
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    print("✅ MediaPipe cargado correctamente.")
except Exception as e:
    print(f"❌ Error de MediaPipe: {e}")
    sys.exit()

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QStackedWidget, 
                             QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

# --- 1. MOTOR DEL JUEGO AR (Físicas, Gestos y Puntuación) ---
class MotorJuegoAR:
    def __init__(self, ancho=900, alto=600):
        # Detección de manos
        self.mp_hands = mp_hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        
        # Configuración
        self.ancho = ancho
        self.alto = alto
        self.puntos = 0
        self.vidas = 3
        self.nivel = 1
        self.puntos_para_siguiente_nivel = 100
        
        # Objetos y Físicas
        self.objetos = []
        self.velocidad_base = 5
        self.colores = {'bueno': (0, 255, 0), 'malo': (0, 0, 255), 'especial': (255, 255, 0)}
        
        # Gestos
        self.gesto_actual = "none"
        self.ultimo_gesto_tiempo = 0
        self.tiempo_gesto = 1.0
        self.ultima_posicion = None
        self.tiempo_inicio = time.time()
        
        self.ranking = self.cargar_ranking()

    def cargar_ranking(self):
        if os.path.exists('ranking.json'):
            with open('ranking.json', 'r') as f:
                return json.load(f)
        return []

    def guardar_ranking(self):
        with open('ranking.json', 'w') as f:
            json.dump(self.ranking, f, indent=2)

    def crear_objeto(self):
        tipo = random.choice(['bueno', 'malo', 'especial'])
        if self.nivel > 3 and random.random() < 0.4:
            tipo = 'malo' # Más dificultad
            
        obj = {
            'x': random.randint(50, self.ancho - 50),
            'y': -50, # Nacen arriba de la pantalla
            'tipo': tipo,
            'radio': 30 if tipo == 'especial' else 20,
            'puntos': 10 if tipo == 'bueno' else -10 if tipo == 'malo' else 50,
            'velocidad': self.velocidad_base * (1.5 if tipo == 'malo' else 1.0)
        }
        self.objetos.append(obj)

    def actualizar_fisicas(self):
        objetos_activos = []
        for obj in self.objetos:
            obj['y'] += int(obj['velocidad'])
            
            if obj['y'] < self.alto + 50:
                objetos_activos.append(obj)
            elif obj['tipo'] == 'bueno':
                self.puntos = max(0, self.puntos - 2) # Penalización si se cae uno bueno
                
        self.objetos = objetos_activos
        
        # Spawn aleatorio (aumenta con el nivel)
        probabilidad = 0.02 + (self.nivel * 0.005)
        if len(self.objetos) < (5 + self.nivel) and random.random() < probabilidad:
            self.crear_objeto()

    def procesar_mano_y_gestos(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        
        posicion_mano = None
        self.gesto_actual = "none"
        
        if res.multi_hand_landmarks:
            hm = res.multi_hand_landmarks[0]
            # Usar nudillo central (9) como hitbox de la mano para mejor precisión
            hitbox = hm.landmark[9] 
            posicion_mano = (int(hitbox.x * self.ancho), int(hitbox.y * self.alto))
            self.ultima_posicion = posicion_mano
            
            # Detectar Gesto
            p_indice = hm.landmark[8]
            n_indice = hm.landmark[6]
            p_medio = hm.landmark[12]
            
            dedos_ext = sum([1 for tip, pip in [(8,6), (12,10), (16,14), (20,18)] if hm.landmark[tip].y < hm.landmark[pip].y])
            
            if dedos_ext == 0: self.gesto_actual = "puño"
            elif dedos_ext == 2 and p_indice.y < n_indice.y and p_medio.y < hm.landmark[10].y: self.gesto_actual = "paz"
            elif dedos_ext >= 4: self.gesto_actual = "abierta"
            
            self.aplicar_gesto(time.time())
            mp_drawing.draw_landmarks(frame, hm, self.mp_hands.HAND_CONNECTIONS)
            
        return frame, posicion_mano

    def aplicar_gesto(self, t_actual):
        if self.gesto_actual == "none" or (t_actual - self.ultimo_gesto_tiempo < self.tiempo_gesto):
            return
            
        if self.gesto_actual == "puño":
            for obj in self.objetos: obj['velocidad'] = max(1, obj['velocidad'] * 0.5)
        elif self.gesto_actual == "paz":
            self.puntos += 20
        elif self.gesto_actual == "abierta" and self.ultima_posicion:
            mx, my = self.ultima_posicion
            # Destruir objetos cercanos como un "empujón de fuerza"
            self.objetos = [o for o in self.objetos if np.hypot(mx - o['x'], my - o['y']) > 150]
            
        self.ultimo_gesto_tiempo = t_actual

    def verificar_colisiones(self, pos_mano):
        if not pos_mano: return
        mx, my = pos_mano
        obj_restantes = []
        
        for obj in self.objetos:
            dist = np.hypot(mx - obj['x'], my - obj['y'])
            if dist < obj['radio'] + 40: # Hitbox tolerante
                self.puntos += obj['puntos']
                if obj['tipo'] == 'malo':
                    self.vidas -= 1
            else:
                obj_restantes.append(obj)
        self.objetos = obj_restantes

    def actualizar_nivel(self):
        nuevo_nivel = (max(0, self.puntos) // self.puntos_para_siguiente_nivel) + 1
        if nuevo_nivel > self.nivel:
            self.nivel = nuevo_nivel
            self.velocidad_base = 5 + (self.nivel - 1) * 2
            self.crear_objeto()

    def dibujar_ui(self, frame):
        # Objetos
        for obj in self.objetos:
            color = self.colores[obj['tipo']]
            cv2.circle(frame, (int(obj['x']), int(obj['y'])), obj['radio'], color, -1)
            cv2.circle(frame, (int(obj['x']), int(obj['y'])), obj['radio'], (255,255,255), 2)
            cv2.putText(frame, str(obj['puntos']), (int(obj['x'])-15, int(obj['y'])+5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # HUD Principal
        cv2.putText(frame, f"Puntos: {self.puntos}  Nivel: {self.nivel}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"Vidas: {self.vidas}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if self.vidas > 1 else (0, 0, 255), 2)
        
        # Gestos Info
        cv2.putText(frame, f"Gesto: {self.gesto_actual}", (self.ancho - 250, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def agregar_ranking(self, nombre):
        self.ranking.append({
            'nombre': nombre, 'puntos': self.puntos, 'nivel': self.nivel,
            'fecha': datetime.now().strftime("%Y-%m-%d")
        })
        self.ranking.sort(key=lambda x: x['puntos'], reverse=True)
        self.ranking = self.ranking[:10]
        self.guardar_ranking()

# --- 2. INTERFAZ GRÁFICA (PyQt6) ---
class PantallaJuego(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        
        self.label_video = QLabel()
        self.label_video.setStyleSheet("background-color: #000; border: 3px solid #4CAF50; border-radius: 10px;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_video)
        
        btn_lay = QHBoxLayout()
        btn_menu = QPushButton("🏠 Volver al Menú")
        btn_menu.clicked.connect(self.volver_menu)
        btn_menu.setStyleSheet("padding: 10px; font-size: 16px; background-color: #555; color: white;")
        btn_lay.addWidget(btn_menu)
        layout.addLayout(btn_lay)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop_juego)

    def iniciar_juego(self):
        self.juego = MotorJuegoAR(ancho=900, alto=600)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.timer.start(30)

    def loop_juego(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (900, 600)) # Fija la resolución para evitar bugs de PyQt
        
        frame, pos_mano = self.juego.procesar_mano_y_gestos(frame)
        self.juego.actualizar_fisicas()
        self.juego.verificar_colisiones(pos_mano)
        self.juego.actualizar_nivel()
        frame = self.juego.dibujar_ui(frame)
        
        if self.juego.vidas <= 0:
            self.game_over()
            return
            
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, 900, 600, 900*3, QImage.Format.Format_RGB888)
        self.label_video.setPixmap(QPixmap.fromImage(qimg))

    def game_over(self):
        self.timer.stop()
        self.cap.release()
        
        # FIX: Usar QInputDialog correctamente
        nombre, ok = QInputDialog.getText(self, "¡JUEGO TERMINADO!", 
            f"💀 Perdiste todas tus vidas.\n⭐ Puntos: {self.juego.puntos}\n📈 Nivel: {self.juego.nivel}\n\nIngresa tu nombre para el Ranking:")
        
        if ok and nombre.strip():
            self.juego.agregar_ranking(nombre[:15])
            
        self.parent.mostrar_ranking()

    def volver_menu(self):
        self.timer.stop()
        if hasattr(self, 'cap'): self.cap.release()
        self.parent.mostrar_menu()

class PantallaRanking(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout(self)
        
        titulo = QLabel("🏆 SALÓN DE LA FAMA")
        titulo.setStyleSheet("font-size: 36px; font-weight: bold; color: #FFD700;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        self.tabla = QTableWidget(10, 4)
        self.tabla.setHorizontalHeaderLabels(["Pos", "Jugador", "Puntos", "Nivel"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.tabla)
        
        btn = QPushButton("◀ Volver al menú")
        btn.clicked.connect(self.parent.mostrar_menu)
        btn.setStyleSheet("padding: 15px; font-size: 18px; background-color: #2196F3; color: white;")
        layout.addWidget(btn)

    def actualizar(self):
        self.tabla.clearContents()
        try:
            with open('ranking.json', 'r') as f:
                datos = json.load(f)
        except: datos = []
        
        for i, d in enumerate(datos[:10]):
            self.tabla.setItem(i, 0, QTableWidgetItem(f"#{i+1}"))
            self.tabla.setItem(i, 1, QTableWidgetItem(d['nombre']))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(d['puntos'])))
            self.tabla.setItem(i, 3, QTableWidgetItem(str(d['nivel'])))

class ARCatcherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 AR Catcher - Master UTNG")
        self.setFixedSize(1000, 750) # Ventana fija para evitar el Resize Loop
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.p_juego = PantallaJuego(self)
        self.p_ranking = PantallaRanking(self)
        
        # --- Pantalla Menú (Creada Inline para ahorrar espacio) ---
        self.p_menu = QWidget()
        l_menu = QVBoxLayout(self.p_menu)
        tit = QLabel("🖐️ AR CATCHER 🖐️")
        tit.setStyleSheet("font-size: 50px; font-weight: bold; color: #4CAF50;")
        tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l_menu.addWidget(tit)
        
        b1 = QPushButton("▶ JUGAR AHORA"); b1.clicked.connect(self.mostrar_juego)
        b2 = QPushButton("🏆 VER RANKING"); b2.clicked.connect(self.mostrar_ranking)
        b3 = QPushButton("❌ SALIR"); b3.clicked.connect(self.close)
        
        for b in [b1, b2, b3]:
            b.setStyleSheet("font-size: 20px; padding: 15px; margin: 10px 100px; background-color: #333; color: white;")
            l_menu.addWidget(b)
            
        self.stack.addWidget(self.p_menu)
        self.stack.addWidget(self.p_juego)
        self.stack.addWidget(self.p_ranking)
        self.mostrar_menu()

    def mostrar_menu(self): self.stack.setCurrentWidget(self.p_menu)
    def mostrar_juego(self): self.stack.setCurrentWidget(self.p_juego); self.p_juego.iniciar_juego()
    def mostrar_ranking(self): self.p_ranking.actualizar(); self.stack.setCurrentWidget(self.p_ranking)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ARCatcherApp()
    win.show()
    sys.exit(app.exec())