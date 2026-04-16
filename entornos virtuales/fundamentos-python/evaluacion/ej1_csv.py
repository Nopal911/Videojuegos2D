import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuración de datos aleatorios
regiones = ['Norte', 'Sur', 'Este', 'Oeste', 'Centro']
productos = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Impresora']
data = []

# Generamos 200 filas de datos
for i in range(200):
    data.append({
        'Región': np.random.choice(regiones),
        'Fecha': (datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d'),
        'Producto': np.random.choice(productos),
        'Ventas': np.random.randint(1000, 10000),
        'Unidades': np.random.randint(1, 50)
    })

# Guardamos el archivo
df = pd.DataFrame(data)
df.to_csv('ventas_regiones.csv', index=False)
print("Archivo 'ventas_regiones.csv' creado con éxito.")