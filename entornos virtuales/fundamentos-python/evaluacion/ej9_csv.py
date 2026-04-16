import pandas as pd
import numpy as np
from datetime import datetime, timedelta

turnos = ['Mañana', 'Tarde', 'Noche']
lineas = ['L1', 'L2', 'L3', 'L4']
operadores = [f'OP{i:02d}' for i in range(1, 13)]
data = []
start_date = datetime(2024, 1, 1)

# Generamos 360 registros (simulando 120 días con 3 turnos cada uno)
for i in range(360):
    fecha = start_date + timedelta(days=i // 3)
    turno = turnos[i % 3]
    
    for linea in lineas:
        produccion_base = np.random.randint(800, 1200)
        data.append({
            'Fecha': fecha.strftime('%Y-%m-%d'),
            'Turno': turno,
            'Línea': linea,
            'Unidades_Producidas': produccion_base,
            'Unidades_Defectuosas': int(produccion_base * np.random.uniform(0.01, 0.08)),
            'Tiempo_Paro': np.random.randint(0, 60),
            'Operador': np.random.choice(operadores)
        })

df = pd.DataFrame(data)
df.to_csv('produccion_industrial.csv', index=False)
print("Archivo 'produccion_industrial.csv' creado.")