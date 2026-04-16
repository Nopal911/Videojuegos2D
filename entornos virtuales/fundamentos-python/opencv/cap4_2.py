import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QAction
from datetime import datetime

class EscanerDocumentos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 Escáner de Documentos - Capítulo 4")
        self.setGeometry(100, 100, 1400, 800)
        
        # Variables
        self.imagen_original = None
        self.imagen_procesada = None
        self.puntos_documento = [] # <-- Inicializado como lista vacía
        
        # Modo: automático o manual
        self.modo_manual = False
        
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        layout = QHBoxLayout(central)
        
        # Panel izquierdo: imágenes
        panel_imagenes = QWidget()
        layout_imagenes = QVBoxLayout(panel_imagenes)
        
        # Imagen original
        layout_imagenes.addWidget(QLabel("📸 Original:"))
        self.label_original = QLabel()
        self.label_original.setMinimumSize(500, 400)
        self.label_original.setStyleSheet("border: 1px solid #333; background-color: #111;")
        self.label_original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_imagenes.addWidget(self.label_original)
        
        # Imagen procesada
        layout_imagenes.addWidget(QLabel("✨ Enderezada:"))
        self.label_procesada = QLabel()
        self.label_procesada.setMinimumSize(500, 400)
        self.label_procesada.setStyleSheet("border: 1px solid #333; background-color: #111;")
        self.label_procesada.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_imagenes.addWidget(self.label_procesada)
        
        layout.addWidget(panel_imagenes, 3)
        
        # Panel derecho: controles
        panel_control = QWidget()
        panel_control.setMaximumWidth(300)
        layout_control = QVBoxLayout(panel_control)
        
        # Grupo: Carga
        grupo_carga = QGroupBox("📁 Cargar imagen")
        layout_carga = QVBoxLayout()
        
        btn_cargar = QPushButton("Seleccionar imagen...")
        btn_cargar.clicked.connect(self.cargar_imagen)
        layout_carga.addWidget(btn_cargar)
        
        btn_webcam = QPushButton("📷 Usar webcam")
        btn_webcam.clicked.connect(self.usar_webcam)
        layout_carga.addWidget(btn_webcam)
        
        grupo_carga.setLayout(layout_carga)
        layout_control.addWidget(grupo_carga)
        
        # Grupo: Modo de detección
        grupo_modo = QGroupBox("🎯 Modo de detección")
        layout_modo = QVBoxLayout()
        
        btn_auto = QPushButton("🤖 Automático")
        btn_auto.clicked.connect(lambda: self.cambiar_modo(False))
        layout_modo.addWidget(btn_auto)
        
        btn_manual = QPushButton("✋ Manual (seleccionar 4 puntos)")
        btn_manual.clicked.connect(lambda: self.cambiar_modo(True))
        layout_modo.addWidget(btn_manual)
        
        grupo_modo.setLayout(layout_modo)
        layout_control.addWidget(grupo_modo)
        
        # Grupo: Ajustes
        grupo_ajustes = QGroupBox("⚙️ Ajustes Canny (Modo Auto)")
        layout_ajustes = QVBoxLayout()
        
        layout_ajustes.addWidget(QLabel("Umbral Canny 1:"))
        self.slider_canny1 = QSlider(Qt.Orientation.Horizontal)
        self.slider_canny1.setRange(0, 255)
        self.slider_canny1.setValue(50)
        self.slider_canny1.valueChanged.connect(self.actualizar_escaner)
        layout_ajustes.addWidget(self.slider_canny1)
        
        layout_ajustes.addWidget(QLabel("Umbral Canny 2:"))
        self.slider_canny2 = QSlider(Qt.Orientation.Horizontal)
        self.slider_canny2.setRange(0, 255)
        self.slider_canny2.setValue(150)
        self.slider_canny2.valueChanged.connect(self.actualizar_escaner)
        layout_ajustes.addWidget(self.slider_canny2)
        
        grupo_ajustes.setLayout(layout_ajustes)
        layout_control.addWidget(grupo_ajustes)
        
        # Grupo: Acciones
        grupo_acciones = QGroupBox("💾 Acciones")
        layout_acciones = QVBoxLayout()
        
        btn_escanear = QPushButton("🔄 Escanear ahora")
        btn_escanear.clicked.connect(self.escanear_documento)
        layout_acciones.addWidget(btn_escanear)
        
        btn_mejorar = QPushButton("✨ Mejorar lectura (Blanco y Negro)")
        btn_mejorar.clicked.connect(self.mejorar_imagen)
        layout_acciones.addWidget(btn_mejorar)
        
        btn_guardar = QPushButton("💾 Guardar resultado")
        btn_guardar.clicked.connect(self.guardar_resultado)
        layout_acciones.addWidget(btn_guardar)
        
        grupo_acciones.setLayout(layout_acciones)
        layout_control.addWidget(grupo_acciones)
        
        layout_control.addStretch()
        layout.addWidget(panel_control, 1)
        
    def setup_menu(self):
        menubar = self.menuBar()
        archivo_menu = menubar.addMenu("&Archivo")
        
        abrir_action = QAction("&Abrir imagen", self)
        abrir_action.triggered.connect(self.cargar_imagen)
        archivo_menu.addAction(abrir_action)
        
        guardar_action = QAction("&Guardar resultado", self)
        guardar_action.triggered.connect(self.guardar_resultado)
        archivo_menu.addAction(guardar_action)
        
        salir_action = QAction("&Salir", self)
        salir_action.triggered.connect(self.close)
        archivo_menu.addAction(salir_action)
        
    def cargar_imagen(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if archivo:
            self.imagen_original = cv2.imread(archivo)
            if self.imagen_original is not None:
                self.puntos_documento = [] # Resetear puntos
                self.mostrar_imagen(self.imagen_original, self.label_original)
                if not self.modo_manual:
                    self.escanear_documento()
                
    def usar_webcam(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            self.imagen_original = frame
            self.puntos_documento = [] # Resetear puntos
            self.mostrar_imagen(self.imagen_original, self.label_original)
            if not self.modo_manual:
                self.escanear_documento()
            
    def cambiar_modo(self, manual):
        self.modo_manual = manual
        self.puntos_documento = [] # Limpiar puntos al cambiar de modo
        
        if self.imagen_original is not None:
            self.mostrar_imagen(self.imagen_original, self.label_original)
            
        if manual:
            QMessageBox.information(self, "Modo manual", 
                "Haz clic en 4 esquinas del documento en la imagen original.\n"
                "El orden se ordenará automáticamente.")
        else:
            self.escanear_documento()
            
    def ordenar_puntos(self, puntos):
        """Ordena 4 puntos en orden correcto para homografía"""
        puntos = np.array(puntos).reshape(4, 2)
        suma = puntos.sum(axis=1)
        diff = np.diff(puntos, axis=1)
        
        ordenados = np.zeros((4, 2), dtype=np.float32)
        ordenados[0] = puntos[np.argmin(suma)]      # Superior-izq
        ordenados[2] = puntos[np.argmax(suma)]      # Inferior-der
        ordenados[1] = puntos[np.argmin(diff)]      # Superior-der
        ordenados[3] = puntos[np.argmax(diff)]      # Inferior-izq
        
        return ordenados
        
    def detectar_documento_auto(self, imagen):
        """Detecta automáticamente el contorno del documento"""
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
        
        canny1 = self.slider_canny1.value()
        canny2 = self.slider_canny2.value()
        bordes = cv2.Canny(desenfoque, canny1, canny2)
        
        kernel = np.ones((5, 5), np.uint8)
        bordes = cv2.morphologyEx(bordes, cv2.MORPH_CLOSE, kernel)
        
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contornos:
            return None
            
        contorno_doc = max(contornos, key=cv2.contourArea)
        peri = cv2.arcLength(contorno_doc, True)
        aproximacion = cv2.approxPolyDP(contorno_doc, 0.02 * peri, True)
        
        if len(aproximacion) == 4:
            return aproximacion
        return None
        
    def escanear_documento(self):
        """Aplica la transformación para enderezar el documento"""
        if self.imagen_original is None:
            return
            
        if self.modo_manual:
            if len(self.puntos_documento) != 4:
                return # Esperamos a que el usuario termine de hacer los 4 clics
            pts_origen = self.ordenar_puntos(self.puntos_documento)
        else:
            esquinas = self.detectar_documento_auto(self.imagen_original)
            if esquinas is None:
                print("No se detectó documento automáticamente.")
                return
            pts_origen = self.ordenar_puntos(esquinas)
            
        # Calcular dimensiones
        (tl, tr, br, bl) = pts_origen
        ancho1 = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        ancho2 = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        max_ancho = max(int(ancho1), int(ancho2))
        
        alto1 = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        alto2 = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_alto = max(int(alto1), int(alto2))
        
        pts_destino = np.array([
            [0, 0],
            [max_ancho - 1, 0],
            [max_ancho - 1, max_alto - 1],
            [0, max_alto - 1]
        ], dtype=np.float32)
        
        H, _ = cv2.findHomography(pts_origen, pts_destino)
        self.imagen_procesada = cv2.warpPerspective(self.imagen_original, H, (max_ancho, max_alto))
        self.mostrar_imagen(self.imagen_procesada, self.label_procesada)
        
    def mejorar_imagen(self):
        """Aplica filtro para que parezca escáner real"""
        if self.imagen_procesada is None:
            return
            
        gris = cv2.cvtColor(self.imagen_procesada, cv2.COLOR_BGR2GRAY)
        mejora = cv2.adaptiveThreshold(gris, 255, 
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        
        self.imagen_procesada = cv2.cvtColor(mejora, cv2.COLOR_GRAY2BGR)
        self.mostrar_imagen(self.imagen_procesada, self.label_procesada)
        
    def actualizar_escaner(self):
        if self.imagen_original is not None and not self.modo_manual:
            self.escanear_documento()
            
    def guardar_resultado(self):
        if self.imagen_procesada is None:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"documento_escaner_{timestamp}.png"
        cv2.imwrite(nombre, self.imagen_procesada)
        QMessageBox.information(self, "Guardado", f"Imagen guardada como:\n{nombre}")
        
    def mostrar_imagen(self, imagen, label):
        rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(
            label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        """Mapea clics de la ventana a píxeles exactos de la imagen original"""
        if not self.modo_manual or self.imagen_original is None:
            return
            
        # Posición del clic relativa a la ventana principal
        pos_ventana = event.pos()
        # Convertir posición a coordenadas relativas al label original
        pos_label = self.label_original.mapFrom(self, pos_ventana)
        
        # Verificar si el clic fue dentro del label original
        if self.label_original.rect().contains(pos_label) and self.label_original.pixmap():
            # Obtener dimensiones
            label_w = self.label_original.width()
            label_h = self.label_original.height()
            pix_w = self.label_original.pixmap().width()
            pix_h = self.label_original.pixmap().height()
            img_h, img_w = self.imagen_original.shape[:2]
            
            # Calcular bordes negros añadidos por KeepAspectRatio
            offset_x = (label_w - pix_w) / 2
            offset_y = (label_h - pix_h) / 2
            
            # Coordenadas relativas solo a la imagen mostrada (ignorando bordes negros)
            x_pix = pos_label.x() - offset_x
            y_pix = pos_label.y() - offset_y
            
            # Si el clic fue sobre la imagen (no en los bordes negros)
            if 0 <= x_pix <= pix_w and 0 <= y_pix <= pix_h:
                # Regla de 3 para calcular el píxel real en la imagen en tamaño completo
                real_x = int(x_pix * (img_w / pix_w))
                real_y = int(y_pix * (img_h / pix_h))
                
                self.puntos_documento.append([real_x, real_y])
                
                # Dibujar un punto rojo donde el usuario hizo clic
                img_dibujo = self.imagen_original.copy()
                for pt in self.puntos_documento:
                    cv2.circle(img_dibujo, (pt[0], pt[1]), min(img_w, img_h)//50, (0, 0, 255), -1)
                self.mostrar_imagen(img_dibujo, self.label_original)
                
                # Si ya tenemos 4 puntos, procesamos automáticamente
                if len(self.puntos_documento) == 4:
                    self.escanear_documento()
                    # Opcional: limpiar la lista si quieres permitir que escojan de nuevo al hacer más clics
                    self.puntos_documento = [] 

def main():
    app = QApplication(sys.argv)
    ventana = EscanerDocumentos()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()