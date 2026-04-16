import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class AnalizadorSatisfaccion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Análisis de Satisfacción (NPS) - v1.0")
        self.resize(1200, 900)
        
        # DataFrame para guardar las encuestas
        self.df = None

        # --- ESTRUCTURA DE PESTAÑAS ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Creamos las secciones principales
        self.tab_respuestas = QWidget()
        self.tab_servicio = QWidget()
        self.tab_aspectos = QWidget()

        self.tabs.addTab(self.tab_respuestas, "📋 Respuestas y NPS")
        self.tabs.addTab(self.tab_servicio, "📊 Análisis por Servicio")
        self.tabs.addTab(self.tab_aspectos, "🎯 Aspectos y Recomendaciones")

        # Configurar el diseño de cada pestaña
        self.configurar_tab_respuestas()
        self.configurar_tab_servicio()
        self.configurar_tab_aspectos()

    def configurar_tab_respuestas(self):
        """Diseño de la pestaña de carga de datos y tabla principal"""
        layout = QVBoxLayout(self.tab_respuestas)

        # Botón para buscar el archivo CSV
        self.btn_cargar = QPushButton("📁 Cargar Encuestas de Satisfacción")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        # Fondo gris azulado con letras gris claro (legible)
        self.btn_cargar.setStyleSheet("background-color: #34495e; color: #ecf0f1; height: 40px; font-weight: bold;")
        layout.addWidget(self.btn_cargar)

        # Panel de métricas generales arriba de la tabla
        self.lbl_nps_global = QLabel("Métricas Globales: Carga un archivo para comenzar.")
        self.lbl_nps_global.setStyleSheet("background-color: #f5f6fa; padding: 15px; border: 1px solid #dcdde1; color: #2d3436; font-size: 14px;")
        layout.addWidget(self.lbl_nps_global)

        # Tabla de encuestas
        self.tabla = QTableWidget()
        self.estilizar_tabla(self.tabla)
        layout.addWidget(self.tabla)

    def configurar_tab_servicio(self):
        """Diseño para filtrar por servicio y ver gráficas"""
        layout = QVBoxLayout(self.tab_servicio)

        # Selector de Servicio
        layout.addWidget(QLabel("Seleccionar Servicio para analizar detalle:"))
        self.combo_servicio = QComboBox()
        self.combo_servicio.currentIndexChanged.connect(self.analizar_servicio)
        layout.addWidget(self.combo_servicio)

        # Métricas del servicio
        self.lbl_stats_serv = QLabel("Estadísticas del servicio seleccionado...")
        self.lbl_stats_serv.setStyleSheet("background-color: #fdfdfd; padding: 20px; border: 1px solid #dcdde1; color: #2d3436;")
        layout.addWidget(self.lbl_stats_serv)

        # Botón para gráficas generales
        self.btn_graficas = QPushButton("📊 Generar Reporte Visual de NPS y Puntuación")
        self.btn_graficas.clicked.connect(self.mostrar_graficas_nps)
        layout.addWidget(self.btn_graficas)

    def configurar_tab_aspectos(self):
        """Diseño para análisis de Atención, Rapidez y Precio"""
        layout = QVBoxLayout(self.tab_aspectos)

        # Panel de fortalezas y debilidades
        self.lbl_recomendaciones = QLabel("Análisis de aspectos críticos...")
        self.lbl_recomendaciones.setStyleSheet("background-color: #f5f6fa; padding: 20px; border-left: 5px solid #2980b9; color: #2d3436; font-size: 14px;")
        layout.addWidget(self.lbl_recomendaciones)

        # Botón para análisis de correlación y radar
        self.btn_radar = QPushButton("🎯 Ver Comparativa de Aspectos (Gráfica de Radar)")
        self.btn_radar.clicked.connect(self.mostrar_grafica_aspectos)
        layout.addWidget(self.btn_radar)

    def estilizar_tabla(self, tabla):
        """Estilo visual para evitar el blanco brillante"""
        tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #2c3e50; color: #bdc3c7; font-weight: bold; }")
        tabla.setAlternatingRowColors(True)
        # Texto negro sobre fondo gris suave
        tabla.setStyleSheet("alternate-background-color: #f2f2f2; color: #000000;")
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        """Abre el explorador de archivos para elegir el CSV"""
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Encuestas", "", "CSV Files (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        """Carga el CSV y realiza la clasificación NPS"""
        try:
            temp_df = pd.read_csv(ruta)
            
            # REQUISITO: Clasificar cada respuesta en una categoría NPS
            def categorizar_nps(puntuacion):
                if puntuacion >= 9: return 'Promotor'
                elif puntuacion >= 7: return 'Pasivo'
                else: return 'Detractor'

            temp_df['Categoría_NPS'] = temp_df['Puntuación_General'].apply(categorizar_nps)
            temp_df['Fecha'] = pd.to_datetime(temp_df['Fecha'])
            
            self.df = temp_df

            # Actualizar selectores
            self.combo_servicio.clear()
            self.combo_servicio.addItems(sorted(self.df['Servicio'].unique()))

            self.llenar_tabla_principal()
            self.calcular_nps_global()
            self.generar_recomendaciones()
            
            QMessageBox.information(self, "Éxito", "Encuestas procesadas y NPS calculado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar: {str(e)}")

    def llenar_tabla_principal(self):
        """Llenar la tabla y aplicar colores por CATEGORÍA NPS"""
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            cat = self.df.iloc[i]['Categoría_NPS']
            for j in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[i, j]))
                
                # Colorear según categoría NPS (Promotores: Verde, Pasivos: Amarillo, Detractores: Rojo)
                if cat == 'Promotor': item.setBackground(QColor("#2ecc71"))
                elif cat == 'Pasivo': item.setBackground(QColor("#f1c40f"))
                else: item.setBackground(QColor("#e74c3c"))
                
                # Letras siempre negras para legibilidad
                item.setForeground(QColor("#000000"))
                self.tabla.setItem(i, j, item)

    def calcular_nps_global(self):
        """Calcula el NPS Score Global: (% Promotores - % Detractores)"""
        if self.df is None: return
        
        total = len(self.df)
        promotores = len(self.df[self.df['Categoría_NPS'] == 'Promotor'])
        detractores = len(self.df[self.df['Categoría_NPS'] == 'Detractor'])
        
        pct_prom = (promotores / total) * 100
        pct_det = (detractores / total) * 100
        nps_score = pct_prom - pct_det
        
        recomiendan = (len(self.df[self.df['Recomendaría'] == 'Sí']) / total) * 100

        self.lbl_nps_global.setText(
            f"GLOBAL: NPS Score: {nps_score:.1f} | Promedio Gral: {self.df['Puntuación_General'].mean():.1f}/10\n"
            f"Distribución: {pct_prom:.1f}% Promotores | {pct_det:.1f}% Detractores | Tasa Recomendación: {recomiendan:.1f}%"
        )

    def analizar_servicio(self):
        """Métricas específicas para el servicio seleccionado"""
        if self.df is None: return
        srv = self.combo_servicio.currentText()
        d = self.df[self.df['Servicio'] == srv]
        
        # NPS del servicio
        nps_srv = ((len(d[d['Categoría_NPS']=='Promotor']) - len(d[d['Categoría_NPS']=='Detractor'])) / len(d)) * 100
        
        # Aspectos promedio
        avg_atencion = d['Atención'].mean()
        avg_rapidez = d['Rapidez'].mean()
        avg_precio = d['Precio'].mean()
        
        # Identificar mejor y peor aspecto
        dict_aspectos = {'Atención': avg_atencion, 'Rapidez': avg_rapidez, 'Precio': avg_precio}
        mejor = max(dict_aspectos, key=dict_aspectos.get)
        peor = min(dict_aspectos, key=dict_aspectos.get)

        self.lbl_stats_serv.setText(
            f"📍 SERVICIO: {srv.upper()}\n"
            f"----------------------------------------\n"
            f"• NPS del Servicio: {nps_srv:.1f}\n"
            f"• Puntuación Promedio: {d['Puntuación_General'].mean():.1f}/10\n"
            f"• ⭐ Fortaleza: {mejor} ({dict_aspectos[mejor]:.2f})\n"
            f"• ⚠️ A mejorar: {peor} ({dict_aspectos[peor]:.2f})"
        )

    def generar_recomendaciones(self):
        """Genera sugerencias automáticas basadas en los puntajes más bajos"""
        if self.df is None: return
        
        # Promedio general de aspectos
        at = self.df['Atención'].mean()
        ra = self.df['Rapidez'].mean()
        pr = self.df['Precio'].mean()
        
        texto = "💡 RECOMENDACIONES ESTRATÉGICAS:\n"
        if at < 3.5: texto += "   - REFUERZO EN ATENCIÓN: Se detecta trato al cliente por debajo del estándar.\n"
        if ra < 3.5: texto += "   - OPTIMIZAR RAPIDEZ: El tiempo de respuesta está afectando la satisfacción.\n"
        if pr < 3.0: texto += "   - REVISAR PRECIOS: Los clientes perciben el costo como un punto negativo.\n"
        
        if at > 4.5 and ra > 4.5:
            texto += "   - EXCELENCIA OPERATIVA: Mantener el ritmo actual de servicio y rapidez."
            
        self.lbl_recomendaciones.setText(texto)

    def mostrar_graficas_nps(self):
        """Gráficas de Pastel, Barras e Histograma"""
        if self.df is None: return
        plt.figure("Reporte Visual de Satisfacción", figsize=(14, 7))

        # 1. Pastel: Distribución NPS
        plt.subplot(1, 3, 1)
        self.df['Categoría_NPS'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c', '#f1c40f'])
        plt.title("Distribución de Clientes (NPS)")

        # 2. Barras: Puntuación por Servicio
        plt.subplot(1, 3, 2)
        self.df.groupby('Servicio')['Puntuación_General'].mean().plot(kind='bar', color='#3498db')
        plt.title("Promedio por Servicio")
        plt.xticks(rotation=45)

        # 3. Histograma: Puntuaciones Generales
        plt.subplot(1, 3, 3)
        plt.hist(self.df['Puntuación_General'], bins=10, color='#9b59b6', edgecolor='black')
        plt.title("Frecuencia de Puntuaciones")
        plt.xlabel("Nota (1-10)")

        plt.tight_layout()
        plt.show()

    def mostrar_grafica_aspectos(self):
        """Compara los 3 aspectos clave en una gráfica de barras comparativa"""
        if self.df is None: return
        
        # Promedios generales de los aspectos 1-5
        medias = [self.df['Atención'].mean(), self.df['Rapidez'].mean(), self.df['Precio'].mean()]
        nombres = ['Atención', 'Rapidez', 'Precio']
        
        plt.figure("Comparativa de Atributos", figsize=(8, 5))
        plt.bar(nombres, medias, color=['#1abc9c', '#e67e22', '#34495e'])
        plt.ylim(0, 5) # La escala es de 1 a 5
        plt.title("Rendimiento por Atributo de Calidad")
        plt.ylabel("Puntuación Media (1-5)")
        
        # Añadimos una línea de "Meta" en 4.0
        plt.axhline(y=4.0, color='red', linestyle='--', label='Meta Ideal (4.0)')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AnalizadorSatisfaccion()
    ventana.show()
    sys.exit(app.exec())