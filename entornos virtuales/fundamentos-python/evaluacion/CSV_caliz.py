import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- PASO 1: CREAR EL ARCHIVO CSV (Simulación de datos) ---
data = []
start_date = datetime(2024, 1, 1)

# Usamos un bucle simple for para crear 365 días
for i in range(365):
    fecha = start_date + timedelta(days=i)
    
    # Generamos temperaturas aleatorias simples
    t_max = np.random.uniform(15, 35) # Entre 15 y 35 grados
    t_min = t_max - np.random.uniform(5, 15) # Mínima es Max menos algo
    
    # Redondeamos a 1 decimal
    t_max = round(t_max, 1)
    t_min = round(t_min, 1)
    
    # Lluvia: A veces 0, a veces un número positivo
    lluvia = 0
    if np.random.random() > 0.7: # 30% de probabilidad de lluvia
        lluvia = round(np.random.uniform(1, 20), 1)

    data.append({
        'Fecha': fecha,
        'Temperatura_Max': t_max,
        'Temperatura_Min': t_min,
        'Humedad': round(np.random.uniform(30, 90), 0),
        'Precipitación': lluvia,
        'Velocidad_Viento': round(np.random.uniform(0, 30), 1)
    })

# Guardamos en un archivo
df = pd.DataFrame(data)
df.to_csv('clima.csv', index=False)
print("Archivo 'clima.csv' creado exitosamente.")
    


    