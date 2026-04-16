import sys
import pandas as pd
import matplotlib.pyplot as plt
# Importamos los componentes necesarios de PyQt6 para crear la ventana y los controles
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
    QComboBox, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QColor

# Definimos la clase principal que heredará de QMainWindow (la ventana de la app)
class AnalizadorVentas(QMainWindow):
    def __init__(self):
        super().__init__()
        # Configuramos el título y el tamaño inicial de la ventana
        self.setWindowTitle("Analizador de Ventas por Región - Ejercicio 1")
        self.resize(1100, 800)

        # Esta variable empezará vacía y guardará nuestros datos de Pandas después
        self.df = None

        # --- CONFIGURACIÓN DE LA INTERFAZ (UI) ---
        
        # Necesitamos un "Widget Central" que contenga todo lo demás
        self.widget_central = QWidget()
        self.setCentralWidget(self.widget_central)
        
        # Usamos un Layout Vertical (un elemento debajo de otro)
        self.layout_principal = QVBoxLayout(self.widget_central)

        # 1. BOTÓN DE CARGA
        self.btn_cargar = QPushButton("1. Cargar Datos (ventas_regiones.csv)")
        # Conectamos el clic del botón con la función 'cargar_datos'
        self.btn_cargar.clicked.connect(self.cargar_datos)
        self.layout_principal.addWidget(self.btn_cargar)

        # 2. TABLA DE DATOS (QTableWidget)
        self.tabla = QTableWidget()
        self.estilizar_tabla() # Llamamos a la función que pone colores
        self.layout_principal.addWidget(self.tabla)

        # 3. FILTRO POR REGIÓN
        # Añadimos un texto de instrucción
        self.layout_principal.addWidget(QLabel("Selecciona una Región para analizar:"))
        self.combo_region = QComboBox()
        # Cuando el usuario cambie la opción del combo, se ejecuta 'actualizar_analisis_region'
        self.combo_region.currentIndexChanged.connect(self.actualizar_analisis_region)
        self.layout_principal.addWidget(self.combo_region)

        # 4. PANEL DE ESTADÍSTICAS (Etiqueta de texto)
        self.lbl_stats = QLabel("Estadísticas: (Carga un archivo para ver resultados)")
        # Le damos un poco de estilo al texto para que resalte
        self.lbl_stats.setStyleSheet("font-weight: bold; color: blue; font-size: 14px;")
        self.layout_principal.addWidget(self.lbl_stats)

        # 5. BOTONES DE ACCIÓN (Gráficas y Reporte)
        layout_botones = QHBoxLayout() # Estos irán uno al lado del otro
        
        self.btn_graficar = QPushButton("📊 Generar Gráficas")
        self.btn_graficar.clicked.connect(self.mostrar_graficas)
        
        self.btn_exportar = QPushButton("📄 Exportar Reporte TXT")
        self.btn_exportar.clicked.connect(self.exportar_reporte)
        
        layout_botones.addWidget(self.btn_graficar)
        layout_botones.addWidget(self.btn_exportar)
        
        # Agregamos el grupo de botones al layout principal
        self.layout_principal.addLayout(layout_botones)

    def estilizar_tabla(self):
        """Aplica los requisitos visuales: encabezado azul y filas alternadas"""
        # Accedemos al encabezado horizontal para pintarlo de azul con letras blancas
        estilo_header = "QHeaderView::section { background-color: #3498db; color: white; font-weight: bold; }"
        self.tabla.horizontalHeader().setStyleSheet(estilo_header)
        
        # Activamos el color de filas alternas (gris/blanco)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("alternate-background-color: #f2f2f2; background-color: white;")
        
        # Hacemos que las columnas se expandan para ocupar todo el ancho disponible
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def cargar_datos(self):
        """Lee el archivo CSV, valida y llena la tabla"""
        try:
            # Leemos el archivo usando Pandas
            self.df = pd.read_csv('ventas_regiones.csv')
            
            # VALIDACIÓN: Lista de columnas que DEBEN estar en el archivo
            columnas_requeridas = ['Región', 'Fecha', 'Producto', 'Ventas', 'Unidades']
            
            # Verificamos si todas las requeridas están en las columnas del DataFrame
            if not all(col in self.df.columns for col in columnas_requeridas):
                QMessageBox.critical(self, "Error de Columnas", "Faltan columnas obligatorias en el CSV.")
                return

            # Si pasa la validación, llenamos la tabla visual
            self.rellenar_tabla_visual()
            
            # Actualizamos el ComboBox con las regiones únicas encontradas en el archivo
            self.combo_region.clear()
            regiones_unicas = self.df['Región'].unique() # Obtiene lista sin repetir
            self.combo_region.addItems(regiones_unicas)
            
            QMessageBox.information(self, "Carga Exitosa", f"Se cargaron {len(self.df)} registros.")

        except FileNotFoundError:
            QMessageBox.warning(self, "Archivo no encontrado", "Asegúrate de ejecutar el generador de CSV primero.")

    def rellenar_tabla_visual(self):
        """Copia los datos del DataFrame (memoria) a la QTableWidget (pantalla)"""
        # Configuramos cuántas filas y columnas tendrá la tabla
        self.tabla.setRowCount(len(self.df))
        self.tabla.setColumnCount(len(self.df.columns))
        
        # Ponemos los nombres de las columnas arriba
        self.tabla.setHorizontalHeaderLabels(self.df.columns)

        # Recorremos fila por fila (i) y columna por columna (j)
        for i in range(len(self.df)):
            for j in range(len(self.df.columns)):
                # Extraemos el valor de la celda usando .iloc de Pandas
                valor = str(self.df.iloc[i, j])
                # Creamos el objeto celda y lo ponemos en la tabla
                self.tabla.setItem(i, j, QTableWidgetItem(valor))

    def actualizar_analisis_region(self):
        """Cálculos dinámicos cuando el usuario elige una región"""
        if self.df is None: return # Si no hay datos, no hace nada

        # 1. Obtener la región seleccionada del ComboBox
        region_elegida = self.combo_region.currentText()
        
        # 2. Filtrar el DataFrame: "Dame solo las filas donde Región sea igual a la elegida"
        datos_filtrados = self.df[self.df['Región'] == region_elegida]

        # 3. Cálculos matemáticos simples con Pandas
        total_ventas = datos_filtrados['Ventas'].sum()
        total_transacciones = len(datos_filtrados) # Cuenta cuántas filas hay
        total_unidades = datos_filtrados['Unidades'].sum()
        
        # Calculamos ticket promedio evitando división por cero
        ticket_promedio = total_ventas / total_unidades if total_unidades > 0 else 0

        # 4. Mostrar resultados en la etiqueta (Label)
        mensaje = (f"ANÁLISIS DE {region_elegida.upper()}:\n"
                   f"• Ventas Totales: ${total_ventas:,}\n"
                   f"• Transacciones: {total_transacciones}\n"
                   f"• Ticket Promedio: ${ticket_promedio:.2f}")
        self.lbl_stats.setText(mensaje)

    def mostrar_graficas(self):
        """Crea una ventana de Matplotlib con 3 gráficos distintos"""
        if self.df is None: 
            QMessageBox.warning(self, "Sin datos", "Carga el CSV primero.")
            return

        # Creamos el lienzo para dibujar (tamaño en pulgadas)
        plt.figure("Visualización de Datos", figsize=(10, 7))

        # GRÁFICA 1: Barras (Ventas por Región)
        plt.subplot(2, 2, 1) # Posición 1 de una cuadrícula 2x2
        # Agrupamos por región y sumamos sus ventas
        self.df.groupby('Región')['Ventas'].sum().plot(kind='bar', color='darkblue')
        plt.title('Ventas Totales por Región')
        plt.ylabel('Monto ($)')

        # GRÁFICA 2: Línea (Evolución en el tiempo)
        plt.subplot(2, 2, 2) # Posición 2
        df_temp = self.df.copy()
        # Convertimos la columna Fecha de texto a formato Fecha real para que se ordene bien
        df_temp['Fecha'] = pd.to_datetime(df_temp['Fecha'])
        # Agrupamos por fecha y sumamos ventas
        df_temp.groupby('Fecha')['Ventas'].sum().plot(kind='line', color='green')
        plt.title('Evolución de Ventas Diarias')

        # GRÁFICA 3: Pastel (Participación %)
        plt.subplot(2, 2, 3) # Posición 3
        # autopct='%1.1f%%' sirve para mostrar el porcentaje con un decimal
        self.df.groupby('Región')['Ventas'].sum().plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title('% Participación por Región')
        plt.ylabel('') # Quitamos la etiqueta lateral para que se vea mejor

        # Ajustamos el espacio entre gráficas para que no se amontonen los títulos
        plt.tight_layout()
        plt.show()

    def exportar_reporte(self):
        """Genera un resumen de texto y lo guarda en disco"""
        if self.df is None: return

        # Obtenemos estadísticas generales para el reporte
        ventas_totales = self.df['Ventas'].sum()
        ventas_regionales = self.df.groupby('Región')['Ventas'].sum()
        promedio_por_region = self.df.groupby('Región')['Ventas'].mean()
        
        # Identificamos la mejor y peor región comparando las sumas
        mejor_reg = ventas_regionales.idxmax()
        peor_reg = ventas_regionales.idxmin()

        try:
            # Creamos (o sobreescribimos) el archivo de texto
            with open('reporte_ventas.txt', 'w', encoding='utf-8') as archivo:
                archivo.write("========================================\n")
                archivo.write(f"      REPORTE DE VENTAS REGIONALES\n")
                archivo.write(f"      Generado el: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
                archivo.write("========================================\n\n")
                
                archivo.write("1. VENTAS POR REGIÓN:\n")
                archivo.write(ventas_regionales.to_string() + "\n\n")
                
                archivo.write("2. ESTADÍSTICAS GENERALES:\n")
                archivo.write(f"• Ventas Totales: ${ventas_totales:,}\n")
                archivo.write(f"• Región Líder: {mejor_reg}\n")
                archivo.write(f"• Región con menor desempeño: {peor_reg}\n")
                archivo.write(f"• Promedio de ventas por región: ${promedio_por_region.mean():.2f}\n")
                archivo.write(f"• Cantidad total de regiones: {len(ventas_regionales)}\n")

            QMessageBox.information(self, "Exportación", "El reporte 'reporte_ventas.txt' se generó con éxito.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el reporte: {str(e)}")

# --- BLOQUE DE INICIO ---
if __name__ == "__main__":
    # Creamos la aplicación
    app = QApplication(sys.argv)
    # Creamos nuestra ventana
    ventana = AnalizadorVentas()
    # La mostramos
    ventana.show()
    # Ejecutamos el bucle de la app
    sys.exit(app.exec())
    
    """
        Manejo de errores: Usé try...except por si el archivo no existe, así el programa no se cierra (no "truena") y te muestra un aviso.

Lógica de Pandas: Uso .groupby() para agrupar los datos. Es como una "Tabla Dinámica" de Excel pero en código.

Matplotlib Subplots: Permite que las 3 gráficas vivan en una sola ventana, lo cual es mucho más profesional.

Codificación UTF-8: Al exportar el reporte, puse encoding='utf-8' para que no tengas problemas con los acentos.
    """