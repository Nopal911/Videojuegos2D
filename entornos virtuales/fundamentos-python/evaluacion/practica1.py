import numpy as np
# Crear array de datos de ventas
ventas = np.array([1200, 1500, 1800, 1300, 2000, 1700])
# Calcular estadísticas
promedio = np.mean(ventas)
desviacion = np.std(ventas)
total = np.sum(ventas)
mejor_mes = np.argmax(ventas)
print(f"Promedio de ventas: ${promedio:.2f}")
print(f"Desviación estándar: ${desviacion:.2f}")
print(f"Total: ${total}")
print(f"Mejor mes: {mejor_mes + 1}")
# Crear matriz de correlación
datos = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
correlacion = np.corrcoef(datos)