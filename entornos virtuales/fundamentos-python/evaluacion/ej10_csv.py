import pandas as pd
import numpy as np
from datetime import datetime, timedelta

servicios = ['Atención al Cliente', 'Soporte Técnico', 'Ventas', 'Post-Venta', 'Delivery']
data = []
start_date = datetime(2024, 1, 1)

# Generamos 500 encuestas de ejemplo
for i in range(500):
    # Generamos puntajes de aspectos (1 a 5)
    atencion = np.random.randint(1, 6)
    rapidez = np.random.randint(1, 6)
    precio = np.random.randint(1, 6)
    
    # Calculamos una puntuación general lógica basada en los aspectos
    promedio_aspectos = (atencion + rapidez + precio) / 3
    puntuacion = int(np.clip(promedio_aspectos * 2 + np.random.normal(0, 1), 1, 10))
    
    data.append({
        'ID_Encuesta': f'ENC-{i+1:05d}',
        'Fecha': (start_date + timedelta(days=np.random.randint(0, 180))).strftime('%Y-%m-%d'),
        'Servicio': np.random.choice(servicios),
        'Puntuación_General': puntuacion,
        'Atención': atencion,
        'Rapidez': rapidez,
        'Precio': precio,
        'Recomendaría': 'Sí' if puntuacion >= 7 else np.random.choice(['Sí', 'No'], p=[0.3, 0.7])
    })

df = pd.DataFrame(data)
df.to_csv('encuestas_satisfaccion.csv', index=False)
print("Archivo 'encuestas_satisfaccion.csv' creado con éxito.")