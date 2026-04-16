import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class MonitorIndustrial(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Producción Industrial - Dashboard v1.0")
        self.resize(1200, 900)
        
        # Variable para guardar los datos de la planta
        self.df = None

        # --- SISTEMA DE PESTAÑAS ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Creamos los contenedores para cada sección
        self.tab_produccion = QWidget()
        self.tab_lineas = QWidget()
        self.tab_calidad_turnos = QWidget()

        self.tabs.addTab(self.tab_produccion, "🏭 Producción Diaria")
        self.tabs.addTab(self.tab_lineas, "📉 Análisis por Línea")
        self.tabs.addTab(self.tab_calidad_turnos, "🏆 Calidad y Turnos")

        # Configurar el contenido de cada pestaña
        self.configurar_tab_produccion()
        self.configurar_tab_lineas()
        self.configurar_tab_calidad_turnos()

    def configurar_tab_produccion(self):
        """Diseño de la pestaña principal: Carga y Tabla"""
        layout = QVBoxLayout(self.tab_produccion)

        # Botón para cargar CSV
        self.btn_cargar = QPushButton("📁 Cargar Datos de Producción")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        # Estilo oscuro con letras gris claro (no blancas)
        self.btn_cargar.setStyleSheet("background-color: #34495e; color: #ecf0f1; height: 40px; font-weight: bold;")
        layout.addWidget(self.btn_cargar)

        # Tabla de registros industriales
        self.tabla = QTableWidget()
        self.estilizar_tabla(self.tabla)
        layout.addWidget(self.tabla)

    def configurar_tab_lineas(self):
        """Diseño para analizar líneas de producción específicas"""
        layout = QVBoxLayout(self.tab_lineas)

        # Selector de Línea (L1, L2, etc.)
        layout.addWidget(QLabel("Seleccionar Línea de Producción:"))
        self.combo_linea = QComboBox()
        self.combo_linea.currentIndexChanged.connect(self.analizar_linea)
        layout.addWidget(self.combo_linea)

        # Panel de métricas (Eficiencia, Paros, etc.)
        self.lbl_stats_linea = QLabel("Estadísticas de línea...")
        self.lbl_stats_linea.setStyleSheet("background-color: #f5f6fa; padding: 20px; border: 1px solid #dcdde1; color: #2d3436;")
        layout.addWidget(self.lbl_stats_linea)

        # Botón para ver gráficas
        self.btn_graficas = QPushButton("📊 Generar Reporte Visual de Producción")
        self.btn_graficas.clicked.connect(self.mostrar_graficas)
        layout.addWidget(self.btn_graficas)

    def configurar_tab_calidad_turnos(self):
        """Diseño para análisis de defectos y comparación de turnos"""
        layout = QVBoxLayout(self.tab_calidad_turnos)

        # Sección Calidad
        layout.addWidget(QLabel("--- ANÁLISIS DE CALIDAD Y OEE ---"))
        self.lbl_calidad = QLabel("Datos de calidad aparecerán aquí.")
        self.lbl_calidad.setStyleSheet("background-color: #fdfdfd; padding: 15px; border: 1px solid #dcdde1; color: #2d3436;")
        layout.addWidget(self.lbl_calidad)

        # Sección Turnos
        layout.addWidget(QLabel("\n--- COMPARACIÓN POR TURNO ---"))
        self.combo_turno = QComboBox()
        self.combo_turno.currentIndexChanged.connect(self.analizar_turno)
        layout.addWidget(self.combo_turno)
        
        self.lbl_stats_turno = QLabel("Métricas del turno...")
        self.lbl_stats_turno.setStyleSheet("background-color: #f5f6fa; padding: 15px; border: 1px solid #dcdde1; color: #2d3436;")
        layout.addWidget(self.lbl_stats_turno)

    def estilizar_tabla(self, tabla):
        """Estilo visual: Fondo grisáceo y texto oscuro para legibilidad"""
        # Encabezado: Gris azulado con texto gris plata
        tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #2c3e50; color: #bdc3c7; font-weight: bold; }")
        tabla.setAlternatingRowColors(True)
        # Texto general en gris oscuro casi negro
        tabla.setStyleSheet("alternate-background-color: #f2f2f2; color: #2d3436;")
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        """Abre el buscador de archivos del sistema"""
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Producción", "", "CSV Files (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        """Carga el CSV y realiza los cálculos industriales automáticos"""
        try:
            temp_df = pd.read_csv(ruta)
            
            # 1. CÁLCULOS REQUERIDOS
            # Tasa de defectos (%)
            temp_df['Tasa_Defectos_%'] = (temp_df['Unidades_Defectuosas'] / temp_df['Unidades_Producidas'] * 100).round(2)
            
            # Eficiencia (%) -> Basado en 8h (480 min)
            # Fórmula: (Tiempo disponible - Tiempo paro) / Tiempo disponible * 100
            temp_df['Eficiencia_%'] = ((480 - temp_df['Tiempo_Paro']) / 480 * 100).round(2)

            self.df = temp_df
            self.df['Fecha'] = pd.to_datetime(self.df['Fecha'])

            # Actualizar Selectores
            self.combo_linea.clear()
            self.combo_linea.addItems(sorted(self.df['Línea'].unique()))
            
            self.combo_turno.clear()
            self.combo_turno.addItems(['Mañana', 'Tarde', 'Noche'])

            self.llenar_tabla_principal()
            self.analizar_calidad_global()
            QMessageBox.information(self, "Éxito", "Datos industriales procesados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar: {str(e)}")

    def llenar_tabla_principal(self):
        """Pasa los datos a la tabla y aplica COLORES por Eficiencia"""
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            eficiencia = self.df.iloc[i]['Eficiencia_%']
            for j in range(len(self.df.columns)):
                valor = self.df.iloc[i, j]
                # Si el valor es una fecha, la formateamos
                if isinstance(valor, pd.Timestamp):
                    valor = valor.strftime('%d/%m/%Y')
                
                item = QTableWidgetItem(str(valor))
                
                # REQUISITO: Colorear según eficiencia
                if eficiencia > 90:
                    item.setBackground(QColor("#27ae60")) # Verde
                    item.setForeground(QColor("#000000")) # Texto negro para contraste
                elif 70 <= eficiencia <= 90:
                    item.setBackground(QColor("#f1c40f")) # Amarillo
                    item.setForeground(QColor("#000000"))
                else:
                    item.setBackground(QColor("#e74c3c")) # Rojo
                    item.setForeground(QColor("#000000")) # Texto negro (No blanco)
                
                self.tabla.setItem(i, j, item)

    def analizar_linea(self):
        """Métricas específicas de la línea seleccionada"""
        if self.df is None: return
        lin = self.combo_linea.currentText()
        d = self.df[self.df['Línea'] == lin]
        
        # Cálculos de la línea
        prod_total = d['Unidades_Producidas'].sum()
        def_total = d['Unidades_Defectuosas'].sum()
        paro_total = d['Tiempo_Paro'].sum()
        eficiencia_avg = d['Eficiencia_%'].mean()
        
        # Identificar mejor turno (el que tuvo más producción acumulada)
        mejor_turno = d.groupby('Turno')['Unidades_Producidas'].sum().idxmax()

        resumen = (f"📍 LÍNEA SELECCIONADA: {lin}\n"
                   f"----------------------------------------\n"
                   f"• Producción Total: {prod_total:,} unidades\n"
                   f"• Unidades Defectuosas: {def_total:,} ({ (def_total/prod_total*100):.2f}%)\n"
                   f"• Tiempo de Paro Acumulado: {paro_total} minutos\n"
                   f"• Eficiencia Promedio: {eficiencia_avg:.1f}%\n"
                   f"• Turno más productivo: {mejor_turno}")
        self.lbl_stats_linea.setText(resumen)

    def analizar_calidad_global(self):
        """Identifica problemas de calidad y calcula el OEE"""
        if self.df is None: return
        
        # Líneas críticas (> 5% defectos)
        def_por_lin = self.df.groupby('Línea')['Tasa_Defectos_%'].mean()
        criticas = def_por_lin[def_por_lin > 5].index.tolist()
        
        # Cálculo OEE simplificado (Disponibilidad * Calidad)
        disponibilidad = (480 - self.df['Tiempo_Paro'].mean()) / 480
        calidad = (self.df['Unidades_Producidas'].sum() - self.df['Unidades_Defectuosas'].sum()) / self.df['Unidades_Producidas'].sum()
        oee = (disponibilidad * calidad) * 100

        texto = (f"⚠️ LÍNEAS CON DEFECTOS > 5%: {', '.join(criticas) if criticas else 'Ninguna'}\n"
                 f"⚙️ OEE ESTIMADO DE PLANTA: {oee:.1f}%\n"
                 f"📅 TOP 3 DÍAS CON MÁS DEFECTOS:\n")
        
        top_dias = self.df.groupby('Fecha')['Unidades_Defectuosas'].sum().sort_values(ascending=False).head(3)
        for fecha, cantidad in top_dias.items():
            texto += f"   - {fecha.strftime('%d/%m/%Y')}: {cantidad} unidades\n"
            
        self.lbl_calidad.setText(texto)

    def analizar_turno(self):
        """Estadísticas comparativas del turno"""
        if self.df is None: return
        turno = self.combo_turno.currentText()
        d = self.df[self.df['Turno'] == turno]
        
        op_top = d.groupby('Operador')['Unidades_Producidas'].sum().idxmax()
        prod_avg = d.groupby('Línea')['Unidades_Producidas'].mean().mean()

        self.lbl_stats_turno.setText(f"🕒 TURNO: {turno}\n"
                                     f"• Producción Promedio por Línea: {prod_avg:.1f}\n"
                                     f"• Operador con Mayor Producción: {op_top}\n"
                                     f"• Tiempo de Paro Promedio: {d['Tiempo_Paro'].mean():.1f} min")

    def mostrar_graficas(self):
        """Genera las 3 visualizaciones industriales"""
        if self.df is None: return
        plt.figure("Dashboard de Producción", figsize=(14, 7))

        # 1. Barras: Producción por línea
        plt.subplot(1, 3, 1)
        self.df.groupby('Línea')['Unidades_Producidas'].sum().plot(kind='bar', color='#2980b9')
        plt.title("Producción Total por Línea")
        plt.ylabel("Unidades")

        # 2. Línea: Evolución Tasa de Defectos
        plt.subplot(1, 3, 2)
        self.df.groupby('Fecha')['Tasa_Defectos_%'].mean().plot(kind='line', color='#c0392b', marker='o')
        plt.title("Evolución Tasa de Defectos")
        plt.grid(True, alpha=0.3)

        # 3. Barras Agrupadas: Producción por Turno y Línea
        plt.subplot(1, 3, 3)
        # unstack() nos permite separar el grupo en columnas para la gráfica
        self.df.groupby(['Turno', 'Línea'])['Unidades_Producidas'].sum().unstack().plot(kind='bar', ax=plt.gca())
        plt.title("Producción por Turno y Línea")
        
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MonitorIndustrial()
    ventana.show()
    sys.exit(app.exec())