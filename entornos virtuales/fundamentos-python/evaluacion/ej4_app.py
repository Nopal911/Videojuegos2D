import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView, 
                             QTabWidget, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class GestorGastos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Gastos Personales - Ejercicio 4")
        self.resize(1100, 850)
        
        # Variable para almacenar los gastos en memoria
        self.df = None

        # --- INTERFAZ PRINCIPAL ---
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Creamos las pestañas
        self.tab_lista = QWidget()
        self.tab_analisis = QWidget()
        self.tabs.addTab(self.tab_lista, "📑 Lista de Gastos")
        self.tabs.addTab(self.tab_analisis, "📊 Análisis y Presupuesto")

        self.configurar_tab_lista()
        self.configurar_tab_analisis()

    def configurar_tab_lista(self):
        """Pestaña para cargar archivos y ver la tabla de gastos"""
        layout = QVBoxLayout(self.tab_lista)

        # Botón de carga con estilo profesional
        self.btn_cargar = QPushButton("📁 Cargar Historial de Gastos (CSV)")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_cargar.setStyleSheet("background-color: #2c3e50; color: white; height: 40px; font-weight: bold;")
        layout.addWidget(self.btn_cargar)

        # Tabla de transacciones
        self.tabla = QTableWidget()
        self.estilizar_tabla(self.tabla)
        layout.addWidget(self.tabla)

    def configurar_tab_analisis(self):
        """Pestaña para ver gráficas, presupuestos y totales"""
        layout = QVBoxLayout(self.tab_analisis)

        # --- SECCIÓN DE PRESUPUESTO ---
        presu_layout = QHBoxLayout()
        presu_layout.addWidget(QLabel("Ingresa tu Presupuesto Mensual ($):"))
        self.input_presupuesto = QDoubleSpinBox()
        self.input_presupuesto.setRange(0, 1000000)
        self.input_presupuesto.setValue(15000) # Valor por defecto
        # Cada vez que cambie el número, recalculamos el indicador
        self.input_presupuesto.valueChanged.connect(self.actualizar_indicador_presupuesto)
        presu_layout.addWidget(self.input_presupuesto)
        layout.addLayout(presu_layout)

        # Indicador visual de presupuesto (Etiqueta de color)
        self.lbl_indicador = QLabel("Carga datos para analizar presupuesto")
        self.lbl_indicador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_indicador.setStyleSheet("padding: 10px; font-weight: bold; font-size: 15px; border-radius: 5px;")
        layout.addWidget(self.lbl_indicador)

        # --- SECCIÓN DE FILTRO TEMPORAL ---
        layout_mes = QHBoxLayout()
        self.combo_mes = QComboBox()
        self.combo_mes.currentIndexChanged.connect(self.actualizar_analisis_completo)
        layout_mes.addWidget(QLabel("Seleccionar Mes de Análisis:"))
        layout_mes.addWidget(self.combo_mes)
        layout.addLayout(layout_mes)

        # Resumen estadístico
        self.lbl_resumen = QLabel("Resumen de categoría y método de pago...")
        self.lbl_resumen.setStyleSheet("background-color: #f5f6fa; padding: 10px; border: 1px solid #dcdde1;")
        layout.addWidget(self.lbl_resumen)

        # Botón para gráficas
        self.btn_graficas = QPushButton("📊 Generar Reporte Visual")
        self.btn_graficas.clicked.connect(self.mostrar_graficas)
        layout.addWidget(self.btn_graficas)

    def estilizar_tabla(self, tabla):
        """Configuración visual para que las letras no cansen la vista"""
        tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #34495e; color: #ecf0f1; font-weight: bold; }")
        tabla.setAlternatingRowColors(True)
        tabla.setStyleSheet("alternate-background-color: #f8f9fa; color: #2d3436;")
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        """Abre el explorador de archivos"""
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir Gastos", "", "Archivos CSV (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        """Carga, valida y prepara los datos del CSV"""
        try:
            temp_df = pd.read_csv(ruta)
            
            # VALIDACIÓN: Montos positivos
            if (temp_df['Monto'] < 0).any():
                QMessageBox.warning(self, "Error", "Se detectaron montos negativos en el archivo.")
                return

            # Convertimos la columna Fecha a formato de fecha real de Python
            temp_df['Fecha'] = pd.to_datetime(temp_df['Fecha'])
            
            # Ordenamos por fecha (más recientes primero según requisito)
            self.df = temp_df.sort_values('Fecha', ascending=False)

            # Llenar el selector de meses basado en los datos cargados
            # Convertimos las fechas a formato "Año-Mes" (ej. 2024-01)
            self.df['Mes_Anio'] = self.df['Fecha'].dt.to_period('M').astype(str)
            meses_disponibles = sorted(self.df['Mes_Anio'].unique(), reverse=True)
            self.combo_mes.clear()
            self.combo_mes.addItems(meses_disponibles)

            self.llenar_tabla_visual()
            self.actualizar_analisis_completo()
            QMessageBox.information(self, "Éxito", "Gastos cargados correctamente.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar: {str(e)}")

    def llenar_tabla_visual(self):
        """Pone los datos en la tabla con formato de MONEDA"""
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns) - 1) # No mostramos la columna auxiliar 'Mes_Anio'
        self.tabla.setHorizontalHeaderLabels(['Fecha', 'Categoría', 'Descripción', 'Monto', 'Método Pago'])

        for i in range(len(self.df)):
            for j in range(5):
                valor = self.df.iloc[i, j]
                
                # Formatear la fecha para que se vea bonita
                if j == 0: 
                    texto = valor.strftime('%d/%m/%Y')
                # Formatear el monto como moneda: $1,234.56
                elif j == 3:
                    texto = f"${valor:,.2f}"
                else:
                    texto = str(valor)
                
                self.tabla.setItem(i, j, QTableWidgetItem(texto))

    def actualizar_analisis_completo(self):
        """Ejecuta toda la lógica de cálculo financiero"""
        if self.df is None: return
        self.actualizar_indicador_presupuesto()
        
        # Filtrar datos por el mes seleccionado en el combo
        mes_sel = self.combo_mes.currentText()
        df_mes = self.df[self.df['Mes_Anio'] == mes_sel]
        
        if df_mes.empty: return

        # Cálculo de método de pago más utilizado
        metodo_top = df_mes['Método_Pago'].value_counts().idxmax()
        metodo_count = df_mes['Método_Pago'].value_counts().max()
        porcentaje_uso = (metodo_count / len(df_mes)) * 100

        # Mostrar resumen en la etiqueta
        resumen = (f"MES: {mes_sel} | Método más usado: {metodo_top} ({porcentaje_uso:.1f}% de veces)\n"
                   f"Día de mayor gasto: {df_mes.groupby('Fecha')['Monto'].sum().idxmax().strftime('%d/%m/%Y')}\n"
                   f"Promedio de gasto diario: ${df_mes.groupby('Fecha')['Monto'].sum().mean():,.2f}")
        self.lbl_resumen.setText(resumen)

    def actualizar_indicador_presupuesto(self):
        """Lógica de colores Verde-Naranja-Rojo para el presupuesto"""
        if self.df is None: return
        
        # Filtramos el mes actual
        mes_sel = self.combo_mes.currentText()
        gasto_total = self.df[self.df['Mes_Anio'] == mes_sel]['Monto'].sum()
        presupuesto = self.input_presupuesto.value()
        
        porcentaje = (gasto_total / presupuesto) * 100 if presupuesto > 0 else 0
        restante = presupuesto - gasto_total

        # Cambiamos el color según el porcentaje de gasto
        if porcentaje < 70:
            color, estado = "#27ae60", "SALUDABLE (Bajo control)" # Verde
        elif 70 <= porcentaje <= 90:
            color, estado = "#e67e22", "ADVERTENCIA (Cerca del límite)" # Naranja
        else:
            color, estado = "#c0392b", "CRÍTICO (Presupuesto excedido)" # Rojo

        self.lbl_indicador.setText(f"Gasto: {porcentaje:.1f}% | {estado} | Disponible: ${restante:,.2f}")
        self.lbl_indicador.setStyleSheet(f"background-color: {color}; color: white; padding: 10px; border-radius: 5px;")

    def mostrar_graficas(self):
        """Genera el análisis visual por categoría, tiempo y método de pago"""
        if self.df is None: return
        
        mes_sel = self.combo_mes.currentText()
        df_mes = self.df[self.df['Mes_Anio'] == mes_sel]
        
        plt.figure("Análisis Financiero Mensual", figsize=(14, 8))

        # 1. Pastel: Gasto por categoría
        plt.subplot(2, 2, 1)
        df_mes.groupby('Categoría')['Monto'].sum().plot(kind='pie', autopct='%1.1f%%')
        plt.title("Distribución por Categoría")

        # 2. Línea: Evolución diaria del mes
        plt.subplot(2, 2, 2)
        # Agrupamos por día y sumamos
        df_mes.groupby('Fecha')['Monto'].sum().plot(kind='line', marker='s', color='blue')
        plt.title(f"Gastos Diarios - {mes_sel}")
        plt.grid(True, alpha=0.3)

        # 3. Barras: Total por método de pago
        plt.subplot(2, 2, 3)
        df_mes.groupby('Método_Pago')['Monto'].sum().plot(kind='bar', color=['#1abc9c', '#3498db', '#9b59b6'])
        plt.title("Gasto por Método de Pago")
        plt.xticks(rotation=0)

        plt.tight_layout()
        plt.show()

# --- ARRANQUE ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = GestorGastos()
    ventana.show()
    sys.exit(app.exec())