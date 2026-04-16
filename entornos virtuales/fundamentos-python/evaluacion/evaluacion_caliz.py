import pandas as pd
import matplotlib.pyplot as plt

# --- A. CARGAR DATOS ---
# Leemos el archivo
df = pd.read_csv('clima.csv')

# Convertimos la columna 'Fecha' a formato de fecha real (muy importante para gráficas)
df['Fecha'] = pd.to_datetime(df['Fecha'])

# --- B. LIMPIEZA Y VALIDACIÓN ---
# Filtramos errores: Solo queremos temperaturas lógicas (-50 a 50)
df = df[ (df['Temperatura_Max'] >= -50) & (df['Temperatura_Max'] <= 50) ]

# --- C. CÁLCULOS DIARIOS ---
# 1. Calcular el Promedio Diario (Suma / 2)
df['Promedio'] = (df['Temperatura_Max'] + df['Temperatura_Min']) / 2

# 2. Asignar Colores (Lógica simple con una función)
def asignar_color(temp):
    if temp < 10:
        return 'Azul'
    elif temp <= 25:
        return 'Verde'
    else:
        return 'Naranja'

# Aplicamos la función a cada fila
df['Color'] = df['Promedio'].apply(asignar_color)

# --- D. ESTADÍSTICAS (Resultados) ---
# Encontramos la temperatura máxima y mínima
temp_maxima = df['Temperatura_Max'].max()
temp_minima = df['Temperatura_Min'].min()
promedio_anual = df['Promedio'].mean()

# Contamos cuántos días llovió (donde Precipitación > 0)
dias_con_lluvia = df[df['Precipitación'] > 0]
total_dias_lluvia = len(dias_con_lluvia)

print("--- RESULTADOS ---")
print(f"Temperatura más alta del año: {temp_maxima} °C")
print(f"Temperatura más baja del año: {temp_minima} °C")
print(f"Promedio de temperatura anual: {round(promedio_anual, 2)} °C")
print(f"Días que llovió: {total_dias_lluvia}")


# --- E. GRÁFICAS ---

# GRÁFICA 1: Temperaturas
plt.figure(figsize=(10, 6)) # Tamaño de la imagen
plt.plot(df['Fecha'], df['Temperatura_Max'], color='red', label='Máxima')
plt.plot(df['Fecha'], df['Temperatura_Min'], color='blue', label='Mínima')
plt.plot(df['Fecha'], df['Promedio'], color='green', label='Promedio')

# Tendencia (Media Móvil de 7 días)
# .rolling(7).mean() calcula el promedio de los últimos 7 días automáticamente
df['Tendencia'] = df['Promedio'].rolling(7).mean()
plt.plot(df['Fecha'], df['Tendencia'], color='black', linestyle='--', label='Tendencia (7 días)')

plt.title('Comportamiento de la Temperatura')
plt.xlabel('Fecha')
plt.ylabel('Grados Centígrados')
plt.legend() # Muestra el cuadro con los nombres de las líneas
plt.show()

# GRÁFICA 2: Lluvia por día
plt.figure(figsize=(10, 6))
plt.bar(df['Fecha'], df['Precipitación'], color='skyblue')
plt.title('Lluvia Diaria')
plt.ylabel('Cantidad de Lluvia (mm)')
plt.show()

# GRÁFICA 3: Promedio por Mes
# Creamos una columna 'Mes' para poder agrupar
df['Mes'] = df['Fecha'].dt.month
# Agrupamos por mes y calculamos el promedio de la temperatura
promedio_mensual = df.groupby('Mes')['Promedio'].mean()

plt.figure(figsize=(10, 6))
promedio_mensual.plot(kind='bar', color='orange')
plt.title('Temperatura Promedio por Mes')
plt.xlabel('Mes (1=Enero, 12=Diciembre)')
plt.ylabel('Temperatura Promedio')
plt.show()