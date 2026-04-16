import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# Configuración de datos aleatorios
productos = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Impresora']
data = []
    
# Generamos 20 datos
for i in range(20):
    
    Cantidad = np.random.randint(1,10)
    Precio = round(np.random.uniform(200,2000),2)
    Total = (Cantidad * Precio)
    Venta_total = Total * Cantidad
    Promedio_total = Venta_total / len(productos)
    
    data.append({
        'Producto': np.random.choice(productos),
        'Cantidad': Cantidad,
        'Precio': Precio,
        'Total': Total,
        'Venta_Total': Venta_total,
        'Promedio': Promedio_total
    })
    
# Guardamos el archivo
df = pd.DataFrame(data)
df.to_csv('examen5.csv', index=False)
print("Archivo 'examen5.csv' creado con éxito.")



"""
    1. Analizador Básico de Ventas
Objetivo
Aplicación con botón para cargar un CSV de ventas.
CSV
Producto, Cantidad, Precio
Requisitos
● Cargar archivo con QFileDialog
● Mostrar datos en QTableWidget
● Crear columna Total (Cantidad × Precio)
● Mostrar:
○ Venta total
○ Promedio de ventas
● Gráfica de barras por producto
    """
    
    