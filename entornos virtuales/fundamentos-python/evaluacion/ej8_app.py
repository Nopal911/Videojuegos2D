import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

class SeguimientoProyectos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Proyectos de Software - Agile Tracker")
        self.resize(1200, 900)
        
        self.df = None

        # --- ESTRUCTURA DE PESTAÑAS ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_kanban = QWidget()
        self.tab_proyectos = QWidget()
        self.tab_desarrolladores = QWidget()

        self.tabs.addTab(self.tab_kanban, "📋 Kanban / Tareas")
        self.tabs.addTab(self.tab_proyectos, "🏗️ Análisis de Proyectos")
        self.tabs.addTab(self.tab_desarrolladores, "💻 Staff / Velocidad")

        self.configurar_tab_kanban()
        self.configurar_tab_proyectos()
        self.configurar_tab_desarrolladores()

    def configurar_tab_kanban(self):
        layout = QVBoxLayout(self.tab_kanban)
        self.btn_cargar = QPushButton("📁 Cargar Proyectos (CSV)")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_cargar.setStyleSheet("background-color: #2c3e50; color: white; height: 35px; font-weight: bold;")
        layout.addWidget(self.btn_cargar)

        self.tabla = QTableWidget()
        self.estilizar_tabla(self.tabla)
        layout.addWidget(self.tabla)

    def configurar_tab_proyectos(self):
        layout = QVBoxLayout(self.tab_proyectos)
        layout.addWidget(QLabel("Seleccionar Proyecto:"))
        self.combo_proyectos = QComboBox()
        self.combo_proyectos.currentIndexChanged.connect(self.analizar_proyecto)
        layout.addWidget(self.combo_proyectos)

        self.lbl_stats_proy = QLabel("Estadísticas del proyecto...")
        # Estilo corregido: texto oscuro (#2d3436) sobre fondo claro
        self.lbl_stats_proy.setStyleSheet("background-color: #f5f6fa; padding: 15px; border: 1px solid #dcdde1; font-size: 14px; color: #2d3436;")
        layout.addWidget(self.lbl_stats_proy)

        btn_graficas = QPushButton("📊 Ver Gráficas de Control")
        btn_graficas.clicked.connect(self.mostrar_graficas_control)
        layout.addWidget(btn_graficas)

    def configurar_tab_desarrolladores(self):
        layout = QVBoxLayout(self.tab_desarrolladores)
        layout.addWidget(QLabel("Seleccionar Desarrollador:"))
        self.combo_devs = QComboBox()
        self.combo_devs.currentIndexChanged.connect(self.analizar_desarrollador)
        layout.addWidget(self.combo_devs)

        self.lbl_stats_dev = QLabel("Métricas de rendimiento individual...")
        # Estilo corregido: texto oscuro para visibilidad
        self.lbl_stats_dev.setStyleSheet("background-color: #fdfdfd; padding: 15px; border: 1px solid #dcdde1; color: #2d3436;")
        layout.addWidget(self.lbl_stats_dev)

        btn_agile = QPushButton("🚀 Ver Dashboard de Velocidad y Métricas Ágiles")
        btn_agile.clicked.connect(self.mostrar_dashboard_agile)
        layout.addWidget(btn_agile)

    def estilizar_tabla(self, tabla):
        tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #34495e; color: #ecf0f1; font-weight: bold; }")
        tabla.setAlternatingRowColors(True)
        # Aseguramos que el color base del texto sea oscuro
        tabla.setStyleSheet("alternate-background-color: #f8f9fa; color: #2d3436;")
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Proyectos", "", "CSV Files (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        try:
            self.df = pd.read_csv(ruta)
            # Manejo de fecha para evitar errores si el CSV no tiene el formato exacto
            self.df['Fecha'] = pd.to_datetime(self.df['Fecha'])
            
            self.combo_proyectos.clear()
            self.combo_proyectos.addItems(sorted(self.df['Proyecto'].unique()))
            self.combo_devs.clear()
            self.combo_devs.addItems(sorted(self.df['Asignado_A'].unique()))

            self.llenar_tabla_kanban()
            QMessageBox.information(self, "Éxito", "Datos de software cargados correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {e}")

    def llenar_tabla_kanban(self):
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            prioridad = self.df.iloc[i]['Prioridad']
            for j in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[i, j]))
                
                # REQUISITO: Colores por prioridad con contraste de texto corregido
                if prioridad == 'Baja':
                    item.setBackground(QColor("#2ecc71")) # Verde
                    item.setForeground(QColor("white"))
                elif prioridad == 'Media':
                    item.setBackground(QColor("#f1c40f")) # Amarillo
                    item.setForeground(QColor("black"))   # Texto negro para amarillo
                elif prioridad == 'Alta':
                    item.setBackground(QColor("#e67e22")) # Naranja
                    item.setForeground(QColor("white"))
                elif prioridad == 'Crítica':
                    item.setBackground(QColor("#e74c3c")) # Rojo
                    item.setForeground(QColor("white"))
                else:
                    item.setForeground(QColor("#2d3436")) # Por defecto oscuro
                
                self.tabla.setItem(i, j, item)

    def analizar_proyecto(self):
        if self.df is None or self.combo_proyectos.currentText() == "": return
        proy = self.combo_proyectos.currentText()
        d = self.df[self.df['Proyecto'] == proy]
        
        total = len(d)
        completas = len(d[d['Estado'] == 'Completada'])
        progreso = len(d[d['Estado'] == 'En Progreso'])
        pct = (completas / total) * 100 if total > 0 else 0
        h_est = d['Horas_Estimadas'].sum()
        h_reales = d['Horas_Reales'].sum()
        dif = h_reales - h_est 

        status_dif = "SUBESTIMADO ⚠️" if dif > 0 else "SOBREESTIMADO ✅"

        texto = (f"🏗️ PROYECTO: {proy}\n"
                 f"----------------------------------------\n"
                 f"• Tareas: {total} | Completadas: {completas} ({pct:.1f}%)\n"
                 f"• En Progreso: {progreso}\n"
                 f"• Horas Estimadas: {h_est} | Reales: {h_reales}\n"
                 f"• Diferencia: {abs(dif)} hrs -> {status_dif}")
        self.lbl_stats_proy.setText(texto)

    def analizar_desarrollador(self):
        if self.df is None or self.combo_devs.currentText() == "": return
        dev = self.combo_devs.currentText()
        d = self.df[self.df['Asignado_A'] == dev]
        
        completas = len(d[d['Estado'] == 'Completada'])
        total = len(d)
        pct = (completas / total) * 100 if total > 0 else 0
        precision = (1 - (abs(d['Horas_Reales'] - d['Horas_Estimadas']).sum() / d['Horas_Estimadas'].sum())) * 100

        self.lbl_stats_dev.setText(f"💻 DESARROLLADOR: {dev}\n"
                                   f"----------------------------------------\n"
                                   f"• Tareas Asignadas: {total} | Tasa Completitud: {pct:.1f}%\n"
                                   f"• Promedio horas/tarea: {d['Horas_Reales'].mean():.1f} hrs\n"
                                   f"• Precisión de Estimación: {precision:.1f}%")

    def mostrar_graficas_control(self):
        if self.df is None: return
        plt.figure("Control de Proyectos", figsize=(14, 6))

        plt.subplot(1, 3, 1)
        self.df['Estado'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#bdc3c7', '#3498db', '#f1c40f', '#2ecc71'])
        plt.title("Estado de Tareas")

        plt.subplot(1, 3, 2)
        self.df.groupby('Asignado_A').size().plot(kind='bar', color='#16a085')
        plt.title("Carga de Trabajo")
        plt.xticks(rotation=45)

        plt.subplot(1, 3, 3)
        plt.scatter(self.df['Horas_Estimadas'], self.df['Horas_Reales'], alpha=0.5, color='purple')
        lims = [0, self.df['Horas_Reales'].max()]
        plt.plot(lims, lims, 'k--', alpha=0.7)
        plt.title("Estimado vs Real")
        plt.xlabel("Estimadas")
        plt.ylabel("Reales")

        plt.tight_layout()
        plt.show()

    def mostrar_dashboard_agile(self):
        if self.df is None: return
        df_comp = self.df[self.df['Estado'] == 'Completada'].copy()
        if df_comp.empty:
            QMessageBox.warning(self, "Aviso", "No hay tareas completadas para calcular velocidad.")
            return

        df_comp['Semana'] = df_comp['Fecha'].dt.isocalendar().week
        velocidad = df_comp.groupby('Semana').size()

        plt.figure("Dashboard de Velocidad", figsize=(10, 5))
        velocidad.plot(kind='line', marker='D', color='#e74c3c', linewidth=2)
        plt.title("Velocidad del Equipo (Tareas Completadas por Semana)")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Estilo Fusion para una apariencia más moderna y consistente
    app.setStyle("Fusion") 
    ventana = SeguimientoProyectos()
    ventana.show()
    sys.exit(app.exec())