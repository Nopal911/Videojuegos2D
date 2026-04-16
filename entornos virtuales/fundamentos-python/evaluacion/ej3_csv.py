import pandas as pd
import numpy as np

nombres = ['Ana García', 'Luis Pérez', 'María López', 'Carlos Ruiz', 
           'Sofía Martínez', 'Pedro Sánchez', 'Laura Torres', 'Diego Ramírez',
           'Carmen Flores', 'Miguel Ángel Castro']
materias = ['Matemáticas', 'Física', 'Química', 'Historia', 'Literatura']
data = []

for nombre in nombres:
    for materia in materias:
        data.append({
            'Estudiante': nombre,
            'Materia': materia,
            'Parcial1': np.random.randint(40, 100), # Bajé un poco el rango para ver reprobados
            'Parcial2': np.random.randint(40, 100),
            'Parcial3': np.random.randint(40, 100),
            'Final': np.random.randint(40, 100)
        })

df = pd.DataFrame(data)
df.to_csv('calificaciones.csv', index=False)
print("Archivo 'calificaciones.csv' creado.")