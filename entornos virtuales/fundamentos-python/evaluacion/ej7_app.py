import sys
import pandas as pd
import matplotlib.pyplot as plt
# CORRECCIÓN: Importación directa de la clase datetime
from datetime import datetime 
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtGui import QColor

class ControlAsistencia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Control de Asistencia - Ejercicio 7")
        self.resize(1200, 900)
        self.df = None

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_asistencia = QWidget()
        self.tab_empleado = QWidget()
        self.tab_depto_reporte = QWidget()

        self.tabs.addTab(self.tab_asistencia, "📅 Registro Diario")
        self.tabs.addTab(self.tab_empleado, "👤 Perfil Empleado")
        self.tabs.addTab(self.tab_depto_reporte, "🏢 Deptos y Reportes")

        self.configurar_asistencia()
        self.configurar_perfil_empleado()
        self.configurar_deptos_reportes()

    def configurar_asistencia(self):
        layout = QVBoxLayout(self.tab_asistencia)
        self.btn_cargar = QPushButton("📂 Cargar Registros de Asistencia (CSV)")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_cargar.setStyleSheet("background-color: #2c3e50; color: white; height: 40px; font-weight: bold;")
        layout.addWidget(self.btn_cargar)
        self.tabla = QTableWidget()
        self.estilizar_tabla(self.tabla)
        layout.addWidget(self.tabla)

    def estilizar_tabla(self, tabla):
        tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #34495e; color: #ecf0f1; font-weight: bold; }")
        tabla.setAlternatingRowColors(True)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Asistencias", "", "CSV Files (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        try:
            temp_df = pd.read_csv(ruta)
            
            def calcular_horas(row):
                if row['Estado'] == 'Ausente' or row['Hora_Entrada'] == 'N/A':
                    return 0.0
                try:
                    fmt = '%H:%M'
                    # Aquí es donde fallaba antes si no importábamos 'from datetime import datetime'
                    t_ent = datetime.strptime(row['Hora_Entrada'], fmt)
                    t_sal = datetime.strptime(row['Hora_Salida'], fmt)
                    diferencia = t_sal - t_ent
                    return round(diferencia.total_seconds() / 3600, 2)
                except:
                    return 0.0

            temp_df['Horas_Trabajadas'] = temp_df.apply(calcular_horas, axis=1)
            temp_df['Fecha'] = pd.to_datetime(temp_df['Fecha'])
            self.df = temp_df

            # Actualizar componentes visuales
            self.combo_empleado.clear()
            self.combo_empleado.addItems(sorted(self.df['Empleado'].unique()))
            self.combo_depto.clear()
            self.combo_depto.addItems(sorted(self.df['Departamento'].unique()))
            self.df['Mes'] = self.df['Fecha'].dt.strftime('%Y-%m')
            self.combo_mes.clear()
            self.combo_mes.addItems(sorted(self.df['Mes'].unique(), reverse=True))

            self.llenar_tabla_principal()
            QMessageBox.information(self, "Éxito", "Datos cargados y procesados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Fallo al cargar CSV: {e}")

    def llenar_tabla_principal(self):
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        col_estado = list(self.df.columns).index('Estado')

        for i in range(len(self.df)):
            estado = self.df.iloc[i, col_estado]
            for j in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iloc[i, j]))
                
                # Colores por estado
                if estado == 'Presente': item.setBackground(QColor("#2ecc71"))
                elif estado == 'Tarde': item.setBackground(QColor("#f1c40f"))
                elif estado == 'Ausente': item.setBackground(QColor("#e74c3c"))
                elif estado == 'Permiso': item.setBackground(QColor("#3498db"))
                
                self.tabla.setItem(i, j, item)

    # --- MÉTODOS DE LAS OTRAS PESTAÑAS (Resumidos para brevedad) ---
    def configurar_perfil_empleado(self):
        layout = QVBoxLayout(self.tab_empleado)
        self.combo_empleado = QComboBox()
        self.combo_empleado.currentIndexChanged.connect(self.analizar_empleado)
        layout.addWidget(QLabel("Seleccionar Empleado:"))
        layout.addWidget(self.combo_empleado)
        self.lbl_stats_emp = QLabel("Cargue datos primero.")
        layout.addWidget(self.lbl_stats_emp)
        self.btn_graficas = QPushButton("📊 Ver Gráficas")
        self.btn_graficas.clicked.connect(self.mostrar_graficas)
        layout.addWidget(self.btn_graficas)

    def configurar_deptos_reportes(self):
        layout = QVBoxLayout(self.tab_depto_reporte)
        self.combo_depto = QComboBox()
        self.combo_depto.currentIndexChanged.connect(self.analizar_departamento)
        layout.addWidget(QLabel("Departamento:"))
        layout.addWidget(self.combo_depto)
        self.lbl_stats_depto = QLabel("Métricas...")
        layout.addWidget(self.lbl_stats_depto)
        self.combo_mes = QComboBox()
        layout.addWidget(QLabel("Mes del Reporte:"))
        layout.addWidget(self.combo_mes)
        btn = QPushButton("💾 Guardar Reporte TXT")
        btn.clicked.connect(self.generar_reporte_mensual)
        layout.addWidget(btn)

    def analizar_empleado(self):
        if self.df is None or self.combo_empleado.currentText() == "": return
        emp = self.combo_empleado.currentText()
        d = self.df[self.df['Empleado'] == emp]
        asist = (len(d[d['Estado'].isin(['Presente', 'Tarde'])]) / len(d)) * 100
        self.lbl_stats_emp.setText(f"👤 {emp}\nAsistencia: {asist:.1f}%\nPromedio Horas: {d['Horas_Trabajadas'].mean():.2f}")

    def analizar_departamento(self):
        if self.df is None or self.combo_depto.currentText() == "": return
        depto = self.combo_depto.currentText()
        d = self.df[self.df['Departamento'] == depto]
        asist = (len(d[d['Estado'].isin(['Presente', 'Tarde'])]) / len(d)) * 100
        self.lbl_stats_depto.setText(f"🏢 {depto}\nAsistencia Grupal: {asist:.1f}%")

    def mostrar_graficas(self):
        if self.df is None: return
        self.df['Estado'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title("Distribución de Asistencia")
        plt.show()

    def generar_reporte_mensual(self):
        if self.df is None: return
        mes = self.combo_mes.currentText()
        nombre = f"Reporte_{mes}.txt"
        with open(nombre, "w") as f:
            f.write(f"REPORTE ASISTENCIA {mes}\n")
            f.write(self.df[self.df['Mes'] == mes].groupby('Empleado')['Horas_Trabajadas'].sum().to_string())
        QMessageBox.information(self, "Reporte", f"Guardado como {nombre}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ControlAsistencia()
    ventana.show()
    sys.exit(app.exec())