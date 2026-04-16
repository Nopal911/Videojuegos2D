import pandas as pd
# Cargar datos de ventas
df = pd.read_csv('ventas.csv')
# Explorar datos
print(f"Dimensiones: {df.shape}")
print(df.head())
print(df.info())
# Limpiar datos
df = df.dropna() # Eliminar valores nulos
df = df.drop_duplicates() # Eliminar duplicados
# Filtrar ventas mayores a $1000
ventas_altas = df[df['total'] > 1000]
# Agrupar por mes y calcular total
ventas_mes = df.groupby('mes')['total'].sum()
print(ventas_mes)
# Crear nueva columna
df['ganancia'] = df['total'] - df['costo']
# Estadísticas
print(f"Promedio de ventas: ${df['total'].mean():.2f}")
print(f"Venta máxima: ${df['total'].max():.2f}")
# Exportar resultados
df.to_excel('reporte_ventas.xlsx', index=False)