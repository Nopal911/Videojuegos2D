import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QGridLayout, QLineEdit
)

class VentanaEstadisticas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Calculadora de estadística')
        self.setGeometry(100, 100, 700, 500)
        
        # Generar datos aleatorios iniciales
        self.datos = np.random.randint(1, 100, 20)
        
        self.inicializar_interfaz()
        self.calcular_estadisticas() # Ahora sí encontrará el método
        
    def inicializar_interfaz(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout_principal = QVBoxLayout()
        widget_central.setLayout(layout_principal)
        
        # Grupo para mostrar datos
        grupo_datos = QGroupBox('Datos Actuales')
        layout_datos = QVBoxLayout()
        grupo_datos.setLayout(layout_datos)
        
        # Etiqueta para mostrar los números
        self.label_datos = QLabel()
        self.label_datos.setStyleSheet(
            """
            QLabel {
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 6px;
                font-family: 'Courier New';
                border: 1px solid #d1d5db;
            }
            """
        )
        self.label_datos.setWordWrap(True)
        layout_datos.addWidget(self.label_datos)
        
        # Botón para generar nuevos datos
        boton_generar = QPushButton('🎲 Generar nuevos datos')
        boton_generar.clicked.connect(self.generar_datos)
        layout_datos.addWidget(boton_generar)
        
        layout_principal.addWidget(grupo_datos)
        
        # Grupo para estadísticas
        grupo_stats = QGroupBox('Estadísticas Calculadas')
        layout_stats = QGridLayout()
        grupo_stats.setLayout(layout_stats)
        
        self.labels_stats = {}
        estadisticas = [
            ('Promedio', '📊'), ('Mediana', '📌'),
            ('Máximo', '⬆️'), ('Mínimo', '⬇️'),
            ('Desv. Estándar', '📏'), ('Varianza', '📐'),
            ('Suma', '➕'), ('Cantidad', '🔢')
        ]

        for i, (nombre, emoji) in enumerate(estadisticas):
            fila = i // 2
            columna = (i % 2) * 3

            label_nombre = QLabel(f'{emoji} {nombre}:')
            layout_stats.addWidget(label_nombre, fila, columna)
            
            label_valor = QLabel('---')
            label_valor.setStyleSheet("font-weight: bold; color: #2563eb;")
            layout_stats.addWidget(label_valor, fila, columna + 1)
            
            self.labels_stats[nombre] = label_valor
            
        layout_principal.addWidget(grupo_stats)

        # Grupo para entrada personalizada
        grupo_entrada = QGroupBox(' Ingresar Datos Personalizados')
        layout_entrada = QHBoxLayout()
        grupo_entrada.setLayout(layout_entrada)
        
        layout_entrada.addWidget(QLabel('Números (separados por comas):'))
        self.input_datos = QLineEdit()
        self.input_datos.setPlaceholderText('Ej: 10, 20, 30, 40, 50')
        layout_entrada.addWidget(self.input_datos)
        
        boton_calcular = QPushButton(' Calcular')
        boton_calcular.clicked.connect(self.calcular_personalizados)
        layout_entrada.addWidget(boton_calcular)
        
        layout_principal.addWidget(grupo_entrada)

    # --- ESTOS MÉTODOS DEBEN ESTAR INDENTADOS DENTRO DE LA CLASE ---

    def calcular_estadisticas(self):
        """Calcular todas las estadísticas usando numpy"""
        self.mostrar_datos()
        
        promedio = np.mean(self.datos)
        mediana = np.median(self.datos)
        maximo = np.max(self.datos)
        minimo = np.min(self.datos)
        desv_std = np.std(self.datos)
        varianza = np.var(self.datos)
        suma = np.sum(self.datos)
        cantidad = len(self.datos)
        
        self.labels_stats['Promedio'].setText(f'{promedio:.2f}')
        self.labels_stats['Mediana'].setText(f'{mediana:.2f}')
        self.labels_stats['Máximo'].setText(f'{maximo}')
        self.labels_stats['Mínimo'].setText(f'{minimo}')
        self.labels_stats['Desv. Estándar'].setText(f'{desv_std:.2f}')
        self.labels_stats['Varianza'].setText(f'{varianza:.2f}')
        self.labels_stats['Suma'].setText(f'{suma}')
        self.labels_stats['Cantidad'].setText(f'{cantidad}')
        
    def generar_datos(self):
        """Generar nuevos datos aleatorios"""
        cantidad = np.random.randint(10, 31)
        self.datos = np.random.randint(1, 100, cantidad)
        self.calcular_estadisticas()
        
    def mostrar_datos(self):
        """Mostrar los datos actuales en la interfaz"""
        datos_str = ', '.join(map(str, self.datos))
        self.label_datos.setText(f'Datos ({len(self.datos)} elementos):\n{datos_str}')
        
    def calcular_personalizados(self):
        """Calcular estadísticas de datos ingresados por el usuario"""
        texto = self.input_datos.text().strip()
        if not texto:
            return
        try:
            numeros = [float(x.strip()) for x in texto.split(',')]
            self.datos = np.array(numeros)
            self.input_datos.setStyleSheet("") # Limpiar error si lo había
            self.calcular_estadisticas()
            self.input_datos.clear()
        except ValueError:
            self.input_datos.setStyleSheet("border: 2px solid #ef4444; background-color: #fee;")

def main():
    app = QApplication(sys.argv)
    ventana = VentanaEstadisticas()
    ventana.show()
    sys.exit(app.exec())
    
if __name__ == '__main__':
    main()