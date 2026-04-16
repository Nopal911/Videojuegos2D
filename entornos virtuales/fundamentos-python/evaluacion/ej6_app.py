import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView)
from datetime import datetime

class AnalizadorTrafico(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador de Tráfico Web - Pro")
        self.resize(1200, 850)
        
        # Variable para guardar nuestro DataFrame
        self.df = None

        # --- DISEÑO DE LA INTERFAZ ---
        self.widget_principal = QWidget()
        self.setCentralWidget(self.widget_principal)
        self.layout_v = QVBoxLayout(self.widget_principal)

        # Botón para cargar el archivo
        self.btn_cargar = QPushButton("📂 Seleccionar Archivo 'trafico_web.csv'")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_cargar.setStyleSheet("background-color: #2c3e50; color: white; height: 40px; font-weight: bold;")
        self.layout_v.addWidget(self.btn_cargar)

        # Filtro por Página (ComboBox)
        layout_filtro = QHBoxLayout()
        self.combo_paginas = QComboBox()
        self.combo_paginas.currentIndexChanged.connect(self.actualizar_metricas_pagina)
        layout_filtro.addWidget(QLabel("Seleccionar Página para detalle:"))
        layout_filtro.addWidget(self.combo_paginas)
        self.layout_v.addLayout(layout_filtro)

        # Tabla de Datos
        self.tabla = QTableWidget()
        self.estilizar_tabla()
        self.layout_v.addWidget(self.tabla)

        # Panel de Indicadores de Rendimiento (KPIs)
        self.lbl_kpis = QLabel("Indicadores: Carga un archivo para ver el rendimiento global.")
        self.lbl_kpis.setStyleSheet("background-color: #f5f6fa; padding: 15px; border: 1px solid #dcdde1; color: #2f3640; font-family: monospace;")
        self.layout_v.addWidget(self.lbl_kpis)

        # Botones de Acción
        layout_acciones = QHBoxLayout()
        btn_graficas = QPushButton("📊 Ver Análisis Visual")
        btn_graficas.clicked.connect(self.mostrar_graficas)
        btn_exportar = QPushButton("💾 Exportar Reporte (TXT)")
        btn_exportar.clicked.connect(self.exportar_reporte)
        
        layout_acciones.addWidget(btn_graficas)
        layout_acciones.addWidget(btn_exportar)
        self.layout_v.addLayout(layout_acciones)

    def estilizar_tabla(self):
        self.tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #34495e; color: white; font-weight: bold; }")
        self.tabla.setAlternatingRowColors(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Tráfico Web", "", "CSV Files (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        try:
            self.df = pd.read_csv(ruta)
            
            # Verificación de columnas necesarias para evitar que la app se cierre
            columnas_esperadas = ['Fecha', 'Página', 'Visitantes', 'Tiempo_Promedio_Seg', 'Tasa_Rebote_Porcentaje']
            for col in columnas_esperadas:
                if col not in self.df.columns:
                    raise KeyError(f"No se encuentra la columna requerida: {col}")

            self.df['Fecha'] = pd.to_datetime(self.df['Fecha'])
            self.df = self.df.sort_values('Visitantes', ascending=False)

            self.combo_paginas.clear()
            self.combo_paginas.addItems(sorted(self.df['Página'].unique()))

            self.llenar_tabla_visual()
            self.actualizar_metricas_pagina() 
            QMessageBox.information(self, "Éxito", "Datos cargados correctamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error de Datos", f"Detalle: {str(e)}")

    def formatear_tiempo(self, segundos):
        minutos = int(segundos // 60)
        segs = int(segundos % 60)
        return f"{minutos:02d}:{segs:02d}"

    def llenar_tabla_visual(self):
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                valor = self.df.iloc[i, j]
                col_nombre = self.df.columns[j]
                
                if col_nombre == 'Tiempo_Promedio_Seg':
                    texto = self.formatear_tiempo(valor)
                elif col_nombre == 'Fecha':
                    texto = valor.strftime('%d/%m/%Y')
                elif col_nombre == 'Tasa_Rebote_Porcentaje':
                    texto = f"{valor}%"
                else:
                    texto = str(valor)
                
                self.tabla.setItem(i, j, QTableWidgetItem(texto))

    def actualizar_metricas_pagina(self):
        if self.df is None or self.combo_paginas.currentText() == "": return

        # KPIs Globales
        total_v = self.df['Visitantes'].sum()
        rebote_prom = self.df['Tasa_Rebote_Porcentaje'].mean()
        tiempo_sitio = self.df['Tiempo_Promedio_Seg'].mean()

        # Detalle por Página
        pag_sel = self.combo_paginas.currentText()
        df_pag = self.df[self.df['Página'] == pag_sel]
        visitantes_pag = df_pag['Visitantes'].sum()
        
        # Obtener fecha pico
        fecha_pico = df_pag.groupby('Fecha')['Visitantes'].sum().idxmax()

        resumen = (
            f"GLOBAL -> Total: {total_v:,} visitas | Rebote Promedio: {rebote_prom:.1f}% | Prom. Tiempo: {self.formatear_tiempo(tiempo_sitio)}\n"
            f"PÁGINA SELECCIONADA ({pag_sel}) -> Total: {visitantes_pag:,} visitas | Día de mayor tráfico: {fecha_pico.strftime('%d/%m/%Y')}"
        )
        self.lbl_kpis.setText(resumen)

    def mostrar_graficas(self):
        if self.df is None: return

        plt.figure("Análisis Visual de Tráfico", figsize=(12, 8))

        # 1. Evolución Temporal
        plt.subplot(2, 2, 1)
        self.df.groupby('Fecha')['Visitantes'].sum().plot(color='teal', marker='s')
        plt.title("Visitantes por Día")
        plt.grid(True, linestyle='--', alpha=0.6)

        # 2. Top 5 Páginas
        plt.subplot(2, 2, 2)
        self.df.groupby('Página')['Visitantes'].sum().sort_values().tail(5).plot(kind='barh', color='coral')
        plt.title("Top 5 Páginas más visitadas")

        # 3. Distribución de Tasa de Rebote
        plt.subplot(2, 1, 2)
        plt.hist(self.df['Tasa_Rebote_Porcentaje'], bins=15, color='skyblue', edgecolor='black')
        plt.axvline(self.df['Tasa_Rebote_Porcentaje'].mean(), color='red', linestyle='dashed', label='Promedio')
        plt.title("Distribución de la Tasa de Rebote")
        plt.legend()

        plt.tight_layout()
        plt.show()

    def exportar_reporte(self):
        if self.df is None: return
        try:
            with open("reporte_final_trafico.txt", "w", encoding='utf-8') as f:
                f.write("--- INFORME DE RENDIMIENTO WEB ---\n\n")
                f.write(f"Fecha del reporte: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"Total de registros analizados: {len(self.df)}\n")
                f.write(f"Visitantes totales: {self.df['Visitantes'].sum()}\n")
                f.write(f"Tasa de rebote promedio: {self.df['Tasa_Rebote_Porcentaje'].mean():.2f}%\n")
                f.write("\nRANKING DE PÁGINAS (VISITANTES):\n")
                f.write(self.df.groupby('Página')['Visitantes'].sum().sort_values(ascending=False).to_string())
            
            QMessageBox.information(self, "Guardado", "Se ha generado 'reporte_final_trafico.txt'")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Estilo visual moderno para la app
    app.setStyle("Fusion") 
    ventana = AnalizadorTrafico()
    ventana.show()
    sys.exit(app.exec())