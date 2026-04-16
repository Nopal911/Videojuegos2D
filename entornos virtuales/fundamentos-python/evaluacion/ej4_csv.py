import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 1. Configuración de datos iniciales
categorias = ['Alimentación', 'Transporte', 'Vivienda', 'Entretenimiento', 'Salud', 'Otros']
metodos = ['Efectivo', 'Tarjeta', 'Transferencia']
descripciones = {
    'Alimentación': ['Supermercado', 'Restaurante', 'Comida rápida'],
    'Transporte': ['Gasolina', 'Uber', 'Transporte público'],
    'Vivienda': ['Renta', 'Servicios', 'Internet'],
    'Entretenimiento': ['Cine', 'Streaming', 'Concierto'],
    'Salud': ['Farmacia', 'Doctor', 'Gimnasio'],
    'Otros': ['Ropa', 'Regalos', 'Varios']
}

data = []
start_date = datetime(2024, 1, 1)
num_transacciones = 180

# 2. Generación de datos
print("Generando transacciones...")
for i in range(num_transacciones):
    cat = np.random.choice(categorias)
    
    # Creamos el registro individual
    registro = {
        'Fecha': (start_date + timedelta(days=np.random.randint(0, 180))).strftime('%Y-%m-%d'),
        'Categoría': cat,
        'Descripción': np.random.choice(descripciones[cat]),
        # CORRECCIÓN: round() de Python para un float individual de numpy
        'Monto': round(float(np.random.uniform(50, 2000)), 2),
        'Método_Pago': np.random.choice(metodos)
    }
    data.append(registro)

# 3. Creación y procesamiento del DataFrame
df = pd.DataFrame(data)

# Convertimos la columna Fecha a objeto datetime para ordenar correctamente
df['Fecha'] = pd.to_datetime(df['Fecha'])
df = df.sort_values('Fecha')

# 4. Exportación
nombre_archivo = 'gastos.csv'
df.to_csv(nombre_archivo, index=False)

print(f"--- Proceso Finalizado ---")
print(f"Archivo '{nombre_archivo}' creado con {len(df)} registros.")
print("\nPrimeras 5 filas del archivo:")
print(df.head())