import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QComboBox, QLabel, QLineEdit, QFileDialog, QMessageBox, QHeaderView)
from PyQt6.QtGui import QColor

class ControlInventario(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Control de Inventario")
        self.resize(1200, 800)
        
        # Guardaremos el DataFrame original aquí
        self.df = None

        # --- INTERFAZ ---
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        self.layout_principal = QVBoxLayout(self.widget_central)

        # SECCIÓN 1: CARGA DE ARCHIVO
        self.btn_cargar = QPushButton("📁 Cargar Inventario (Seleccionar archivo)")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_cargar.setStyleSheet("background-color: #2c3e50; color: white; height: 40px; font-weight: bold;")
        self.layout_principal.addWidget(self.btn_cargar)

        # SECCIÓN 2: FILTROS
        layout_filtros = QHBoxLayout()
        
        # Filtro por nombre
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por nombre...")
        self.input_buscar.textChanged.connect(self.aplicar_filtros) # Busca mientras escribes
        
        # Filtro por categoría
        self.combo_cat = QComboBox()
        self.combo_cat.currentIndexChanged.connect(self.aplicar_filtros)
        
        # Filtro por precio (Min - Max)
        self.input_min = QLineEdit()
        self.input_min.setPlaceholderText("Precio Min")
        self.input_min.textChanged.connect(self.aplicar_filtros)
        
        self.input_max = QLineEdit()
        self.input_max.setPlaceholderText("Precio Max")
        self.input_max.textChanged.connect(self.aplicar_filtros)

        layout_filtros.addWidget(QLabel("Nombre:"))
        layout_filtros.addWidget(self.input_buscar)
        layout_filtros.addWidget(QLabel("Categoría:"))
        layout_filtros.addWidget(self.combo_cat)
        layout_filtros.addWidget(QLabel("Precios:"))
        layout_filtros.addWidget(self.input_min)
        layout_filtros.addWidget(self.input_max)
        
        self.layout_principal.addLayout(layout_filtros)

        # SECCIÓN 3: TABLA
        self.tabla = QTableWidget()
        self.estilizar_tabla()
        self.layout_principal.addWidget(self.tabla)

        # SECCIÓN 4: PANEL DE ALERTAS (Texto)
        self.lbl_alertas = QLabel("Carga datos para ver el estado del inventario.")
        self.lbl_alertas.setStyleSheet("background-color: #f5f6fa; border: 1px solid #dcdde1; padding: 10px; color: #2f3640;")
        self.layout_principal.addWidget(self.lbl_alertas)

        # SECCIÓN 5: BOTONES DE ACCIÓN
        layout_acciones = QHBoxLayout()
        self.btn_graficas = QPushButton("📊 Ver Gráficas")
        self.btn_graficas.clicked.connect(self.mostrar_graficas)
        
        self.btn_orden = QPushButton("🛒 Generar Orden de Compra")
        self.btn_orden.clicked.connect(self.generar_orden)
        self.btn_orden.setStyleSheet("background-color: #27ae60; color: white;")

        layout_acciones.addWidget(self.btn_graficas)
        layout_acciones.addWidget(self.btn_orden)
        self.layout_principal.addLayout(layout_acciones)

    def estilizar_tabla(self):
        """Aplica colores oscuros y profesionales para evitar el blanco brillante"""
        self.tabla.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #2c3e50; color: #ecf0f1; font-weight: bold; }")
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("alternate-background-color: #f5f6fa; background-color: white; color: #2f3640;")
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        """Abre el explorador de archivos para elegir un CSV"""
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Inventario", "", "Archivos CSV (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        """Carga el CSV y valida el formato"""
        try:
            nuevo_df = pd.read_csv(ruta)
            columnas_ok = ['Código', 'Producto', 'Categoría', 'Stock', 'Precio', 'Proveedor']
            
            if not all(col in nuevo_df.columns for col in columnas_ok):
                QMessageBox.critical(self, "Error", "Formato de columnas inválido.")
                return

            self.df = nuevo_df
            # Llenar ComboBox de categorías
            self.combo_cat.clear()
            self.combo_cat.addItem("Todas")
            self.combo_cat.addItems(self.df['Categoría'].unique())
            
            self.aplicar_filtros()
            QMessageBox.information(self, "Éxito", "Inventario cargado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {str(e)}")

    def aplicar_filtros(self):
        """Filtra los datos por nombre, categoría y precio simultáneamente"""
        if self.df is None: return
        
        temp_df = self.df.copy()

        # Filtro por nombre
        texto = self.input_buscar.text().lower()
        temp_df = temp_df[temp_df['Producto'].str.lower().str.contains(texto)]

        # Filtro por categoría
        cat = self.combo_cat.currentText()
        if cat != "Todas":
            temp_df = temp_df[temp_df['Categoría'] == cat]

        # Filtro por precio
        try:
            p_min = float(self.input_min.text()) if self.input_min.text() else 0
            p_max = float(self.input_max.text()) if self.input_max.text() else 999999
            temp_df = temp_df[(temp_df['Precio'] >= p_min) & (temp_df['Precio'] <= p_max)]
        except ValueError:
            pass # Si el usuario escribe letras en el precio, lo ignoramos

        self.mostrar_en_tabla(temp_df)
        self.actualizar_panel_alertas(temp_df)

    def mostrar_en_tabla(self, datos):
        """Llena la tabla y aplica los colores condicionales por STOCK"""
        self.tabla.setRowCount(len(datos))
        self.tabla.setColumnCount(len(datos.columns))
        self.tabla.setHorizontalHeaderLabels(datos.columns)

        for i in range(len(datos)):
            stock = datos.iloc[i]['Stock']
            for j in range(len(datos.columns)):
                item = QTableWidgetItem(str(datos.iloc[i, j]))
                
                # REQUISITO: Colores condicionales según el Stock
                if stock < 10:
                    item.setBackground(QColor("#e74c3c")) # Rojo suave
                    item.setForeground(QColor("white"))
                elif 10 <= stock <= 20:
                    item.setBackground(QColor("#e67e22")) # Naranja suave
                    item.setForeground(QColor("white"))
                elif stock > 20:
                    item.setBackground(QColor("#2ecc71")) # Verde suave
                    item.setForeground(QColor("white"))
                
                self.tabla.setItem(i, j, item)

    def actualizar_panel_alertas(self, datos):
        """Calcula los datos del panel de estadísticas"""
        if datos.empty: return
        
        total_inv = (datos['Stock'] * datos['Precio']).sum()
        p_caro = datos.loc[datos['Precio'].idxmax(), 'Producto']
        m_stock = datos.loc[datos['Stock'].idxmax(), 'Producto']
        criticos = len(datos[datos['Stock'] < 10])

        texto = (f"🚨 PRODUCTOS CRÍTICOS: {criticos}\n"
                 f"💰 VALOR TOTAL INVENTARIO: ${total_inv:,.2f}\n"
                 f"💎 PRODUCTO MÁS CARO: {p_caro}\n"
                 f"📦 MAYOR EXISTENCIA: {m_stock}")
        self.lbl_alertas.setText(texto)

    def mostrar_graficas(self):
        """Genera las 3 visualizaciones requeridas"""
        if self.df is None: return
        plt.figure("Analítica de Almacén", figsize=(12, 5))

        # 1. Barras: Stock por categoría
        plt.subplot(1, 3, 1)
        self.df.groupby('Categoría')['Stock'].sum().plot(kind='bar', color='teal')
        plt.title("Stock por Categoría")

        # 2. Pastel: Valor de inventario (Stock * Precio)
        plt.subplot(1, 3, 2)
        df_valor = self.df.copy()
        df_valor['Valor'] = df_valor['Stock'] * df_valor['Precio']
        df_valor.groupby('Categoría')['Valor'].sum().plot(kind='pie', autopct='%1.1f%%')
        plt.title("Valor por Categoría")

        # 3. Histograma: Distribución de precios
        plt.subplot(1, 3, 3)
        plt.hist(self.df['Precio'], bins=15, color='orange', edgecolor='black')
        plt.title("Distribución de Precios")

        plt.tight_layout()
        plt.show()

    def generar_orden(self):
        """Crea un CSV con los productos que faltan (Stock < 50)"""
        if self.df is None: return
        
        # Filtramos los que necesitan reabastecimiento
        faltantes = self.df[self.df['Stock'] < 50].copy()
        # Cantidad sugerida = 50 - stock actual
        faltantes['Cantidad Sugerida'] = 50 - faltantes['Stock']
        
        reporte = faltantes[['Código', 'Producto', 'Stock', 'Cantidad Sugerida']]
        reporte.to_csv('orden_compra.csv', index=False)
        QMessageBox.information(self, "Orden Creada", f"Se generó 'orden_compra.csv' con {len(reporte)} productos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ControlInventario()
    ventana.show()
    sys.exit(app.exec())