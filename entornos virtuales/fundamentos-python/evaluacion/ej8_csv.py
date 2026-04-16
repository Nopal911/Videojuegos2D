import pandas as pd
import numpy as np
from datetime import datetime, timedelta

proyectos = ['Sistema CRM', 'App Móvil', 'Dashboard Analytics', 'API REST']
desarrolladores = ['Dev1', 'Dev2', 'Dev3', 'Dev4', 'Dev5']
estados = ['Por Hacer', 'En Progreso', 'En Revisión', 'Completada']
prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
tareas_tipo = ['Diseño', 'Desarrollo', 'Testing', 'Bug Fix', 'Documentación']

data = []
# Fecha inicial para simular semanas
start_date = datetime(2024, 1, 1)

for i in range(200):
    horas_est = np.random.randint(4, 40)
    # Generamos una fecha aleatoria en un rango de 12 semanas
    fecha_tarea = start_date + timedelta(days=np.random.randint(0, 84))
    
    data.append({
        'ID_Tarea': f'TASK-{i+1:04d}',
        'Fecha': fecha_tarea.strftime('%Y-%m-%d'),
        'Proyecto': np.random.choice(proyectos),
        'Tarea': f'{np.random.choice(tareas_tipo)} - Tarea {i+1}',
        'Asignado_A': np.random.choice(desarrolladores),
        'Estado': np.random.choice(estados, p=[0.2, 0.3, 0.2, 0.3]),
        'Prioridad': np.random.choice(prioridades, p=[0.3, 0.4, 0.2, 0.1]),
        'Horas_Estimadas': horas_est,
        'Horas_Reales': int(horas_est * np.random.uniform(0.7, 1.3))
    })

df = pd.DataFrame(data)
df.to_csv('proyectos_software.csv', index=False)
print("Archivo 'proyectos_software.csv' creado con éxito.")