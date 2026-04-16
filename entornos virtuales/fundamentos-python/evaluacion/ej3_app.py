import sys
import pandas as pd
import matplotlib.pyplot as plt
# Importamos todas las piezas de la interfaz que vamos a armar
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
    QComboBox, QLabel, QFileDialog, QMessageBox, QHeaderView, QTabWidget
)
from PyQt6.QtGui import QColor

# Clase principal para el Analizador Académico
class AnalizadorAcademico(QMainWindow):
    def __init__(self):
        super().__init__()
        # Definimos el nombre y el tamaño de la ventana
        self.setWindowTitle("Sistema de Análisis de Rendimiento Académico - Ejercicio 3")
        self.resize(1200, 850)
        
        # Aquí guardaremos el DataFrame (la "tabla" de datos en memoria)
        self.df = None

        # --- ESTRUCTURA DE PESTAÑAS (TABS) ---
        # El QTabWidget permite tener varias "páginas" en una misma ventana
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Creamos dos contenedores (pestañas) vacíos
        self.tab_general = QWidget()
        self.tab_reporte = QWidget()
        
        # Los añadimos al control de pestañas con sus respectivos nombres
        self.tabs.addTab(self.tab_general, "📊 Vista General y Materias")
        self.tabs.addTab(self.tab_reporte, "👤 Reporte Individual por Alumno")

        # Llamamos a funciones separadas para organizar el diseño de cada pestaña
        self.configurar_tab_general()
        self.configurar_tab_reporte()

    def configurar_tab_general(self):
        """Diseña la primera pestaña: Carga de datos, Tabla total y Filtro de Materia"""
        layout = QVBoxLayout(self.tab_general)

        # 1. BOTÓN DE CARGA: Con estilo oscuro para que no brille tanto
        self.btn_cargar = QPushButton("📁 PASO 1: Cargar Calificaciones (CSV)")
        self.btn_cargar.clicked.connect(self.seleccionar_archivo)
        self.btn_cargar.setStyleSheet("background-color: #2c3e50; color: white; height: 40px; font-weight: bold;")
        layout.addWidget(self.btn_cargar)

        # 2. SELECTOR DE MATERIA: Layout horizontal para que el texto y el combo estén alineados
        layout_materia = QHBoxLayout()
        self.combo_materia = QComboBox()
        # Conectamos el cambio de materia con la actualización de las estadísticas inferiores
        self.combo_materia.currentIndexChanged.connect(self.actualizar_analisis_materia)
        layout_materia.addWidget(QLabel("Selecciona una Materia para analizar:"))
        layout_materia.addWidget(self.combo_materia)
        layout.addLayout(layout_materia)

        # 3. TABLA PRINCIPAL: Donde se verán todos los alumnos
        self.tabla = QTableWidget()
        self.estilizar_tabla(self.tabla)
        layout.addWidget(self.tabla)

        # 4. PANEL DE ESTADÍSTICAS: Una etiqueta que actúa como cuadro de texto informativo
        self.lbl_stats_materia = QLabel("Esperando carga de datos...")
        # Estilo con borde y fondo gris suave para legibilidad
        self.lbl_stats_materia.setStyleSheet("padding: 15px; background-color: #f5f6fa; color: #2f3640; border: 1px solid #dcdde1; font-size: 13px;")
        layout.addWidget(self.lbl_stats_materia)

        # 5. BOTONES DE ACCIÓN (Gráficas y Ranking)
        layout_btns = QHBoxLayout()
        btn_graficas = QPushButton("📈 Ver Gráficas Comparativas")
        btn_graficas.clicked.connect(self.mostrar_graficas_generales)
        
        btn_ranking = QPushButton("🏆 Ver Top 5 Mejores Alumnos")
        btn_ranking.clicked.connect(self.mostrar_ranking)
        
        layout_btns.addWidget(btn_graficas)
        layout_btns.addWidget(btn_ranking)
        layout.addLayout(layout_btns)

    def configurar_tab_reporte(self):
        """Diseña la segunda pestaña: Reporte específico por estudiante"""
        layout = QVBoxLayout(self.tab_reporte)
        
        # Selector de Estudiante
        layout.addWidget(QLabel("Selecciona un Estudiante para ver su historial:"))
        self.combo_estudiante = QComboBox()
        # Al elegir un alumno, actualizamos su tabla y su reporte
        self.combo_estudiante.currentIndexChanged.connect(self.generar_reporte_individual)
        layout.addWidget(self.combo_estudiante)

        # Tabla que solo mostrará las materias del alumno seleccionado
        self.tabla_individual = QTableWidget()
        self.estilizar_tabla(self.tabla_individual)
        layout.addWidget(self.tabla_individual)

        # Botón para exportar el reporte a texto
        self.btn_exportar_txt = QPushButton("💾 Guardar Reporte del Alumno (.txt)")
        self.btn_exportar_txt.clicked.connect(self.exportar_txt_alumno)
        layout.addWidget(self.btn_exportar_txt)

    def estilizar_tabla(self, tabla):
        """Ajusta los colores para que las letras no se vean muy blancas y la vista descanse"""
        # Encabezado azul oscuro con letras gris claro (mejor que blanco puro)
        estilo_header = "QHeaderView::section { background-color: #34495e; color: #ecf0f1; font-weight: bold; border: 1px solid #2c3e50; }"
        tabla.horizontalHeader().setStyleSheet(estilo_header)
        
        # Habilitamos filas de colores alternos (blanco y gris muy suave)
        tabla.setAlternatingRowColors(True)
        # El texto de la tabla será gris carbón (#2d3436) para evitar el brillo del negro puro
        tabla.setStyleSheet("alternate-background-color: #f8f9fa; color: #2d3436;")
        
        # Hacemos que las columnas se ajusten solas al ancho de la ventana
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def seleccionar_archivo(self):
        """Abre el explorador de Windows/Mac para que elijas tu archivo CSV"""
        archivo, _ = QFileDialog.getOpenFileName(self, "Buscar Archivo de Calificaciones", "", "Archivos de Datos (*.csv)")
        if archivo:
            self.cargar_datos(archivo)

    def cargar_datos(self, ruta):
        """Lógica de Pandas para leer, validar y calcular promedios automáticamente"""
        try:
            temp_df = pd.read_csv(ruta)
            
            # REQUISITO: Validar que las notas estén entre 0 y 100
            columnas_notas = ['Parcial1', 'Parcial2', 'Parcial3', 'Final']
            for col in columnas_notas:
                # .between(0, 100).all() verifica que CADA CELDA cumpla la regla
                if not temp_df[col].between(0, 100).all():
                    QMessageBox.warning(self, "Error de Datos", f"Se detectaron notas inválidas en la columna {col}. Deben ser de 0 a 100.")
                    return

            # REQUISITO: Calcular promedio automáticamente (horizontalmente por fila)
            # axis=1 significa "calcula el promedio sumando las columnas, no las filas"
            temp_df['Promedio'] = temp_df[columnas_notas].mean(axis=1).round(2)
            
            # REQUISITO: Determinar si el alumno Aprobó o Reprobó (>= 70)
            temp_df['Estado'] = temp_df['Promedio'].apply(lambda x: "APROBADO" if x >= 70 else "REPROBADO")
            
            # Guardamos el resultado en nuestra variable principal
            self.df = temp_df

            # Actualizamos los ComboBox con los datos reales del archivo
            self.combo_materia.clear()
            self.combo_materia.addItems(self.df['Materia'].unique())
            
            self.combo_estudiante.clear()
            # Ordenamos los nombres alfabéticamente para que sea fácil buscarlos
            self.combo_estudiante.addItems(sorted(self.df['Estudiante'].unique()))

            # Llenamos la tabla visual
            self.llenar_tabla_visual(self.tabla, self.df)
            QMessageBox.information(self, "Carga Exitosa", "Calificaciones cargadas y procesadas con éxito.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Lectura", f"No se pudo leer el archivo: {str(e)}")

    def llenar_tabla_visual(self, objeto_tabla, datos_df):
        """Pasa los datos del DataFrame de Pandas a la QTableWidget de PyQt6"""
        objeto_tabla.setRowCount(len(datos_df))
        objeto_tabla.setColumnCount(len(datos_df.columns))
        objeto_tabla.setHorizontalHeaderLabels(datos_df.columns)

        for i in range(len(datos_df)):
            # Obtenemos el estado para saber de qué color pintar la fila más adelante
            estado_fila = datos_df.iloc[i]['Estado']
            
            for j in range(len(datos_df.columns)):
                valor = str(datos_df.iloc[i, j])
                item = QTableWidgetItem(valor)
                
                # REQUISITO: Resaltar visualmente si aprobó o reprobó
                if j == datos_df.columns.get_loc('Estado'):
                    if valor == "REPROBADO":
                        item.setForeground(QColor("#c0392b")) # Rojo oscuro (legible)
                    else:
                        item.setForeground(QColor("#27ae60")) # Verde bosque
                
                objeto_tabla.setItem(i, j, item)

    def actualizar_analisis_materia(self):
        """Realiza cálculos estadísticos cada vez que cambias de materia en el combo"""
        if self.df is None: return
        
        materia_actual = self.combo_materia.currentText()
        # Filtramos los datos para quedarnos solo con los de esa materia
        df_filtrado = self.df[self.df['Materia'] == materia_actual]
        
        # Calculamos los KPI (indicadores clave)
        promedio_general = df_filtrado['Promedio'].mean()
        mejor_nota = df_filtrado['Promedio'].max()
        peor_nota = df_filtrado['Promedio'].min()
        total_alumnos = len(df_filtrado)
        
        # Calculamos el porcentaje de aprobados
        aprobados = len(df_filtrado[df_filtrado['Estado'] == "APROBADO"])
        tasa_exito = (aprobados / total_alumnos) * 100 if total_alumnos > 0 else 0

        # Mostramos los resultados en la etiqueta del panel
        resumen_texto = (
            f"📈 ANALIZANDO: {materia_actual}\n"
            f"----------------------------------------------------------\n"
            f"• Promedio del Grupo: {promedio_general:.2f} pts\n"
            f"• Calificación más Alta: {mejor_nota:.2f} | Más Baja: {peor_nota:.2f}\n"
            f"• Estudiantes inscritos: {total_alumnos}\n"
            f"• Tasa de Aprobación: {tasa_exito:.1f}%"
        )
        self.lbl_stats_materia.setText(resumen_texto)

    def mostrar_ranking(self):
        """Busca a los 5 mejores promedios generales de toda la escuela"""
        if self.df is None: return
        
        # Agrupamos por nombre (por si un alumno tiene varias materias) y sacamos su promedio final
        top_5 = self.df.groupby('Estudiante')['Promedio'].mean().sort_values(ascending=False).head(5)
        
        texto_ranking = "🏆 CUADRO DE HONOR - TOP 5 ESTUDIANTES 🏆\n\n"
        # Usamos enumerate(..., 1) para que el conteo empiece en 1 y no en 0
        for posicion, (nombre, promedio) in enumerate(top_5.items(), 1):
            texto_ranking += f"{posicion}º Lugar: {nombre} ({promedio:.2f} pts)\n"
        
        QMessageBox.information(self, "Ranking de Excelencia", texto_ranking)

    def mostrar_graficas_generales(self):
        """Genera las 3 visualizaciones requeridas por el ejercicio"""
        if self.df is None: return
        
        materia_sel = self.combo_materia.currentText()
        df_mat = self.df[self.df['Materia'] == materia_sel]
        
        # Definimos el lienzo de dibujo
        plt.figure("Análisis Visual del Desempeño", figsize=(14, 6))

        # 1. HISTOGRAMA: ¿Cómo se distribuyen las notas de la materia?
        plt.subplot(1, 3, 1)
        plt.hist(df_mat['Promedio'], bins=8, color='#8e44ad', edgecolor='white')
        plt.title(f"Distribución de Notas: {materia_sel}")
        plt.xlabel("Rango de Calificación")
        plt.ylabel("Número de Alumnos")

        # 2. BARRAS: Comparación de promedios entre todas las materias
        plt.subplot(1, 3, 2)
        self.df.groupby('Materia')['Promedio'].mean().plot(kind='bar', color='#2980b9')
        plt.title("Promedio General por Materia")
        plt.xticks(rotation=45) # Giramos los nombres para que se lean bien

        # 3. PASTEL: ¿Cuántos pasaron y cuántos no en toda la escuela?
        plt.subplot(1, 3, 3)
        self.df['Estado'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=['#27ae60', '#e74c3c'], startangle=90)
        plt.title("Estado Académico Global")
        plt.ylabel("") # Quitamos el nombre del eje que sale por defecto

        plt.tight_layout() # Evita que las gráficas se pisen entre sí
        plt.show()

    def generar_reporte_individual(self):
        """Muestra los datos y la gráfica de evolución de un solo alumno"""
        if self.df is None: return
        
        nombre_alumno = self.combo_estudiante.currentText()
        # Filtramos el DataFrame para obtener solo las filas de ese estudiante
        df_individual = self.df[self.df['Estudiante'] == nombre_alumno]
        
        # Rellenamos la tabla de la segunda pestaña
        self.llenar_tabla_visual(self.tabla_individual, df_individual)

    def exportar_txt_alumno(self):
        """Guarda un reporte detallado en un archivo .txt"""
        if self.df is None: return
        
        alumno = self.combo_estudiante.currentText()
        df_alu = self.df[self.df['Estudiante'] == alumno]
        
        # Nombre de archivo sin espacios
        nombre_archivo = f"Reporte_{alumno.replace(' ', '_')}.txt"
        
        try:
            with open(nombre_archivo, "w", encoding='utf-8') as f:
                f.write(f"REPORTE ACADÉMICO INDIVIDUAL\n")
                f.write(f"Estudiante: {alumno}\n")
                f.write(f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n")
                f.write("="*40 + "\n\n")
                f.write(df_alu[['Materia', 'Promedio', 'Estado']].to_string(index=False))
                f.write(f"\n\nPromedio General Final: {df_alu['Promedio'].mean():.2f}")
            
            QMessageBox.information(self, "Exportación Exitosa", f"El reporte de {alumno} se ha guardado en la carpeta del proyecto.")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

# --- INICIO DEL PROGRAMA ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AnalizadorAcademico()
    ventana.show()
    sys.exit(app.exec())